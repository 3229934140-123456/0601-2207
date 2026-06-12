from typing import Optional, Tuple
from .board import Board
from .pieces import (
    Piece, PieceColor, PieceType,
    King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
)
from .move import Move
from .rules import generate_moves


PIECE_CHAR_MAP = {
    'K': (PieceColor.RED, PieceType.KING),
    'A': (PieceColor.RED, PieceType.ADVISOR),
    'B': (PieceColor.RED, PieceType.ELEPHANT),
    'N': (PieceColor.RED, PieceType.HORSE),
    'R': (PieceColor.RED, PieceType.CHARIOT),
    'C': (PieceColor.RED, PieceType.CANNON),
    'P': (PieceColor.RED, PieceType.PAWN),
    'k': (PieceColor.BLACK, PieceType.KING),
    'a': (PieceColor.BLACK, PieceType.ADVISOR),
    'b': (PieceColor.BLACK, PieceType.ELEPHANT),
    'n': (PieceColor.BLACK, PieceType.HORSE),
    'r': (PieceColor.BLACK, PieceType.CHARIOT),
    'c': (PieceColor.BLACK, PieceType.CANNON),
    'p': (PieceColor.BLACK, PieceType.PAWN),
}


CHAR_PIECE_MAP = {
    (PieceColor.RED, PieceType.KING): 'K',
    (PieceColor.RED, PieceType.ADVISOR): 'A',
    (PieceColor.RED, PieceType.ELEPHANT): 'B',
    (PieceColor.RED, PieceType.HORSE): 'N',
    (PieceColor.RED, PieceType.CHARIOT): 'R',
    (PieceColor.RED, PieceType.CANNON): 'C',
    (PieceColor.RED, PieceType.PAWN): 'P',
    (PieceColor.BLACK, PieceType.KING): 'k',
    (PieceColor.BLACK, PieceType.ADVISOR): 'a',
    (PieceColor.BLACK, PieceType.ELEPHANT): 'b',
    (PieceColor.BLACK, PieceType.HORSE): 'n',
    (PieceColor.BLACK, PieceType.CHARIOT): 'r',
    (PieceColor.BLACK, PieceType.CANNON): 'c',
    (PieceColor.BLACK, PieceType.PAWN): 'p',
}


def char_to_piece(char: str) -> Optional[Piece]:
    if not char or char not in PIECE_CHAR_MAP:
        return None
    color, ptype = PIECE_CHAR_MAP[char]
    if ptype == PieceType.KING:
        return King(color)
    elif ptype == PieceType.ADVISOR:
        return Advisor(color)
    elif ptype == PieceType.ELEPHANT:
        return Elephant(color)
    elif ptype == PieceType.HORSE:
        return Horse(color)
    elif ptype == PieceType.CHARIOT:
        return Chariot(color)
    elif ptype == PieceType.CANNON:
        return Cannon(color)
    elif ptype == PieceType.PAWN:
        return Pawn(color)
    return None


def piece_to_char(piece: Piece) -> str:
    return CHAR_PIECE_MAP.get((piece.color, piece.type), '')


def board_from_grid(grid) -> Board:
    board = Board()
    for y in range(Board.HEIGHT):
        for x in range(Board.WIDTH):
            char = grid[y][x] if y < len(grid) and x < len(grid[y]) else ''
            piece = char_to_piece(char)
            board.set_piece(x, Board.HEIGHT - 1 - y, piece)
    return board


def board_to_grid(board: Board):
    grid = [['' for _ in range(Board.WIDTH)] for _ in range(Board.HEIGHT)]
    for y in range(Board.HEIGHT):
        for x in range(Board.WIDTH):
            piece = board.get_piece(x, Board.HEIGHT - 1 - y)
            if piece:
                grid[y][x] = piece_to_char(piece)
    return grid


def parse_move_str(board: Board, move_str: str, color: PieceColor) -> Optional[Move]:
    """
    解析简谱走法字符串，如 'N7+9'、'C5=7'、'P4+1'
    红方用大写字母，黑方用小写字母
    """
    if len(move_str) < 3:
        return None

    piece_char = move_str[0]
    target_info = move_str[1:]

    piece_type = None
    if piece_char.upper() == 'K':
        piece_type = PieceType.KING
    elif piece_char.upper() == 'A':
        piece_type = PieceType.ADVISOR
    elif piece_char.upper() == 'B':
        piece_type = PieceType.ELEPHANT
    elif piece_char.upper() == 'N':
        piece_type = PieceType.HORSE
    elif piece_char.upper() == 'R':
        piece_type = PieceType.CHARIOT
    elif piece_char.upper() == 'C':
        piece_type = PieceType.CANNON
    elif piece_char.upper() == 'P':
        piece_type = PieceType.PAWN

    if piece_type is None:
        return None

    move_type = None
    if '+' in target_info:
        move_type = 'forward'
        parts = target_info.split('+')
    elif '-' in target_info:
        move_type = 'backward'
        parts = target_info.split('-')
    elif '=' in target_info:
        move_type = 'sideways'
        parts = target_info.split('=')
    else:
        return None

    if len(parts) != 2:
        return None

    try:
        from_col_num = int(parts[0])
        from_col = 9 - from_col_num
        target = parts[1]
    except ValueError:
        return None

    all_moves = generate_moves(board, color)
    candidates = []
    for m in all_moves:
        if m.piece.type != piece_type:
            continue
        if m.from_x != from_col:
            continue

        if move_type == 'sideways':
            try:
                to_col_num = int(target)
                to_col = 9 - to_col_num
                if m.to_x == to_col and m.from_y == m.to_y:
                    candidates.append(m)
            except ValueError:
                pass
        elif move_type in ('forward', 'backward'):
            if m.from_y == m.to_y:
                continue
            is_forward = (m.to_y > m.from_y) if color == PieceColor.RED else (m.to_y < m.from_y)
            if (move_type == 'forward' and is_forward) or (move_type == 'backward' and not is_forward):
                diagonal_pieces = {PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT}
                if piece_type in diagonal_pieces:
                    try:
                        to_col_num = int(target)
                        to_col = 9 - to_col_num
                        if m.to_x == to_col:
                            candidates.append(m)
                    except ValueError:
                        pass
                else:
                    distance = abs(m.to_y - m.from_y)
                    try:
                        target_dist = int(target)
                        if distance == target_dist:
                            candidates.append(m)
                    except ValueError:
                        pass

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        return candidates[0]

    return None


def find_solution_move(board: Board, solution_steps, color: PieceColor) -> Optional[Move]:
    """从解法步骤中找到当前局面的对应走法"""
    for step in solution_steps:
        move = parse_move_str(board, step, color)
        if move:
            return move
    return None
