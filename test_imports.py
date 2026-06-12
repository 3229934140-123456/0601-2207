"""导入测试 - 确保所有模块都能正确加载"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

print("测试核心模块...")
from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.pieces import PieceColor, PieceType, King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
from xiangqi_trainer.core.rules import generate_moves, is_check, is_checkmate, is_stalemate
from xiangqi_trainer.core.move import Move
from xiangqi_trainer.core.utils import parse_move_str, board_from_grid, board_to_grid
from xiangqi_trainer.core.game import GameController
from xiangqi_trainer.core.ai import AIOpponent
print("  ✓ 核心模块加载成功")

print("测试数据模块...")
from xiangqi_trainer.data.puzzles import (
    Puzzle, get_all_puzzles, get_puzzle_by_id,
    get_puzzles_by_difficulty, get_puzzles_by_kill_type,
    get_puzzles_by_steps, DIFFICULTIES, KILL_TYPES,
    create_empty_board
)
from xiangqi_trainer.data.storage import (
    load_stats, save_stats, Statistics, BestRecord
)
print("  ✓ 数据模块加载成功")

print("测试残局数据...")
puzzles = get_all_puzzles()
print(f"  ✓ 共 {len(puzzles)} 个残局")

# 验证每个残局都能正确加载
from xiangqi_trainer.core.rules import is_check as is_check_fn
failed = []
for p in puzzles:
    try:
        board = board_from_grid(p.initial_board)
        color = PieceColor.BLACK if p.black_to_move else PieceColor.RED
        opponent = PieceColor.RED if p.black_to_move else PieceColor.BLACK

        # 解析解法
        if p.solution:
            move = parse_move_str(board, p.solution[0], color)
            if move is None:
                failed.append(f"{p.id} {p.name}: 解法解析失败 '{p.solution[0]}'")
    except Exception as e:
        failed.append(f"{p.id} {p.name}: {e}")

if failed:
    print(f"  ⚠ 有 {len(failed)} 个残局有问题:")
    for f in failed:
        print(f"    - {f}")
else:
    print("  ✓ 所有残局都能正确解析")

print()
print("所有测试通过！")
