import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk

# 初始化Tkinter窗口
root = tk.Tk()
root.title("人体骨骼识别与渲染")
root.geometry("1200x600")

# MediaPipe Pose初始化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# 获取可用摄像头列表
def get_camera_list():
    camera_list = []
    for i in range(10):  # 假设最多有10个摄像头
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_list.append(i)
            cap.release()
    return camera_list

# 选择摄像头
def choose_camera():
    camera_list = get_camera_list()
    if not camera_list:
        messagebox.showerror("错误", "未检测到可用摄像头")
        return None
    camera_id = camera_list[0]  # 默认选择第一个摄像头
    if len(camera_list) > 1:
        camera_id = int(ttk.Combobox(root, values=camera_list).get())
    return camera_id

# 显示摄像头画面的函数
def show_frame(cap):
    _, frame = cap.read()
    if frame is None:
        return
    
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 处理帧以识别骨骼
    results = pose.process(frame_rgb)
    
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    # 转换为PIL图像并显示
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, lambda: show_frame(cap))

# 开始识别骨骼的函数
def start_pose_detection():
    camera_id = choose_camera()
    if camera_id is None:
        return
    
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        messagebox.showerror("错误", "无法打开摄像头")
        return
    
    show_frame(cap)

# 创建主界面按钮
start_button = tk.Button(root, text="开始识别", command=start_pose_detection)
start_button.pack(pady=20)

# 创建用于显示摄像头画面的Label
lmain = tk.Label(root)
lmain.pack(pady=20)

# 运行主循环
root.mainloop()

# 释放摄像头资源
if 'cap' in locals() and cap:
    cap.release()
