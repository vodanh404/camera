from flask import Flask, Response
import cv2
import time
import sys

app = Flask(__name__)

# Thử mở camera với index 0.
# Nếu không hoạt động, bạn có thể thử các index khác từ 0 đến 31
# dựa trên đầu ra của ls /dev/video* mà bạn thấy.
# Tuy nhiên, thông thường camera chính sẽ là 0 hoặc 1.
camera = cv2.VideoCapture(0)

# --- CÁC THIẾT LẬP QUAN TRỌNG ĐỂ TỐI ƯU HIỆU SUẤT TRÊN RASPBERRY PI 4 ---
if not camera.isOpened():
    print("Lỗi: Không thể mở camera. Vui lòng kiểm tra lại kết nối hoặc thử index camera khác (ví dụ: cv2.VideoCapture(1)).", file=sys.stderr)
    sys.exit(1)

# Đặt độ phân giải cho camera.
# 640x480 là một điểm khởi đầu tốt để tiết kiệm tài nguyên.
# Nếu muốn chất lượng cao hơn sau này, hãy tăng dần lên 800x600, 1280x720.
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Đặt tốc độ khung hình (FPS) cho camera.
# 15 FPS là đủ mượt và giảm tải CPU đáng kể so với 30 FPS.
camera.set(cv2.CAP_PROP_FPS, 15)

# --- KẾT THÚC THIẾT LẬP ---

def generate_frames():
    while True:
        try:
            success, frame = camera.read()
            if not success:
                print("Cảnh báo: Không thể đọc khung hình từ camera. Đang thử lại...", file=sys.stderr)
                # Có thể thêm một đoạn sleep ngắn ở đây để tránh lặp vô hạn quá nhanh
                time.sleep(0.1)
                continue # Bỏ qua khung hình này và thử lại

            # Mã hóa khung hình thành JPEG
            # Chất lượng nén JPEG mặc định thường là 95, có thể giảm xuống để giảm kích thước file
            # ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80]) # Giảm chất lượng JPEG
            ret, buffer = cv2.imencode('.jpg', frame) # Dùng mặc định 95 chất lượng
            if not ret:
                print("Lỗi: Không thể mã hóa khung hình thành JPEG.", file=sys.stderr)
                time.sleep(0.1)
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # time.sleep(0.03) # Bỏ comment hoặc điều chỉnh nếu muốn giới hạn FPS rõ ràng
                               # Tuy nhiên, nếu đã set FPS ở camera.set, thường không cần thiết
                               # để tránh giới hạn kép hoặc xung đột
        except Exception as e:
            print(f"Lỗi trong quá trình tạo khung hình: {e}", file=sys.stderr)
            # Thử lại sau một khoảng thời gian
            time.sleep(1)
            # Có thể thêm logic để thoát nếu lỗi liên tục

@app.route('/video_feed')
def video_feed():
    print("Đã có kết nối đến /video_feed")
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Ứng dụng Flask đang khởi động...")
    # Tắt debug mode khi chạy thực tế để giảm tài nguyên và tăng ổn định
    app.run(host='0.0.0.0', port=5000, debug=False)
