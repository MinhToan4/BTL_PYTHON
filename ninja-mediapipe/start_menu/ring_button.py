from __future__ import annotations
import pygame, os, math

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets")

def _try_load(paths: tuple[str, ...]) -> pygame.Surface | None:
    for name in paths:
        p = os.path.join(ASSETS_DIR, name)
        if os.path.exists(p):
            try:
                return pygame.image.load(p).convert_alpha()
            except Exception:
                pass
    return None

def _fit_into_box(img: pygame.Surface, box: int) -> pygame.Surface:
    w, h = img.get_width(), img.get_height()
    s = min(box / max(w, h), 1.0)
    return pygame.transform.smoothscale(img, (max(1, int(w*s)), max(1, int(h*s))))

class RingButtonCW:
    """
    Nút tròn chữ chạy theo CHIỀU KIM ĐỒNG HỒ (đọc xuôi), quả xoay NGƯỢC chiều.
    - TỰ CĂN số ký tự quanh vòng (auto-fit), không còn cố định *6.
    - Có thể nới khoảng cách giữa các từ qua `word_gap`.
    - Tham số chính:
        label:        chuỗi nhãn (ví dụ: "HOW TO PLAY")
        speed_deg:    tốc độ quay chữ (deg/second), dương → text quay thuận
        density:      hệ số mật độ chữ (0.8–1.3 khuyến nghị)
        word_gap:     số khoảng trắng thêm giữa các từ (0,1,2...)
        sep_spaces:   số khoảng trắng giữa 2 bản sao nhãn (khi lặp)
    """
    def __init__(self, center, radius, label, *,
                 ring_color=(60,160,220), glow_color=(60,160,220),
                 fruit_candidates=(), fruit_fallback=(220,220,220),
                 font_name="Consolas",
                 speed_deg: float = 30.0,
                 density: float = 1.0,
                 word_gap: int = 0,
                 sep_spaces: int = 3,
                 min_repeat: int = 1,
                 max_repeat: int = 12):
        self.cx, self.cy = center
        self.r = radius
        self.label = str(label)
        self.ring_color, self.glow_color = ring_color, glow_color
        self.font = pygame.font.SysFont(font_name, max(22, radius//5), bold=True)

        # animation
        self.speed = float(speed_deg)          # text: quay THUẬN (clockwise)
        self.angle = 0.0                       # tích luỹ góc cho text
        self.fruit_angle = 0.0                 # góc quay quả (ngược chiều)
        self.fruit_speed = abs(self.speed)     # tốc độ quả; sẽ quay CCW do pygame dùng CCW dương

        # spacing controls
        self.density = max(0.5, float(density))
        self.word_gap = max(0, int(word_gap))
        self.sep_spaces = max(1, int(sep_spaces))
        self.min_repeat = max(1, int(min_repeat))
        self.max_repeat = max(self.min_repeat, int(max_repeat))

        fruit = _try_load(fruit_candidates)
        if fruit is None:
            fruit = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(fruit, fruit_fallback, (radius, radius), int(radius*0.7))
        self.fruit_img = _fit_into_box(fruit, int(radius*1.25))

        self._ring_base = self._make_ring_graphics(radius, ring_color, glow_color)
        self._cached_text = None  # cache chuỗi đã auto-fit theo bán kính & font

    # ---------- graphics helpers ----------
    def _make_ring_graphics(self, radius: int, ring_color, glow_color) -> pygame.Surface:
        size = radius*2 + 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size//2, size//2)
        outer = radius
        inner = int(radius*0.6)
        # glow
        for i in range(8, 0, -1):
            a = max(8, int(18*i))
            pygame.draw.circle(surf, (*glow_color, a), center, outer + i*2, width=8)
        # ring
        pygame.draw.circle(surf, (*ring_color, 220), center, outer, width=16)
        pygame.draw.circle(surf, (255,255,255,180), center, outer, width=3)
        pygame.draw.circle(surf, (0,0,0,40), center, inner, width=3)
        return surf

    def _build_text_for_ring(self) -> str:
        """
        Xây chuỗi ký tự để rải đều quanh vòng:
        - Thêm khoảng trắng giữa các từ (word_gap).
        - Thêm sep_spaces giữa các bản sao nhãn.
        - Lặp đủ số lần (auto-fit) để kín chu vi.
        """
        # R là bán kính vẽ chữ (nhỏ hơn vòng một chút)
        R = int(self.r * 0.86)
        circumference = 2 * math.pi * R

        # Ước lượng độ rộng ký tự trung bình
        avg_w = max(6, int(self.font.size("A")[0] * 0.9))
        # Số ký tự cần có quanh vòng
        desired_chars = max(12, int((circumference / avg_w) * self.density))

        # Tăng khoảng cách giữa các từ (nếu có)
        if " " in self.label and self.word_gap > 0:
            parts = self.label.split()
            gap = " " * (self.word_gap + 1)   # +1 vì đã có 1 khoảng trắng
            base_label = gap.join(parts)
        else:
            base_label = self.label

        # Thêm khoảng trắng phân cách giữa các bản sao nhãn
        sep = " " * self.sep_spaces
        base = base_label + sep

        # Tính số lần lặp tối thiểu để đạt desired_chars
        if len(base) == 0:
            base = " " * 3  # fallback an toàn
        repeat = max(self.min_repeat, min(self.max_repeat, math.ceil(desired_chars / len(base))))
        text = base * repeat

        # Nếu vẫn thiếu một chút → nối thêm partial để đủ phủ kín
        while len(text) < desired_chars and repeat < self.max_repeat:
            text += base
            repeat += 1
        return text

    def _draw_text_clockwise(self, target: pygame.Surface, base_angle_deg: float):
        """
        Vẽ chữ xoay THUẬN chiều kim đồng hồ, đọc xuôi:
          - đi theo theta_deg = base - i*step (i tăng → theta giảm → clockwise)
          - đặt glyph xoay bám tiếp tuyến: rot = -theta_deg + 90
        """
        # cache chuỗi theo font/radius để không rebuild mỗi frame
        if self._cached_text is None:
            self._cached_text = self._build_text_for_ring()

        text = self._cached_text
        R = int(self.r * 0.86)
        step = 360 / max(1, len(text))
        base = base_angle_deg
        for i, ch in enumerate(text):
            theta_deg = base - i * step
            theta = math.radians(theta_deg)
            x = self.cx + R * math.cos(theta)
            y = self.cy + R * math.sin(theta)
            rot = -theta_deg + 90  # chữ hướng ra ngoài, đọc xuôi
            glyph = self.font.render(ch, True, (255,255,255))
            glyph = pygame.transform.rotozoom(glyph, rot, 1.0)
            target.blit(glyph, glyph.get_rect(center=(x, y)))

    # ---------- public API ----------
    def update(self, dt: float):
        self.angle = (self.angle + self.speed * dt) % 360.0
        # pygame.transform.rotozoom: góc dương = CCW → để quả quay NGƯỢC, dùng +fruit_speed
        self.fruit_angle = (self.fruit_angle + self.fruit_speed * dt) % 360.0

    def draw(self, screen: pygame.Surface, highlight=False):
        # nền vòng
        ring_rect = self._ring_base.get_rect(center=(self.cx, self.cy))
        screen.blit(self._ring_base, ring_rect)

        # CHỮ: quay THUẬN → base = -self.angle
        self._draw_text_clockwise(screen, base_angle_deg=-self.angle)

        # QUẢ: quay NGƯỢC (CCW với góc dương)
        rot = pygame.transform.rotozoom(self.fruit_img, self.fruit_angle, 1.0)
        fr = rot.get_rect(center=(self.cx, self.cy))
        screen.blit(rot, fr)

        if highlight:
            s = pygame.Surface((self.r*2+10, self.r*2+10), pygame.SRCALPHA)
            pygame.draw.circle(s, (255,255,255,30), (s.get_width()//2, s.get_height()//2), self.r+5)
            screen.blit(s, (self.cx - s.get_width()//2, self.cy - s.get_height()//2))

    def hit(self, pos) -> bool:
        mx, my = pos
        return (mx - self.cx) ** 2 + (my - self.cy) ** 2 <= (self.r * 0.95) ** 2
