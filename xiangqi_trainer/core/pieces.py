from enum import Enum
from typing import Optional


class PieceColor(str, Enum):
    RED = "red"
    BLACK = "black"


class PieceType(str, Enum):
    KING = "king"
    ADVISOR = "advisor"
    ELEPHANT = "elephant"
    HORSE = "horse"
    CHARIOT = "chariot"
    CANNON = "cannon"
    PAWN = "pawn"


class Piece:
    def __init__(self, color: PieceColor, piece_type: PieceType):
        self.color = color
        self.type = piece_type

    @property
    def chinese_name(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.chinese_name

    def __repr__(self) -> str:
        return f"{self.color.value}_{self.type.value}"


class King(Piece):
    def __init__(self, color: PieceColor):
        super().__init__(color, PieceType.KING)

    @property
    def chinese_name(self) -> str:
        return "帅" if self.color == PieceColor.RED else "将"


class Advisor(Piece):
    def __init__(self, color: PieceColor):
        super().__init__(color, PieceType.ADVISOR)

    @property
    def chinese_name(self) -> str:
        return "仕" if self.color == PieceColor.RED else "士"


class Elephant(Piece):
    def __init__(self, color: PieceColor):
        super().__init__(color, PieceType.ELEPHANT)

    @property
    def chinese_name(self) -> str:
        return "相" if self.color == PieceColor.RED else "象"


class Horse(Piece):
    def __init__(self, color: PieceColor):
        super().__init__(color, PieceType.HORSE)

    @property
    def chinese_name(self) -> str:
        return "马"


class Chariot(Piece):
    def __init__(self, color: PieceColor):
        super().__init__(color, PieceType.CHARIOT)

    @property
    def chinese_name(self) -> str:
        return "车"


class Cannon(Piece):
    def __init__(self, color: PieceColor):
        super().__init__(color, PieceType.CANNON)

    @property
    def chinese_name(self) -> str:
        return "炮"


class Pawn(Piece):
    def __init__(self, color: PieceColor):
        super().__init__(color, PieceType.PAWN)

    @property
    def chinese_name(self) -> str:
        return "兵" if self.color == PieceColor.RED else "卒"
