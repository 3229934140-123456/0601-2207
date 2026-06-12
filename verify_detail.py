"""详细验证重炮杀残局"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, King, Advisor, Cannon


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


# 创建残局
board = Board()
for x in range(9):
    for y in range(10):
        board.set_piece(x, y, None)

board.set_piece(4, 9, King(PieceColor.BLACK))
board.set_piece(3, 9, Advisor(PieceColor.BLACK))
board.set_piece(5, 9, Advisor(PieceColor.BLACK))
board.set_piece(4, 0, King(PieceColor.RED))
board.set_piece(0, 5, Cannon(PieceColor.RED))
board.set_piece(4, 3, Cannon(PieceColor.RED))

print("初始局面:")
print_board(board)

# 红方走子：炮九平五
print("红方走：炮九平五 (0,5) -> (4,5)")
board.move_piece(0, 5, 4, 5)

print("走后局面:")
print_board(board)

# 检查黑方是否被将军
print(f"黑方是否被将军: {is_check(board, PieceColor.BLACK)}")

# 生成合法走法（考虑将军）
legal_moves = generate_moves(board, PieceColor.BLACK)
print(f"黑方合法走法: {len(legal_moves)} 个")
for m in legal_moves:
    piece = board.get_piece(m.from_x, m.from_y)
    print(f"  {piece.chinese_name} ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

print()

# 列出黑方所有棋子
print("黑方所有棋子:")
black_pieces = []
for x in range(9):
    for y in range(10):
        piece = board.get_piece(x, y)
        if piece and piece.color == PieceColor.BLACK:
            black_pieces.append((x, y, piece))
            print(f"  {piece.chinese_name} ({x},{y})")

print()

# 检查士能不能走
print("检查士 (3,9) 的走法:")
# 士可以走到 (4,8) 吗？
advisor = board.get_piece(3, 9)
print(f"  士在 (3,9)")
# 尝试移动
test_board = board.clone()
test_board.set_piece(3, 9, None)
test_board.set_piece(4, 8, advisor)
print(f"  假设士走到 (4,8)")
print(f"  走后是否还被将军: {is_check(test_board, PieceColor.BLACK)}")
print()

# 检查士 (5,9) 的走法
print("检查士 (5,9) 的走法:")
advisor2 = board.get_piece(5, 9)
print(f"  士在 (5,9)")
test_board2 = board.clone()
test_board2.set_piece(5, 9, None)
test_board2.set_piece(4, 8, advisor2)
print(f"  假设士走到 (4,8)")
print(f"  走后是否还被将军: {is_check(test_board2, PieceColor.BLACK)}")

print()

# 测试士走一步垫子后是否还在将军
print("测试：士从 (3,9) 走到 (4,8) 垫子:")
test_board = board.clone()
test_board.move_piece(3, 9, 4, 8)
print_board(test_board)
print(f"走后黑方是否被将军: {is_check(test_board, PieceColor.BLACK)}")

# 详细检查将军情况
print("\n详细检查将军：")
print(f"  后炮位置: (4,3)")
print(f"  前炮位置: (4,5)")
print(f"  士位置: (4,8)")
print(f"  将位置: (4,9)")
print()

# 计算炮和将之间的棋子数
print("沿中路（x=4）从下往上数棋子：")
count = 0
for y in range(0, 10):
    piece = board.get_piece(4, y)
    if piece:
        count += 1
        print(f"  y={y}: {piece.chinese_name} (第{count}个)")

print()
print("士垫子后，沿中路从下往上数棋子：")
count = 0
for y in range(0, 10):
    piece = test_board.get_piece(4, y)
    if piece:
        count += 1
        print(f"  y={y}: {piece.chinese_name} (第{count}个)")
