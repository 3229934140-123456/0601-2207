"""残局验证脚本 - 验证残局数据和走法解析是否正确"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.utils import board_from_grid, parse_move_str
from xiangqi_trainer.core.move import Move
from xiangqi_trainer.core.pieces import PieceColor, PieceType
from xiangqi_trainer.data.puzzles import get_all_puzzles


def print_board(board: Board):
    """打印棋盘"""
    print("  9 8 7 6 5 4 3 2 1")
    print("  ─────────────────")
    for y in range(Board.HEIGHT - 1, -1, -1):
        row = f"{y+1:2d}"
        for x in range(Board.WIDTH):
            piece = board.get_piece(x, y)
            if piece:
                row += piece.chinese_name
            else:
                row += "·"
        print(row)
    print()


def test_puzzle(puzzle):
    """测试单个残局"""
    print(f"{'='*50}")
    print(f"残局: {puzzle.name} ({puzzle.id})")
    print(f"难度: {puzzle.difficulty} | 杀法: {puzzle.kill_type} | 步数: {puzzle.steps}")
    print(f"描述: {puzzle.description}")
    print()

    board = board_from_grid(puzzle.initial_board)
    current_color = PieceColor.BLACK if puzzle.black_to_move else PieceColor.RED

    print("初始局面:")
    print_board(board)

    # 检查是否在将军（不应该）
    in_check = is_check(board, current_color)
    print(f"轮到 {current_color.value} 走子")
    print(f"当前是否被将军: {in_check}")

    # 生成所有合法走法
    moves = generate_moves(board, current_color)
    print(f"合法走法数量: {len(moves)}")

    # 检查是否已经是杀局（不应该）
    checkmate = is_checkmate(board, current_color)
    print(f"是否已被将死: {checkmate}")

    if checkmate:
        print("错误：残局初始局面就已经是将死了！")
        return False

    print()

    # 验证解法第一步
    if puzzle.solution:
        first_move_str = puzzle.solution[0]
        print(f"解法第一步: {first_move_str}")

        try:
            move = parse_move_str(board, first_move_str, current_color)
            print(f"解析成功: {move.from_x},{move.from_y} -> {move.to_x},{move.to_y}")

            # 检查是否在合法走法中
            is_legal = any(m.from_x == move.from_x and m.from_y == move.from_y and
                          m.to_x == move.to_x and m.to_y == move.to_y
                          for m in moves)
            print(f"是否合法: {is_legal}")

            if not is_legal:
                print("错误：解法第一步不合法！")
                # 显示该棋子所有合法走法
                piece = board.get_piece(move.from_x, move.from_y)
                if piece:
                    piece_moves = [m for m in moves if m.from_x == move.from_x and m.from_y == move.from_y]
                    print(f"  该棋子的合法走法有 {len(piece_moves)} 个:")
                    for m in piece_moves[:5]:
                        print(f"    ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")
                return False

            # 执行走法
            new_board = board.clone()
            new_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)

            # 检查对方是否被将死
            opponent = PieceColor.RED if current_color == PieceColor.BLACK else PieceColor.BLACK
            opp_checkmate = is_checkmate(new_board, opponent)
            opp_check = is_check(new_board, opponent)

            print(f"走子后对方是否被将军: {opp_check}")
            print(f"走子后对方是否被将死: {opp_checkmate}")

            if puzzle.steps == 1 and not opp_checkmate:
                print("警告：一步杀残局但第一步走后不是将死！")

            if opp_checkmate:
                print("✓ 第一步确实是杀着！")

            print()
            print("走子后局面:")
            print_board(new_board)

            return True

        except Exception as e:
            print(f"错误：走法解析失败: {e}")
            return False

    return True


def main():
    puzzles = get_all_puzzles()
    print(f"共 {len(puzzles)} 个残局\n")

    passed = 0
    failed = 0

    for puzzle in puzzles:
        result = test_puzzle(puzzle)
        if result:
            passed += 1
            print("✓ 测试通过")
        else:
            failed += 1
            print("✗ 测试失败")
        print()

    print(f"{'='*50}")
    print(f"总结: 通过 {passed}/{len(puzzles)}, 失败 {failed}/{len(puzzles)}")


if __name__ == '__main__':
    main()
