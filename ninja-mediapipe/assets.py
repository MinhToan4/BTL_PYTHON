# assets.py
import pygame
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


# ========== Helpers ==========
def _load_img_raw(name: str):
    """Load ảnh với convert_alpha nếu tồn tại, ngược lại trả None."""
    p = ASSETS_DIR / name
    if not p.exists():
        return None
    try:
        surf = pygame.image.load(str(p)).convert_alpha()
        return surf
    except Exception:
        return None


def _first_existing(names):
    """Thử nhiều tên file, trả về surface đầu tiên tìm thấy hoặc None."""
    for n in names:
        s = _load_img_raw(n)
        if s is not None:
            return s
    return None


def _fit_into_box(img: pygame.Surface, box: tuple[int, int], preserve_ratio: bool = True) -> pygame.Surface:
    """Scale ảnh vào trong hộp (w,h). Nếu preserve_ratio=True thì giữ tỉ lệ, không méo."""
    w, h = box
    if not preserve_ratio:
        return pygame.transform.smoothscale(img, (max(1, w), max(1, h)))
    iw, ih = img.get_width(), img.get_height()
    if iw == 0 or ih == 0:
        return pygame.transform.smoothscale(img, (max(1, w), max(1, h)))
    s = min(w / iw, h / ih)
    nw, nh = max(1, int(iw * s)), max(1, int(ih * s))
    return pygame.transform.smoothscale(img, (nw, nh))


def create_fruit_image(color, size=(120, 120)):
    """Fallback tạo ảnh tròn màu nếu thiếu file thực."""
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    r = min(w, h) // 2 - 4
    pygame.draw.circle(s, color, (w // 2, h // 2), r)
    pygame.draw.circle(s, (255, 255, 255, 180), (w // 2, h // 2), r, 2)
    return s


# ========== Background ==========
def load_background(size, names=("background.jpg","background.png","bg.jpg","bg.png")):
    """Tìm 1 file background trong ./assets rồi scale đúng kích thước cửa sổ."""
    for name in names:
        surf = _load_img_raw(name)
        if surf is not None:
            return pygame.transform.smoothscale(surf, size)

    # Fallback: nền gradient tối
    w, h = size
    bg = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        c = int(12 + 28 * t)
        pygame.draw.line(bg, (c, c, c + 6), (0, y), (w, y))
    # vệt highlight
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.circle(overlay, (60, 120, 200, 40), (int(w * 0.75), int(h * 0.25)), int(min(w, h) * 0.5))
    bg.blit(overlay, (0, 0))
    return bg


# ========== Fruit/Bomb loader ==========
def load_images():
    """
    Trả về:
        fruit_imgs: list[pygame.Surface] các quả đã scale hợp lý (giữ tỉ lệ)
        bomb_img  : pygame.Surface
    Hỗ trợ các file (thử lần lượt):
        - Táo       : apple.png, fruit_apple.png, red_apple.png   -> hộp 120x120
        - Cam       : orange.png, fruit_orange.png                 -> hộp 120x120
        - Dưa hấu   : fruit_watermelon.png, watermelon.png, melon.png, fruit_melon.png -> hộp 150x150
        - Dứa       : fruit_pineapple.png, pineapple.png, ananas.png -> hộp 150x150
        - Dâu       : fruit_strawberry.png, strawberry.png         -> hộp 120x120
        - Chuối     : fruit_banana.png, banana.png                 -> hộp 140x140
        - Nho       : fruit_grape.png, grape.png, fruit_grapes.png -> hộp 130x130
        - Bom       : bomb.png -> hộp 100x100
    """
    fruit_imgs = []

    # Apple (120)
    apple_raw = _first_existing(["apple.png", "fruit_apple.png", "red_apple.png"])
    apple = _fit_into_box(apple_raw, (120, 120)) if apple_raw else create_fruit_image((255, 60, 60), (120, 120))
    fruit_imgs.append(apple)

    # Orange (120)
    orange_raw = _first_existing(["orange.png", "fruit_orange.png"])
    orange = _fit_into_box(orange_raw, (120, 120)) if orange_raw else create_fruit_image((255, 165, 0), (120, 120))
    fruit_imgs.append(orange)

    # Watermelon (150)
    watermelon_raw = _first_existing(["fruit_watermelon.png", "watermelon.png", "melon.png", "fruit_melon.png"])
    watermelon = _fit_into_box(watermelon_raw, (150, 150)) if watermelon_raw else create_fruit_image((60, 200, 90), (150, 150))
    fruit_imgs.append(watermelon)

    # Pineapple (150)
    pineapple_raw = _first_existing(["fruit_pineapple.png", "pineapple.png", "ananas.png"])
    pineapple = _fit_into_box(pineapple_raw, (150, 150)) if pineapple_raw else create_fruit_image((250, 220, 60), (150, 150))
    fruit_imgs.append(pineapple)

    # Strawberry (120)
    strawberry_raw = _first_existing(["fruit_strawberry.png", "strawberry.png"])
    strawberry = _fit_into_box(strawberry_raw, (120, 120)) if strawberry_raw else create_fruit_image((235, 40, 70), (120, 120))
    fruit_imgs.append(strawberry)

    # Banana (140)
    banana_raw = _first_existing(["fruit_banana.png", "banana.png"])
    banana = _fit_into_box(banana_raw, (140, 140)) if banana_raw else create_fruit_image((250, 230, 80), (140, 140))
    fruit_imgs.append(banana)

    # >>> NEW: Grape (130)
    grape_raw = _first_existing(["fruit_grape.png", "grape.png", "fruit_grapes.png"])
    grape = _fit_into_box(grape_raw, (130, 130)) if grape_raw else create_fruit_image((160, 100, 255), (130, 130))
    fruit_imgs.append(grape)

    # Bomb (100)
    bomb_raw = _first_existing(["bomb.png"])
    bomb = _fit_into_box(bomb_raw, (100, 100)) if bomb_raw else create_fruit_image((50, 50, 50), (100, 100))

    return fruit_imgs, bomb
