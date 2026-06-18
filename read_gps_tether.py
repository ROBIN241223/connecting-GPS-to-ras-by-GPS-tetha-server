import socket
import pynmea2

# --- CẤU HÌNH ĐỒNG BỘ Ở ĐÂY ---
PHONE_IP = '192.168.188.109'  # IP của mainboard OPPO
PORT = 11123                   # <--- BẮT BUỘC: Thay bằng số cổng thực tế bạn vừa xem trên app ở Bước 1

def get_gps_stream():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"Đang kết nối tới GPS Tether Server ({PHONE_IP}:{PORT})...")
        s.connect((PHONE_IP, PORT))
        print("Kết nối thành công! Đang chờ dữ liệu GPS...")
        
        while True:
            data = s.recv(1024)
            if not data:
                break
                
            nmea_sentences = data.decode('utf-8', errors='ignore').split('\n')
            for sentence in nmea_sentences:
                # Lọc các gói tin định vị tiêu chuẩn (GGA, RMC)
                if any(sentence.startswith(x) for x in ['$GPGGA', '$GNGGA', '$GPRMC', '$GNRMC']):
                    try:
                        msg = pynmea2.parse(sentence)
                        lat = msg.latitude
                        lon = msg.longitude
                        
                        # Kiểm tra xem có phải gói GGA (có số vệ tinh, độ cao) không
                        alt = getattr(msg, 'altitude', 'None')
                        sats = getattr(msg, 'num_sats', '0')
                        
                        print(f"Tọa độ: [{lat:.6f}, {lon:.6f}] | Độ cao: {alt}m | Vệ tinh: {sats}")
                    except:
                        pass

    except ConnectionRefusedError:
        print(f"\n[Lỗi kết nối]: Máy tính bị từ chối truy cập.")
        print(f"-> Hãy chắc chắn app GPS Tether Server trên điện thoại đã bấm START.")
        print(f"-> Kiểm tra xem số PORT trong code ({PORT}) đã khớp chính xác với số Port hiển thị trên màn hình app chưa.")
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        s.close()

if __name__ == '__main__':
    get_gps_stream()