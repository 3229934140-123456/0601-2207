from typing import Optional
from .pieces import Piece, PieceColor, PieceType


CHINESE_NUMBERS_RED = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
CHINESE_NUMBERS_BLACK = ['1', '2', '3', '4', '5', '6', '7', '8', '9']


class Move:
    def __init__(self, from_x: int, from_y: int, to_x: int, to_y: int,
                 piece: Piece, captured_piece: Optional[Piece] = None):
        self.from_x = from_x
        self.from_y = from_y
        self.to_x = to_x
        self.to_y = to_y
        self.piece = piece
        self.captured_piece = captured_piece

    @property
    def color(self) -> PieceColor:
        return self.piece.color

    def _column_number(self, x: int) -> int:
        return 9 - x

    def _column_str(self, x: int) -> str:
        num = self._column_number(x)
        if self.color == PieceColor.RED:
            return CHINESE_NUMBERS_RED[num - 1]
        else:
            return CHINESE_NUMBERS_BLACK[num - 1]

    def _is_diagonal(self) -> bool:
        dx = abs(self.to_x - self.from_x)
        dy = abs(self.to_y - self.from_y)
        return dx != 0 and dy != 0

    def _get_movement_type(self) -> str:
        if self.from_y == self.to_y:
            return '平'

        if self.color == PieceColor.RED:
            return '进' if self.to_y > self.from_y else '退'
        else:
            return '进' if self.to_y < self.from_y else '退'

    def _get_target_info(self) -> str:
        movement = self._get_movement_type()
        if movement == '平':
            return self._column_str(self.to_x)

        if self._is_diagonal():
            return self._column_str(self.to_x)
        else:
            distance = abs(self.to_y - self.from_y)
            if self.color == PieceColor.RED:
                return CHINESE_NUMBERS_RED[distance - 1]
            else:
                return CHINESE_NUMBERS_BLACK[distance - 1]

    def to_chinese(self) -> str:
        piece_name = self.piece.chinese_name
        from_col = self._column_str(self.from_x)
        movement = self._get_movement_type()
        target_info = self._get_target_info()
        return f'{piece_name}{from_col}{movement}{target_info}'

    def __str__(self) -> str:
        return self.to_chinese()

    def __repr__(self) -> str:
        cap = f' x{self.captured_piece}' if self.captured_piece else ''
        return f'Move({self.from_x},{self.from_y})->({self.to_x},{self.to_y}){cap}'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Move):
            return False
        return (self.from_x == other.from_x
                and self.from_y == other.from_y
                and self.to_x == other.to_x
                and self.to_y == other.to_y)

    def __hash__(self) -> int:
        return hash((self.from_x, self.from_y, self.to_x, self.to_y))
