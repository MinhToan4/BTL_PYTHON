from dataclasses import dataclass

@dataclass
class MenuConfig:
    difficulty: str = "Normal"
    fruit_interval: float = 1.4
    bomb_rate: float = 0.15
    gravity: float = 0.35
    max_lives: int = 3
    hand_enabled: bool = True
    hand_preview: bool = False
    camera_index: int = 0
    music_volume: float = 0.20
    sfx_volume: float = 1.00

def apply_difficulty(cfg: MenuConfig, name: str) -> None:
    name = name.title()
    if name == "Easy":
        cfg.difficulty, cfg.fruit_interval, cfg.bomb_rate, cfg.gravity, cfg.max_lives = "Easy", 1.8, 0.10, 0.30, 3
    elif name == "Hard":
        cfg.difficulty, cfg.fruit_interval, cfg.bomb_rate, cfg.gravity, cfg.max_lives = "Hard", 1.0, 0.22, 0.40, 2
    else:
        cfg.difficulty, cfg.fruit_interval, cfg.bomb_rate, cfg.gravity, cfg.max_lives = "Normal", 1.4, 0.15, 0.35, 3
