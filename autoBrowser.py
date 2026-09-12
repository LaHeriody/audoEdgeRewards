import time
import pyautogui

# print("按 Ctrl+C 停止，当前鼠标屏幕坐标：")
# try:
#     while True:
#         x, y = pyautogui.position()
#         position_str = f"X: {x:4d} Y: {y:4d}"
#         print(position_str, end="\r")
# except KeyboardInterrupt:
#     print("\n结束。")

# ---------- 屏幕坐标参数（你测得的） ----------
A = (1860, 60)          # 固定点击点 A
B_x = 1700              # B 的 x 坐标（固定）
B_y_base = 395          # B 的基础 y 坐标
delta = 31.875          # 每次循环 B 的 y 增量
repeat = 17             # 循环次数（0～repeat-1）
wait_between = 2        # 两次点击间的等待时间（秒）
# -------------------------------------------

def is_top_left():
    """检测鼠标是否位于屏幕左上角（安全区域）"""
    x, y = pyautogui.position()
    return x < 10 and y < 10

# --------------------------------
print("请将目标窗口（浏览器）置于最前，程序将在 3 秒后开始点击...")
print("提示：将鼠标移到屏幕左上角可随时停止程序。")
time.sleep(3)

try:
    # 初始点击前检测
    if is_top_left():
        print("检测到鼠标在左上角，停止程序。")
        raise KeyboardInterrupt

    pyautogui.click(A[0], A[1])
    time.sleep(wait_between)
    pyautogui.click(B_x, B_y_base)
    time.sleep(wait_between)

    for times in range(repeat):
        # 每次循环开始前检测
        if is_top_left():
            print("检测到鼠标移到左上角，停止程序。")
            raise KeyboardInterrupt

        # 1. 点击 A
        pyautogui.click(A[0], A[1])
        print(f"第{times+1}轮：点击 A {A}")
        time.sleep(wait_between)

        # 点击 B 前再次检测
        if is_top_left():
            print("检测到鼠标移到左上角，停止程序。")
            raise KeyboardInterrupt

        # 2. 点击 B + times * delta （y 坐标取整）
        target_y = int(B_y_base + times * delta)   # 取整（向下取整）
        pyautogui.click(B_x, target_y)
        print(f"第{times+1}轮：点击 B 偏移点 ({B_x}, {target_y})")
        time.sleep(wait_between)

    print("所有点击完成！")
except KeyboardInterrupt:
    print("\n结束。")