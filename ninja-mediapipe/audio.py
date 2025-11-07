# audio.py
import pygame
from pathlib import Path
from typing import Tuple

SOUNDS_DIR = Path(__file__).resolve().parent / "sounds"

class NullSound:
    def play(self): pass
    def set_volume(self, v: float): pass

def _load_sound(name: str):
    p = SOUNDS_DIR / name
    try:
        return pygame.mixer.Sound(str(p))
    except Exception as e:
        print(f"[audio] WARNING: cannot load {p.name} in {SOUNDS_DIR} -> {e}")
        return NullSound()

def init_audio() -> Tuple[pygame.mixer.Sound, pygame.mixer.Sound]:
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"[audio] WARNING: mixer init failed -> {e}")
    slice_sound = _load_sound("slice.wav")
    bomb_sound  = _load_sound("bomb.wav")

    # Nhạc nền (tùy chọn)
    music_path = SOUNDS_DIR / "bg_music.mp3"
    try:
        if music_path.exists():
            pygame.mixer.music.load(str(music_path))
        else:
            print("[audio] INFO: bg_music.mp3 not found (optional).")
    except Exception as e:
        print(f"[audio] WARNING: cannot load bg_music.mp3 -> {e}")

    return slice_sound, bomb_sound
