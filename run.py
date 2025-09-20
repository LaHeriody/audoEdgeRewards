# pyautogui_automate.py
# 要求: pip install pyautogui pygetwindow
# 注意: 在运行前把要操作的窗口激活到前台，脚本会按当前焦点窗口执行按键。
import time
import random
import argparse
import sys
import pyautogui
import pyperclip
from pywinauto import Desktop

# Fail-safe: 将鼠标移到屏幕左上角可立即中断脚本
pyautogui.FAILSAFE = True


def rand_sleep(base, jitter):
    """短随机延迟，减少机械感"""
    time.sleep(base + random.uniform(-jitter, jitter))
    # time.sleep(base)


def main(m, initial_delay=5, wait_time=0.8, debug=False):
    print(f"脚本将在 {initial_delay} 秒后开始。FAILSAFE 激活（将鼠标移到屏幕左上角可终止）。")
    for i in range(initial_delay, 0, -1):
        print(f"开始倒计时：{i}...", end="\r")
        time.sleep(1)
    print("\n开始执行。按 Ctrl+C 可中止（或把鼠标移到屏幕左上角）。")

    try:
        from crawl import fetch_poems
        contents = fetch_poems()
        contents = random.sample(contents, min(400, len(contents)))
        iterator = iter(contents)
        for i in range(1, m+1):
            if debug:
                print(f"[{i}/{m}] 激活所有 Edge 窗口并执行 Ctrl+E / Ctrl+V / Enter")
            windows = Desktop(backend="uia").windows()  # 获取所有窗口
            target_windows = []
            target_windows.extend([w for w in windows if w.window_text().endswith("Edge")])
            target_windows.extend([w for w in windows if w.window_text().endswith("Chrome")])
            print(f"找到 {len(target_windows)} 个标题以 'Edge' 或 'Chrome' 结尾的窗口。")
            target_windows = target_windows[::-1]

            for win in target_windows:
                pyperclip.copy(next(iterator))  # 复制内容到剪贴板
                # text = f"Hello, world!  {i}  {edge_windows.index(win)+1}/{len(edge_windows)}"
                # pyperclip.copy(text)
                win.set_focus()
                pyautogui.hotkey('ctrl', 'e')
                pyautogui.hotkey('ctrl', 'e')
                rand_sleep(wait_time, 0.3)
                # Ctrl+V (粘贴)
                pyautogui.hotkey('ctrl', 'v')
                rand_sleep(wait_time, 0.3)
                # Enter
                pyautogui.press('enter')
                rand_sleep(wait_time, 0.3)

            rand_sleep(wait_time, 0.3)
        print("所有循环完成。")
    except KeyboardInterrupt:
        print("\n用户中断 (KeyboardInterrupt)。脚本终止。")
    except pyautogui.FailSafeException:
        print("\nFailSafe 触发：鼠标移到左上角，已终止。")
    except Exception as e:
        print(f"\n发生异常: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PyAutoGUI 自动按键脚本：循环 m 次")
    parser.add_argument("--m", type=int, default=40, help="循环次数 (默认 40)")
    parser.add_argument("--delay", type=int, default=5, help="开始前的初始倒计时（秒））（默认 5）")
    parser.add_argument("--wait", type=int, default=1, help="每次循环之间的等待时间（秒））（默认 1）")
    parser.add_argument("--debug", action="store_true", help="打印更多调试信息")
    args = parser.parse_args()
    # 小保护：防止误用把 m 设置过大
    if args.m <= 0:
        print("m 必须为正整数。")
        sys.exit(1)
    if args.m > 100:
        print("警告：m 超过 100，确认是否真的要这么多。继续请再次运行并设置 --m 大于 100。")
        sys.exit(1)

    main(args.m, initial_delay=args.delay, wait_time=args.wait, debug=args.debug)
