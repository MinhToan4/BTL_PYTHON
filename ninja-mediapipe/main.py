# main.py
import pygame, math, random, time, string
from collections import deque

from start_menu import run_menu, MenuConfig
from start_menu.game_over_menu import run_game_over_menu
from settings import GameSettings, apply_menu_to_settings
from audio import init_audio
from assets import load_images, load_background
from entities import set_dependencies, spawn_fruit, Fruit, Bomb, Explosion
from hand_tracking import HandInput
from ui import draw_text
from highscores import best_score, qualifies, submit_score
from decals import make_splat_from_img, update_and_draw_splats
from start_menu.pause_menu import run_pause_menu  # ⏸️ import thêm menu tạm dừng

# ================================================================
#  FRUIT NINJA AIR SLICE - BOSS EDITION
# ================================================================

pygame.init()
settings = GameSettings()
screen = pygame.display.set_mode((settings.width, settings.height))
pygame.display.set_caption("Fruit Ninja Air Slice")
clock = pygame.time.Clock()

# --- Âm thanh ---
slice_sound, bomb_sound = init_audio()
try:
    pygame.mixer.music.set_volume(settings.music_volume)
    pygame.mixer.music.play(-1)
except Exception:
    pass

# --- Hình ảnh ---
fruit_imgs, bomb_img = load_images()
bg_img = load_background((settings.width, settings.height))

# --- Menu khởi đầu ---
_bs = best_score()
best_for_menu = int(_bs) if _bs is not None else None
initial_cfg = MenuConfig()
action, cfg = run_menu(
    screen, clock,
    title="Fruit Ninja Air Slice",
    initial=initial_cfg,
    best_score=best_for_menu
)
if action != "start":
    pygame.quit(); raise SystemExit

settings = apply_menu_to_settings(cfg, settings)
settings.difficulty = cfg.difficulty
settings.hand_preview = cfg.hand_preview
set_dependencies(settings.gravity, slice_sound, bomb_sound)

# --- Camera / Hand tracking ---
hand = HandInput()
hand.setup(settings.hand_enabled, settings.camera_index)

# ================================================================
#   STATE
# ================================================================

fruits = []
explosions = []
splats = []
score = 0
lives = settings.max_lives
combo_count = 0
last_slice_time = 0
last_spawn_time = 0
game_over = False
entering_name = False
name_str = ""
hiscore_saved = False

shake_timer = 0.0
shake_strength = 0

# --- Boss ---
boss_active = False
boss_obj = None
boss_hp = 0
next_boss_score = 350

# --- GUI ---
slice_trail = deque(maxlen=settings.slice_trail_length)
skip_rect = pygame.Rect(0, 0, 120, 40)  # Made the skip button smaller
font = pygame.font.SysFont("Arial", 36)
_ALLOWED = string.ascii_letters + string.digits + " _-."


# ================================================================
#   HÀM HỖ TRỢ
# ================================================================
def reset_game():
    """Reset toàn bộ trạng thái để chơi lại."""
    global fruits, explosions, splats, score, lives
    global combo_count, last_slice_time, last_spawn_time
    global game_over, entering_name, name_str, hiscore_saved
    global shake_timer, shake_strength, boss_active, boss_obj, boss_hp, next_boss_score

    fruits.clear(); explosions.clear(); splats.clear()
    score = 0; lives = settings.max_lives
    combo_count = 0; last_slice_time = 0
    last_spawn_time = time.time()
    game_over = False; entering_name = False
    name_str = ""; hiscore_saved = False
    shake_timer = 0.0; shake_strength = 0
    boss_active = False; boss_obj = None; boss_hp = 0; next_boss_score = 350
    slice_trail.clear()


def back_to_menu():
    """Trở về menu chính và áp dụng cấu hình."""
    global settings, screen, bg_img, cfg
    hand.setup(False, 0)
    _bs = best_score()
    best_for_menu2 = int(_bs) if _bs is not None else None
    action, new_cfg = run_menu(
        screen, clock,
        title="Fruit Ninja Air Slice",
        initial=cfg,
        best_score=best_for_menu2
    )
    if action != "start":
        hand.close(); pygame.quit(); raise SystemExit

    cfg = new_cfg
    settings = apply_menu_to_settings(new_cfg, settings)
    settings.difficulty = new_cfg.difficulty
    settings.hand_preview = new_cfg.hand_preview
    set_dependencies(settings.gravity, slice_sound, bomb_sound)
    hand.setup(settings.hand_enabled, settings.camera_index)

    if screen.get_width() != settings.width or screen.get_height() != settings.height:
        screen = pygame.display.set_mode((settings.width, settings.height))
    bg_img = load_background((settings.width, settings.height))
    reset_game()


def open_game_over_menu_blocking():
    """Hiện menu khi game over."""
    choice = run_game_over_menu(screen, clock, bg_surface=bg_img)
    if choice == "play_again":
        reset_game()
    elif choice == "back_to_menu":
        back_to_menu()
    elif choice == "quit":
        hand.close(); pygame.quit(); raise SystemExit


def trigger_screen_shake(duration=0.5, strength=15):
    """Rung mạnh khi Boss nổ."""
    global shake_timer, shake_strength
    shake_timer = duration
    shake_strength = strength


# ================================================================
#   VÒNG LẶP CHÍNH
# ================================================================

while True:
    dt = clock.get_time() / 1000.0
    finger_pos, rgb = hand.read(settings.width, settings.height) if settings.hand_enabled else (None, None)
    if finger_pos is None:
        finger_pos = pygame.mouse.get_pos()

    # ---------------- Sự kiện ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            hand.close(); pygame.quit(); raise SystemExit

        # ⏸️ Thêm xử lý ESC để mở menu pause
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not (game_over and entering_name):
            result = run_pause_menu(screen, clock, bg_surface=bg_img)
            if result == "resume":
                continue  # tiếp tục chơi
            elif result == "restart":
                reset_game()  # chơi lại mà không cần hàm main
                continue
            elif result == "menu":
                back_to_menu()
                continue
            elif result == "quit":
                hand.close(); pygame.quit(); raise SystemExit
            continue  # ngăn ESC gốc phía dưới chạy thêm

        if event.type == pygame.KEYDOWN:
            if game_over and entering_name:
                if event.key == pygame.K_RETURN:
                    player = name_str.strip() or "PLAYER"
                    try:
                        submit_score(player, score, getattr(settings, "difficulty", "Normal"))
                    except Exception: pass
                    hiscore_saved = True; entering_name = False
                elif event.key == pygame.K_ESCAPE:
                    hiscore_saved = True; entering_name = False
                elif event.key == pygame.K_BACKSPACE:
                    name_str = name_str[:-1]
                else:
                    ch = event.unicode
                    if ch and ch in _ALLOWED and len(name_str) < 16:
                        name_str += ch
                continue
            if event.key == pygame.K_ESCAPE:
                hand.close(); pygame.quit(); raise SystemExit

        if game_over and entering_name and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if skip_rect.collidepoint(event.pos):
                hiscore_saved = True; entering_name = False


    # ---------------- Rung màn hình ----------------
    offset_x = offset_y = 0
    if shake_timer > 0:
        shake_timer -= dt
        offset_x = random.randint(-shake_strength, shake_strength)
        offset_y = random.randint(-shake_strength, shake_strength)

    # ---------------- Vẽ nền ----------------
    if rgb is not None and getattr(settings, "hand_preview", False):
        frame_rgb = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
        frame_rgb = pygame.transform.smoothscale(frame_rgb, (settings.width, settings.height))
        screen.blit(frame_rgb, (offset_x, offset_y))
    else:
        rect = bg_img.get_rect(topleft=(offset_x, offset_y))
        screen.blit(bg_img, rect)

    # ---------------- Decals ----------------
    update_and_draw_splats(screen, splats, dt)

    # ---------------- Trail ----------------
    if not game_over and finger_pos:
        slice_trail.append(finger_pos)
    if len(slice_trail) > 1:
        trail_surf = pygame.Surface((settings.width, settings.height), pygame.SRCALPHA)
        for i in range(len(slice_trail) - 1):
            pygame.draw.line(trail_surf, (255, 255, 255, 150), slice_trail[i], slice_trail[i+1], 5)
        screen.blit(trail_surf, (0, 0))
    if finger_pos:
        pygame.draw.circle(screen, (0, 255, 255), finger_pos, 8)
      # ---------------- Nút Pause hiển thị góc màn hình ----------------
    pause_rect = pygame.Rect(settings.width - 100, 20, 80, 40)
    mouse_pos = pygame.mouse.get_pos()
    hovering = pause_rect.collidepoint(mouse_pos)
    color = (180, 80, 80) if hovering else (150, 50, 50)
    # Draw pause button filled and a border so it matches the style of skip_rect
    pygame.draw.rect(screen, color, pause_rect, border_radius=10)
    pygame.draw.rect(screen, (240,240,240), pause_rect, 2, border_radius=10)
    draw_text(screen, "PAUSE", pause_rect.center, (255, 255, 255), size=22, center=True)

    # Nếu click chuột trái vào nút Pause → mở menu tạm dừng
    if pygame.mouse.get_pressed()[0] and hovering:
        result = run_pause_menu(screen, clock, bg_surface=bg_img)
        if result == "resume":
            continue  # tiếp tục chơi
        elif result == "restart":
            reset_game()
            continue
        elif result == "menu":
            back_to_menu()
            continue
        elif result == "quit":
            hand.close(); pygame.quit(); raise SystemExit
    


    # ================================================================
    #   SPAWN
    # ================================================================
    
    now = time.time()
    if not game_over and not boss_active and now - last_spawn_time > settings.fruit_spawn_interval:
        count = random.randint(1, 3)
        for _ in range(count):
            fruits.append(spawn_fruit(settings.width, settings.height, settings.bomb_rate, fruit_imgs, bomb_img))
        last_spawn_time = now

    # ================================================================
    #   BOSS
    # ================================================================
    if not boss_active and score >= next_boss_score:
        boss_active = True
        boss_hp = 15  # boss trâu hơn
        boss_img = pygame.transform.scale(random.choice(fruit_imgs), (220, 220))
        boss_obj = Fruit(settings.width // 2, settings.height // 2 + 200, boss_img)
        boss_obj.vel_x = 0
        boss_obj.vel_y = -4
        fruits.append(boss_obj)


    # --- Cập nhật Boss ---
    # --- Cập nhật Boss ---
    if boss_active and boss_obj is not None:
        boss_obj.update()

    # Nếu boss vượt khỏi màn hình -> huỷ boss, cho phép spawn lại
    if (
        boss_obj is None
        or boss_obj.y > settings.height + 200
        or boss_obj.y < -200
        or boss_obj.x < -200
        or boss_obj.x > settings.width + 200
    ):
        boss_active = False
        boss_obj = None
        boss_hp = 0
    else:
        # --- Giai đoạn di chuyển boss ---
        target_y_top = settings.height // 2        # bay lên tới giữa màn hình (cao hơn trước)
        target_y_mid = settings.height // 2 + 120  # điểm dừng giữa màn hình, thấp hơn tí cho đẹp

        # Bay lên đến 1/2 màn hình -> bắt đầu rơi chậm xuống giữa
        if boss_obj.vel_y < 0 and boss_obj.y <= target_y_top:
            boss_obj.vel_y = 4  # đảo chiều rơi nhanh xuống
        elif boss_obj.vel_y > 0 and boss_obj.y >= target_y_mid:
            boss_obj.vel_y = 0  # dừng lại lơ lửng

        # --- Hiệu ứng ánh sáng quanh boss ---
        glow_radius = int(140 + 10 * math.sin(pygame.time.get_ticks() * 0.005))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 120, 120), (glow_radius, glow_radius), glow_radius)
        pygame.draw.circle(glow_surf, (255, 255, 180, 80), (glow_radius, glow_radius), glow_radius - 30)
        glow_rect = glow_surf.get_rect(center=(boss_obj.x, boss_obj.y))
        screen.blit(glow_surf, glow_rect)

        boss_obj.draw(screen)





    # ================================================================
    #   UPDATE TRÁI CÂY THƯỜNG
    # ================================================================
    for fruit in fruits[:]:
        if boss_active and fruit is boss_obj:
            continue
        fruit.update()
        if fruit.x < -200 or fruit.x > settings.width + 200 or fruit.y > settings.height + 200:
            if isinstance(fruit, Fruit) and not fruit.is_sliced:
                lives -= 1
            fruits.remove(fruit)
            continue
        fruit.draw(screen)

        if not game_over and not fruit.is_sliced and finger_pos:
            if fruit.get_rect().collidepoint(finger_pos):
                swipe_angle = 0.0
                if len(slice_trail) > 1:
                    p1, p2 = slice_trail[-2], slice_trail[-1]
                    swipe_angle = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
                halves = fruit.slice(push_dir=(0, -1), swipe_angle_rad=swipe_angle)
                combo = (time.time() - last_slice_time) < settings.combo_time
                combo_count = combo_count + 1 if combo else 1
                last_slice_time = time.time()

                if isinstance(fruit, Bomb):
                    lives -= 1
                    score = max(0, score - 5)
                    for h in halves:
                        if isinstance(h, Explosion):
                            explosions.append(h)
                else:
                    score += 10 * combo_count
                    splats.append(make_splat_from_img(fruit.img, (int(fruit.x), int(fruit.y)), swipe_angle, 1.0))
                if fruit in fruits: fruits.remove(fruit)
                if halves:
                    for h in halves:
                        if isinstance(h, Explosion): explosions.append(h)
                        else: fruits.append(h)

    # ================================================================
    #   CHÉM BOSS
    # ================================================================
    if boss_active and boss_obj and finger_pos and boss_obj.get_rect().collidepoint(finger_pos):
        swipe_angle = 0.0
        if len(slice_trail) > 1:
            p1, p2 = slice_trail[-2], slice_trail[-1]
            swipe_angle = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
        boss_hp -= 1
        splats.append(make_splat_from_img(boss_obj.img, (int(boss_obj.x), int(boss_obj.y)), swipe_angle, 1.5))
        if _ := slice_sound: slice_sound.play()
        if boss_hp <= 0:
            trigger_screen_shake()
            for _ in range(6):
                explosions.append(Explosion((boss_obj.x + random.randint(-40,40),
                                             boss_obj.y + random.randint(-40,40))))
            for _ in range(5):
                splats.append(make_splat_from_img(boss_obj.img, (int(boss_obj.x)+random.randint(-30,30),
                                                                 int(boss_obj.y)+random.randint(-30,30)),
                                                                 random.random()*math.pi*2, 2.0))
            score += 70
            boss_active = False
            next_boss_score += 350
            if boss_obj in fruits: fruits.remove(boss_obj)
            boss_obj = None
            boss_hp = 0
            last_spawn_time = time.time() + 1.5  # delay spawn lại sau boss

    # ================================================================
    #   EXPLOSION UPDATE
    # ================================================================
    for ex in explosions[:]:
        ex.update(); ex.draw(screen)
        if ex.is_finished(): explosions.remove(ex)

    # ================================================================
    #   HUD
    # ================================================================
    draw_text(screen, f"Score: {score}", (20, 20))
    draw_text(screen, f"Lives: {lives}", (20, 60))
    draw_text(screen, f"Mode: {getattr(settings,'difficulty','Normal')}", (20, 100))

    # ================================================================
    #   GAME OVER
    # ================================================================
    if lives <= 0 and not game_over:
        game_over = True
        entering_name = True      # luôn cho nhập tên
        hiscore_saved = False

    if game_over:
        if entering_name:
            draw_text(screen, "NEW HIGH SCORE!", (settings.width//2, settings.height//2 - 90),
                      (255, 215, 0), size=40, center=True)
            draw_text(screen, f"Your Score: {score}  •  Mode: {getattr(settings,'difficulty','Normal')}",
                      (settings.width//2, settings.height//2 - 50), (255,255,255), size=28, center=True)
            box_w, box_h = 460, 58
            box_rect = pygame.Rect(0, 0, box_w, box_h)
            box_rect.center = (settings.width//2, settings.height//2 + 10)
            pygame.draw.rect(screen, (30,30,30), box_rect, border_radius=10)
            pygame.draw.rect(screen, (220,220,220), box_rect, 2, border_radius=10)
            disp_name = name_str if name_str else "Enter your name..."
            color = (255,255,255) if name_str else (170,170,170)
            draw_text(screen, disp_name, box_rect.center, color, size=28, center=True)
            mouse_pos = pygame.mouse.get_pos()
            is_hover = skip_rect.collidepoint(mouse_pos)
            # Position the skip button below the Pause control (top-right)
            # pause_rect is defined earlier in the main loop; place skip button under it
            try:
                skip_rect.center = (pause_rect.centerx, pause_rect.bottom + 30)
            except NameError:
                # Fallback: center under the name box if pause_rect isn't available for some reason
                skip_rect.center = (settings.width//2, settings.height//2 + 70)

            pygame.draw.rect(screen, (140,60,60) if is_hover else (120,40,40), skip_rect, border_radius=10)
            pygame.draw.rect(screen, (240,240,240), skip_rect, 2, border_radius=10)
            draw_text(screen, "SKIP SAVE", skip_rect.center, (255,255,255), size=20, center=True)
            # Helper text: put back under the name entry box (original position)
            draw_text(screen, "Enter = Save • ESC = Skip",
                      (settings.width//2, settings.height//2 + 70),
                      (200,200,200), size=22, center=True)
        else:
            pygame.display.flip()
            open_game_over_menu_blocking()
            continue

    pygame.display.flip()
    clock.tick(settings.fps)

hand.close()
pygame.quit()
