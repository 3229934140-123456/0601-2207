import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime, date

from .puzzles import Puzzle


@dataclass
class BestRecord:
    steps: int = 0
    time: float = 0.0
    hints_used: int = 0


@dataclass
class Statistics:
    total_puzzles: int = 0
    correct_count: int = 0
    streak_days: int = 0
    last_play_date: Optional[str] = None
    error_types: Dict[str, int] = field(default_factory=dict)
    best_records: Dict[str, BestRecord] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = asdict(self)
        data['best_records'] = {
            pid: asdict(rec) for pid, rec in self.best_records.items()
        }
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Statistics':
        stats = cls(
            total_puzzles=data.get('total_puzzles', 0),
            correct_count=data.get('correct_count', 0),
            streak_days=data.get('streak_days', 0),
            last_play_date=data.get('last_play_date'),
            error_types=data.get('error_types', {}),
        )
        best_records_data = data.get('best_records', {})
        for pid, rec_data in best_records_data.items():
            stats.best_records[pid] = BestRecord(
                steps=rec_data.get('steps', 0),
                time=rec_data.get('time', 0.0),
                hints_used=rec_data.get('hints_used', 0),
            )
        return stats


def get_config_dir() -> str:
    home = os.path.expanduser('~')
    config_dir = os.path.join(home, '.xiangqi_trainer')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_dir


def get_stats_path() -> str:
    return os.path.join(get_config_dir(), 'stats.json')


def get_custom_puzzles_path() -> str:
    return os.path.join(get_config_dir(), 'custom_puzzles.json')


def load_stats() -> Statistics:
    stats_path = get_stats_path()
    if not os.path.exists(stats_path):
        return Statistics()
    try:
        with open(stats_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Statistics.from_dict(data)
    except (json.JSONDecodeError, IOError):
        return Statistics()


def save_stats(stats: Statistics) -> None:
    stats_path = get_stats_path()
    try:
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats.to_dict(), f, ensure_ascii=False, indent=2)
    except IOError:
        pass


def update_streak(stats: Statistics) -> None:
    today = date.today().isoformat()
    if stats.last_play_date == today:
        return

    if stats.last_play_date:
        try:
            last_date = date.fromisoformat(stats.last_play_date)
            today_date = date.today()
            delta = (today_date - last_date).days
            if delta == 1:
                stats.streak_days += 1
            elif delta > 1:
                stats.streak_days = 1
        except ValueError:
            stats.streak_days = 1
    else:
        stats.streak_days = 1

    stats.last_play_date = today


def record_puzzle_result(
    stats: Statistics,
    puzzle_id: str,
    correct: bool,
    steps: int,
    time_used: float,
    hints_used: int = 0,
    error_type: Optional[str] = None,
) -> None:
    stats.total_puzzles += 1

    if correct:
        stats.correct_count += 1

        current_best = stats.best_records.get(puzzle_id)
        is_better = False
        if current_best is None:
            is_better = True
        else:
            if steps < current_best.steps:
                is_better = True
            elif steps == current_best.steps and time_used < current_best.time:
                is_better = True

        if is_better:
            stats.best_records[puzzle_id] = BestRecord(
                steps=steps,
                time=time_used,
                hints_used=hints_used,
            )
    else:
        if error_type:
            stats.error_types[error_type] = stats.error_types.get(error_type, 0) + 1

    update_streak(stats)


def puzzle_to_dict(puzzle: Puzzle) -> dict:
    return {
        'id': puzzle.id,
        'name': puzzle.name,
        'description': puzzle.description,
        'difficulty': puzzle.difficulty,
        'kill_type': puzzle.kill_type,
        'steps': puzzle.steps,
        'initial_board': puzzle.initial_board,
        'solution': puzzle.solution,
        'black_to_move': puzzle.black_to_move,
    }


def puzzle_from_dict(data: dict) -> Puzzle:
    return Puzzle(
        id=data['id'],
        name=data['name'],
        description=data.get('description', ''),
        difficulty=data.get('difficulty', '简单'),
        kill_type=data.get('kill_type', '其他'),
        steps=data.get('steps', 1),
        initial_board=data['initial_board'],
        solution=data.get('solution', []),
        black_to_move=data.get('black_to_move', False),
    )


def add_custom_puzzle(puzzle: Puzzle) -> None:
    puzzles = get_custom_puzzles()
    puzzles.append(puzzle)
    _save_custom_puzzles(puzzles)


def get_custom_puzzles() -> List[Puzzle]:
    path = get_custom_puzzles_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [puzzle_from_dict(pd) for pd in data]
    except (json.JSONDecodeError, IOError):
        return []


def _save_custom_puzzles(puzzles: List[Puzzle]) -> None:
    path = get_custom_puzzles_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([puzzle_to_dict(p) for p in puzzles], f, ensure_ascii=False, indent=2)
    except IOError:
        pass


def delete_custom_puzzle(puzzle_id: str) -> bool:
    puzzles = get_custom_puzzles()
    filtered = [p for p in puzzles if p.id != puzzle_id]
    if len(filtered) == len(puzzles):
        return False
    _save_custom_puzzles(filtered)
    return True
