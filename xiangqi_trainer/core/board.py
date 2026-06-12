from typing import Optional, List
from .pieces import (
    Piece, PieceColor, PieceType,
    King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
)


class Board:
    WIDTH = 9
    HEIGHT = 10

    def __init__(self):
        self._grid: List[List[Optional[Piece]]] = [
            [None for _ in range(self.WIDTH)]
            for _ in range(self.HEIGHT)
        ]
        self._init_standard_layout()

    def _init_standard_layout(self):
        for x in range(self.WIDTH):
            self._grid[0][x] = self._create_piece(PieceColor.RED, x, 0)
            self._grid[2][x] = self._create_piece(PieceColor.RED, x, 2)
            self._grid[4][x] = self._create_piece(PieceColor.RED, x, 4)

            self._grid[9][x] = self._create_piece(PieceColor.BLACK, x, 9)
            self._grid[7][x] = self._create_piece(PieceColor.BLACK, x, 7)
            self._grid[5][x] = self._create_piece(PieceColor.BLACK, x, 5)

    def _create_piece(self, color: PieceColor, x: int, y: int) -> Optional[Piece]:
        if color == PieceColor.RED:
            if y == 0:
                if x in (0, 8):
                    return Chariot(color)
                elif x in (1, 7):
                    return Horse(color)
                elif x in (2, 6):
                    return Elephant(color)
                elif x in (3, 5):
                    return Advisor(color)
                elif x == 4:
                    return King(color)
            elif y == 2:
                if x in (1, 7):
                    return Cannon(color)
            elif y == 4:
                if x in (0, 2, 4, 6, 8):
                    return Pawn(color)
        else:
            if y == 9:
                if x in (0, 8):
                    return Chariot(color)
                elif x in (1, 7):
                    return Horse(color)
                elif x in (2, 6):
                    return Elephant(color)
                elif x in (3, 5):
                    return Advisor(color)
                elif x == 4:
                    return King(color)
            elif y == 7:
                if x in (1, 7):
                    return Cannon(color)
            elif y == 5:
                if x in (0, 2, 4, 6, 8):
                    return Pawn(color)
        return None

    def get_piece(self, x: int, y: int) -> Optional[Piece]:
        if not self.is_in_board(x, y):
            return None
        return self._grid[y][x]

    def set_piece(self, x: int, y: int, piece: Optional[Piece]):
        if not self.is_in_board(x, y):
            return
        self._grid[y][x] = piece

    def move_piece(self, from_x: int, from_y: int, to_x: int, to_y: int) -> Optional[Piece]:
        piece = self.get_piece(from_x, from_y)
        if piece is None:
            return None
        captured = self.get_piece(to_x, to_y)
        self._grid[to_y][to_x] = piece
        self._grid[from_y][from_x] = None
        return captured

    def is_in_board(self, x: int, y: int) -> bool:
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def is_in_palace(self, x: int, y: int, color: PieceColor) -> bool:
        if not (3 <= x <= 5):
            return False
        if color == PieceColor.RED:
            return 0 <= y <= 2
        else:
            return 7 <= y <= 9

    def is_river_crossed(self, x: int, y: int, color: PieceColor) -> bool:
        if color == PieceColor.RED:
            return y >= 5
        else:
            return y <= 4

    def clone(self) -> 'Board':
        new_board = Board()
        new_board._grid = [
            [piece for piece in row]
            for row in self._grid
        ]
        return new_board

    def __str__(self) -> str:
        lines = []
        for y in range(self.HEIGHT - 1, -1, -1):
            row = []
            for x in range(self.WIDTH):
                piece = self._grid[y][x]
                if piece:
                    row.append(piece.chinese_name)
                else:
                    row.append('．')
            lines.append(''.join(row))
        return '\n'.join(lines)
