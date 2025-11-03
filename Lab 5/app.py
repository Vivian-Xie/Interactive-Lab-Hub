# app.py
from flask import Flask, render_template, jsonify
from teachable_machine_lite import TeachableMachineLite
import cv2 as cv
import threading
import time

app = Flask(__name__)

# Global variable to store recognition results
current_result = {"label": "blank", "confidence": 0}

# Teachable Machine setup
model_path = 'model/model.tflite'
image_file_name = "frame.jpg"
labels_path = "model/labels.txt"

def run_camera():
    """Run camera recognition in background"""
    global current_result
    
    cap = cv.VideoCapture(0)
    tm_model = TeachableMachineLite(model_path=model_path, labels_file_path=labels_path)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read camera")
            break
            
        cv.imwrite(image_file_name, frame)
        results = tm_model.classify_image(image_file_name)
        
        if results:
            print("Results:", results)
            current_result = {
                "label": results['label'],
                "confidence": results['confidence']
            }
            print(f"Top result: {results['label']} - {results['confidence']:.2f}%")
        
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

# New API endpoint to get current result
@app.route('/api/result')
def get_result():
    return jsonify(current_result)

if __name__ == '__main__':
    camera_thread = threading.Thread(target=run_camera, daemon=True)
    camera_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)