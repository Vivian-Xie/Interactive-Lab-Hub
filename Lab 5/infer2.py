"""
Real-time image classification using OpenCV and PyTorch.
Every 2 seconds, classify the current frame.
"""
import time
import torch
import numpy as np
from torchvision import models, transforms
import cv2
from PIL import Image
import json

# open classes as dict
with open('classes.json') as f:
    classes = json.load(f)

torch.backends.quantized.engine = 'qnnpack'

# video capture setup
cap = cv2.VideoCapture(0)  # 改：不指定CAP_V4L2，更通用
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 改：分辨率提高
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# preprocess
preprocess = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# get model
net = models.quantization.mobilenet_v2(pretrained=True, quantize=True)
net = torch.jit.script(net)

# 新增：计时变量
last_inference_time = time.time()
inference_interval = 2.0  # 2秒识别一次

print("Press 'q' to quit")

with torch.no_grad():
    while True:
        # read frame
        ret, image = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        
        # 新增：显示实时画面
        display_image = image.copy()
        
        # 新增：检查是否到了识别时间
        current_time = time.time()
        if current_time - last_inference_time >= inference_interval:
            print("\n--- Running inference ---")
            
            # resize to 224x224 for model
            image_resized = cv2.resize(image, (224, 224))
            
            # convert BGR to RGB
            image_rgb = image_resized[:, :, [2, 1, 0]]
            
            # preprocess
            input_tensor = preprocess(image_rgb)
            input_batch = input_tensor.unsqueeze(0)
            
            # run model
            output = net(input_batch)
            top = list(enumerate(output[0].softmax(dim=0)))
            top.sort(key=lambda x: x[1], reverse=True)
            
            # 显示top 3结果
            print("Top 3 predictions:")
            for idx, val in top[:3]:
                print(f"  {val.item()*100:.2f}% - {classes[str(idx)]}")
            
            # 新增：在图像上显示结果
            text = f"{classes[str(top[0][0])]} {top[0][1].item()*100:.1f}%"
            cv2.putText(display_image, text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            last_inference_time = current_time
        
        # 新增：显示窗口
        cv2.imshow('Camera - Press q to quit', display_image)
        
        # 新增：按q退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()