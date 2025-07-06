from flask import Flask, Response
import cv2
import time
import sys

app = Flask(__name__)
camera = cv2.VideoCapture(0)
# --- CÁC THIẾT LẬP QUAN TRỌNG ĐỂ TỐI ƯU HIỆU SUẤT TRÊN RASPBERRY PI 4 ---
if not camera.isOpened():
    print("Lỗi: Không thể mở camera. Vui lòng kiểm tra lại kết nối.", file=sys.stderr)
    sys.exit(1)
# Đặt độ phân giải cho camera.
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# Đặt tốc độ khung hình (FPS) cho camera.
camera.set(cv2.CAP_PROP_FPS, 15)# 15 FPS là đủ mượt và giảm tải CPU 

# ------------Chương trình chính---------------
def generate_frames():
    while True:
        try:
            success, frame = camera.read()
            if not success:
                print("Cảnh báo: Không thể đọc khung hình từ camera. Đang thử lại...", file=sys.stderr)
                time.sleep(0.1)
                continue 
            # Mã hóa khung hình thành JPEG
            ret, buffer = cv2.imencode('.jpg', frame) 
            if not ret:
                print("Lỗi: Không thể mã hóa khung hình thành JPEG.", file=sys.stderr)
                time.sleep(0.1)
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Lỗi trong quá trình tạo khung hình: {e}", file=sys.stderr)
            time.sleep(1)
@app.route('/video_feed')
def video_feed():
    print("Đã có kết nối đến /video_feed")
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__ == '__main__':
    print("Ứng dụng Flask đang khởi động...")
    app.run(host='0.0.0.0', port=5000, debug=False)
#-----------------------------------------------------------------------------------------
# 1 số lưu ý:
# - Khi sử dụng trên raspberry pi 4 thì nên phát mạng từ thiết bị nhận cho raspberry pi 4 để đảm bảo kết nối được mượt mà và ổn định
# - Qua quá trình thử nghiệm cho thấy camera khá ổn định, không bị trễ :P
