import time
from PIL import Image
from mss import mss
import win32gui
import cv2
import numpy as np

class GameWindowCapture:
    """
    游戏窗口捕获类 (基于 MSS)
    用于捕获使用 DirectX/OpenGL 渲染的游戏窗口
    """
    def __init__(self, window_title):
        """
        初始化窗口捕获器
        :param window_title: 要捕获的游戏窗口标题
        """
        # 根据窗口标题查找窗口句柄 (hwnd)
        self.hwnd = win32gui.FindWindow(None, window_title)
        if not self.hwnd:
            raise ValueError(f"找不到窗口: {window_title}")
        # 获取窗口的屏幕坐标 (left, top, right, bottom), GetWindowRect 返回的是屏幕坐标系中的矩形区域
        self.rect = win32gui.GetWindowRect(self.hwnd)
        # 构造 MSS 所需的监控区域字典
        # MSS 需要明确的 top, left, width, height 来指定截图区域
        self.monitor = {
            "top": self.rect[1],
            "left": self.rect[0],
            "width": self.rect[2] - self.rect[0],
            "height": self.rect[3] - self.rect[1]
        }
        self.sct = mss()

    def capture(self):
        """
        捕获当前窗口的一帧画面
        :return: PIL.Image 对象 (RGB 模式)
        """
        # 执行截图操作
        # grab 方法会直接从显存读取指定区域的像素数据
        sct_img = self.sct.grab(self.monitor)
        # 格式转换与返回
        # sct_img 的原始数据是 BGRA 格式（带透明度通道）
        # 这里转换为 PIL 图像，去掉 Alpha 通道，转为 RGB 格式供后续处理
        img_pil = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        # 再转成 OpenCV Mat
        img_np = np.array(img_pil)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        return img_cv

    def start_loop_capture(self, callback_func, frequency=5):
        """
        启动循环截图。

        :param callback_func: 一个回调函数，它将接收到截取到的PIL Image对象作为参数。
                              例如: lambda img: img.save(f"screenshot_{int(time.time())}.png")
        :param frequency: 截图频率，单位 Hz
        """
        interval = 1.0 / frequency
        print(f"开始以 {frequency}Hz 的频率监视窗口...")
        print("按 Ctrl+C 停止。")
        
        try:
            while True:
                start_time = time.time()                
                # 检查窗口是否仍然存在
                if not win32gui.IsWindow(self.hwnd):
                    print(f"窗口已关闭，停止监视。")
                    break                
                # 执行截图
                image = self.capture()                
                # 调用用户定义的回调函数处理图像
                callback_func(image)                
                # 控制循环频率
                elapsed = time.time() - start_time
                sleep_time = interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("\n用户中断，停止监视。")


# --- 主程序 ---
if __name__ == "__main__":
    # 1. 首先确定要监视的窗口标题
    TARGET_WINDOW_TITLE = "赛马娘(繁中服)"

    # 2. 创建窗口捕获实例
    try:
        wc = GameWindowCapture(window_title=TARGET_WINDOW_TITLE)
        print(f"成功找到窗口: {TARGET_WINDOW_TITLE}")
    except ValueError as e:
        print(e)
        exit()

    # 3. 定义一个回调函数来处理每一帧图像
    counter = 0
    def process_image(img):
        global counter
        counter += 1
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        filename = f"capture_frame_{counter:05d}.png"
        img_pil.save(filename)
        print(f"已保存第 {counter} 帧: {filename}", end='\r') # \r 让输出在同一行刷新

    # 4. 启动循环截图
    wc.start_loop_capture(process_image, frequency=1)
