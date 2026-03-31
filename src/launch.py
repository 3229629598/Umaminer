import os
import psutil
from vision import Vision
from screen import ScreenCapture
import time
import logging
import sys

TARGET_WINDOW_TITLE = "赛马娘(繁中服)"
FREQUENCY = 5

class Launch:
    """
    启动程序
    """
    def __init__(self):
        # 获取程序PID
        self.process = psutil.Process(os.getpid())
        # 配置日志格式和级别
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [%(threadName)s] - %(message)s',
            handlers=[
                logging.StreamHandler(),  # 输出到控制台
                # logging.FileHandler('umaminer.log')  # 同时输出到文件
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.drop_cnt = 0

        try:
            self.sc = ScreenCapture(window_title=TARGET_WINDOW_TITLE)
            self.logger.info(f"成功找到窗口: {TARGET_WINDOW_TITLE}")
        except ValueError as e:
            print(e)
            exit()

        self.detector = Vision(template_path = './img/coin.png', threshold=0.6)
        self.logger.info(f"开始以 {FREQUENCY}Hz 的频率监视窗口...")
        self.logger.info("按 Ctrl+C 停止")

    def process_image(self,img):
        """
        定时器回调函数
        :param img: cv2.Mat 图像
        """
        self.detector.loop(img_cv = img, x_min=20, x_max=250)
        mem = self.process.memory_info().rss / 1024 / 1024  # 字节 → MB
        #print(f"掉落次数: {detector.drop_cnt} , 程序占用内存: {mem:.1f} MB", end='\r')
        if self.drop_cnt < self.detector.drop_cnt:
            self.drop_cnt = self.detector.drop_cnt
            sys.stdout.flush()
            self.logger.info("掉落一次")
        # 使用 sys.stdout.write 实现覆盖式输出
        sys.stdout.write(f"掉落次数: {self.drop_cnt}，程序占用内存: {mem:.1f} MB\r")
        sys.stdout.flush()  # 强制刷新缓冲区

    def loop(self):
        try:
            self.sc.tim_loop_capture(self.process_image, FREQUENCY)
            while True:
                time.sleep(0.1)  # 让主线程短暂休眠，避免空转导致接收不到键盘中断信号
        except KeyboardInterrupt:
            self.sc.stop_capture()
            self.logger.info("用户中断, 停止监视。")
            self.logger.info(f"总共掉落 {self.drop_cnt} 次。")

if __name__ == "__main__":
    launch = Launch()
    launch.loop()
