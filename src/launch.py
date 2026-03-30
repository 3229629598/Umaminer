import os
import psutil
from vision import Vision
from touch import GameWindowCapture

process = psutil.Process(os.getpid())

TARGET_WINDOW_TITLE = "赛马娘(繁中服)"

try:
    wc = GameWindowCapture(window_title=TARGET_WINDOW_TITLE)
    print(f"成功找到窗口: {TARGET_WINDOW_TITLE}")
except ValueError as e:
    print(e)
    exit()

detector = Vision(template_path = './img/coin.png', threshold=0.6)

def process_image(img):
    detector.loop(img_cv = img)
    mem = process.memory_info().rss / 1024 / 1024  # 字节 → MB
    print(f"掉落次数: {detector.drop_cnt} , 程序占用内存: {mem:.1f} MB", end='\r')

wc.start_loop_capture(process_image, frequency=5)
