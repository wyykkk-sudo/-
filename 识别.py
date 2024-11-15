import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pygame
import math

# 初始化pygame以播放声音
pygame.mixer.init()

# 生成蜂鸣器声音
def generate_beep(frequency, duration, volume=0.5):
    sample_rate = 44100  # 采样率
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    beep = np.sin(2 * np.pi * frequency * t) * volume
    beep = np.int16(beep * 32767)  # 转换为16位整数
    return beep

# 生成小于5米的滴滴声
beep_5m = generate_beep(360, 0.5)  # 440Hz, 0.1秒
beep_5m_sound = pygame.mixer.Sound(beep_5m.tobytes())

# 生成小于2米的急促滴滴声
beep_2m = generate_beep(660, 0.05)  # 880Hz, 0.05秒
beep_2m_sound = pygame.mixer.Sound(beep_2m.tobytes())

# 已知物体的实际宽度（单位：米）
KNOWN_WIDTH = 0.1  

# 已知物体到摄像头的距离（单位：米）
KNOWN_DISTANCE = 0.09  

# 计算焦距
def calculate_focal_length(known_width, known_distance, width_in_rf_image):
    return (width_in_rf_image * known_distance) / known_width

# 计算距离
def calculate_distance(focal_length, known_width, width_in_frame):
    return (known_width * focal_length) / width_in_frame

# 打开摄像头
cap = cv2.VideoCapture(0)

# 计算焦距
# 这里假设我们已经知道物体在1米远处的像素宽度
# 例如，物体在1米远处的像素宽度为100像素
focal_length = calculate_focal_length(KNOWN_WIDTH, KNOWN_DISTANCE, 1280)

# 创建主窗口
root = tk.Tk()
root.title("易联工作室x西高科技社 视觉测距beta标定1")

# 创建一个标签用于显示摄像头画面
label = tk.Label(root)
label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# 加载logo图像并调整大小
logo_image = Image.open("logo.png")
logo_image = logo_image.resize((500, 200), Image.Resampling.LANCZOS)  # 调整logo大小为200x100像素
logo_photo = ImageTk.PhotoImage(logo_image)

# 创建一个标签用于显示logo
logo_label = tk.Label(root, image=logo_photo)
logo_label.grid(row=1, column=0, padx=10, pady=10)

# 创建一个标签用于显示文字
text_label = tk.Label(root, text="数据标定测试版本1", font=("Arial", 16))
text_label.grid(row=1, column=1, padx=10, pady=10)

# 创建一个开关按钮用于选择是否开启声音预警
sound_enabled = tk.BooleanVar(value=True)
sound_switch = ttk.Checkbutton(root, text="开启声音预警", variable=sound_enabled)
sound_switch.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# 更新摄像头画面和距离信息
def update_frame():
    ret, frame = cap.read()
    if ret:
        # 转换为灰度图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 使用高斯模糊减少噪声
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 使用Canny边缘检测
        edges = cv2.Canny(blurred, 50, 150)

        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 用于存储每个100x100像素网格中的标注值
        grid_values = {}

        for contour in contours:
            # 计算轮廓的边界框
            x, y, w, h = cv2.boundingRect(contour)

            # 计算物体的像素宽度
            width_in_frame = w

            # 计算距离
            distance = calculate_distance(focal_length, KNOWN_WIDTH, width_in_frame)

            # 计算网格位置
            grid_x = x // 136
            grid_y = y // 136
            grid_key = (grid_x, grid_y)

            # 初始颜色为绿色
            color = (0, 255, 0)

            # 根据距离改变颜色
            if distance < 2:
                color = (0, 0, 255)  # 红色
                if sound_enabled.get():
                    beep_2m_sound.play()  # 播放小于2米的急促滴滴声
            elif distance < 5:
                color = (0, 255, 255)  # 黄色
                if sound_enabled.get():
                    beep_5m_sound.play()  # 播放小于5米的滴滴声

            # 如果该网格中还没有标注值，则绘制标注
            if grid_key not in grid_values:
                # 计算标注位置
                text_x = x
                text_y = y - 10 if y - 10 > 0 else y + h + 20

                # 绘制边界框和距离信息
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, f'Distance: {distance:.2f} m', (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                # 记录该网格中的标注值
                grid_values[grid_key] = True

        # 将OpenCV图像转换为PIL图像
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)

        # 将PIL图像转换为Tkinter图像
        img = ImageTk.PhotoImage(image=img)

        # 更新标签中的图像
        label.config(image=img)
        label.image = img

    # 每隔150毫秒更新一次画面
    root.after(150, update_frame)

# 启动更新帧的循环
update_frame()

# 运行主循环
root.mainloop()

# 释放摄像头并关闭窗口
cap.release()
