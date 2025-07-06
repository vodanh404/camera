# Cài thư viện bằng lệnh: pip install opencv-python flask
# Khai báo thư viện
from flask import Flask, Response
import cv2
import time

app = Flask(__name__)
camera = cv2.VideoCapture(0) 
def generate_frames():
    while True:
        success, frame = camera.read()
        ret, buffer = cv2.imencode('.jpg', frame) # Mã hóa khung hình thành JPEG
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03) # Giảm tải CPU, khoảng 30 FPS

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# Cách xem: truy cập vào  http://[Địa chỉ IP của máy phát]:5000/video_feed
