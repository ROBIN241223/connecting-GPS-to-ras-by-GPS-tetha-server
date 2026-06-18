import socket
import pynmea2

# --- CẤU HÌNH TCP (Giữ nguyên như lúc bạn chạy thành công) ---
PHONE_IP = '192.168.188.109'  # Hãy kiểm tra ip route nếu bị lỗi kết nối
PORT = 11123                  # Cổng TCP trên app

def get_gps_tcp_optimized():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Đặt timeout 3 giây để code không bao giờ bị treo cứng nếu rớt mạng
    s.settimeout(3.0) 
    
    try:
        print(f"Đang kết nối tới TCP {PHONE_IP}:{PORT}...")
        s.connect((PHONE_IP, PORT))
        print("Kết nối TCP thành công! Bắt đầu nhận dữ liệu...")
        
        # Biến buffer để nối các mảnh dữ liệu bị đứt gãy của TCP
        buffer = ""
        
        while True:
            try:
                # Kéo dữ liệu về (dùng chunk lớn 4096 để lấy trọn gói)
                data = s.recv(4096)
                if not data:
                    print("\n[Ngắt kết nối] Điện thoại đã đóng cổng.")
                    break
                    
                buffer += data.decode('utf-8', errors='ignore')
                
                # Tách từng dòng hoàn chỉnh để xử lý ngay lập tức
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    # Chỉ bắt đúng gói GGA để lọc rác và tăng tốc
                    if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                        try:
                            msg = pynmea2.parse(line)
                            lat = msg.latitude
                            lon = msg.longitude
                            alt = getattr(msg, 'altitude', 'None')
                            sats = getattr(msg, 'num_sats', '0')
                            
                            print(f"Tọa độ: [{lat:.6f}, {lon:.6f}] | Cao: {alt}m | Vệ tinh: {sats}")
                        except pynmea2.ParseError:
                            pass # Bỏ qua nếu chuỗi bị lỗi vật lý
                            
            except socket.timeout:
                print("... (Chờ dữ liệu từ điện thoại)")
                
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        s.close()

if __name__ == '__main__':
    get_gps_tcp_optimized()