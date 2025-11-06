# Race Master 3D 🏎️

**Game Đua Xe 3D** được xây dựng với Python và Ursina Engine, có nhiều đường đua, phương tiện và cả chế độ chơi đơn lẻ và nhiều người chơi.

## ✨ Tính Năng

- **Nhiều Chế Độ Chơi**: Đua xe đơn lẻ và nhiều người chơi
- **6 Đường Đua Khác Nhau**: Môi trường Rừng, Cỏ, Hồ, Cát, Thảo Nguyên và Tuyết
- **Lựa Chọn Phương Tiện**: Chọn từ 6 loại xe khác nhau (Xe thể thao, Xe đua, Hatchback, Limousine, Xe tải, Xe cơ bắp)
- **Hệ Thống Thành Tựu**: Mở khóa thành tựu khi chơi
- **Vật Lý Thực Tế**: Vật lý xe 3D với điều khiển và va chạm chính xác
- **Hiệu Ứng Âm Thanh**: Trải nghiệm âm thanh sống động với tiếng động cơ và hiệu ứng
- **Đa Nền Tảng**: Chạy trên Windows, macOS và Linux

## 📋 Yêu Cầu

- **Python 3.7+**
- **Ursina Engine** (Khuyến nghị phiên bản GitHub)
- **Thư Viện Phụ Thuộc**: Được liệt kê trong `requirements.txt`

## 🚀 Bắt Đầu Nhanh

### Tùy Chọn 1: Tải từ itch.io
Truy cập [Race Master 3D trên itch.io](https://mandaw2014.itch.io/rally) để có phiên bản sẵn sàng chơi.

### Tùy Chọn 2: Chạy từ Mã Nguồn

1. **Sao Chép hoặc Tải** repository này
2. **Cài Đặt Thư Viện Phụ Thuộc**:
   ```bash
   pip install -r requirements.txt
   ```
   > **Lưu Ý**: Cài đặt phiên bản GitHub của Ursina để có khả năng tương thích tốt nhất:
   ```bash
   pip install git+https://github.com/pokepetter/ursina.git
   ```

3. **Chạy Game**:
   ```bash
   python main.py
   ```

## 🎮 Chế Độ Chơi

### Chơi Đơn Lẻ
- Chọn từ 6 đường đua độc đáo
- Chọn phương tiện yêu thích của bạn
- Đua với đối thủ AI
- Hoàn thành thành tựu
- Theo dõi thời gian vòng đua tốt nhất

### Nhiều Người Chơi
1. **Tạo Server**:
   - Chạy `main.py` → Nhấp "Multiplayer"
   - Nhập địa chỉ IP (dùng 'localhost' cho chơi local)
   - Nhập cổng (mặc định: 25565)
   - Nhấp "Create Server" → "Join Server"

2. **Tham Gia Server**:
   - Chạy `main.py` → Nhấp "Multiplayer" → "Join Server"
   - Nhập địa chỉ IP công khai của server và cổng
   - Nhấp "JOIN"
   - **Không giới hạn người chơi!** Số lượng người chơi không giới hạn có thể tham gia server

## 🕹️ Điều Khiển

| Phím | Hành Động |
|------|-----------|
| **W** | Tăng Tốc |
| **S** | Phanh/Lùi |
| **A/D** | Rẽ Trái/Phải |
| **SPACE** | Phanh Tay |
| **G** | Hồi Sinh Xe |
| **ESC** | Menu Tạm Dừng |

## 🏁 Đường Đua

- **Đường Đua Rừng** - Đua xe trong rừng rậm
- **Đường Đua Cỏ** - Đường đua cánh đồng rộng mở
- **Đường Đua Hồ** - Đua xe bên hồ nước tuyệt đẹp
- **Đường Đua Cát** - Thử thách trên đồi cát sa mạc
- **Đường Đua Thảo Nguyên** - Phiêu lưu đồng cỏ châu Phi
- **Đường Đua Tuyết** - Đua xe trong xứ sở băng tuyết

## 🚗 Phương Tiện

Mỗi phương tiện có đặc điểm điều khiển độc đáo:
- **Xe Thể Thao** - Tốc độ cao, điều khiển chính xác
- **Xe Đua** - Hiệu suất cân bằng, đa địa hình
- **Hatchback** - Thân thiện với người mới, ổn định
- **Limousine** - Nặng, khó điều khiển
- **Xe Tải** - Mạnh mẽ nhưng tăng tốc chậm
- **Xe Cơ Bắp** - Tăng tốc cao, dễ trượt

## 🏆 Hệ Thống Thành Tựu

Mở khóa thành tựu bằng cách:
- Hoàn thành cuộc đua
- Đạt thời gian vòng đua nhanh
- Thành thạo các phương tiện khác nhau
- Khám phá tất cả đường đua

## 📁 Cấu Trúc Dự Án

```
Race Master 3D/
├── main.py              # Điểm vào game
├── car.py               # Vật lý và render phương tiện
├── main_menu.py         # Giao diện menu chính
├── multiplayer.py       # Chức năng nhiều người chơi  
├── server.py            # Game server
├── ai.py                # Logic đối thủ AI
├── achievements.py      # Hệ thống thành tựu
├── tracks/              # Định nghĩa đường đua
├── assets/              # Mô hình 3D, texture, âm thanh
└── requirements.txt     # Thư viện Python phụ thuộc
```

## 🛠️ Chi Tiết Kỹ Thuật

- **Engine**: Ursina (Engine 3D dựa trên Python)
- **Vật Lý**: Triển khai vật lý xe tùy chỉnh
- **Mạng**: Hệ thống nhiều người chơi dựa trên UDP
- **Đồ Họa**: Render OpenGL qua Ursina
- **Âm Thanh**: Tích hợp âm thanh Pygame

## 🔧 Khắc Phục Sự Cố

**Game không khởi động?**
- Đảm bảo bạn đã cài đặt phiên bản GitHub của Ursina
- Kiểm tra tất cả thư viện phụ thuộc trong `requirements.txt` đã được cài đặt
- Xác minh phiên bản Python là 3.7 trở lên

**Vấn đề kết nối nhiều người chơi?**
- Kiểm tra cài đặt firewall cho cổng được chỉ định
- Đảm bảo địa chỉ IP server là chính xác
- Thử dùng 'localhost' để test local

## 🤝 Ghi Nhận

- **Hiệu Ứng Âm Thanh**: [Car Game SFX Pack bởi Touati](https://touati.itch.io/car-game-sfx-pack)
- **Mô Hình Xe Thể Thao**: [Poly Pizza](https://poly.pizza/m/dVLJ5CjB0h)
- **Hướng Dẫn Mô Hình Hóa Xe**: [YouTube Tutorial](https://www.youtube.com/watch?v=YALV3HqfdLY)
- **Thư Viện Thành Tựu**: [UrsinaAchievements bởi TheAssassin](https://github.com/megat69/UrsinaAchievements)
- **Thư Viện Mạng**: [UrsinaNetworking bởi K3](https://github.com/kstzl/UrsinaNetworking)

### Người Đóng Góp Đặc Biệt
- **Tusnad30**: Hệ thống bóng đổ & ánh sáng
- **TheAssassin**: Hệ thống thành tựu, tải tài sản, triển khai Threading

## 📄 Giấy Phép

Dự án này được cấp phép theo các điều khoản được chỉ định trong tệp LICENSE.

---

**Chúc bạn đua xe vui vẻ! 🏁** 

*Hãy thoải mái đóng góp hoặc báo cáo vấn đề để giúp cải thiện game.*