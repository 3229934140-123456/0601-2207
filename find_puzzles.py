"""自动搜索一步杀残局"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, PieceType, King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
from xiangqi_trainer.core.utils import parse_move_str


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


def is_valid_puzzle(board: Board, color: PieceColor):
    """检查是否是有效的一步杀残局"""
    # 检查当前是否在将军（不应该）
    if is_check(board, color):
        return False, []

    # 检查是否已经是杀局（不应该）
    if is_checkmate(board, color):
        return False, []

    # 找出所有红方的走法
    moves = generate_moves(board, color)

    # 找出所有杀着
    mate_moves = []
    for m in moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        opponent = PieceColor.RED if color == PieceColor.BLACK else PieceColor.BLACK
        if is_checkmate(new_board, opponent):
            mate_moves.append(m)

    return len(mate_moves) > 0, mate_moves


def find_chongpao_mate():
    """寻找重炮杀一步杀残局"""
    print("寻找重炮杀一步杀残局...")
    print()

    # 基础布局：黑将+双士在九宫
    # 红方：帅 + 双炮

    # 尝试不同的炮的位置
    for cannon1_x in range(9):
        for cannon1_y in range(5, 8):  # 炮在黑方半场附近
            for cannon2_x in range(9):
                for cannon2_y in range(3, cannon1_y):  # 另一个炮在后面
                    if cannon1_x == cannon2_x and cannon1_y == cannon2_y:
                        continue

                    board = Board()
                    # 清空
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)

                    # 黑方
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))

                    # 红方
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(cannon1_x, cannon1_y, Cannon(PieceColor.RED))
                    board.set_piece(cannon2_x, cannon2_y, Cannon(PieceColor.RED))

                    # 检查是否是有效残局
                    valid, mate_moves = is_valid_puzzle(board, PieceColor.RED)

                    if valid and len(mate_moves) >= 1:
                        # 只保留重炮杀（两个炮在同一条线上）
                        is_chongpao = False
                        for m in mate_moves:
                            # 走子后两个炮在同一条竖线
                            if m.from_x != m.to_x:  # 平移
                                # 平移后，检查两个炮是否在同一条竖线
                                other_cannon_x = cannon2_x if (m.from_x == cannon1_x and m.from_y == cannon1_y) else cannon1_x
                                other_cannon_y = cannon2_y if (m.from_x == cannon1_x and m.from_y == cannon1_y) else cannon1_y
                                if m.to_x == other_cannon_x and m.to_y != other_cannon_y:
                                    is_chongpao = True
                                    break

                        if is_chongpao:
                            print(f"找到重炮杀残局！")
                            print(f"炮1位置: ({cannon1_x}, {cannon1_y})")
                            print(f"炮2位置: ({cannon2_x}, {cannon2_y})")
                            print(f"杀着数量: {len(mate_moves)}")
                            print_board(board)

                            # 显示杀着
                            for i, m in enumerate(mate_moves):
                                piece = board.get_piece(m.from_x, m.from_y)
                                print(f"  杀着 {i+1}: {piece.chinese_name} ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

                                # 尝试生成记谱
                                col = 9 - m.from_x
                                if m.from_y == m.to_y:
                                    direction = "平"
                                    target = 9 - m.to_x
                                elif m.to_y > m.from_y:
                                    direction = "进"
                                    target = abs(m.to_y - m.from_y)
                                else:
                                    direction = "退"
                                    target = abs(m.to_y - m.from_y)

                                move_str = f"C{col}{direction}{target}"
                                print(f"    记谱: {move_str}")

                                # 验证解析
                                parsed = parse_move_str(board, move_str, PieceColor.RED)
                                if parsed:
                                    print(f"    解析验证: ✓")
                                else:
                                    print(f"    解析验证: ✗")

                            print()
                            return board, mate_moves

    print("未找到重炮杀残局")
    return None, None


def find_mabing_mate():
    """寻找马兵配合的简单杀法"""
    print("寻找马兵杀一步杀残局...")
    print()

    # 黑方：将在九宫角落 + 一个士
    # 红方：帅 + 马 + 兵

    # 将的位置：(3,9) 左上角
    king_x, king_y = 3, 9

    for advisor_x in [3, 4, 5]:
        for advisor_y in [7, 8, 9]:
            if not (3 <= advisor_x <= 5 and 7 <= advisor_y <= 9):
                continue
            if advisor_x == king_x and advisor_y == king_y:
                continue

            # 马的位置
            for horse_x in range(9):
                for horse_y in range(9):
                    # 兵的位置（需要当炮架？不，是马兵配合）
                    for pawn_x in range(9):
                        for pawn_y in range(9):
                            if horse_x == pawn_x and horse_y == pawn_y:
                                continue

                            board = Board()
                            for x in range(9):
                                for y in range(10):
                                    board.set_piece(x, y, None)

                            # 黑方
                            board.set_piece(king_x, king_y, King(PieceColor.BLACK))
                            board.set_piece(advisor_x, advisor_y, Advisor(PieceColor.BLACK))

                            # 红方
                            board.set_piece(4, 0, King(PieceColor.RED))
                            board.set_piece(horse_x, horse_y, Horse(PieceColor.RED))
                            board.set_piece(pawn_x, pawn_y, Pawn(PieceColor.RED))

                            valid, mate_moves = is_valid_puzzle(board, PieceColor.RED)
                            if valid and len(mate_moves) >= 1:
                                print(f"找到马兵杀残局！")
                                print(f"将: ({king_x},{king_y})")
                                print(f"士: ({advisor_x},{advisor_y})")
                                print(f"马: ({horse_x},{horse_y})")
                                print(f"兵: ({pawn_x},{pawn_y})")
                                print_board(board)

                                for i, m in enumerate(mate_moves):
                                    piece = board.get_piece(m.from_x, m.from_y)
                                    print(f"  杀着 {i+1}: {piece.chinese_name} ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

                                print()
                                return board, mate_moves

    print("未找到马兵杀残局")
    return None, None


def main():
    print("=" * 60)
    print("一步杀残局搜索器")
    print("=" * 60)
    print()

    # 找重炮杀
    board, mate_moves = find_chongpao_mate()

    if not board:
        print("\n尝试搜索其他类型...")
        # 找马兵杀
        find_mabing_mate()


if __name__ == '__main__':
    main()
