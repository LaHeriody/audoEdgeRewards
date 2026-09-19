import datetime
import os
import pickle
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


CACHE_DIR = Path(__file__).resolve().parent / "crawl_cache"
CACHE_FILE_PATTERN = re.compile(r"poems_(\d{4}-\d{2}-\d{2})\.pkl")


def _cache_file_for_today():
    today = datetime.date.today().isoformat()
    return CACHE_DIR / f"poems_{today}.pkl"


def _save_successful_crawl(contents):
    """原子写入当天缓存，避免中途中断留下损坏文件。"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _cache_file_for_today()
    temporary_file = cache_file.with_suffix(cache_file.suffix + ".tmp")

    with temporary_file.open("wb") as file:
        pickle.dump(contents, file)
    os.replace(temporary_file, cache_file)

    return cache_file


def _load_latest_successful_crawl():
    """按文件名中的日期倒序查找，损坏的缓存会被跳过。"""
    if not CACHE_DIR.exists():
        return None, None

    candidates = []
    try:
        for cache_file in CACHE_DIR.iterdir():
            match = CACHE_FILE_PATTERN.fullmatch(cache_file.name)
            if match:
                candidates.append((match.group(1), cache_file))
    except OSError as error:
        print(f"缓存目录读取失败：{CACHE_DIR}（{error}）")
        return None, None

    for _, cache_file in sorted(candidates, reverse=True):
        try:
            with cache_file.open("rb") as file:
                contents = pickle.load(file)
            if isinstance(contents, list) and contents:
                return contents, cache_file
            print(f"缓存文件为空或格式无效，已跳过：{cache_file}")
        except Exception as error:
            print(f"缓存文件读取失败，已跳过：{cache_file}（{error}）")

    return None, None


def _crawl_poems():
    """从网站抓取诗词；只有全部页面成功时才视为本次抓取成功。"""
    urls = [f'https://www.gushiwen.cn/default_{i}.aspx' for i in range(10)]
    poems = []

    for url in urls:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        for sons in soup.find_all("div", class_="sons"):
            cont = sons.find("div", class_="cont")
            if not cont:
                continue

            try:
                title_tag = cont.find("p").find("a")
                title = title_tag.get_text(strip=True) if title_tag else ""

                source_p = cont.find("p", class_="source")
                if source_p:
                    author_tags = source_p.find_all("a")
                    if len(author_tags) >= 2:
                        author = author_tags[0].get_text(strip=True)
                        dynasty = author_tags[1].get_text(strip=True)
                    else:
                        author, dynasty = "", ""
                else:
                    author, dynasty = "", ""

                contson = cont.find("div", class_="contson")
                content = contson.get_text(separator="\n", strip=True) if contson else ""

                poems.append({
                    "title": title,
                    "author": author,
                    "dynasty": dynasty,
                    "content": content
                })
            except (AttributeError, TypeError):
                continue

    contents = []
    for poem in poems:
        contents.extend(re.split("\n|，|。|！|：|？|；", poem["content"]))
    contents = [line.strip() for line in contents if line.strip()]

    if not contents:
        raise ValueError("爬取结果为空")

    return contents


def fetch_poems():
    try:
        contents = _crawl_poems()
    except Exception as error:
        cached_contents, cache_file = _load_latest_successful_crawl()
        if cached_contents is None:
            raise RuntimeError(
                f"当天爬取失败，且没有可用的历史成功缓存：{error}"
            ) from error
        print(f"当天爬取失败（{error}），改用最近一次成功缓存：{cache_file}")
        return cached_contents

    try:
        cache_file = _save_successful_crawl(contents)
        print(f"爬取成功，已保存缓存：{cache_file}")
    except OSError as error:
        # 缓存失败不应丢弃本次已经成功获取的数据。
        print(f"爬取成功，但缓存写入失败：{error}")

    return contents
