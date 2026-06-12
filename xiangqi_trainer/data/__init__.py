from .puzzles import (
    Puzzle,
    get_all_puzzles,
    get_puzzle_by_id,
    get_puzzles_by_difficulty,
    get_puzzles_by_kill_type,
    get_puzzles_by_steps,
    DIFFICULTIES,
    KILL_TYPES,
    create_empty_board,
)

from .storage import (
    Statistics,
    BestRecord,
    load_stats,
    save_stats,
    update_streak,
    record_puzzle_result,
    add_custom_puzzle,
    get_custom_puzzles,
    delete_custom_puzzle,
)

__all__ = [
    'Puzzle',
    'get_all_puzzles',
    'get_puzzle_by_id',
    'get_puzzles_by_difficulty',
    'get_puzzles_by_kill_type',
    'get_puzzles_by_steps',
    'DIFFICULTIES',
    'KILL_TYPES',
    'create_empty_board',
    'Statistics',
    'BestRecord',
    'load_stats',
    'save_stats',
    'update_streak',
    'record_puzzle_result',
    'add_custom_puzzle',
    'get_custom_puzzles',
    'delete_custom_puzzle',
]
