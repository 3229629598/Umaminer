import win32gui
import win32ui
import win32con
from PIL import Image
import time
import threading
import cv2
import numpy as np

class ScreenCapture:
    """
    窗口捕获, 解决被遮挡问题
    """
    def __init__(self, window_title):
        # 1. 获取窗口句柄
        self.hwnd = win32gui.FindWindow(None, window_title)
        if not self.hwnd:
            raise ValueError(f"找不到窗口: {window_title}")
        
        # 2. 获取客户区尺寸
        rect = win32gui.GetClientRect(self.hwnd)
        self.width = rect[2] - rect[0]
        self.height = rect[3] - rect[1]
        
        # 3. 预创建DC和位图
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        
        self.saveBitMap = win32ui.CreateBitmap()
        self.saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.width, self.height)
        self.saveDC.SelectObject(self.saveBitMap)

        self._running = False
        self._thread = None

    def capture(self):
        """
        捕获当前窗口的一帧画面
        :return: cv2.Mat 图像
        """
        # 直接使用数值 0x40000000，不引用 win32con
        # SRCCOPY = 0x00CC0020
        # CAPTUREBLT = 0x40000000
        win32gui.BitBlt(
            self.saveDC.GetSafeHdc(),
            0, 0,
            self.width, self.height,
            self.hwndDC,
            0, 0,
            0x00CC0020 | 0x40000000  # 直接写常量值，避免导入错误
        )

        # 转换为 PIL Image
        bmp_info = self.saveBitMap.GetInfo()
        bmp_str = self.saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_str,
            'raw',
            'BGRX',
            0,
            1
        )
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img_cv
    
    def tim_loop_capture(self, callback_func, frequency=5):
        """
        定时器截图, 独立线程
        :param callback_func: 回调函数, 将截取到的Image对象作为参数
        :param frequency: 截图频率，单位 Hz
        """
        if self._running:
            #print("⚠️ 截图线程已在运行中")
            return
        self._running = True
        interval = 1.0 / frequency

        def capture_thread():
            try:
                while self._running:
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
            finally:
                self._running = False
        
        # 创建并启动线程
        self._thread = threading.Thread(target=capture_thread, daemon=False)
        self._thread.start()

    def stop_capture(self):
        """
        停止截图循环，并等待线程结束。
        """
        if self._running:
            self._running = False            
            if self._thread and self._thread.is_alive():
                self._thread.join() # 等待线程结束
        else:
            return

    def __del__(self):
        """
        析构函数，释放资源
        """
        try:
            win32gui.DeleteObject(self.saveBitMap.GetHandle())
            self.saveDC.DeleteDC()
            self.mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, self.hwndDC)
        except:
            pass

# 测试
if __name__ == "__main__":
    try:
        capture = ScreenCapture("赛马娘(繁中服)")
        img_cv = capture.capture()
        img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        img.save("screen_test.png")
        print("✅ 截图成功！")
    except Exception as e:
        print(f"❌ 错误: {e}")
