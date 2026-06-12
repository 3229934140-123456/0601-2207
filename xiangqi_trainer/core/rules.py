from typing import List, Optional, Tuple
from .pieces import Piece, PieceColor, PieceType, King
from .board import Board
from .move import Move


def generate_moves(board: Board, color: PieceColor) -> List[Move]:
    moves = []
    for y in range(Board.HEIGHT):
        for x in range(Board.WIDTH):
            piece = board.get_piece(x, y)
            if piece and piece.color == color:
                piece_moves = generate_moves_for_piece(board, x, y)
                moves.extend(piece_moves)

    legal_moves = []
    for move in moves:
        if _is_move_safe(board, move):
            legal_moves.append(move)

    return legal_moves


def generate_moves_for_piece(board: Board, x: int, y: int) -> List[Move]:
    piece = board.get_piece(x, y)
    if piece is None:
        return []

    if piece.type == PieceType.KING:
        return _generate_king_moves(board, x, y, piece)
    elif piece.type == PieceType.ADVISOR:
        return _generate_advisor_moves(board, x, y, piece)
    elif piece.type == PieceType.ELEPHANT:
        return _generate_elephant_moves(board, x, y, piece)
    elif piece.type == PieceType.HORSE:
        return _generate_horse_moves(board, x, y, piece)
    elif piece.type == PieceType.CHARIOT:
        return _generate_chariot_moves(board, x, y, piece)
    elif piece.type == PieceType.CANNON:
        return _generate_cannon_moves(board, x, y, piece)
    elif piece.type == PieceType.PAWN:
        return _generate_pawn_moves(board, x, y, piece)
    return []


def _generate_king_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    moves = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if board.is_in_palace(nx, ny, piece.color):
            target = board.get_piece(nx, ny)
            if target is None or target.color != piece.color:
                moves.append(Move(x, y, nx, ny, piece, target))

    return moves


def _generate_advisor_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    moves = []
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if board.is_in_palace(nx, ny, piece.color):
            target = board.get_piece(nx, ny)
            if target is None or target.color != piece.color:
                moves.append(Move(x, y, nx, ny, piece, target))

    return moves


def _generate_elephant_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    moves = []
    directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
    eye_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    for (dx, dy), (ex, ey) in zip(directions, eye_directions):
        nx, ny = x + dx, y + dy
        if not board.is_in_board(nx, ny):
            continue
        if board.is_river_crossed(nx, ny, piece.color):
            continue
        eye_x, eye_y = x + ex, y + ey
        if board.get_piece(eye_x, eye_y) is not None:
            continue
        target = board.get_piece(nx, ny)
        if target is None or target.color != piece.color:
            moves.append(Move(x, y, nx, ny, piece, target))

    return moves


def _generate_horse_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    moves = []
    knight_moves = [
        (1, 2, 0, 1), (-1, 2, 0, 1),
        (1, -2, 0, -1), (-1, -2, 0, -1),
        (2, 1, 1, 0), (2, -1, 1, 0),
        (-2, 1, -1, 0), (-2, -1, -1, 0),
    ]

    for dx, dy, bx, by in knight_moves:
        nx, ny = x + dx, y + dy
        if not board.is_in_board(nx, ny):
            continue
        block_x, block_y = x + bx, y + by
        if board.get_piece(block_x, block_y) is not None:
            continue
        target = board.get_piece(nx, ny)
        if target is None or target.color != piece.color:
            moves.append(Move(x, y, nx, ny, piece, target))

    return moves


def _generate_chariot_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    moves = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        while board.is_in_board(nx, ny):
            target = board.get_piece(nx, ny)
            if target is None:
                moves.append(Move(x, y, nx, ny, piece, None))
            else:
                if target.color != piece.color:
                    moves.append(Move(x, y, nx, ny, piece, target))
                break
            nx += dx
            ny += dy

    return moves


def _generate_cannon_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    moves = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        jumped = False
        while board.is_in_board(nx, ny):
            target = board.get_piece(nx, ny)
            if not jumped:
                if target is None:
                    moves.append(Move(x, y, nx, ny, piece, None))
                else:
                    jumped = True
            else:
                if target is not None:
                    if target.color != piece.color:
                        moves.append(Move(x, y, nx, ny, piece, target))
                    break
            nx += dx
            ny += dy

    return moves


def _generate_pawn_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    moves = []

    if piece.color == PieceColor.RED:
        forward = (0, 1)
    else:
        forward = (0, -1)

    fx, fy = forward
    nx, ny = x + fx, y + fy
    if board.is_in_board(nx, ny):
        target = board.get_piece(nx, ny)
        if target is None or target.color != piece.color:
            moves.append(Move(x, y, nx, ny, piece, target))

    if board.is_river_crossed(x, y, piece.color):
        for dx in [-1, 1]:
            nx, ny = x + dx, y
            if board.is_in_board(nx, ny):
                target = board.get_piece(nx, ny)
                if target is None or target.color != piece.color:
                    moves.append(Move(x, y, nx, ny, piece, target))

    return moves


def _find_king(board: Board, color: PieceColor) -> Optional[Tuple[int, int]]:
    for y in range(Board.HEIGHT):
        for x in range(Board.WIDTH):
            piece = board.get_piece(x, y)
            if piece and piece.type == PieceType.KING and piece.color == color:
                return (x, y)
    return None


def _is_king_facing(board: Board) -> bool:
    red_king = _find_king(board, PieceColor.RED)
    black_king = _find_king(board, PieceColor.BLACK)

    if red_king is None or black_king is None:
        return False

    rx, ry = red_king
    bx, by = black_king

    if rx != bx:
        return False

    min_y = min(ry, by)
    max_y = max(ry, by)
    for y in range(min_y + 1, max_y):
        if board.get_piece(rx, y) is not None:
            return False

    return True


def is_check(board: Board, color: PieceColor) -> bool:
    if _is_king_facing(board):
        return True

    king_pos = _find_king(board, color)
    if king_pos is None:
        return True

    kx, ky = king_pos
    opponent_color = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED

    for y in range(Board.HEIGHT):
        for x in range(Board.WIDTH):
            piece = board.get_piece(x, y)
            if piece and piece.color == opponent_color:
                moves = _generate_attack_moves(board, x, y, piece)
                for move in moves:
                    if move.to_x == kx and move.to_y == ky:
                        return True

    return False


def _generate_attack_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    if piece.type == PieceType.KING:
        return _generate_king_attack_moves(board, x, y, piece)
    elif piece.type == PieceType.ADVISOR:
        return _generate_advisor_moves(board, x, y, piece)
    elif piece.type == PieceType.ELEPHANT:
        return _generate_elephant_moves(board, x, y, piece)
    elif piece.type == PieceType.HORSE:
        return _generate_horse_moves(board, x, y, piece)
    elif piece.type == PieceType.CHARIOT:
        return _generate_chariot_moves(board, x, y, piece)
    elif piece.type == PieceType.CANNON:
        return _generate_cannon_moves(board, x, y, piece)
    elif piece.type == PieceType.PAWN:
        return _generate_pawn_moves(board, x, y, piece)
    return []


def _generate_king_attack_moves(board: Board, x: int, y: int, piece: Piece) -> List[Move]:
    moves = _generate_king_moves(board, x, y, piece)

    opponent_color = PieceColor.BLACK if piece.color == PieceColor.RED else PieceColor.RED
    opponent_king = _find_king(board, opponent_color)
    if opponent_king:
        ox, oy = opponent_king
        if ox == x:
            min_y = min(y, oy)
            max_y = max(y, oy)
            blocked = False
            for ty in range(min_y + 1, max_y):
                if board.get_piece(x, ty) is not None:
                    blocked = True
                    break
            if not blocked:
                target = board.get_piece(ox, oy)
                moves.append(Move(x, y, ox, oy, piece, target))

    return moves


def _is_move_safe(board: Board, move: Move) -> bool:
    new_board = board.clone()
    new_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)
    return not is_check(new_board, move.color)


def is_move_legal(board: Board, move: Move) -> bool:
    piece = board.get_piece(move.from_x, move.from_y)
    if piece is None or piece != move.piece:
        return False

    possible_moves = generate_moves_for_piece(board, move.from_x, move.from_y)
    for pm in possible_moves:
        if (pm.to_x == move.to_x and pm.to_y == move.to_y):
            return _is_move_safe(board, move)

    return False


def is_checkmate(board: Board, color: PieceColor) -> bool:
    if not is_check(board, color):
        return False

    moves = generate_moves(board, color)
    return len(moves) == 0


def is_stalemate(board: Board, color: PieceColor) -> bool:
    if is_check(board, color):
        return False

    moves = generate_moves(board, color)
    return len(moves) == 0
