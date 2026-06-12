"""验证找到的残局"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, King, Advisor, Cannon
from xiangqi_trainer.core.utils import parse_move_str


def print_board(board: Board):
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


# 创建找到的残局
board = Board()
for x in range(9):
    for y in range(10):
        board.set_piece(x, y, None)

# 黑方
board.set_piece(4, 9, King(PieceColor.BLACK))
board.set_piece(3, 9, Advisor(PieceColor.BLACK))
board.set_piece(5, 9, Advisor(PieceColor.BLACK))

# 红方
board.set_piece(4, 0, King(PieceColor.RED))
board.set_piece(0, 5, Cannon(PieceColor.RED))  # 左炮
board.set_piece(4, 3, Cannon(PieceColor.RED))  # 中路炮

print("初始局面:")
print_board(board)

# 检查是否将军
print(f"红方是否被将军: {is_check(board, PieceColor.RED)}")
print(f"黑方是否被将军: {is_check(board, PieceColor.BLACK)}")

# 红方合法走法
red_moves = generate_moves(board, PieceColor.RED)
print(f"\n红方合法走法: {len(red_moves)}")

# 找出将军的走法
check_moves = []
for m in red_moves:
    new_board = board.clone()
    new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
    if is_check(new_board, PieceColor.BLACK):
        check_moves.append(m)

print(f"将军的走法: {len(check_moves)}")
for m in check_moves:
    piece = board.get_piece(m.from_x, m.from_y)
    print(f"  {piece.chinese_name} ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

    # 显示黑方应法
    new_board = board.clone()
    new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
    black_moves = generate_moves(new_board, PieceColor.BLACK)
    print(f"    黑方应法: {len(black_moves)} 个")
    
    for bm in black_moves:
        bp = new_board.get_piece(bm.from_x, bm.from_y)
        # 检查走后是否还在将军
        after_board = new_board.clone()
        after_board.move_piece(bm.from_x, bm.from_y, bm.to_x, bm.to_y)
        still_check = is_check(after_board, PieceColor.BLACK)
        status = "✗" if still_check else "✓"
        print(f"      {status} {bp.chinese_name} ({bm.from_x},{bm.from_y}) -> ({bm.to_x},{bm.to_y})")

    checkmate = is_checkmate(new_board, PieceColor.BLACK)
    print(f"    是否将死: {checkmate}")

# 测试走法解析
print("\n\n测试走法解析:")
test_moves = [
    'C9=5',  # 炮九平五
]

for move_str in test_moves:
    move = parse_move_str(board, move_str, PieceColor.RED)
    if move:
        print(f"  ✓ {move_str}: ({move.from_x},{move.from_y}) -> ({move.to_x},{move.to_y})")
    else:
        print(f"  ✗ {move_str}: 解析失败")
