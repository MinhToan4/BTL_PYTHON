# 🎮 MediaPipe Hand Tracking Games Collection

Bộ sưu tập **3 game kinh điển** điều khiển bằng **cử chỉ tay qua webcam**, sử dụng công nghệ **MediaPipe Hand Tracking**. Dự án được xây dựng hoàn toàn bằng **Python**, kết hợp **OpenCV** và **MediaPipe** để nhận diện chuyển động bàn tay trong không gian 3D.

> 🎮 **Đặc biệt**: Không cần chuột, không cần bàn phím - chỉ cần vẫy tay để chơi!

---

## 🎯 3 Game trong Bộ sưu tập

### 🍉 **Fruit Ninja - Air Slice Edition**
Game chém hoa quả cổ điển với điều khiển bằng tay không

**Công nghệ**: Pygame + MediaPipe + OpenCV

**Tính năng nổi bật:**
- 🖐️ **Hand Tracking**: Quét ngón tay trỏ để chém quả
- 🍎 **Dynamic Spawn**: Sinh 1-3 quả mỗi lần với quỹ đạo ngẫu nhiên
- 💥 **Bomb System**: Tránh chém bomb - mất mạng và điểm
- 🌀 **Combo Multiplier**: Chém liên tiếp để nhân điểm (×1.3, ×1.6, ×1.9...)
- 🧃 **Realistic Juice**: Hiệu ứng nước bắn với màu sắc theo từng loại quả
- 👑 **Boss Mode**: Boss 6-10 HP xuất hiện định kỳ, bay lên rồi rơi xuống
- 🎚️ **3 Difficulty Levels**: Easy/Normal/Hard với thông số khác nhau
- 🏆 **High Score System**: Lưu top điểm cao, nhập tên khi lập kỷ lục

**Cách chơi:**
- Di chuyển ngón trỏ trước camera
- Quét nhanh qua trái cây để chém
- Tránh bomb và tạo combo dài để đạt điểm cao

**Thư mục**: `ninja-mediapipe/`

---

### 🐦 **Flappy Bird - Hand Control Edition**
Game Flappy Bird điều khiển bằng cử chỉ tay

**Công nghệ**: Pygame + MediaPipe + OpenCV

**Tính năng nổi bật:**
- 🖐️ **Hand Gesture Control**: Giơ tay lên để chim bay, hạ tay xuống để chim rơi
- 🎮 **Fallback Keyboard**: Có thể chơi bằng phím Space khi không có camera
- 📊 **3 Difficulty Levels**:
  - **Easy**: Ống chậm, khoảng cách rộng
  - **Medium**: Tốc độ vừa phải
  - **Hard**: Ống nhanh, khoảng cách hẹp
- 🏆 **High Score System**: Lưu điểm cao nhất với tên người chơi
- 🎵 **Sound Effects**: Âm thanh bay, va chạm, điểm số
- 📹 **Real-time Detection**: Nhận diện 2 tay với độ chính xác cao
- 🎨 **Smooth Animation**: Chim xoay mượt theo góc bay

**Cách chơi:**
- **Hand Tracking Mode**: Giơ tay lên cao để chim bay lên, hạ tay xuống để rơi
- **Keyboard Mode**: Nhấn Space hoặc mũi tên lên để bay
- Tránh ống và mặt đất để sống sót
- Cố gắng vượt qua nhiều ống nhất có thể

**Thư mục**: `flappy-mediapipe/`

---

### 🏎️ **Race Master 3D - Hand Steering Edition**
Game đua xe 3D điều khiển bằng cử chỉ tay

**Công nghệ**: Ursina 3D Engine + MediaPipe + OpenCV

**Tính năng nổi bật:**
- 🖐️ **Hand Steering Control**: 
  - Nghiêng tay trái/phải để lái xe
  - Mở rộng bàn tay để tăng tốc
  - Chụm tay để pause
- 🏁 **6 Unique Tracks**: Sand, Grass, Snow, Forest, Savannah, Lake
- 🤖 **AI Opponents**: Đua với 3 AI có chiến thuật thông minh
- 🎮 **Multiple Control Modes**:
  - Hand tracking (cử chỉ tay)
  - Keyboard (WASD/Arrow keys)
  - Gamepad support
- 🌅 **Dynamic Sun System**: Ánh sáng mặt trời thay đổi theo track
- 🏆 **Achievement System**: Mở khóa thành tựu khi hoàn thành mục tiêu
- 💨 **Particle Effects**: Hiệu ứng bụi, khói, drift
- 🎵 **3D Audio**: Âm thanh động cơ, phanh, va chạm

**Cách chơi:**
- **Hand Tracking Mode**:
  - Nghiêng tay trái để rẽ trái
  - Nghiêng tay phải để rẽ phải
  - Mở rộng bàn tay để tăng tốc
  - Chụm ngón tay để pause
- **Keyboard Mode**: WASD hoặc Arrow keys
- Vượt qua 3 vòng đua nhanh nhất có thể
- Tránh va chạm với AI và rào chắn

**Thư mục**: `Race Master 3D/`

---

## 🎯 Yêu cầu hệ thống

- **Python**: 3.10 trở lên (khuyến nghị Python 3.11)
- **Webcam**: Cần thiết để sử dụng tính năng hand tracking (tùy chọn)
- **RAM**: Tối thiểu 4GB (8GB cho Race Master 3D)
- **CPU**: Dual-core 2.0GHz trở lên (MediaPipe cần xử lý realtime)
- **GPU**: Không bắt buộc nhưng khuyến nghị cho Race Master 3D

---

## 🔧 Cài đặt

### 1. Clone hoặc tải dự án về máy

```bash
git clone <repository-url>
cd BTL_PYTHON
```

### 2. Cài đặt thư viện phụ thuộc

**Cho Fruit Ninja:**
```bash
cd ninja-mediapipe
pip install -r requirements.txt
```

**Cho Flappy Bird:**
```bash
cd flappy-mediapipe
pip install pygame opencv-python mediapipe numpy
```

**Cho Race Master 3D:**
```bash
cd "Race Master 3D"
pip install -r requirements.txt
```

**Hoặc cài đặt tất cả cùng lúc từ thư mục gốc:**
```bash
pip install -r requirements.txt
```

**Các thư viện cần thiết:**
- `pygame==2.5.2` - Game engine cho 2D games
- `opencv-python==4.10.0.84` - Xử lý camera/video
- `mediapipe==0.10.14~0.10.15` - Hand tracking AI
- `numpy>=1.26.0` - Xử lý ma trận/mảng
- `ursina==4.1.1` - 3D game engine cho Race Master 3D
- `ursinanetworking==2.1.4` - Multiplayer support

### 3. Chạy game

**Fruit Ninja:**
```bash
cd ninja-mediapipe
python main.py
```

**Flappy Bird:**
```bash
cd flappy-mediapipe
python main.py
```

**Race Master 3D:**
```bash
cd "Race Master 3D"
python main.py
```

**Hoặc dùng Game Launcher (nếu có):**
```bash
python game_launcher.py
```

---

## 🕹️ Hướng dẫn chơi chi tiết

## 🍉 Fruit Ninja - Air Slice

### Điều khiển

**Chế độ Hand Tracking (mặc định):**
- Di chuyển **ngón trỏ** trước camera để điều khiển con trỏ
- **Quét** ngón tay nhanh qua trái cây để chém
- Càng di chuyển nhanh, hiệu ứng chém càng đẹp

**Chế độ chuột (fallback):**
- Dùng chuột để chém như bình thường
- Tự động kích hoạt khi tắt camera hoặc không phát hiện bàn tay

### Luật chơi

- **Mục tiêu**: Đạt điểm cao nhất có thể bằng cách chém trái cây
- **Điểm cơ bản**: Mỗi quả +10 điểm
- **Combo**: Chém nhiều quả liên tiếp trong 1 giây để nhân điểm (×1.3, ×1.6, ×1.9...)
- **Bomb**: Chém bomb = mất 1 mạng + trừ điểm
- **Boss**: Xuất hiện định kỳ, cần chém nhiều lần (6-10 HP), thưởng +70 điểm
- **Game Over**: Hết 3 mạng hoặc để rơi quá nhiều quả

### Tips & Tricks

- 💡 **Combo là chìa khóa**: Tập trung chém nhanh để tạo combo dài
- 💡 **Quan sát**: Nhìn quỹ đạo bay để dự đoán vị trí chém tối ưu
- 💡 **Tránh bomb**: Đừng quá tham, chém sai bomb sẽ mất combo và mạng
- 💡 **Boss strategy**: Chém liên tục vào boss, đừng để nó rơi xuống
- 💡 **Lighting**: Chơi ở nơi có ánh sáng tốt để camera tracking chính xác hơn

---

## 🐦 Flappy Bird - Hand Control

### Điều khiển

**Chế độ Hand Tracking:**
- **Giơ tay lên cao** (cả 2 tay hoặc 1 tay) → Chim bay lên
- **Hạ tay xuống thấp** → Chim rơi xuống
- Độ cao của tay quyết định tốc độ bay

**Chế độ Keyboard (fallback):**
- **Space** hoặc **↑ (Arrow Up)** → Chim bay lên
- Không nhấn → Chim rơi tự nhiên

### Luật chơi

- **Mục tiêu**: Bay qua nhiều ống nhất có thể
- **Điểm số**: Mỗi ống vượt qua +1 điểm
- **Game Over**: Va chạm với ống hoặc mặt đất
- **Độ khó tăng dần**: Ống di chuyển nhanh hơn khi điểm tăng

### Tips & Tricks

- 💡 **Timing**: Giơ tay đúng lúc, không quá sớm hay muộn
- 💡 **Nhịp điệu**: Tạo nhịp đều để bay qua ống dễ hơn
- 💡 **Tầm nhìn**: Nhìn trước 2-3 ống để chuẩn bị
- 💡 **Camera position**: Ngồi đủ xa để camera thấy cả tay

---

## 🏎️ Race Master 3D - Hand Steering

### Điều khiển

**Chế độ Hand Tracking:**
- **Nghiêng tay trái** (>12% angle) → Rẽ trái
- **Nghiêng tay phải** (>12% angle) → Rẽ phải
- **Mở rộng bàn tay** (khoảng cách ngón tay > 2.0) → Tăng tốc
- **Chụm ngón tay** (khoảng cách < 0.6) → Pause game
- **Giữ tay thẳng** → Đi thẳng

**Chế độ Keyboard:**
- **W/↑** → Tăng tốc
- **S/↓** → Phanh
- **A/←** → Rẽ trái
- **D/→** → Rẽ phải
- **Space** → Phanh tay (drift)

### Luật chơi

- **Mục tiêu**: Hoàn thành 3 vòng đua nhanh nhất
- **Đối thủ**: Đua với 3 AI có kỹ năng khác nhau
- **Tracks**: Chọn 1 trong 6 đường đua
- **Thứ hạng**: Top 1 = Winner, Top 2-4 = hoàn thành

### Tips & Tricks

- 💡 **Drift**: Vào cua nhanh với góc hơi lớn
- 💡 **Racing line**: Đi theo đường ngắn nhất
- 💡 **Overtake**: Vượt AI ở đoạn thẳng, không cua
- 💡 **Practice**: Chơi Easy track trước khi thử Hard

---

## 📁 Cấu trúc dự án tổng quan

```
BTL_PYTHON/
├── game_launcher.py          # Launcher chọn game (nếu có)
├── ai_config.py              # Cấu hình AI trợ lý (nếu có)
├── requirements.txt          # Dependencies tổng hợp
│
├── ninja-mediapipe/          # 🍉 Fruit Ninja
│   ├── main.py
│   ├── settings.py
│   ├── entities.py
│   ├── hand_tracking.py
│   ├── assets.py
│   ├── audio.py
│   ├── decals.py
│   ├── ui.py
│   ├── highscores.py
│   ├── requirements.txt
│   ├── scores.json
│   ├── start_menu/
│   ├── assets/
│   └── sounds/
│
├── flappy-mediapipe/         # 🐦 Flappy Bird
│   ├── main.py
│   ├── game_core.py
│   ├── game_process.py
│   ├── main_menu.py
│   ├── difficulty_menu.py
│   ├── highscores_process.py
│   ├── utils_mediapipe.py
│   ├── utils_mediapipe_mock.py
│   ├── global_variables.py
│   ├── highscores.json
│   └── gallery/
│       ├── sprites/
│       └── audio/
│
└── Race Master 3D/           # 🏎️ Race Master 3D
    ├── main.py
    ├── car.py
    ├── ai.py
    ├── hand_controller.py
    ├── drive.py
    ├── steering.py
    ├── main_menu.py
    ├── achievements.py
    ├── multiplayer.py
    ├── sun.py
    ├── particles.py
    ├── requirements.txt
    ├── tracks/
    ├── assets/
    └── highscore/
```

---

## 🧠 Kiến trúc kỹ thuật tổng quan

### MediaPipe Hand Tracking Pipeline

**Fruit Ninja & Flappy Bird:**
1. **Camera Input**: OpenCV capture frame từ webcam
2. **Hand Detection**: MediaPipe phát hiện bàn tay trong frame
3. **Landmark Extraction**: Lấy 21 điểm khớp của bàn tay
4. **Index Finger Tracking**: Theo dõi vị trí ngón trỏ (Fruit Ninja)
5. **Hand Height Detection**: Đo độ cao trung bình của tay (Flappy Bird)
6. **Game Input**: Chuyển đổi thành input game

**Race Master 3D:**
1. **Camera Input**: OpenCV capture frame từ webcam
2. **Hand Detection**: MediaPipe phát hiện bàn tay
3. **Hand Angle Calculation**: Tính góc nghiêng của bàn tay
4. **Gesture Recognition**: Nhận diện cử chỉ (mở rộng/chụm)
5. **Steering Control**: Điều khiển góc lái theo góc tay
6. **Drive Control**: Điều khiển tăng tốc/phanh theo gesture

### Sơ đồ Architecture

```
┌─────────────┐
│   Webcam    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   OpenCV    │ ← Capture frame
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  MediaPipe  │ ← Hand detection & landmarks
└──────┬──────┘
       │
       ├──────────────────┬──────────────────┐
       ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Fruit Ninja  │  │ Flappy Bird  │  │Race Master 3D│
│   (Pygame)   │  │   (Pygame)   │  │   (Ursina)   │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🎨 Screenshots & Demo

*(Có thể thêm ảnh chụp màn hình ở đây)*

**Fruit Ninja:**
- Menu chính với ring buttons
- Gameplay với combo counter
- Boss battle với glow effect
- Camera preview mode
- High score board

**Flappy Bird:**
- Main menu với difficulty selection
- Gameplay với hand tracking overlay
- High score screen
- Game over animation

**Race Master 3D:**
- 3D race tracks từ nhiều góc nhìn
- Hand steering demo
- AI opponents racing
- Achievement unlock screen
- Multiple camera views

---

## 🔍 Debug & Troubleshooting

### Camera không hoạt động
```
✓ Kiểm tra quyền truy cập webcam
✓ Đóng các ứng dụng khác đang dùng camera (Zoom, Teams...)
✓ Thử đổi camera_index trong settings (0, 1, 2...)
✓ Cài driver camera mới nhất
✓ Kiểm tra camera có sáng đèn LED hay không
```

### Lag/FPS thấp
```
✓ Tắt camera preview trong settings
✓ Giảm resolution camera (edit hand_tracking.py hoặc hand_controller.py)
✓ Giảm max decals (Fruit Ninja)
✓ Giảm số lượng particles (Race Master 3D)
✓ Đóng các chương trình nặng khác
✓ Chơi ở chế độ windowed thay vì fullscreen
```

### Tracking không chính xác
```
✓ Chơi ở nơi có ánh sáng tốt
✓ Tránh ánh sáng từ phía sau (backlight)
✓ Giữ bàn tay trong frame camera
✓ Tránh mặc áo màu da (khó phân biệt với da tay)
✓ Chỉnh `min_detection_confidence` trong code
✓ Ngồi đủ xa để camera thấy cả tay
```

### Không có âm thanh
```
✓ Kiểm tra loa/headphone
✓ Điều chỉnh volume trong settings menu
✓ Mixer có thể lỗi init nhưng game vẫn chạy bình thường
✓ Kiểm tra Windows sound settings
```

### Race Master 3D không chạy
```
✓ Cài đặt đầy đủ Ursina: pip install ursina==4.1.1
✓ Cài đặt pywin32: pip install pywin32==306
✓ Kiểm tra có đủ RAM (tối thiểu 4GB free)
✓ Update driver card màn hình
```

### Hand tracking bị lag hoặc nhảy cóc
```
✓ Giảm `max_num_hands` xuống 1 (thay vì 2)
✓ Tăng `min_tracking_confidence` lên 0.7-0.8
✓ Giảm FPS camera xuống (30 FPS thay vì 60)
✓ Sử dụng webcam tốt hơn (720p/1080p)
```

---

## 🎓 Công nghệ sử dụng

### Game Engines & Frameworks
- **Pygame 2.5.2**: 2D game framework (Fruit Ninja, Flappy Bird)
- **Ursina 4.1.1**: 3D game engine dựa trên Panda3D (Race Master 3D)
- **Panda3D**: 3D engine nền tảng cho Ursina

### AI & Computer Vision
- **MediaPipe 0.10.14-0.10.15**: ML solution cho hand tracking
- **OpenCV 4.10.0**: Computer vision, camera input
- **NumPy**: Xử lý array/matrix cho image processing

### Networking & Others
- **UrsinaNetworking 2.1.4**: Multiplayer support cho Race Master 3D
- **PyWin32**: Windows API integration

---

## 📝 Ghi chú phát triển

### Performance Optimization
- **Fruit Ninja**: Decals batch rendering, particle auto-despawn
- **Flappy Bird**: Mock MediaPipe fallback khi không có camera
- **Race Master 3D**: Thread riêng cho hand detection, không block game loop

### Design Patterns
- **Dependency Injection**: Các module độc lập, dễ test
- **Dataclass**: Cấu hình game (MenuConfig, GameSettings)
- **State Machine**: Menu flow (main → difficulty → game → gameover)
- **Observer Pattern**: Event handling cho input
- **Singleton**: Camera instance dùng chung

### Code Quality
- **Modular Architecture**: Mỗi tính năng là 1 module riêng
- **Error Handling**: Graceful fallback khi không có camera
- **Documentation**: Docstrings và comments chi tiết
- **Naming Convention**: PEP 8 compliant

---

## 🚀 Phát triển tương lai

### Fruit Ninja
- [ ] Multiplayer local (2 players 2 cameras)
- [ ] Power-ups (freeze time, double score...)
- [ ] Leaderboard online
- [ ] Thêm nhiều loại boss với patterns khác nhau
- [ ] Gesture controls nâng cao (pinch to slice)

### Flappy Bird
- [ ] Nhiều skin chim để unlock
- [ ] Day/night cycle
- [ ] Power-ups (shield, slow-mo)
- [ ] Endless mode với random obstacles
- [ ] Gesture alternatives (clap, wave)

### Race Master 3D
- [ ] Online multiplayer với dedicated server
- [ ] Car customization (color, decals)
- [ ] More tracks (city, highway, mountain)
- [ ] Weather effects (rain, fog)
- [ ] Advanced AI với machine learning
- [ ] VR support

### Tổng quan
- [ ] Game launcher với AI assistant (Gemini integration)
- [ ] Universal settings manager
- [ ] Cross-game achievements
- [ ] Unified leaderboard
- [ ] Tutorial system cho hand gestures

---

## 🏆 Thành tích dự án

- ✅ 3 game hoàn chỉnh với hand tracking
- ✅ Hỗ trợ cả 2D và 3D engines
- ✅ Fallback modes khi không có camera
- ✅ High score systems
- ✅ Multiple difficulty levels
- ✅ Professional menu systems
- ✅ Sound và visual effects

---

## 👥 Đóng góp & Credits

**Phát triển bởi**: Nhóm 8 - CT01  
**Dự án**: Bài tập lớn Python - Game với AI  
**Công nghệ**: Pygame + Ursina + MediaPipe + OpenCV

**Special Thanks:**
- Google MediaPipe team
- Pygame community
- Ursina Engine developers
- OpenCV contributors

---



✂️🍉 **Happy Gaming!** 🐦🏎️✨

**Chúc bạn chơi game vui vẻ và trải nghiệm công nghệ AI tuyệt vời!**