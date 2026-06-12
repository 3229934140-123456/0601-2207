"""查看所有找到的双车错残局"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, King, Advisor, Chariot
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


def is_valid_mate_in_one(board: Board, color: PieceColor = PieceColor.RED):
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


def get_notation(board, move, color):
    from xiangqi_trainer.core.pieces import PieceType
    piece = board.get_piece(move.from_x, move.from_y)
    col = 9 - move.from_x
    piece_char = 'R'
    if move.from_y == move.to_y:
        direction = '='
        target = 9 - move.to_x
    elif move.to_y > move.from_y:
        direction = '+'
        target = abs(move.to_y - move.from_y)
    else:
        direction = '-'
        target = abs(move.to_y - move.from_y)
    return f"{piece_char}{col}{direction}{target}"


# 搜索所有双车错
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
                    notation = get_notation(board, mates[0], PieceColor.RED)
                    parsed = parse_move_str(board, notation, PieceColor.RED)
                    if parsed:
                        results.append({
                            'r1x': r1x, 'r1y': r1y,
                            'r2x': r2x, 'r2y': r2y,
                            'mates': mates,
                            'notation': notation
                        })

print(f"共找到 {len(results)} 个双车错一步杀残局")
print()

for i, r in enumerate(results):
    print(f"残局 #{i+1}:")
    print(f"  车1: ({r['r1x']},{r['r1y']})")
    print(f"  车2: ({r['r2x']},{r['r2y']})")
    print(f"  解法: {r['notation']}")
    m = r['mates'][0]
    print(f"  走法: ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y})")

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

    print_board(board)
    print()
