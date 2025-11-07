from __future__ import annotations
import pygame, random, math

# -------------------------------------------------
# Juice decals (vệt nước bắn lên nền)
# - Thời gian tồn tại ~6 giây
# - Màu đậm hơn ~20% (tăng RGB + tăng alpha)
# - Giữ nguyên API:
#     make_splat_from_img(img, pos, angle_rad, scale=1.0) -> JuiceSplat
#     update_and_draw_splats(screen, splats, dt, max_count=50) -> None
# -------------------------------------------------

# Hệ số tăng màu (RGB) ~ +20%
_COLOR_BOOST = 1.20
# Alpha cơ bản tăng (so với trước đây ~180), giờ ~216
_BASE_ALPHA = 216
# Alpha cho các vệt streak
_STREAK_ALPHA = 180
# Khoảng thời gian sống (giây) ~6s
_LIFE_MIN, _LIFE_MAX = 5.5, 6.3


class JuiceSplat:
    def __init__(self, surf: pygame.Surface, pos: tuple[int, int], life: float = 6.0):
        self.surf = surf
        self.pos = pos  # center
        self.life = life
        self.max_life = life
        self.alpha = 255

    def update(self, dt: float):
        self.life -= dt
        if self.life < 0:
            self.life = 0
        # Fade tuyến tính theo thời gian còn lại
        self.alpha = int(255 * (self.life / self.max_life))

    def draw(self, screen: pygame.Surface):
        if self.alpha <= 0:
            return
        img = self.surf.copy()
        img.set_alpha(self.alpha)
        rect = img.get_rect(center=self.pos)
        screen.blit(img, rect)


def _guess_juice_color(img: pygame.Surface) -> tuple[int, int, int, int]:
    """
    Lấy màu 'trung bình' của quả (không cần numpy).
    Bỏ pixel trong suốt, sau đó tăng đậm màu (RGB) + alpha.
    """
    w, h = img.get_width(), img.get_height()
    sample_w, sample_h = max(1, w // 8), max(1, h // 8)
    small = pygame.transform.smoothscale(img, (sample_w, sample_h))

    r = g = b = n = 0
    for y in range(sample_h):
        for x in range(sample_w):
            col = small.get_at((x, y))
            if col.a > 8:  # bỏ pixel trong suốt
                r += col.r; g += col.g; b += col.b; n += 1

    if n == 0:
        return (255, 80, 80, _BASE_ALPHA)

    r //= n; g //= n; b //= n

    # tăng đậm màu ~20%
    r = max(0, min(255, int(r * _COLOR_BOOST)))
    g = max(0, min(255, int(g * _COLOR_BOOST)))
    b = max(0, min(255, int(b * _COLOR_BOOST)))

    return (r, g, b, _BASE_ALPHA)


def _make_blob(color: tuple[int, int, int, int], angle_rad: float, scale: float) -> pygame.Surface:
    """
    Sinh 'vệt nước' bằng ellipse + chấm loang + streak theo hướng chém.
    """
    base_w, base_h = 220, 150
    base_w = int(base_w * scale)
    base_h = int(base_h * scale)

    surf = pygame.Surface((base_w, base_h), pygame.SRCALPHA)

    # lõi ellipse đậm
    pygame.draw.ellipse(surf, color, (0, base_h // 6, base_w, base_h * 2 // 3))

    # các bọt loang xung quanh (alpha cao hơn trước -> đậm hơn)
    for _ in range(16):
        rr = random.randint(10, 28)
        rx = random.randint(rr // 2, base_w - rr // 2)
        ry = random.randint(rr // 2, base_h - rr // 2)
        # giảm mức trừ alpha để đậm hơn (trước là -0..70)
        alpha = max(90, color[3] - random.randint(0, 50))
        pygame.draw.circle(surf, (color[0], color[1], color[2], alpha), (rx, ry), rr)

    # vệt kéo theo hướng chém (streak) với alpha cao hơn
    streak_len = int(base_w * 0.9)
    streak_w   = max(8, int(base_h * 0.12))
    cx, cy = base_w // 2, base_h // 2
    for i in range(4):
        off = (i - 1.5) * (streak_w * 0.75)
        rect = pygame.Rect(0, 0, streak_len, streak_w)
        rect.center = (cx, cy + off)
        pygame.draw.rect(surf, (color[0], color[1], color[2], _STREAK_ALPHA), rect, border_radius=streak_w // 2)

    # xoay theo góc chém
    deg = math.degrees(angle_rad)
    surf = pygame.transform.rotate(surf, deg)
    return surf


def make_splat_from_img(img: pygame.Surface, pos: tuple[int, int], angle_rad: float, scale: float = 1.0) -> JuiceSplat:
    """
    Tạo 1 vệt nước từ ảnh quả:
      - màu lấy theo trung bình của ảnh, tăng đậm 20%
      - kích cỡ vệt phụ thuộc kích cỡ quả
      - tuổi thọ ~6s
    """
    color = _guess_juice_color(img)

    # scale phụ thuộc vào cỡ quả (quả lớn -> vệt to)
    w, h = img.get_width(), img.get_height()
    size_factor = max(w, h) / 140.0
    blob = _make_blob(color, angle_rad, scale * size_factor)

    # thời gian sống ~6s
    life = random.uniform(_LIFE_MIN, _LIFE_MAX)
    return JuiceSplat(blob, pos, life)


def update_and_draw_splats(screen: pygame.Surface, splats: list[JuiceSplat], dt: float, max_count: int = 50):
    """
    Cập nhật + vẽ; tự xoá nếu hết đời; giới hạn số lượng để nhẹ máy.
    Gọi sau khi vẽ background, trước khi vẽ trái cây/HUD.
    """
    for s in splats[:]:
        s.update(dt)
        if s.alpha <= 0:
            splats.remove(s)

    # giới hạn số lượng (giữ các vệt mới nhất)
    while len(splats) > max_count:
        splats.pop(0)

    for s in splats:
        s.draw(screen)


# -------------------------------------------------
# 💥 BOSS EXPLOSION EFFECT (mở rộng)
# -------------------------------------------------
def make_boss_explosion(img: pygame.Surface, center: tuple[int, int], piece_count: int = 40) -> list[JuiceSplat]:
    """
    Hiệu ứng nổ đặc biệt khi BossFruit vỡ:
      - Tung ra nhiều vệt nước lớn.
      - Mỗi vệt có hướng ngẫu nhiên và độ sáng khác nhau.
    Trả về danh sách JuiceSplat để thêm vào splats.
    """
    splats: list[JuiceSplat] = []
    color = _guess_juice_color(img)
    for i in range(piece_count):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(50, 250)
        offset = (int(center[0] + math.cos(angle) * dist),
                  int(center[1] + math.sin(angle) * dist))
        scale = random.uniform(0.6, 1.5)
        splats.append(make_splat_from_img(img, offset, angle, scale))
    return splats
