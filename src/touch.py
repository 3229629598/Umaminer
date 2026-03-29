import win32gui
import win32process
import win32api

def enum_windows_callback(hwnd, windows):
    """
    回调函数，用于传递给 EnumWindows API。
    如果窗口可见，则将其句柄和标题添加到列表中。
    """
    if win32gui.IsWindowVisible(hwnd):
        window_title = win32gui.GetWindowText(hwnd)
        # 过滤掉空标题的窗口（通常是一些系统窗口）
        if window_title:
            windows.append((hwnd, window_title))
    return True # 继续枚举

def get_all_window_titles():
    """
    获取所有可见的顶层窗口标题。
    """
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows

if __name__ == "__main__":
    print("当前可见的所有窗口:")
    for hwnd, title in get_all_window_titles():
        print(f"句柄: {hwnd}, 标题: {title}")