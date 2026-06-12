"""调试搜索：为什么某些杀法类型找不到一步杀残局"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, PieceType, King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
from xiangqi_trainer.core.utils import parse_move_str


def is_valid_puzzle(board: Board, color: PieceColor = PieceColor.RED):
    """检查残局是否合法"""
    if is_check(board, color):
        return False, [], "走棋方被将军"

    opponent = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
    if is_check(board, opponent):
        return False, [], "对方被将军（应该对方走）"

    if is_checkmate(board, opponent):
        return False, [], "已经是杀局"

    moves = generate_moves(board, color)
    mate_moves = []
    for m in moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_checkmate(new_board, opponent):
            mate_moves.append(m)

    if len(mate_moves) == 0:
        return False, [], "没有杀着"

    return True, mate_moves, "OK"


def print_board(board):
    """打印棋盘"""
    print("  9 8 7 6 5 4 3 2 1")
    print("  ─────────────────")
    for y in range(9, -1, -1):
        row_str = f"{y+1:2d}"
        for x in range(9):
            piece = board.get_piece(x, y)
            if piece is None:
                row_str += "·"
            else:
                if piece.color == PieceColor.RED:
                    row_str += piece.chinese_name[0]
                else:
                    row_str += piece.chinese_name[0].lower()
        print(row_str)
    print()


def test_mahoupao():
    """测试马后炮"""
    print("=" * 50)
    print("测试马后炮一步杀")
    print()

    # 尝试不同布局
    # 将在右侧，士堵住一边，马控制另一边，炮从后面将军
    # 等等，炮要将军需要炮架，如果马是炮架，那马和炮、将在同一条线

    # 布局1：将在(3,9)，士在(4,9)，马在(3,7)，炮在(3,5)
    # 将和马、炮同列，马是炮架，炮将军... 初始就将军了，不行

    # 布局2：将在(3,9)，士在(4,9)、(5,8)，马在(4,7)，炮在(2,7)
    # 炮和马同行，将不在同线
    # 红方走炮7平6？不对，要形成马后炮

    # 让我想：马后炮是炮将军，马是炮架，马还控制将的逃跑
    # 如果炮平移到马的后面，和马、将同线
    # 但马挡着的话，炮不能直接走过去... 不对，炮可以越过棋子（吃子时

    # 等等，炮走的时候，不吃子是不能越子的。
    # 所以炮不能直接走到马后面，如果马在中间的话。

    # 那马后炮的一步杀，应该是炮从另一条线走过来？
    # 比如炮在马的斜后方，走一步平移或前进，形成马后炮？

    # 让我用程序遍历试试，只遍历少量位置
    count = 0

    # 将的位置：九宫范围内
    for kx in range(3, 6):
        for ky in range(7, 10):
            # 马的位置
            for nx in range(9):
                for ny in range(4, 9):
                    if nx == kx and ny == ky:
                        continue
                    # 炮的位置
                    for cx in range(9):
                        for cy in range(2, 7):
                            if cx == nx and cy == ny:
                                continue
                            if cx == kx and cy == ky:
                                continue

                            board = Board()
                            for x in range(9):
                                for y in range(10):
                                    board.set_piece(x, y, None)
                            board.set_piece(kx, ky, King(PieceColor.BLACK))
                            board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                            board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                            board.set_piece(4, 0, King(PieceColor.RED))
                            board.set_piece(nx, ny, Horse(PieceColor.RED))
                            board.set_piece(cx, cy, Cannon(PieceColor.RED))

                            valid, mates, reason = is_valid_puzzle(board)
                            if valid:
                                count += 1
                                if count <= 3:
                                    print(f"找到第{count}个马后炮杀:")
                                    print_board(board)
                                    print(f"  杀着数: {len(mates)}")
                                    for m in mates[:2]:
                                        piece = board.get_piece(m.from_x, m.from_y)
                                        print(f"  {piece.chinese_name} ({m.from_x},{m.from_y})->({m.to_x},{m.to_y})")
                                    print()

    print(f"共找到 {count} 个马后炮一步杀残局")
    print()


def test_shuangche():
    """测试双车错"""
    print("=" * 50)
    print("测试双车错一步杀")
    print()

    count = 0
    # 将在九宫
    for kx in range(3, 6):
        for ky in range(7, 10):
            # 两个车
            for r1x in range(9):
                for r1y in range(2, 8):
                    for r2x in range(9):
                        for r2y in range(2, 8):
                            if r1x == r2x and r1y == r2y:
                                continue
                            if r1x == kx and r1y == ky:
                                continue
                            if r2x == kx and r2y == ky:
                                continue

                            board = Board()
                            for x in range(9):
                                for y in range(10):
                                    board.set_piece(x, y, None)
                            board.set_piece(kx, ky, King(PieceColor.BLACK))
                            board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                            board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                            board.set_piece(4, 0, King(PieceColor.RED))
                            board.set_piece(r1x, r1y, Chariot(PieceColor.RED))
                            board.set_piece(r2x, r2y, Chariot(PieceColor.RED))

                            valid, mates, reason = is_valid_puzzle(board)
                            if valid:
                                count += 1
                                if count <= 3:
                                    print(f"找到第{count}个双车错杀:")
                                    print_board(board)
                                    print(f"  杀着数: {len(mates)}")
                                    for m in mates[:2]:
                                        piece = board.get_piece(m.from_x, m.from_y)
                                        print(f"  {piece.chinese_name} ({m.from_x},{m.from_y})->({m.to_x},{m.to_y})")
                                    print()

    print(f"共找到 {count} 个双车错一步杀残局")
    print()


def test_tiemenshuan():
    """测试铁门栓（车+炮）"""
    print("=" * 50)
    print("测试铁门栓一步杀（车+炮）")
    print()

    count = 0
    for kx in range(3, 6):
        for ky in range(7, 10):
            for rx in range(9):
                for ry in range(3, 8):
                    for cx in range(9):
                        for cy in range(2, 7):
                            if rx == cx and ry == cy:
                                continue

                            board = Board()
                            for x in range(9):
                                for y in range(10):
                                    board.set_piece(x, y, None)
                            board.set_piece(kx, ky, King(PieceColor.BLACK))
                            board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                            board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                            board.set_piece(4, 0, King(PieceColor.RED))
                            board.set_piece(rx, ry, Chariot(PieceColor.RED))
                            board.set_piece(cx, cy, Cannon(PieceColor.RED))

                            valid, mates, reason = is_valid_puzzle(board)
                            if valid:
                                count += 1
                                if count <= 3:
                                    print(f"找到第{count}个铁门栓杀:")
                                    print_board(board)
                                    print(f"  杀着数: {len(mates)}")
                                    for m in mates[:2]:
                                        piece = board.get_piece(m.from_x, m.from_y)
                                        print(f"  {piece.chinese_name} ({m.from_x},{m.from_y})->({m.to_x},{m.to_y})")
                                    print()

    print(f"共找到 {count} 个铁门栓一步杀残局")
    print()


if __name__ == '__main__':
    test_mahoupao()
    test_shuangche()
    test_tiemenshuan()
