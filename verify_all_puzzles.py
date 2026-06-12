"""验证所有残局的解法是否正确"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor
from xiangqi_trainer.core.utils import parse_move_str, board_from_grid
from xiangqi_trainer.data.puzzles import get_all_puzzles


def verify_puzzle(puzzle):
    """验证单个残局"""
    board = board_from_grid(puzzle.initial_board)

    # 检查初始局面
    color = PieceColor.BLACK if puzzle.black_to_move else PieceColor.RED
    opponent = PieceColor.RED if puzzle.black_to_move else PieceColor.BLACK

    issues = []

    # 检查走棋方是否被将军（不应该）
    if is_check(board, color):
        issues.append("初始局面走棋方被将军（不合法）")

    # 检查对方是否被将军（也不应该）
    if is_check(board, opponent):
        issues.append("初始局面对方被将军（不合法，应该对方走）")

    # 验证解法
    solution_moves = []
    current_board = board.clone()
    current_color = color

    for i, move_str in enumerate(puzzle.solution):
        move = parse_move_str(current_board, move_str, current_color)
        if move is None:
            issues.append(f"解法第{i+1}步 '{move_str}' 解析失败")
            break

        # 执行走法
        new_board = current_board.clone()
        new_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)

        solution_moves.append(move)
        current_board = new_board
        current_color = opponent if current_color == color else color

    # 检查最后一步后是否杀棋
    if solution_moves and not issues:
        if is_checkmate(current_board, opponent if puzzle.solution and len(puzzle.solution) % 2 == 1 else color):
            # 最后一步是攻方走的，应该将死对方
            pass
        else:
            # 检查是否将死了
            last_mover = opponent if puzzle.solution and len(puzzle.solution) % 2 == 0 else color
            other = color if last_mover == opponent else opponent
            if not is_checkmate(current_board, other):
                issues.append("解法执行后没有形成杀局")

    return len(issues) == 0, issues


def main():
    puzzles = get_all_puzzles()
    print(f"共 {len(puzzles)} 个残局")
    print("=" * 60)

    passed = 0
    failed = 0

    for puzzle in puzzles:
        ok, issues = verify_puzzle(puzzle)
        status = "✓ 通过" if ok else "✗ 失败"
        print(f"{puzzle.id} {puzzle.name}: {status}")
        if issues:
            for issue in issues:
                print(f"    - {issue}")
            failed += 1
        else:
            passed += 1

    print("=" * 60)
    print(f"通过: {passed}, 失败: {failed}, 总计: {len(puzzles)}")


if __name__ == '__main__':
    main()
