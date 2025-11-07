# highscores.py
from __future__ import annotations
from pathlib import Path
import json, time
from typing import List, Dict

DATA_PATH = Path(__file__).resolve().parent / "scores.json"
MAX_ENTRIES = 50  # lưu tối đa 50 cho thoải mái

DIFFICULTY_ORDER = {
    "Easy": 0,
    "Normal": 1,
    "Hard": 2,
}


def _as_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _sanitize_entry(raw: Dict) -> Dict:
    """Normalize stored fields and strip unsupported ones."""
    if not isinstance(raw, dict):
        return {
            "name": "PLAYER",
            "score": 0,
            "difficulty": "Normal",
            "ts": 0,
        }
    name = str(raw.get("name", "PLAYER")).strip() or "PLAYER"
    difficulty = str(raw.get("difficulty", "Normal")).title()
    score = _as_int(raw.get("score", 0), 0)
    ts = _as_int(raw.get("ts", 0), 0)
    return {
        "name": name,
        "score": score,
        "difficulty": difficulty,
        "ts": ts,
    }


def _difficulty_rank(difficulty: str) -> int:
    return DIFFICULTY_ORDER.get(str(difficulty).title(), -1)


def _sort_key(item: Dict) -> tuple[int, int, int]:
    score = _as_int(item.get("score"), 0)
    diff_rank = _difficulty_rank(item.get("difficulty"))
    ts = _as_int(item.get("ts"), 0)
    return (-score, -diff_rank, -ts)

def _load_all() -> List[Dict]:
    if not DATA_PATH.exists():
        return []
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return [_sanitize_entry(it) for it in data]
    except Exception:
        return []

def _save_all(items: List[Dict]) -> None:
    try:
        clean_items = [_sanitize_entry(it) for it in items]
        DATA_PATH.write_text(json.dumps(clean_items, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def _sorted(items: List[Dict]) -> List[Dict]:
    return sorted((_sanitize_entry(it) for it in items), key=_sort_key)

def submit_score(name: str, score: int, difficulty: str = "Normal") -> None:
    """Thêm điểm mới và sắp xếp theo điểm thô với độ khó làm tiêu chí phụ."""
    items = _load_all()
    entry = _sanitize_entry({
        "name": name,
        "score": score,
        "difficulty": difficulty,
        "ts": int(time.time()),
    })
    items.append(entry)
    items = _sorted(items)[:MAX_ENTRIES]
    _save_all(items)

def best_score() -> int | None:
    """Trả về điểm cao nhất (ưu tiên độ khó cao hơn khi bằng điểm)."""
    items = _sorted(_load_all())
    if not items:
        return None
    return _as_int(items[0].get("score"), 0)

def qualifies(score: int, difficulty: str = "Normal", top_n: int = 10) -> bool:
    """Điểm hiện tại có vào TOP hay không?"""
    items = _sorted(_load_all())
    if len(items) < top_n:
        return True
    candidate = _sanitize_entry({
        "name": "PLAYER",
        "score": score,
        "difficulty": difficulty,
        "ts": int(time.time()),
    })
    cutoff = items[min(top_n - 1, len(items) - 1)]
    return _sort_key(candidate) < _sort_key(cutoff)

def get_top(limit: int = 10) -> List[Dict]:
    """Trả về danh sách top (đã sort theo điểm thô và độ khó)."""
    return _sorted(_load_all())[:limit]

def delete_by_rank(rank: int) -> None:
    """Xoá mục theo thứ hạng hiện tại (1-based)."""
    items = _sorted(_load_all())
    if 1 <= rank <= len(items):
        items.pop(rank - 1)
        _save_all(items)

def delete_by_name(name: str) -> None:
    """Xoá tất cả mục có tên trùng (không phân biệt hoa/thường)."""
    name_low = (name or "").strip().lower()
    items = _load_all()
    items = [it for it in items if it.get("name", "").strip().lower() != name_low]
    items = _sorted(items)
    _save_all(items)

def reset_scores() -> None:
    """Xoá toàn bộ bảng xếp hạng."""
    _save_all([])
