import pygame, random, math, time
from decals import make_boss_explosion  # 👑 thêm hiệu ứng boss

# phụ thuộc sẽ được set từ main
GRAVITY = 0.35
_slice_sound = None
_bomb_sound = None

def set_dependencies(gravity: float, slice_sound, bomb_sound):
    global GRAVITY, _slice_sound, _bomb_sound
    GRAVITY = gravity
    _slice_sound = slice_sound
    _bomb_sound = bomb_sound


# -------------------------------------------------
# 💫 Particle & Explosion (giữ nguyên gốc)
# -------------------------------------------------
class Particle:
    def __init__(self, pos):
        import random
        self.pos = [pos[0], pos[1]]
        self.vel = [random.uniform(-3, 3), random.uniform(-5, -2)]
        self.radius = random.randint(3, 6)
        self.life = 24
        self.color = (255, random.randint(50, 100), 0)
    def update(self):
        self.life -= 1
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[1] += 0.3
    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)


class ExplosionParticle:
    def __init__(self, pos):
        import random, math
        self.pos = [pos[0], pos[1]]
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5, 15)
        self.vel = [speed * math.cos(angle), speed * math.sin(angle)]
        self.radius = random.randint(4, 12)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0), (255, 255, 0)]
        self.color = random.choice(colors)
    def update(self):
        self.life -= 1
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[0] *= 0.95
        self.vel[1] *= 0.95
        self.vel[1] += 0.2
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color_with_alpha = (*self.color, alpha)
            particle_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (self.radius, self.radius), self.radius)
            surface.blit(particle_surf, (self.pos[0] - self.radius, self.pos[1] - self.radius))


class Explosion:
    def __init__(self, pos):
        self.pos = pos
        self.particles = [ExplosionParticle(pos) for _ in range(25)]
        self.boom_scale = 0.1
        self.boom_life = 30
        self.max_boom_life = 30
    def update(self):
        self.boom_life -= 1
        if self.boom_life > self.max_boom_life * 0.7:
            self.boom_scale = min(1.2, self.boom_scale + 0.15)
        else:
            self.boom_scale = max(0, self.boom_scale - 0.05)
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
    def is_finished(self):
        return self.boom_life <= 0 and len(self.particles) == 0


# -------------------------------------------------
# 🎯 Base object
# -------------------------------------------------
class GameObject:
    def __init__(self, x, y, img):
        self.x = x; self.y = y; self.img = img
        self.width = img.get_width(); self.height = img.get_height()
        self.vel_x = 0; self.vel_y = 0
        self.angle = 0; self.angle_vel = 0
        self.is_sliced = False
        self.particles = []
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY
        self.angle += self.angle_vel
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
    def draw(self, surface):
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        rect = rotated_img.get_rect(center=(self.x, self.y))
        surface.blit(rotated_img, rect.topleft)
        for p in self.particles:
            p.draw(surface)
    def get_rect(self):
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        return rotated_img.get_rect(center=(self.x, self.y))


# -------------------------------------------------
# ✂️ Fruit and halves
# -------------------------------------------------
def split_surface_simple(img: pygame.Surface, swipe_angle_rad: float):
    w, h = img.get_width(), img.get_height()
    left_half = pygame.Surface((w, h), pygame.SRCALPHA)
    right_half = pygame.Surface((w, h), pygame.SRCALPHA)
    left_half.blit(img, (0, 0)); right_half.blit(img, (0, 0))
    center_x, center_y = w // 2, h // 2
    mask_left = pygame.Surface((w, h), pygame.SRCALPHA)
    mask_right = pygame.Surface((w, h), pygame.SRCALPHA)
    mask_left.fill((255, 255, 255, 255)); mask_right.fill((255, 255, 255, 255))
    line_length = max(w, h) * 2
    dx = math.cos(swipe_angle_rad) * line_length
    dy = math.sin(swipe_angle_rad) * line_length
    cut_points = [(center_x - dx, center_y - dy),
                  (center_x + dx, center_y + dy),
                  (center_x + dx + dy, center_y + dy - dx),
                  (center_x - dx + dy, center_y - dy - dx)]
    pygame.draw.polygon(mask_right, (0, 0, 0, 0), cut_points)
    opposite_points = [(center_x - dx, center_y - dy),
                       (center_x + dx, center_y + dy),
                       (center_x + dx - dy, center_y + dy + dx),
                       (center_x - dx - dy, center_y - dy + dx)]
    pygame.draw.polygon(mask_left, (0, 0, 0, 0), opposite_points)
    left_half.blit(mask_left, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    right_half.blit(mask_right, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return left_half, right_half


class Fruit(GameObject):
    def __init__(self, x, y, img):
        import random
        super().__init__(x, y, img)
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-10, -15)
        self.angle_vel = random.uniform(-5, 5)
        self.sliced_time = None

    def slice(self, push_dir=(1.0, 0.0), swipe_angle_rad: float = 0.0):
        if self.is_sliced: return []
        self.is_sliced = True
        self.sliced_time = time.time()
        if _slice_sound: _slice_sound.play()
        for _ in range(15):
            self.particles.append(Particle((self.x, self.y)))
        left_img, right_img = split_surface_simple(self.img, swipe_angle_rad)
        nx, ny = push_dir; PUSH = 8.0; ANG_BOOST = 3.0
        half1 = FruitHalf(left_img,  self.x - 6*nx, self.y - 6*ny,
                          self.vel_x + PUSH*nx, self.vel_y + PUSH*ny,
                          self.angle, self.angle_vel - ANG_BOOST)
        half2 = FruitHalf(right_img, self.x + 6*nx, self.y + 6*ny,
                          self.vel_x - PUSH*nx, self.vel_y - PUSH*ny,
                          self.angle, self.angle_vel + ANG_BOOST)
        return [half1, half2]


class FruitHalf(GameObject):
    def __init__(self, img, x, y, vel_x, vel_y, angle, angle_vel):
        super().__init__(x, y, img)
        self.vel_x = vel_x; self.vel_y = vel_y
        self.angle = angle; self.angle_vel = angle_vel
        self.is_sliced = True


# -------------------------------------------------
# 💣 Bomb + Slice
# -------------------------------------------------
class Bomb(GameObject):
    def __init__(self, x, y, bomb_img):
        import random
        super().__init__(x, y, bomb_img)
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-10, -15)
        self.angle_vel = random.uniform(-5, 5)
    def slice(self, *args, **kwargs):
        if not self.is_sliced:
            self.is_sliced = True
            if _bomb_sound: _bomb_sound.play()
            for _ in range(15):
                p = Particle((self.x, self.y))
                p.color = (255, 0, 0)
                p.vel = [random.uniform(-8, 8), random.uniform(-8, -2)]
                self.particles.append(p)
            self.vel_x *= 2; self.vel_y *= 1.5; self.angle_vel *= 3
            return [Explosion((self.x, self.y))]
        return []


# -------------------------------------------------
# 👑 BossFruit - đặc biệt, cần nhiều nhát chém
# -------------------------------------------------
class BossFruit(GameObject):
    def __init__(self, x, y, img, hp=8):
        super().__init__(x, y, img)
        self.hp = hp
        self.max_hp = hp
        self.scale = 2.3
        self.img = pygame.transform.smoothscale(img, (int(img.get_width()*self.scale),
                                                      int(img.get_height()*self.scale)))
        self.hit_timer = 0
        self.vel_x = 0
        self.vel_y = random.uniform(-2, -4)
        self.move_phase = random.uniform(0, 2*math.pi)

    def update(self):
        # di chuyển nhẹ
        self.move_phase += 0.03
        self.y += math.sin(self.move_phase) * 0.5
        self.angle += math.sin(self.move_phase * 0.8) * 0.4
        self.hit_timer = max(0, self.hit_timer - 0.02)

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.img, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)
        # HP bar
        bar_w = rect.width * 0.7
        filled = int(bar_w * (self.hp / self.max_hp))
        pygame.draw.rect(surface, (80, 0, 0), (self.x-bar_w/2, self.y-rect.height/2-16, bar_w, 10), border_radius=4)
        pygame.draw.rect(surface, (255, 80, 80), (self.x-bar_w/2, self.y-rect.height/2-16, filled, 10), border_radius=4)

    def slice(self, swipe_angle_rad: float = 0.0):
        if self.hp <= 0: return []
        self.hp -= 1
        self.hit_timer = 0.15
        if _slice_sound: _slice_sound.play()
        if self.hp <= 0:
            # Boss chết
            return [Explosion((self.x, self.y))] + make_boss_explosion(self.img, (self.x, self.y))
        return []


# -------------------------------------------------
# 🪄 Spawn utilities
# -------------------------------------------------
def spawn_fruit(width: int, height: int, bomb_rate: float, fruit_imgs, bomb_img):
    import random, math
    x = random.randint(150, width - 150)
    y = height + 10
    is_bomb = (random.random() < bomb_rate)
    angle_deg = random.uniform(-110, -70)
    speed = random.uniform(18, 25)
    rad = math.radians(angle_deg)
    vel_x = speed * math.cos(rad)
    vel_y = speed * math.sin(rad)
    if is_bomb:
        b = Bomb(x, y, bomb_img)
        b.vel_x, b.vel_y = vel_x, vel_y
        return b
    else:
        img = random.choice(fruit_imgs)
        f = Fruit(x, y, img)
        f.vel_x, f.vel_y = vel_x, vel_y
        return f


def spawn_fruit_batch(width: int, height: int, bomb_rate: float, fruit_imgs, bomb_img, max_spawn: int = 5):
    """Tạo 1 đợt gồm 1–max_spawn quả hoặc bom."""
    fruits = []
    count = random.randint(1, max_spawn)
    for _ in range(count):
        obj = spawn_fruit(width, height, bomb_rate, fruit_imgs, bomb_img)
        fruits.append(obj)
    return fruits
