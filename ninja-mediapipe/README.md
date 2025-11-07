# 🍉 Fruit Ninja (Pygame + OpenCV + MediaPipe)

**Fruit Ninja** là phiên bản “chém hoa quả” điều khiển bằng **cử chỉ tay qua webcam** (hoặc dùng chuột nếu tắt camera).
Dự án viết bằng **Python + Pygame**, nhận diện bàn tay bằng **MediaPipe**, có **combo**, **Boss 15 HP**, **juice decals**, **rung màn hình khi nổ**, menu Start/Game Over, và **High Score**.

> Repo tối ưu để **clone về chạy ngay** với `requirements.txt` tối giản.

---

## ✨ Tính năng chính
- 🎥 Air control: chém bằng tay (hoặc chuột).
- 🍎 Spawn 1–3 quả theo nhịp, vị trí/vận tốc ngẫu nhiên.
- 💥 Bomb: trừ mạng khi chém trúng, hiệu ứng nổ particle.
- 🌀 Combo: chém nhiều quả nhanh liên tiếp nhân điểm (cấu hình được).
- 🧃 Juice decals: nước bắn dính nền, mờ dần ~6 giây, màu theo ảnh quả.
- 👹 Boss: mỗi 350 điểm, **HP=15**, phát sáng, **bay lên 1/2 màn** rồi **rơi xuống dừng giữa**, nổ rung +70 điểm.
- 🎚️ Difficulty: chỉnh trong menu; FPS, gravity, spawn… trong `settings.py`.
- 🏆 High Score: lưu `scores.json`, nhập tên khi lập kỷ lục.
- 🎵 Audio: nhạc nền + hiệu ứng chém/nổ (`pygame.mixer`).

---

## 🧱 Cấu trúc thư mục (rút gọn)
```
project/
├── assets/            # ảnh
├── sounds/            # âm thanh
├── start_menu/        # menu chính + game over
├── assets.py          # load ảnh/background
├── audio.py           # init âm thanh
├── decals.py          # hiệu ứng vệt nước
├── entities.py        # Fruit, Bomb, Explosion, ...
├── hand_tracking.py   # MediaPipe + OpenCV
├── highscores.py      # điểm cao (scores.json)
├── main.py            # game loop & gameplay
├── settings.py        # cấu hình game
├── ui.py              # HUD helpers
├── scores.json        # dữ liệu high score
├── requirements.txt   # thư viện
└── README.md
```

---

## 🧠 Vai trò các mô-đun
- **main.py**: khởi tạo & vòng lặp game; spawn; slash; combo; boss; HUD; high score; menu.
- **entities.py**: `Fruit/Bomb/FruitHalf/Explosion/Particle`; `spawn_fruit()`; `set_dependencies()`.
- **decals.py**: blob + streak theo góc chém, mờ dần; màu suy ra từ ảnh quả; API `make_splat_from_img()`, `update_and_draw_splats()`.
- **hand_tracking.py**: MediaPipe Hands + OpenCV; trả toạ độ ngón trỏ theo kích thước màn.
- **audio.py**: init mixer; trả `slice_sound`, `bomb_sound`; bật nhạc nền.
- **assets.py**: load ảnh trái cây/bomb; scale background hợp kích thước.
- **ui.py**: `draw_text(...)` vẽ HUD.
- **start_menu/**: `run_menu(...)`, `game_over_menu`.
- **highscores.py**: `best_score()`, `qualifies()`, `submit_score()`.

---

## 🔧 Cài đặt & chạy
**Yêu cầu:** Python 3.10+ (khuyến nghị 3.11), webcam (nếu dùng air control).

Cài thư viện:
```bash
pip install -r requirements.txt
```
`requirements.txt` gợi ý:
```txt
pygame==2.5.2
opencv-python==4.10.0.84
mediapipe==0.10.15
numpy>=1.26.0
```

Chạy game:
```bash
python main.py
```

---

## 🕹️ Cách chơi
- Quét ngón trỏ (hoặc chuột) qua trái cây để chém.
- Combo: chém nhiều quả nhanh liên tiếp để nhân điểm.
- Tránh Bomb: chém trúng sẽ mất 1 mạng và trừ điểm.
- Boss: xuất hiện mỗi 350 điểm, **15 HP**, phát sáng, bay lên rồi rơi xuống giữa màn, nổ +70 điểm.

---

## ⚙️ Tinh chỉnh nhanh (settings.py)
- `fruit_spawn_interval`, `bomb_rate`, `gravity`, `slice_trail_length`, `combo_time`, `max_lives`, `fps`.
- Boss: `next_boss_score` (mốc kích hoạt, +350 sau mỗi lần), `boss_hp = 15`.

---

## 🧰 Troubleshooting
- `pygame.error: font not initialized` → gọi `pygame.init()` trước khi tạo font.
- Camera đen → kiểm tra quyền webcam / ứng dụng khác đang dùng camera.
- Âm thanh không phát → mixer không init; game vẫn chạy.
- Lag → giảm độ phân giải, giảm số lượng decal (tham số `max_count` trong `decals.py`).

---

## 📦 .gitignore gợi ý
```
__pycache__/
*.pyc
.venv/
.env/
.idea/
.vscode/
scores.json
.DS_Store
Thumbs.db
```

---

## 🕒 Changelog ngắn
- v1.0: nền Pygame + camera + slash + bomb + decal.
- v1.1: combo, spawn 1–3 quả, tối ưu assets.
- v1.2: Boss 15 HP, glow + rung + splash lớn, bay lên/rơi xuống mượt.

**Enjoy slicing!** ✂️🍉

