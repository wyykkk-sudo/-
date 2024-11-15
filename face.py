import cv2
import face_recognition
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# 加载目标图片
target_image = face_recognition.load_image_file("sb.jpg")
target_face_encoding = face_recognition.face_encodings(target_image)[0]

# 打开摄像头
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    messagebox.showerror("错误", "无法打开摄像头")
    exit()

# 创建主窗口
root = tk.Tk()
root.title("摄像头识别人物")

# 创建一个标签用于显示摄像头捕捉的图像
label = tk.Label(root)
label.pack()

# 创建一个标签用于显示logo
logo_label = tk.Label(root)
logo_label.pack(side=tk.TOP, anchor=tk.NW)

# 创建一个标签用于显示版本信息
version_label = tk.Label(root, text="测试版本1", font=("Arial", 12))
version_label.pack(side=tk.TOP, anchor=tk.NW)

def update_frame():
    # 读取一帧图像
    ret, frame = cap.read()

    if not ret:
        messagebox.showerror("错误", "无法获取图像帧")
        return

    # 查找当前帧中的人脸
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # 计算当前人脸与目标人脸的相似度
        matches = face_recognition.compare_faces([target_face_encoding], face_encoding)
        face_distances = face_recognition.face_distance([target_face_encoding], face_encoding)
        best_match_index = face_distances.argmin()
        similarity = (1 - face_distances[best_match_index]) * 100 + 25

        # 根据相似度设置矩形颜色和文本
        if similarity < 60:
            color = (0, 255, 0)  # 绿色
            text = f"Similarity: {similarity:.2f}%"
        elif 60 <= similarity < 80:
            color = (0, 255, 255)  # 黄色
            text = f"Similarity: {similarity:.2f}%"
        elif 80 <= similarity < 90:
            color = (0, 0, 255)  # 红色
            text = f"Similarity: {similarity:.2f}%"
        elif 90 <= similarity < 95:
            color = (0, 0, 255)  # 红色
            text = "Basic Match"
        elif 95 <= similarity < 99:
            color = (0, 0, 255)  # 红色
            text = "Match"
        elif similarity >= 99:
            color = (0, 0, 255)  # 红色
            text = "Absolute Match"

        # 绘制矩形框和文本
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # 将OpenCV图像转换为PIL图像
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame)
    image_tk = ImageTk.PhotoImage(image)

    # 更新标签中的图像
    label.config(image=image_tk)
    label.image = image_tk

    # 每30毫秒更新一次图像
    label.after(30, update_frame)

# 加载logo图片
logo_img = Image.open("logo.png")
logo_tk = ImageTk.PhotoImage(logo_img)

# 设置logo标签的图像
logo_label.config(image=logo_tk)
logo_label.image = logo_tk

# 开始更新图像
update_frame()

# 运行主循环
root.mainloop()

# 释放摄像头并关闭所有窗口
cap.release()
cv2.destroyAllWindows()
