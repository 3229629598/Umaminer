import time
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
from ctypes import windll

class WindowCapture:
    def __init__(self, window_title=None, hwnd=None):
        """
        初始化窗口捕获器。
        必须提供 window_title 或 hwnd 中的一个。
        
        :param window_title: 要捕获的窗口的标题（精确匹配）。
        :param hwnd: 要捕获的窗口的句柄。
        """
        self.hwnd = hwnd
        if not self.hwnd and window_title:
            self.hwnd = win32gui.FindWindow(None, window_title)
            if not self.hwnd:
                raise ValueError(f"找不到标题为 '{window_title}' 的窗口")
        if not self.hwnd:
            raise ValueError("必须提供有效的窗口句柄(hwnd)或窗口标题(title)")
        
        # 检查窗口是否存在
        if not win32gui.IsWindow(self.hwnd):
            raise ValueError("提供的窗口句柄无效或窗口已关闭")

    def capture(self):
        """
        截取窗口内容并返回一个PIL Image对象。
        """
        # 获取窗口大小
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        width = right - left
        height = bot - top

        # 获取窗口DC（设备上下文）
        hwndDC = win32gui.GetWindowDC(self.hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        # 创建一个空的位图，并准备将窗口内容绘制到它上面
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(bitmap)

        # 使用 BitBlt 将窗口内容“位块传送”到位图上
        # SWP_DRAWFRAME: 确保窗口边框也被包含
        # win32gui.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), win32con.PW_RENDERFULLCONTENT)
        # 更常用且兼容性更好的方式是使用 3 参数版本
        result = windll.user32.PrintWindow(
            self.hwnd,
            saveDC.GetSafeHdc(),
            3 # PW_RENDERFULLCONTENT | PW_CLIENTONLY
        )
        
        if not result:
            # 如果失败，尝试使用 0 或 2 参数版本作为备选
            result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 0)

        # 转换为PIL Image
        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )

        # 清理资源
        win32gui.DeleteObject(bitmap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwndDC)

        return img

    def start_loop_capture(self, callback_func, frequency=10):
        """
        启动循环截图。

        :param callback_func: 一个回调函数，它将接收到截取到的PIL Image对象作为参数。
                              例如: lambda img: img.save(f"screenshot_{int(time.time())}.png")
        :param frequency: 截图频率，单位 Hz。
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
    # 1. 首先确定你要监视的窗口标题
    TARGET_WINDOW_TITLE = "赛马娘(繁中服)" # 请替换为你想监视的窗口的实际标题

    # 2. 创建窗口捕获实例
    try:
        wc = WindowCapture(window_title=TARGET_WINDOW_TITLE)
        print(f"成功找到窗口: {TARGET_WINDOW_TITLE}")
    except ValueError as e:
        print(e)
        exit()

    # 3. 定义一个回调函数来处理每一帧图像
    # 这里我们简单地保存图片，并打印一些信息
    counter = 0
    def process_image(img):
        global counter
        counter += 1
        filename = f"capture_frame_{counter:05d}.png"
        img.save(filename)
        print(f"已保存第 {counter} 帧: {filename}", end='\r') # \r 让输出在同一行刷新

    # 4. 启动循环截图
    # 第一个参数是处理图像的函数，第二个参数是频率(Hz)
    wc.start_loop_capture(process_image, frequency=10)