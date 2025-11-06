# Giải thích chi tiết về chức năng và cấu trúc từng file trong game Race Master 3D

## Tổng quan về dự án
Game Race Master 3D là một game đua xe 3D được phát triển bằng framework Ursina (Python). Game bao gồm các chế độ chơi như Race, Time Trial, Drift, và Multiplayer. Người chơi có thể điều khiển xe bằng bàn phím hoặc cử chỉ tay qua webcam.

## Cấu trúc tổng quan
- **main.py**: File chính khởi tạo game và vòng lặp chính
- **car.py**: Class Car - đối tượng xe chính của người chơi
- **ai.py**: Class AICar - AI điều khiển xe bot
- **hand_controller.py**: Điều khiển xe bằng cử chỉ tay
- **drive.py**: Xử lý logic tiến/lùi (W/S)
- **steering.py**: Xử lý logic rẽ trái/phải (A/D)
- **keyinput.py**: Simulate nhấn phím
- **main_menu.py**: Hệ thống giao diện menu
- **multiplayer.py**: Chế độ chơi mạng
- **server.py**: Server cho multiplayer
- **particles.py**: Hiệu ứng hạt (bụi, trail)
- **sun.py**: Hệ thống ánh sáng mặt trời
- **achievements.py**: Hệ thống thành tựu
- **tracks/**: Các file định nghĩa đường đua
- **UrsinaAchievements/**: Thư viện thành tựu

---

## Chi tiết từng file

### 1. main.py
**Chức năng**: File chính của game, khởi tạo toàn bộ ứng dụng Ursina, tải assets, tạo các đối tượng game chính (xe, AI, menu, tracks), và xử lý vòng lặp game.

**Cấu trúc chính**:
- `load_assets()`: Tải models và textures song song
- `delayed_load_assets()`: Gọi tải assets sau khi app khởi tạo
- `update()`: Hàm update chính mỗi frame - xử lý multiplayer, server, achievements
- `input(key)`: Xử lý input bàn phím (h để toggle hand controller)

**Các đối tượng chính**:
- `car`: Instance của Car (xe người chơi)
- `ai_list`: List 3 xe AI
- `main_menu`: Instance của MainMenu
- `achievements`: Instance của RaceMasterAchievements
- `sun`: Instance của SunLight

### 2. car.py
**Chức năng**: Định nghĩa class Car - đối tượng xe chính của người chơi. Quản lý vật lý xe, di chuyển, drift, âm thanh, hiệu ứng hạt, camera, và các chế độ chơi.

**Cấu trúc chính**:
- `__init__()`: Khởi tạo xe với các thuộc tính vật lý, hiệu ứng, âm thanh
- `update()`: Logic chính mỗi frame - xử lý input, vật lý, collision, camera
- `sports_car()`, `muscle_car()`, etc.: Thay đổi loại xe
- `reset_car()`: Reset vị trí xe
- `check_highscore()`: Kiểm tra và lưu highscore
- `save_highscore()`: Lưu highscore vào file JSON

**Thuộc tính quan trọng**:
- `speed`, `velocity_y`: Tốc độ và vận tốc
- `rotation_speed`: Tốc độ xoay
- `topspeed`, `acceleration`: Thông số vật lý
- `gamemode`: Chế độ chơi (race, time trial, drift)
- `highscore_count`: Điểm cao nhất

### 3. ai.py
**Chức năng**: Định nghĩa class AICar - xe AI thông minh có thể tự lái theo đường đua. Sử dụng pathfinding để theo dõi các điểm mốc trên track.

**Cấu trúc chính**:
- `__init__()`: Khởi tạo AI với các thuộc tính vật lý và danh sách path points
- `update()`: Logic AI mỗi frame - drift, collision, pathfinding, movement
- `set_random_car()`, `set_random_texture()`: Random hóa ngoại hình AI
- `same_pos()`: Phòng tránh AI bị mắc kẹt
- `reset()`: Reset vị trí AI
- `simple_intersects()`: Kiểm tra va chạm đơn giản

**Path points**: Mỗi track có danh sách điểm path mà AI theo dõi (sap1-sap8 cho sand track, etc.)

### 4. hand_controller.py
**Chức năng**: Điều khiển xe bằng cử chỉ tay sử dụng MediaPipe và OpenCV. Phát hiện cử chỉ để lái xe, tăng tốc, và pause game.

**Cấu trúc chính**:
- `__init__()`: Khởi tạo với car reference và cấu hình MediaPipe
- `start()`/`stop()`: Bắt đầu/dừng detection
- `_run_detection()`: Thread chính detect cử chỉ
- `_palm_center()`: Tính tâm bàn tay
- `_pinch_ratio()`: Tính tỷ lệ chụm ngón (cho pause)
- `_draw_debug()`: Vẽ debug info lên camera feed

**Controllers**:
- `drive_controller`: Xử lý tiến/lùi
- `steering_controller`: Xử lý rẽ trái/phải

### 5. drive.py
**Chức năng**: Xử lý logic tiến/lùi (W/S) dựa trên cử chỉ tay. Phân biệt giữa 1 tay (lùi) và 2 tay (tiến).

**Cấu trúc chính**:
- `__init__()`: Khởi tạo với last_drive_state
- `update_drive()`: Cập nhật trạng thái dựa trên hand_count và positions
- `stop_drive()`: Dừng tất cả drive controls

**Logic**:
- 2 tay: Tiến (W) nếu vị trí trung bình trong khoảng 0.3-0.7
- 1 tay: Lùi (S)

### 6. steering.py
**Chức năng**: Xử lý logic rẽ trái/phải (A/D) dựa trên vị trí tương đối của 2 tay.

**Cấu trúc chính**:
- `__init__()`: Khởi tạo với car reference
- `update_steering()`: Cập nhật trạng thái dựa trên hand_count và positions
- `stop_steering()`: Dừng tất cả steering controls

**Logic**:
- 2 tay: Kiểm tra vị trí tương đối để xác định rẽ trái/phải
- Áp dụng flip_steering nếu được bật

### 7. keyinput.py
**Chức năng**: Simulate nhấn và thả phím trên Windows sử dụng ctypes. Được sử dụng để điều khiển xe từ hand controller.

**Cấu trúc chính**:
- `keys`: Dictionary mapping key names to scan codes
- `press_key(key)`: Simulate nhấn phím
- `release_key(key)`: Simulate thả phím

**Keys hỗ trợ**: w, a, s, d

### 8. main_menu.py
**Chức năng**: Hệ thống giao diện người dùng chính. Quản lý tất cả menus: start, main, maps, settings, garage, multiplayer, pause.

**Cấu trúc chính**:
- `__init__()`: Khởi tạo tất cả menu entities và UI elements
- Các hàm xử lý click: `singleplayer()`, `multiplayer()`, `quit()`, etc.
- Animation cho menu transitions

**Menus chính**:
- `start_menu`: Menu khởi động
- `main_menu`: Menu chính với các chế độ chơi
- `maps_menu`: Chọn đường đua
- `settings_menu`: Cài đặt game
- `garage_menu`: Chọn xe và phụ kiện
- `pause_menu`: Menu tạm dừng

### 9. multiplayer.py
**Chức năng**: Xử lý chế độ chơi mạng. Đồng bộ hóa vị trí, rotation, model, texture, username, highscore của các người chơi.

**Cấu trúc chính**:
- `__init__()`: Khởi tạo client và event handlers
- `update_multiplayer()`: Cập nhật vị trí người chơi mỗi frame
- Event handlers: `onReplicatedVariableCreated`, `onReplicatedVariableUpdated`, etc.

**Đồng bộ hóa**:
- Vị trí, rotation, model, texture
- Username, highscore, cosmetic
- Leaderboard cập nhật real-time

### 10. server.py
**Chức năng**: Tạo và quản lý server multiplayer. Handle client connections và đồng bộ hóa dữ liệu.

**Cấu trúc chính**:
- `__init__()`: Khởi tạo server với IP/PORT
- `update_server()`: Khởi tạo server khi start_server = True
- Event handlers: `onClientConnected`, `onClientDisconnected`
- Message handlers: `MyPosition`, `MyRotation`, etc.

**Standalone mode**: Có thể chạy server riêng biệt

### 11. particles.py
**Chức năng**: Tạo hiệu ứng hạt (particles) cho game. Bao gồm bụi khi xe chạy và trail khi drift.

**Cấu trúc chính**:
- `Particles`: Class tạo bụi với texture khác nhau theo track
- `TrailRenderer`: Class tạo đường trail khi drift
- `PathObject`: Class điểm path cho AI (không phải particle)

### 12. sun.py
**Chức năng**: Tạo hệ thống ánh sáng mặt trời với shadows. Sử dụng DirectionalLight của Panda3D.

**Cấu trúc chính**:
- `__init__()`: Tạo DirectionalLight với shadow caster
- `update()`: Cập nhật vị trí light theo xe
- `update_resolution()`: Thay đổi độ phân giải shadow

### 13. achievements.py
**Chức năng**: Hệ thống thành tựu. Tạo và kiểm tra các thành tựu dựa trên hành động người chơi.

**Cấu trúc chính**:
- `RaceMasterAchievements`: Class chính quản lý tất cả thành tựu
- Các subclass theo track: `SandTrackAchievements`, `GrassTrackAchievements`, etc.
- `CarAchievements`: Thành tựu mở khóa xe và màu sắc

**Các loại thành tựu**:
- Cơ bản: Chơi game, vào garage, chơi multiplayer
- Thời gian: Đạt thời gian nhất định trên mỗi track
- Mở khóa: Xe mới, màu sắc, đường đua, chế độ drift

### 14. tracks/forest_track.py (và các track khác)
**Chức năng**: Định nghĩa đường đua Forest Track. Bao gồm model, boundaries, walls, decorations.

**Cấu trúc chính**:
- `__init__()`: Khởi tạo track với model, collider, walls, decorations
- `update()`: Logic đặc biệt cho track (wall triggers, finish line)

**Components**:
- `finish_line`: Điểm kết thúc
- `boundaries`: Ranh giới track
- `wall1-8`: Các bức tường động
- `trees`, `thin_trees`: Decorations
- `track`: List các elements chính
- `details`: List decorations

---

## Các file track khác (sand_track.py, grass_track.py, etc.)
Tương tự forest_track.py nhưng với layout và decorations khác nhau cho từng loại đường đua.

## UrsinaAchievements/
Thư viện bên thứ 3 để quản lý thành tựu, bao gồm:
- `__init__.py`: Code chính của thư viện
- `achievements.json`: Lưu trạng thái thành tựu
- `confetti.png`: Icon thành tựu

---

## Kết luận
Game Rally có cấu trúc modular rõ ràng với từng file chịu trách nhiệm một chức năng cụ thể. Việc tách biệt logic giúp code dễ maintain và mở rộng. Hệ thống hand controller và multiplayer là những tính năng nổi bật, sử dụng các thư viện bên ngoài như MediaPipe, OpenCV, và UrsinaNetworking.