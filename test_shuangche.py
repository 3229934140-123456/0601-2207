"""验证双车错残局"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, King, Advisor, Chariot


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


# 双车错残局：车(4,7)和车(7,6)
board = Board()
for x in range(9):
    for y in range(10):
        board.set_piece(x, y, None)

board.set_piece(4, 9, King(PieceColor.BLACK))
board.set_piece(3, 9, Advisor(PieceColor.BLACK))
board.set_piece(5, 9, Advisor(PieceColor.BLACK))
board.set_piece(4, 0, King(PieceColor.RED))
board.set_piece(4, 7, Chariot(PieceColor.RED))
board.set_piece(7, 6, Chariot(PieceColor.RED))

print("初始局面:")
print_board(board)

print(f"红方是否被将军: {is_check(board, PieceColor.RED)}")
print(f"黑方是否被将军: {is_check(board, PieceColor.BLACK)}")

# 红方走：车五进二 (4,7)->(4,9)
print("\n红方走：车五进二 (4,7)->(4,9)")
board.move_piece(4, 7, 4, 9)

print("走后局面:")
print_board(board)

print(f"黑方是否被将军: {is_check(board, PieceColor.BLACK)}")

# 黑方合法走法
black_moves = generate_moves(board, PieceColor.BLACK)
print(f"\n黑方合法走法: {len(black_moves)} 个")
for m in black_moves:
    piece = board.get_piece(m.from_x, m.from_y)
    print(f"  {piece.chinese_name} ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

print(f"\n是否将死: {is_checkmate(board, PieceColor.BLACK)}")

# 手动测试：士(5,9)->(4,8) 垫子
print("\n\n手动测试：士(5,9)->(4,8) 垫子")
test_board = board.clone()
test_board.set_piece(5, 9, None)
test_board.set_piece(4, 8, Advisor(PieceColor.BLACK))
print_board(test_board)
print(f"走后黑方是否被将军: {is_check(test_board, PieceColor.BLACK)}")

# 检查两个车的攻击线
print("\n检查各车的攻击线:")
for x in range(9):
    for y in range(10):
        piece = test_board.get_piece(x, y)
        if piece and piece.type.name == 'CHARIOT' and piece.color == PieceColor.RED:
            print(f"  红车 ({x},{y}):")
            # 检查竖线
            print(f"    竖线: ", end="")
            for ty in range(10):
                p = test_board.get_piece(x, ty)
                if p and ty != y:
                    print(f"({x},{ty})={p.chinese_name}", end=" ")
            print()
            # 检查横线
            print(f"    横线: ", end="")
            for tx in range(9):
                p = test_board.get_piece(tx, y)
                if p and tx != x:
                    print(f"({tx},{y})={p.chinese_name}", end=" ")
            print()
