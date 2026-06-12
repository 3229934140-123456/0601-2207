"""残局设计和验证脚本"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, PieceType, King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
from xiangqi_trainer.core.utils import parse_move_str, board_to_grid
from xiangqi_trainer.core.move import Move


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


def design_puzzle_1():
    """设计残局1：重炮杀（一步杀）"""
    print("=" * 60)
    print("设计残局：重炮杀（一步杀）")
    print()

    board = Board()

    # 清空棋盘
    for x in range(Board.WIDTH):
        for y in range(Board.HEIGHT):
            board.set_piece(x, y, None)

    # 黑方
    board.set_piece(4, 9, King(PieceColor.BLACK))  # 将在九宫顶中央
    board.set_piece(3, 9, Advisor(PieceColor.BLACK))  # 左士
    board.set_piece(5, 9, Advisor(PieceColor.BLACK))  # 右士

    # 红方
    board.set_piece(4, 0, King(PieceColor.RED))  # 帅在中路
    board.set_piece(4, 7, Cannon(PieceColor.RED))  # 前炮（中路）
    board.set_piece(1, 7, Cannon(PieceColor.RED))  # 后炮（第8列，需要平到中路）

    print("初始局面:")
    print_board(board)

    # 检查红方走子
    moves = generate_moves(board, PieceColor.RED)
    print(f"红方合法走法: {len(moves)}")

    # 找出所有将军的走法
    check_moves = []
    for m in moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_check(new_board, PieceColor.BLACK):
            check_moves.append(m)

    print(f"将军的走法: {len(check_moves)}")

    # 找出杀着
    mate_moves = []
    for m in check_moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_checkmate(new_board, PieceColor.BLACK):
            mate_moves.append(m)

    print(f"杀着: {len(mate_moves)}")
    for m in mate_moves:
        print(f"  ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

    if mate_moves:
        print("\n✓ 找到一步杀！")
        
        # 尝试用记谱表示
        for m in mate_moves:
            col = 9 - m.from_x
            direction = ""
            if m.from_y == m.to_y:
                direction = "平"
                target = 9 - m.to_x
            elif m.to_y > m.from_y:
                direction = "进"
                target = abs(m.to_y - m.from_y)
            else:
                direction = "退"
                target = abs(m.to_y - m.from_y)

            piece_char = ""
            if m.piece.type == PieceType.CANNON:
                piece_char = "C"
            elif m.piece.type == PieceType.CHARIOT:
                piece_char = "R"
            elif m.piece.type == PieceType.HORSE:
                piece_char = "N"
            elif m.piece.type == PieceType.PAWN:
                piece_char = "P"

            move_str = f"{piece_char}{col}{direction}{target}"
            print(f"  记谱: {move_str}")

            # 验证解析
            parsed = parse_move_str(board, move_str, PieceColor.RED)
            if parsed:
                print(f"  解析验证: ✓")
            else:
                print(f"  解析验证: ✗")

    else:
        print("\n✗ 没有一步杀，需要调整")

    print()
    return board, mate_moves


def design_puzzle_1():
    """设计残局1：重炮杀（一步杀）"""
    print("=" * 60)
    print("设计残局：重炮杀（一步杀）")
    print()

    board = Board()

    # 清空棋盘
    for x in range(Board.WIDTH):
        for y in range(Board.HEIGHT):
            board.set_piece(x, y, None)

    # 黑方
    board.set_piece(4, 9, King(PieceColor.BLACK))  # 将在九宫顶中央
    board.set_piece(3, 9, Advisor(PieceColor.BLACK))  # 左士
    board.set_piece(5, 9, Advisor(PieceColor.BLACK))  # 右士

    # 红方
    board.set_piece(4, 0, King(PieceColor.RED))  # 帅在中路
    board.set_piece(4, 7, Cannon(PieceColor.RED))  # 前炮（中路）
    board.set_piece(1, 7, Cannon(PieceColor.RED))  # 后炮（第8列，需要平到中路）

    print("初始局面:")
    print_board(board)

    # 检查红方走子
    moves = generate_moves(board, PieceColor.RED)
    print(f"红方合法走法: {len(moves)}")

    # 找出所有将军的走法
    check_moves = []
    for m in moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_check(new_board, PieceColor.BLACK):
            check_moves.append(m)

    print(f"将军的走法: {len(check_moves)}")
    for m in check_moves:
        piece = board.get_piece(m.from_x, m.from_y)
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        black_moves = generate_moves(new_board, PieceColor.BLACK)
        print(f"  {piece.chinese_name} ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")
        print(f"    黑方应法: {len(black_moves)} 个")
        for bm in black_moves[:5]:
            bp = new_board.get_piece(bm.from_x, bm.from_y)
            print(f"      {bp.chinese_name} ({bm.from_x},{bm.from_y}) -> ({bm.to_x},{bm.to_y})")

    # 找出杀着
    mate_moves = []
    for m in check_moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_checkmate(new_board, PieceColor.BLACK):
            mate_moves.append(m)

    print(f"\n杀着: {len(mate_moves)}")
    for m in mate_moves:
        print(f"  ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

    if mate_moves:
        print("\n✓ 找到一步杀！")
    else:
        print("\n✗ 没有一步杀，需要调整")

    print()
    return board, mate_moves


def design_puzzle_3():
    """设计残局3：双车错杀（一步杀）"""
    print("=" * 60)
    print("设计残局：双车错杀（一步杀）")
    print()

    board = Board()

    # 清空棋盘
    for x in range(Board.WIDTH):
        for y in range(Board.HEIGHT):
            board.set_piece(x, y, None)

    # 黑方
    board.set_piece(3, 9, King(PieceColor.BLACK))  # 将在九宫左上角
    board.set_piece(4, 8, Advisor(PieceColor.BLACK))  # 中心士

    # 红方
    board.set_piece(4, 0, King(PieceColor.RED))  # 帅在中路
    board.set_piece(4, 6, Chariot(PieceColor.RED))  # 中路车
    board.set_piece(3, 6, Chariot(PieceColor.RED))  # 左肋车

    print("初始局面:")
    print_board(board)

    # 检查红方走子
    moves = generate_moves(board, PieceColor.RED)
    print(f"红方合法走法: {len(moves)}")

    # 找出所有将军的走法
    check_moves = []
    for m in moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_check(new_board, PieceColor.BLACK):
            check_moves.append(m)

    print(f"将军的走法: {len(check_moves)}")
    for m in check_moves:
        piece = board.get_piece(m.from_x, m.from_y)
        print(f"  {piece.chinese_name} ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

    # 找出杀着
    mate_moves = []
    for m in check_moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_checkmate(new_board, PieceColor.BLACK):
            mate_moves.append(m)

    print(f"\n杀着: {len(mate_moves)}")
    for m in mate_moves:
        print(f"  ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

    if mate_moves:
        print("\n✓ 找到一步杀！")
    else:
        print("\n✗ 没有一步杀，需要调整")

    print()
    return board, mate_moves


def main():
    design_puzzle_1()
    # design_puzzle_2()
    # design_puzzle_3()


if __name__ == '__main__':
    main()
