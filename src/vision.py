import cv2
import numpy as np

class Vision:
    def __init__(self, template_path: str, screen_width: int = 450, threshold: float = 0.8):
        """
        初始化视觉检测器
        :param template_path: 模板图像路径（如萝卜图标）
        :param screen_width: 识别窗口宽度，默认 450
        :param threshold: 匹配阈值，默认 0.8
        """
        self.threshold = threshold
        self.screen_width = screen_width
        self.screen = None
        self.screen_gray = None
        self.is_carrot = False
        self.drop_cnt = 0
        # 加载模板
        self.src_template = cv2.imread(template_path)
        # 缩放模板
        #screen_width = screen.shape[1]
        carrot_width = self.screen_width/6
        scale = carrot_width/self.src_template.shape[1]
        self.template = cv2.resize(self.src_template, None, fx=scale, fy=scale)
        # 转换为灰度图
        self.template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)

    def loop(self, screen_path: str, show_result=False):
        """
        循环函数
        :param screen_path: 识别图像路径
        :param show_result: 识别结果可视化，默认 False
        """
        self.screen = cv2.imread(screen_path)
        self.screen_gray = cv2.cvtColor(self.screen, cv2.COLOR_BGR2GRAY)
        # 使用模板匹配（方法选择：TM_CCOEFF_NORMED 更适合颜色对比）
        result = cv2.matchTemplate(self.screen_gray, self.template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= self.threshold)
        if len(loc[0])==0:
            if self.is_carrot == True:
                self.is_carrot = False
            return
        else:
            # 筛选横坐标在 20 到 25 之间的匹配点
            valid_position = []
            for pt in zip(*loc[::-1]):  # pt[0] 是 x 坐标, pt[1] 是 y 坐标
                x, y = pt
                x_min = self.screen_width*20/450
                x_max = self.screen_width*25/450
                if self.is_carrot == False and x_min <= x <= x_max:
                    self.is_carrot = True
                    self.drop_cnt+=1
                    valid_position.append(pt)
                if self.is_carrot == True and not(x_min <= x <= x_max):
                    self.is_carrot = False
            if show_result:
                # 绘制矩形框
                for pt in valid_position:
                    cv2.rectangle(self.screen, pt, (pt[0] + self.template.shape[1], pt[1] + self.template.shape[0]), (0, 255, 0), 2)
                    print(f"\n找到一个对象, 中心点坐标({pt[0]+self.template.shape[1]/2},{pt[1]+self.template.shape[0]/2})")
                cv2.imshow('Result', self.screen)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

# 使用示例
if __name__ == "__main__":
    detector = Vision(template_path = './img/carrot.png')
    positions = detector.loop(screen_path = './img/test1.png', show_result = True)
