# Tài liệu dự án Race Master 3D

## Tổng quan dự án

Race Master 3D là một game đua xe 3D được phát triển bằng Python sử dụng framework Ursina. Game bao gồm các chế độ chơi như đua đơn, đua với AI, multiplayer, time trial, và drift. Người chơi có thể tùy chỉnh xe với nhiều loại xe khác nhau, màu sắc, và trang phục.

## Cấu trúc dự án

Dự án được tổ chức thành các file Python chính và thư mục assets chứa models, textures, và âm thanh.

### File chính

#### main.py
- **Chức năng**: File chính khởi tạo ứng dụng Ursina, tải assets, tạo các đối tượng game chính (xe, đường đua, AI, menu), và xử lý vòng lặp game.
- **Cấu trúc**:
  - Import các module cần thiết
  - Cấu hình Ursina (fullscreen, font, etc.)
  - Hàm tải assets song song
  - Khởi tạo đối tượng Car, Tracks, AI, MainMenu, Achievements
  - Hàm update() và input() chính
- **Điểm quan trọng**: Sử dụng thread để tải assets không block main thread, hỗ trợ multiplayer và hand controller.

#### car.py
- **Chức năng**: Định nghĩa class Car - đối tượng xe chính của người chơi, quản lý vật lý xe, điều khiển, hiệu ứng, âm thanh, camera, và các chế độ chơi.
- **Cấu trúc**:
  - Class Car kế thừa từ Entity của Ursina
  - Thuộc tính vật lý (speed, acceleration, friction, etc.)
  - Các phương thức thay đổi loại xe (sports_car, muscle_car, etc.)
  - Hàm update() xử lý logic mỗi frame
  - Quản lý highscore, unlocked items, cosmetics
- **Điểm quan trọng**: Hỗ trợ drift, particle effects, trail rendering, và nhiều chế độ chơi khác nhau.

#### ai.py
- **Chức năng**: Định nghĩa class AICar - xe AI đối thủ, có thể tự lái theo đường đua và tránh vật cản.
- **Cấu trúc**:
  - Class AICar kế thừa từ Entity
  - Hệ thống pathfinding với các điểm mốc cho từng track
  - Logic tránh vật cản và theo dõi đường đua
  - Hỗ trợ nhiều loại xe và màu sắc ngẫu nhiên
- **Điểm quan trọng**: AI có độ khó khác nhau tùy theo loại track, và có cơ chế tránh bị mắc kẹt.

#### main_menu.py
- **Chức năng**: Hệ thống giao diện người dùng chính, quản lý tất cả menu trong game (start, main, maps, settings, garage, etc.).
- **Cấu trúc**:
  - Class MainMenu kế thừa từ Entity
  - Nhiều menu con (start_menu, main_menu, maps_menu, etc.)
  - Tạo UI elements (buttons, text, input fields)
  - Logic điều hướng giữa các menu
  - Xử lý input (pause, quit, etc.)
- **Điểm quan trọng**: Sử dụng Ursina UI với animation mượt mà, hỗ trợ multiplayer setup và leaderboard.

#### multiplayer.py
- **Chức năng**: Xử lý chế độ chơi mạng, đồng bộ hóa vị trí, rotation, model, texture của người chơi khác.
- **Cấu trúc**:
  - Class Multiplayer sử dụng UrsinaNetworking
  - Quản lý client kết nối đến server
  - Xử lý events (player joined, updated, removed)
  - Cập nhật leaderboard
- **Điểm quan trọng**: Nội suy mượt mà vị trí người chơi, hỗ trợ cosmetics và username.

#### achievements.py
- **Chức năng**: Hệ thống thành tựu, tạo và kiểm tra các thành tựu dựa trên hành động người chơi.
- **Cấu trúc**:
  - Class RallyAchievements chính
  - Các class con cho từng track (SandTrackAchievements, etc.)
  - Class CarAchievements cho unlock xe và màu sắc
  - Sử dụng UrsinaAchievements để hiển thị thông báo
- **Điểm quan trọng**: Thành tựu dựa trên thời gian, unlock items, và hoàn thành track.

### File tracks (trong thư mục tracks/)

Mỗi file track định nghĩa một đường đua riêng với models, bounds, và logic đặc biệt.

#### sand_track.py
- **Chức năng**: Định nghĩa đường đua sa mạc với các chi tiết như đá, xương rồng.
- **Cấu trúc**: Class SandTrack kế thừa từ Entity, tạo models và bounds.

#### grass_track.py
- **Chức năng**: Đường đua đồng cỏ với cây cối và đá.
- **Cấu trúc**: Tương tự sand_track nhưng với assets khác.

#### snow_track.py
- **Chức năng**: Đường đua tuyết với nhiều điểm path phức tạp.
- **Cấu trúc**: Có nhiều wall objects để tạo biên giới phức tạp.

#### forest_track.py
- **Chức năng**: Đường đua rừng với cây cối dày đặc.
- **Cấu trúc**: Logic đặc biệt tại một số điểm path.

#### savannah_track.py
- **Chức năng**: Đường đua thảo nguyên.
- **Cấu trúc**: Đường đua tương đối thẳng.

#### lake_track.py
- **Chức năng**: Đường đua hồ với bounds đặc biệt để ngăn xe rơi xuống nước.
- **Cấu trúc**: Có lake_bounds để phát hiện va chạm với nước.

### File khác

#### server.py
- **Chức năng**: Server cho multiplayer, quản lý kết nối và đồng bộ hóa dữ liệu người chơi.
- **Cấu trúc**: Sử dụng networking để handle multiple clients.

#### particles.py
- **Chức năng**: Hệ thống hiệu ứng hạt (particles) cho bụi khi xe chạy.
- **Cấu trúc**: Class Particles tạo và quản lý các hạt bụi.

#### sun.py
- **Chức năng**: Hệ thống ánh sáng mặt trời với shadows.
- **Cấu trúc**: Class SunLight điều chỉnh độ phân giải shadows.

#### hand_controller.py
- **Chức năng**: Điều khiển xe bằng cử chỉ tay (hand tracking).
- **Cấu trúc**: Sử dụng camera để detect cử chỉ.

#### keyinput.py
- **Chức năng**: Xử lý input từ bàn phím.
- **Cấu trúc**: Mapping keys cho điều khiển xe.

#### steering.py
- **Chức năng**: Logic lái xe và drift.
- **Cấu trúc**: Tính toán rotation và speed.

#### drive.py
- **Chức năng**: Logic di chuyển xe.
- **Cấu trúc**: Xử lý acceleration và friction.

### Thư mục assets/

Chứa tất cả tài nguyên game:
- **cars/**: Models và textures của các loại xe
- **tracks/**: Models của đường đua và chi tiết
- **particles/**: Textures cho hiệu ứng hạt
- **audio/**: Âm thanh (rally.mp3, skid.mp3, etc.)
- **fonts/**: Font chữ (Roboto.ttf)
- **icons/**: Icons cho menu

### Thư mục highscore/

Chứa dữ liệu lưu trữ:
- **highscore.json**: Điểm cao cho từng track và chế độ
- **unlocked.json**: Items đã unlock (xe, màu sắc, cosmetics)
- **username.txt**: Tên người chơi

## Cách chạy game

1. Cài đặt Python 3.11
2. Cài đặt dependencies: `pip install -r requirements.txt`
3. Chạy: `python main.py`

## Lưu ý phát triển

- Game sử dụng Ursina framework cho 3D graphics
- Networking sử dụng UrsinaNetworking
- Achievements sử dụng UrsinaAchievements
- Tất cả code được viết bằng Python với style hướng đối tượng
- Assets được tải song song để tối ưu hiệu năng