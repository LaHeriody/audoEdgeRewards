import requests
from bs4 import BeautifulSoup
import re

def fetch_poems():
    # 目标URL
    url1 = 'https://www.gushiwen.cn/default_1.aspx'
    url2 = 'https://www.gushiwen.cn/default_2.aspx'
    url3 = 'https://www.gushiwen.cn/default_3.aspx'
    url4 = 'https://www.gushiwen.cn/default_4.aspx'
    poems = []

    urls = [url1, url2, url3, url4]
    for url in urls:
        # 发送GET请求
        response = requests.get(url)
        response.encoding = 'utf-8'

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
            
        for sons in soup.find_all("div", class_="sons"):
            cont = sons.find("div", class_="cont")
            if not cont:
                continue

            try:
                # 1. 标题
                title_tag = cont.find("p").find("a")
                title = title_tag.get_text(strip=True) if title_tag else ""

                # 2. 作者 + 朝代
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

                # 3. 内容
                contson = cont.find("div", class_="contson")
                if contson:
                    # 保留诗词换行
                    content = contson.get_text(separator="\n", strip=True)
                else:
                    content = ""

                # print("标题：", title)
                # print("作者：", author)
                # print("朝代：", dynasty)
                # print("内容：\n", content)
                # print("="*40)

                poems.append({
                    "title": title,
                    "author": author,
                    "dynasty": dynasty,
                    "content": content
                })
            except Exception as e:
                continue

    contents = []
    for poem in poems:
        contents.extend(re.split("\n|，|。|！", poem["content"]))
    contents = [line.strip() for line in contents if line.strip()]
    
    return contents
