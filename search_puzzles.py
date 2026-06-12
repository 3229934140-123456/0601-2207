"""批量搜索一步杀残局（精简版）"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, PieceType, King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
from xiangqi_trainer.core.utils import parse_move_str


def is_valid_mate_in_one(board: Board, color: PieceColor = PieceColor.RED):
    """检查是否是一步杀残局"""
    if is_check(board, color):
        return False, []
    if is_checkmate(board, color):
        return False, []

    moves = generate_moves(board, color)
    mate_moves = []
    opponent = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED

    for m in moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_checkmate(new_board, opponent):
            mate_moves.append(m)

    return len(mate_moves) > 0, mate_moves


def get_move_notation(board: Board, move, color: PieceColor):
    """获取走法的记谱表示"""
    piece = board.get_piece(move.from_x, move.from_y)
    col = 9 - move.from_x

    piece_char = ''
    if piece.type == PieceType.KING:
        piece_char = 'K'
    elif piece.type == PieceType.ADVISOR:
        piece_char = 'A'
    elif piece.type == PieceType.ELEPHANT:
        piece_char = 'B'
    elif piece.type == PieceType.HORSE:
        piece_char = 'N'
    elif piece.type == PieceType.CHARIOT:
        piece_char = 'R'
    elif piece.type == PieceType.CANNON:
        piece_char = 'C'
    elif piece.type == PieceType.PAWN:
        piece_char = 'P'

    if move.from_y == move.to_y:
        direction = '='
        target = 9 - move.to_x
    elif move.to_y > move.from_y:
        direction = '+'
        diagonal = {PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT}
        if piece.type in diagonal:
            target = 9 - move.to_x
        else:
            target = abs(move.to_y - move.from_y)
    else:
        direction = '-'
        diagonal = {PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT}
        if piece.type in diagonal:
            target = 9 - move.to_x
        else:
            target = abs(move.to_y - move.from_y)

    notation = f"{piece_char}{col}{direction}{target}"
    return notation


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


def search_chongpao():
    """搜索重炮杀残局（黑方双士在底线）"""
    results = []

    for c1x in range(9):
        for c1y in range(3, 7):
            for c2x in range(9):
                for c2y in range(1, c1y - 1):
                    if c1x == c2x and c1y == c2y:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)

                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(c1x, c1y, Cannon(PieceColor.RED))
                    board.set_piece(c2x, c2y, Cannon(PieceColor.RED))

                    valid, mates = is_valid_mate_in_one(board)
                    if valid:
                        notation = get_move_notation(board, mates[0], PieceColor.RED)
                        # 验证解析
                        parsed = parse_move_str(board, notation, PieceColor.RED)
                        if parsed:
                            results.append({
                                'c1x': c1x, 'c1y': c1y,
                                'c2x': c2x, 'c2y': c2y,
                                'mates': mates,
                                'notation': notation
                            })

    return results


def search_shuangche():
    """搜索双车错杀残局"""
    results = []

    for r1x in range(9):
        for r1y in range(4, 9):
            for r2x in range(9):
                for r2y in range(4, 9):
                    if r1x == r2x and r1y == r2y:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)

                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(r1x, r1y, Chariot(PieceColor.RED))
                    board.set_piece(r2x, r2y, Chariot(PieceColor.RED))

                    valid, mates = is_valid_mate_in_one(board)
                    if valid:
                        notation = get_move_notation(board, mates[0], PieceColor.RED)
                        parsed = parse_move_str(board, notation, PieceColor.RED)
                        if parsed:
                            results.append({
                                'r1x': r1x, 'r1y': r1y,
                                'r2x': r2x, 'r2y': r2y,
                                'mates': mates,
                                'notation': notation
                            })
                        if len(results) >= 5:
                            return results

    return results


def main():
    print("=" * 60)
    print("搜索一步杀残局")
    print("=" * 60)
    print()

    # 重炮杀
    print("搜索重炮杀...")
    chongpao = search_chongpao()
    print(f"找到 {len(chongpao)} 个重炮杀残局（记谱解析正确）")

    if chongpao:
        # 显示第一个
        r = chongpao[0]
        board = Board()
        for x in range(9):
            for y in range(10):
                board.set_piece(x, y, None)
        board.set_piece(4, 9, King(PieceColor.BLACK))
        board.set_piece(3, 9, Advisor(PieceColor.BLACK))
        board.set_piece(5, 9, Advisor(PieceColor.BLACK))
        board.set_piece(4, 0, King(PieceColor.RED))
        board.set_piece(r['c1x'], r['c1y'], Cannon(PieceColor.RED))
        board.set_piece(r['c2x'], r['c2y'], Cannon(PieceColor.RED))

        print("\n第一个重炮杀残局:")
        print_board(board)
        print(f"解法: {r['notation']}")
        m = r['mates'][0]
        print(f"走法: ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

    print()

    # 双车错
    print("搜索双车错...")
    shuangche = search_shuangche()
    print(f"找到 {len(shuangche)} 个双车错残局（记谱解析正确）")

    if shuangche:
        r = shuangche[0]
        board = Board()
        for x in range(9):
            for y in range(10):
                board.set_piece(x, y, None)
        board.set_piece(4, 9, King(PieceColor.BLACK))
        board.set_piece(3, 9, Advisor(PieceColor.BLACK))
        board.set_piece(5, 9, Advisor(PieceColor.BLACK))
        board.set_piece(4, 0, King(PieceColor.RED))
        board.set_piece(r['r1x'], r['r1y'], Chariot(PieceColor.RED))
        board.set_piece(r['r2x'], r['r2y'], Chariot(PieceColor.RED))

        print("\n第一个双车错残局:")
        print_board(board)
        print(f"解法: {r['notation']}")
        m = r['mates'][0]
        print(f"走法: ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

    print()
    print("搜索完成！")


if __name__ == '__main__':
    main()
