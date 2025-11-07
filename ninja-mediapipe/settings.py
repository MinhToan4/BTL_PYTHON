# settings.py
from dataclasses import dataclass
from start_menu import MenuConfig  # lấy cấu hình từ menu (độ khó, âm thanh, v.v.)

@dataclass
class GameSettings:
    # Kích thước màn
    width: int = 1280
    height: int = 720
    fps: int = 60

    # Vật lý & gameplay cơ bản
    fruit_spawn_interval: float = 1.4
    bomb_rate: float = 0.15
    gravity: float = 0.35
    max_lives: int = 3
    slice_trail_length: int = 15
    combo_time: float = 1.0

    # Spawn nâng cao
    max_spawn_per_wave: int = 5         # tối đa 5 quả cùng lúc
    combo_bonus_multiplier: float = 0.3 # cộng thêm % theo combo
    base_score_per_fruit: int = 10

    # Boss settings
    boss_enabled: bool = True
    boss_spawn_threshold_easy: int = 400
    boss_spawn_threshold_normal: int = 300
    boss_spawn_threshold_hard: int = 250
    boss_hp_min: int = 6
    boss_hp_max: int = 10
    boss_score_bonus: int = 70
    boss_pause_duration: float = 0.5  # dừng nhẹ khi boss nổ

    # hand tracking
    hand_enabled: bool = True
    camera_index: int = 0
    hand_preview: bool = False

    # audio
    music_volume: float = 0.20
    sfx_volume: float = 1.00


def apply_menu_to_settings(cfg: MenuConfig, s: GameSettings | None = None) -> GameSettings:
    s = GameSettings() if s is None else s
    s.fruit_spawn_interval = cfg.fruit_interval
    s.bomb_rate           = cfg.bomb_rate
    s.gravity             = cfg.gravity
    s.max_lives           = cfg.max_lives
    s.hand_enabled        = cfg.hand_enabled
    s.camera_index        = cfg.camera_index
    s.hand_preview        = cfg.hand_preview
    s.music_volume        = cfg.music_volume
    s.sfx_volume          = cfg.sfx_volume

    # chọn ngưỡng Boss theo độ khó
    if cfg.difficulty == "Easy":
        s.boss_spawn_threshold = s.boss_spawn_threshold_easy
    elif cfg.difficulty == "Hard":
        s.boss_spawn_threshold = s.boss_spawn_threshold_hard
    else:
        s.boss_spawn_threshold = s.boss_spawn_threshold_normal
    return s
