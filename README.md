# 🎮 KHO GAME GESTURE AI - ĐIỀU KHIỂN BẰNG CỬ CHỈ TAY


**Kho Game GestureAI** là một bộ sưu tập game Python tích hợp công nghệ **MediaPipe Hand Tracking** để điều khiển game bằng cử chỉ tay qua webcam. Dự án bao gồm 3 game hoàn chỉnh, launcher đẹp mắt với PyQt6, và AI Chatbot trợ lý được hỗ trợ bởi Google Gemini AI.

## 📋 Mục Lục

- [Tổng Quan](#-tổng-quan)
- [Tính Năng](#-tính-năng)
- [Công Nghệ](#-công-nghệ-sử-dụng)
- [Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [Yêu Cầu Hệ Thống](#-yêu-cầu-hệ-thống)
- [Cài Đặt](#-cài-đặt)
- [Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng)
- [Các Game Có Sẵn](#-các-game-có-sẵn)
- [Điều Khiển](#-điều-khiển)
- [AI Chatbot](#-ai-chatbot-trợ-lý)
- [Đóng Góp](#-đóng-góp)

---

## 🌟 Tổng Quan

Dự án này là một hệ thống game giải trí tích hợp AI, cho phép người chơi:
- ✨ **Điều khiển game không tiếp xúc** bằng cử chỉ tay qua camera
- 🎯 **Trải nghiệm 3 game đa dạng** với thể loại khác nhau
- 🤖 **Trò chuyện với AI** để nhận gợi ý về game, mẹo chơi, và so sánh
- 🎨 **Giao diện launcher hiện đại** với PyQt6 và gradient đẹp mắt
- 🏆 **Hệ thống điểm cao** lưu trữ thành tích người chơi



---

## ✨ Tính Năng

### 🎮 Launcher Chính
- **Giao diện PyQt6 hiện đại** với gradient và hiệu ứng đẹp mắt
- **4 Tab chức năng**:
  - 🎯 Kho Game - Chọn và khởi chạy game
  - 🤖 AI Trợ Lý - Chat với AI về game
  - ⚙️ Cài Đặt - Tùy chỉnh camera, âm thanh, độ nhạy
  - 📖 Hướng Dẫn - HDSD chi tiết

### 🤖 AI Chatbot Trợ Lý
- **Powered by Google Gemini AI** (2.5 Flash & Pro)
- **Auto-failover** giữa các API key và model
- **Đa ngôn ngữ** - Tự động phát hiện và trả lời bằng ngôn ngữ phù hợp
- **Gợi ý thông minh** về game phù hợp, mẹo chơi, so sánh game

### 🎯 3 Game Hoàn Chỉnh
1. **🐦 Flappy Bird** - Arcade endless runner
2. **🍎 Fruit Ninja** - Action slicing game
3. **🏎️ Race Master 3D** - Racing 3D với multiplayer

### 🔧 Tính Năng Kỹ Thuật
- **MediaPipe Hand Tracking** - Nhận diện 21 điểm trên bàn tay
- **Fallback Mode** - Chơi bằng bàn phím nếu không có camera
- **Mock MediaPipe** - Chạy được ngay cả khi MediaPipe không khả dụng
- **Hot-reload** - Launcher không đóng khi chạy game
- **Cross-platform** - Hỗ trợ Windows, macOS, Linux

---

## 🛠️ Công Nghệ Sử Dụng

### Backend & Game Engine
- **Python 3.8+** - Ngôn ngữ lập trình chính
- **Pygame** - Engine cho Flappy Bird và Fruit Ninja
- **Ursina Engine** - Engine 3D cho Race Master 3D
- **OpenCV** - Xử lý video từ webcam
- **MediaPipe** - Nhận diện bàn tay và cử chỉ

### Frontend & UI
- **PyQt6** - Framework UI cho launcher
- **Custom styling** - Gradient, animation, hover effects

### AI & Machine Learning
- **Google Generative AI (Gemini)** - Chatbot AI
- **gemini-2.5-flash** - Model chính (nhanh, nhiều quota)
- **gemini-2.5-pro** - Model dự phòng (chất lượng cao)

### Storage & Data
- **JSON** - Lưu trữ điểm cao, cài đặt
- **Local file system** - Quản lý assets và data

---

## 📁 Cấu Trúc Dự Án

```
BTL_PYTHON/
├── 📄 game_launcher.py          # Launcher chính (PyQt6)
├── 📄 ai_config.py               # Cấu hình AI Gemini
├── 📄 README.md                  # File này
├── 📄 requirements.txt           # Dependencies chung
│
├── 🎮 flappy-mediapipe/          # Game Flappy Bird
│   ├── main.py                   # Entry point
│   ├── game_core.py              # Core game logic
│   ├── game_process.py           # Game loop & collision
│   ├── main_menu.py              # Menu chính
│   ├── difficulty_menu.py        # Menu độ khó
│   ├── highscores_process.py     # Xử lý điểm cao
│   ├── global_variables.py       # Biến toàn cục
│   ├── utils_mediapipe.py        # MediaPipe wrapper
│   ├── utils_mediapipe_mock.py   # Mock cho testing
│   ├── highscores.json           # Dữ liệu điểm cao
│   └── gallery/                  # Assets (sprites, audio)
│
├── 🍎 ninja-mediapipe/           # Game Fruit Ninja
│   ├── main.py                   # Entry point & game loop
│   ├── entities.py               # Fruit, Bomb, Explosion
│   ├── hand_tracking.py          # MediaPipe integration
│   ├── assets.py                 # Asset loader
│   ├── audio.py                  # Audio system
│   ├── decals.py                 # Juice effects
│   ├── highscores.py             # High score system
│   ├── settings.py               # Game settings
│   ├── ui.py                     # UI helpers
│   ├── scores.json               # High scores data
│   ├── requirements.txt          # Dependencies
│   ├── assets/                   # Hình ảnh (fruits, bomb, bg)
│   ├── sounds/                   # Âm thanh (slice, bomb, music)
│   └── start_menu/               # Menu system
│
├── 🏎️ Race Master 3D/            # Game đua xe 3D
│   ├── main.py                   # Entry point
│   ├── car.py                    # Player car class
│   ├── ai.py                     # AI opponent
│   ├── multiplayer.py            # Multiplayer system
│   ├── server.py                 # Game server
│   ├── main_menu.py              # Menu system
│   ├── hand_controller.py        # Hand gesture control
│   ├── achievements.py           # Achievement system
│   ├── particles.py              # Particle effects
│   ├── sun.py                    # Lighting system
│   ├── requirements.txt          # Dependencies
│   ├── README.md                 # Game-specific docs
│   ├── assets/                   # 3D models, textures
│   ├── tracks/                   # Track definitions
│   └── highscore/                # High score data
│
└── 📊 UML/                       # Tài liệu thiết kế
    ├── Activity Diagram/
    ├── Sequence Diagram/
    └── Use case Diagram/
```

---

## 💻 Yêu Cầu Hệ Thống

### Phần Cứng
- **CPU**: Intel Core i3 hoặc tương đương (i5+ khuyến nghị cho Race Master 3D)
- **RAM**: 4GB (8GB khuyến nghị)
- **GPU**: Integrated graphics (Dedicated GPU cho Race Master 3D)
- **Webcam**: Bất kỳ (720p+ khuyến nghị)
- **Lưu trữ**: 500MB trống

### Phần Mềm
- **OS**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 hoặc cao hơn
- **Webcam Driver**: Phải được cài đặt và hoạt động

### Kết Nối (Tùy chọn)
- **Internet**: Cần thiết cho AI Chatbot
- **LAN/Internet**: Cần thiết cho Race Master 3D Multiplayer

---

## 🚀 Cài Đặt

### Bước 1: Clone Repository

```bash
git clone https://github.com/your-username/BTL_PYTHON.git
cd BTL_PYTHON
```

### Bước 2: Tạo Virtual Environment (Khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài Đặt Dependencies

#### Cài Đặt Toàn Bộ (Tất cả games)

```bash
# Dependencies cho Launcher và AI
pip install PyQt6 google-generativeai

# Dependencies cho Flappy Bird & Fruit Ninja
pip install pygame opencv-python mediapipe numpy

# Dependencies cho Race Master 3D
pip install ursina ursinanetworking
```

#### Hoặc Cài Đặt Từng Game

**Flappy Bird:**
```bash
cd flappy-mediapipe
pip install pygame opencv-python mediapipe numpy
```

**Fruit Ninja:**
```bash
cd ninja-mediapipe
pip install -r requirements.txt
```

**Race Master 3D:**
```bash
cd "Race Master 3D"
pip install -r requirements.txt
# Khuyến nghị cài Ursina từ GitHub
pip install git+https://github.com/pokepetter/ursina.git
```

### Bước 4: Cấu Hình API Key (Cho AI Chatbot)


### Bước 5: Kiểm Tra Camera

```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Error')"
```

---

## 🎯 Hướng Dẫn Sử Dụng

### Khởi Chạy Launcher

```bash
# Chạy từ thư mục gốc
python game_launcher.py
```

Launcher sẽ hiển thị với 4 tab:
1. **🎯 Kho Game** - Nhấn "🎮 CHƠI NGAY" để khởi chạy game
2. **🤖 AI Trợ Lý** - Chat với AI về game
3. **⚙️ Cài Đặt** - Tùy chỉnh camera, âm lượng, độ nhạy
4. **📖 Hướng Dẫn** - Đọc HDSD chi tiết

### Khởi Chạy Game Riêng Lẻ

**Flappy Bird:**
```bash
cd flappy-mediapipe
python main.py
```

**Fruit Ninja:**
```bash
cd ninja-mediapipe
python main.py
```

**Race Master 3D:**
```bash
cd "Race Master 3D"
python main.py
```

---

## 🎮 Các Game Có Sẵn

### 🐦 1. FLAPPY BIRD

**Thể loại**: Arcade, Endless Runner  
**Độ khó**: Dễ → Trung bình → Khó (3 cấp độ)  
**Thời gian chơi**: 1-5 phút/lượt

#### Đặc điểm
- ✨ **2 chế độ chơi**: 1 tay hoặc 2 tay
- 🎚️ **3 mức độ khó**: Easy (gap rộng, chậm), Medium, Hard (gap hẹp, nhanh)
- 🏆 **Bảng điểm cao**: Top 5 người chơi
- 🎨 **Đồ họa pixel art** phong cách retro
- 🔊 **Âm thanh đầy đủ**: Wing, point, hit, die
- 👁️ **God Mode**: Chế độ bất tử (cho testing)

#### Cách Chơi
- **Chế độ 1 tay**: Di chuyển tay lên → chim bay lên, xuống → chim rơi
- **Chế độ 2 tay**: Tay trái bay lên, tay phải bay xuống
- **Mục tiêu**: Bay qua các ống, tránh va chạm
- **Điểm số**: +1 điểm cho mỗi ống vượt qua

#### Mẹo Chơi
1. 💡 Giữ tay ở giữa màn hình làm điểm chuẩn
2. 💡 Di chuyển nhẹ nhàng, tránh vung mạnh
3. 💡 Nhìn xa phía trước, dự đoán vị trí ống
4. 💡 Giữ nhịp đều, không bay quá cao/thấp

---

### 🍎 2. FRUIT NINJA (CHÉM HOA QUẢ)

**Thể loại**: Action, Arcade  
**Độ khó**: Dễ → Trung bình  
**Thời gian chơi**: 3-10 phút/lượt

#### Đặc điểm
- 🎯 **Air Slicing**: Chém bằng cử chỉ tay qua không trung
- 💥 **7 loại trái cây**: Táo, chuối, nho, cam, dứa, dâu, dưa hấu
- 💣 **Bomb**: Trừ mạng khi chém nhầm
- 🌀 **Hệ thống Combo**: Chém nhanh nhiều quả để nhân điểm
- 🧃 **Juice Decals**: Nước hoa quả bắn tung tóe, màu theo loại quả
- 👹 **Boss Mode**: Xuất hiện mỗi 350 điểm, 15 HP, +70 điểm khi hạ
- 📳 **Screen Shake**: Rung màn hình khi bomb nổ
- 🏆 **High Score System**: Lưu top điểm cao, nhập tên

#### Cách Chơi
- **Điều khiển**: Vung tay để tạo đường chém (theo dõi ngón trỏ)
- **Chém hoa quả**: +10 điểm (điều chỉnh được)
- **Combo**: Chém nhiều quả nhanh → điểm nhân lên
- **Tránh bomb**: Chạm bomb → -1 mạng, hiệu ứng nổ
- **Boss**: 15 HP, bay lên cao, rơi xuống dừng giữa màn hình

#### Mẹo Chơi
1. 💡 Giữ tay ở vị trí trung tâm, sẵn sàng chém mọi hướng
2. 💡 Ưu tiên chém nhiều quả cùng lúc (combo)
3. 💡 Tránh bomb là ưu tiên số 1
4. 💡 Với Boss: Vung tay nhanh liên tục, tập trung vào 1 điểm

#### Cấu Hình Độ Khó
Điều chỉnh trong menu Start hoặc `settings.py`:
- **FPS**: Tốc độ game
- **Gravity**: Trọng lực ảnh hưởng rơi quả
- **Spawn Rate**: Tần suất xuất hiện
- **Combo Window**: Thời gian tính combo

---

### 🏎️ 3. RACE MASTER 3D

**Thể loại**: Racing 3D, Multiplayer  
**Độ khó**: Trung bình → Khó  
**Thời gian chơi**: 5-15 phút/race

#### Đặc điểm
- 🏁 **6 đường đua độc đáo**: Rừng, Cỏ, Hồ, Cát, Thảo Nguyên, Tuyết
- 🚗 **6 loại xe**: Sports Car, Rally Car, Hatchback, Limousine, Lorry, Muscle Car
- 🤖 **AI đối thủ**: Nhiều độ khó, lái xe thông minh
- 🌐 **Multiplayer Mode**: LAN/Online, không giới hạn người chơi
- 🏆 **Hệ thống thành tựu**: Mở khóa achievements
- ☀️ **Dynamic Lighting**: Ánh sáng mặt trời chuyển động
- 💨 **Particle Effects**: Bụi, khói, hiệu ứng drift
- 🎵 **3D Audio**: Âm thanh động cơ, va chạm

#### Cách Chơi
- **Rẽ trái/phải**: Nghiêng tay trái/phải
- **Tăng tốc**: Mở bàn tay (hoặc W)
- **Phanh/Lùi**: Đóng bàn tay (hoặc S)
- **Phanh tay**: Space
- **Reset xe**: G (khi bị lật)
- **Menu**: ESC

#### Multiplayer Setup

**Tạo Server:**
1. Chạy game → Multiplayer
2. Nhập IP (localhost cho local)
3. Nhập Port (mặc định: 25565)
4. Create Server → Join Server

**Tham gia Server:**
1. Chạy game → Multiplayer → Join Server
2. Nhập IP công khai của server
3. Nhập Port
4. Nhấn JOIN

#### Mẹo Chơi
1. 💡 Rẽ mượt mà, tránh đánh lái gấp
2. 💡 Tăng tốc tối đa ở đoạn đường thẳng
3. 💡 Phanh trước khi vào cua gấp
4. 💡 Dự đoán đường đi của đối thủ
5. 💡 Dùng phanh tay để drift góc hẹp

#### Đường Đua Chi Tiết
- **Forest Track** 🌲: Rừng rậm, đường quanh co
- **Grass Track** 🌾: Cánh đồng rộng, tốc độ cao
- **Lake Track** 🏞️: Bên hồ, cảnh đẹp, cua nhiều
- **Sand Track** 🏜️: Sa mạc, đồi cát, trơn trượt
- **Savannah Track** 🦁: Thảo nguyên châu Phi, đường dài
- **Snow Track** ❄️: Băng tuyết, khó kiểm soát

---

## 🕹️ Điều Khiển

### 🖐️ Điều Khiển Bằng Cử Chỉ Tay

#### Flappy Bird
| Cử chỉ | Hành động |
|--------|-----------|
| **Tay lên** (Chế độ 1 tay) | Chim bay lên |
| **Tay xuống** (Chế độ 1 tay) | Chim rơi |
| **Tay trái lên** (Chế độ 2 tay) | Chim bay lên |
| **Tay phải xuống** (Chế độ 2 tay) | Chim rơi |

#### Fruit Ninja
| Cử chỉ | Hành động |
|--------|-----------|
| **Vung tay** | Tạo đường chém (theo ngón trỏ) |
| **Giữ tay yên** | Không chém |

#### Race Master 3D
| Cử chỉ | Hành động |
|--------|-----------|
| **Nghiêng tay trái** | Xe rẽ trái |
| **Nghiêng tay phải** | Xe rẽ phải |
| **Mở bàn tay** | Tăng tốc |
| **Đóng bàn tay** | Phanh |

### ⌨️ Điều Khiển Bằng Bàn Phím (Fallback)

#### Flappy Bird
- **SPACE** hoặc **↑**: Chim bay lên
- **ESC**: Tạm dừng

#### Fruit Ninja
- **Chuột trái + Kéo**: Tạo đường chém
- **ESC**: Tạm dừng

#### Race Master 3D
- **W**: Tăng tốc
- **S**: Phanh/Lùi
- **A/D**: Rẽ trái/phải
- **SPACE**: Phanh tay
- **G**: Reset xe
- **ESC**: Menu

---

## 🤖 AI Chatbot Trợ Lý

### Tính Năng AI

- **🧠 Thông minh**: Powered by Google Gemini 2.5 Flash/Pro
- **🌍 Đa ngôn ngữ**: Tự động phát hiện và trả lời (Việt, Anh, Trung, Nhật...)
- **⚡ Auto-failover**: Tự chuyển model khi quota hết
- **💡 Gợi ý thông minh**: Game phù hợp theo sở thích
- **📚 Tri thức sâu**: Hiểu rõ cơ chế, mẹo chơi từng game

### Ví Dụ Câu Hỏi

**Gợi ý game:**
- "Game nào dễ chơi nhất cho người mới?"
- "Tôi thích tốc độ, nên chơi game nào?"
- "Game nào chơi được với bạn bè?"

**Mẹo chơi:**
- "Làm sao để vượt qua ống trong Flappy Bird?"
- "Mẹo chém hoa quả hiệu quả?"
- "Cách drift trong Race Master 3D?"

**So sánh:**
- "So sánh 3 game về độ khó"
- "Flappy Bird vs Fruit Ninja, game nào hay hơn?"

**Kỹ thuật:**
- "MediaPipe hoạt động như thế nào?"
- "Cử chỉ tay nào dễ nhận diện nhất?"
- "Cài đặt camera tối ưu ra sao?"

### Câu Trả Lời Mẫu

**Q: "Game nào dễ nhất?"**

*AI: 🐦 Flappy Bird là game dễ nhất cho người mới!*

*Lý do:*
- *Cử chỉ đơn giản (chỉ di chuyển tay lên/xuống)*
- *Cơ chế rõ ràng (tránh ống)*
- *Có 3 mức độ khó để làm quen từ từ*

*Mẹo: Bắt đầu ở chế độ Easy, giữ tay ở giữa màn hình! 💡*

---

## 🎨 Screenshots

### Launcher
```
┌─────────────────────────────────────────┐
│   🎮 KHO GAME GESTURE AI 🎮              │
│   ✨ Điều khiển bằng cử chỉ tay ✨        │
├─────────────────────────────────────────┤
│ [🎯 Kho Game] [🤖 AI] [⚙️ Cài Đặt] [📖] │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │🐦 Flappy│  │🍎 Fruit │  │🏎️ Race  │ │
│  │  Bird   │  │  Ninja  │  │ Master  │ │
│  │[🎮 CHƠI]│  │[🎮 CHƠI]│  │[🎮 CHƠI]│ │
│  └─────────┘  └─────────┘  └─────────┘ │
└─────────────────────────────────────────┘

---

## 🔧 Cấu Hình Nâng Cao

### Tùy Chỉnh MediaPipe

**Độ nhạy nhận diện** (`utils_mediapipe.py`):
```python
hand = MediaPipeHand(
    static_image_mode=False,
    max_num_hands=2,              # Số tay tối đa (1-2)
    min_detection_confidence=0.5,  # Độ tin cậy phát hiện (0-1)
    min_tracking_confidence=0.5    # Độ tin cậy theo dõi (0-1)
)
```

### Tùy Chỉnh Độ Khó Game

**Flappy Bird** (`global_variables.py`):
```python
DIFFICULTY_LEVELS = {
    'Easy': {'pipe_vel_x': -3, 'gap_offset': SCREENHEIGHT / 3 * 1.5},
    'Medium': {'pipe_vel_x': -4, 'gap_offset': SCREENHEIGHT / 3},
    'Hard': {'pipe_vel_x': -6, 'gap_offset': SCREENHEIGHT / 3 * 0.8}
}
```

**Fruit Ninja** (`settings.py`):
```python
class GameSettings:
    gravity = 0.4           # Trọng lực
    max_lives = 3           # Mạng tối đa
    slice_points = 10       # Điểm mỗi quả
    combo_window = 1.0      # Thời gian combo (giây)
```

---

## 📊 Hiệu Năng & Tối Ưu

### Yêu Cầu FPS
- **Flappy Bird**: 32 FPS (cố định)
- **Fruit Ninja**: 60 FPS (khuyến nghị)
- **Race Master 3D**: 30-60 FPS (tùy GPU)

### Tối Ưu Hiệu Năng

**Nếu game lag:**
1. Giảm resolution webcam (640x480 thay vì 1280x720)
2. Tắt particle effects (Race Master 3D)
3. Giảm FPS target trong settings
4. Đóng các ứng dụng nền

**Nếu MediaPipe chậm:**
1. Tăng `min_detection_confidence` lên 0.7
2. Giảm `max_num_hands` xuống 1 nếu chỉ dùng 1 tay
3. Giảm resolution camera

---

## 🐛 Xử Lý Lỗi Thường Gặp

### Camera không hoạt động
```
✅ Giải pháp:
1. Kiểm tra camera đã cắm và được cấp quyền
2. Thử chỉ số camera khác trong code (0, 1, 2...)
3. Cài đặt lại driver camera
4. Chơi bằng keyboard (game vẫn chạy)
```

### MediaPipe không cài được
```
✅ Giải pháp:
1. pip install --upgrade pip
2. pip install mediapipe==0.10.14 (phiên bản cụ thể)
3. Dùng mock mode (tự động fallback)
```

### Ursina không chạy (Race Master 3D)
```
✅ Giải pháp:
1. pip install git+https://github.com/pokepetter/ursina.git
2. Cài Visual C++ Redistributable (Windows)
3. Cài Panda3D thủ công: pip install panda3d
```

### AI Chatbot không trả lời
```
✅ Giải pháp:
1. Kiểm tra kết nối Internet
2. Xác nhận API key hợp lệ
3. Kiểm tra quota API (https://makersuite.google.com)
4. Chatbot sẽ tự fallback sang response mặc định
```

### Lỗi Import Module
```
✅ Giải pháp:
1. Kích hoạt virtual environment
2. Cài lại dependencies: pip install -r requirements.txt
3. Kiểm tra Python version (phải 3.8+)
```

---

## 📝 Roadmap Phát Triển

### ✅ Đã Hoàn Thành
- [x] 3 game hoàn chỉnh với MediaPipe
- [x] Launcher PyQt6 với UI đẹp
- [x] AI Chatbot tích hợp Gemini
- [x] Hệ thống highscore cho từng game
- [x] Multiplayer cho Race Master 3D
- [x] Mock mode cho testing không camera

### 🚧 Đang Phát Triển
- [ ] Thêm game thứ 4 (Snake 3D)
- [ ] Voice control (điều khiển bằng giọng nói)
- [ ] Mobile version (Android)
- [ ] Cloud highscore leaderboard
- [ ] Tournament mode

### 💡 Ý Tưởng Tương Lai
- [ ] VR support
- [ ] Streaming integration (Twitch/YouTube)
- [ ] Custom gesture training
- [ ] Mini-games bổ sung
- [ ] Achievements cross-game

---

## 🤝 Đóng Góp

Chúng tôi hoan nghênh mọi đóng góp! 

### Cách Đóng Góp

1. **Fork** repository này
2. **Clone** fork của bạn về máy
3. **Tạo branch** mới: `git checkout -b feature/TenTinhNang`
4. **Commit** thay đổi: `git commit -m 'Thêm tính năng X'`
5. **Push** lên branch: `git push origin feature/TenTinhNang`
6. Tạo **Pull Request**

### Guidelines

- ✅ Code theo chuẩn PEP 8
- ✅ Comment bằng tiếng Việt hoặc tiếng Anh
- ✅ Test kỹ trước khi PR
- ✅ Cập nhật README nếu thêm tính năng
- ✅ Giữ commit message rõ ràng

### Báo Lỗi (Bug Report)

Tạo **Issue** với thông tin:
- Mô tả lỗi chi tiết
- Các bước tái hiện
- OS và Python version
- Log lỗi (nếu có)
- Screenshots/Video (nếu cần)

---

## 👥 Tác Giả & Credits

### Nhóm Phát Triển
- **Tên nhóm**: VTV_VietToanVy
- **Môn học**: BTL Python
- **Năm**: 2025

### Công Nghệ & Thư Viện

Cảm ơn các thư viện mã nguồn mở:
- [MediaPipe](https://mediapipe.dev/) - Hand tracking
- [Pygame](https://www.pygame.org/) - Game framework
- [Ursina](https://www.ursinaengine.org/) - 3D engine
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - UI framework
- [OpenCV](https://opencv.org/) - Computer vision
- [Google Generative AI](https://ai.google.dev/) - AI chatbot

### Tài Nguyên
- Sprites & Assets: [OpenGameArt](https://opengameart.org/)
- Sound Effects: [FreeSound](https://freesound.org/)
- Fonts: [Google Fonts](https://fonts.google.com/)





## 🌟 Lời Cảm Ơn

Cảm ơn bạn đã quan tâm đến **Kho Game GestureAI**! 

Nếu thấy dự án hữu ích, hãy cho chúng tôi một ⭐ trên GitHub!

---

<div align="center">

**🎮 Chơi Game Không Cần Chạm - Chỉ Cần Cử Chỉ! 🎮**

Made with ❤️ by VTV_VietToanVy

[⬆ Về đầu trang](#-kho-game-gesture-ai---điều-khiển-bằng-cử-chỉ-tay)

</div>
