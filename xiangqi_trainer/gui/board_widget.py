from typing import Optional, List, Tuple
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics

from ..core.board import Board
from ..core.pieces import Piece, PieceColor


class BoardWidget(QWidget):
    move_made = pyqtSignal(int, int, int, int)
    piece_selected = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._board: Optional[Board] = None
        self._night_mode: bool = False
        self._large_pieces: bool = False

        self._selected_x: int = -1
        self._selected_y: int = -1
        self._highlight_moves: List[Tuple[int, int]] = []
        self._last_move_from: Optional[Tuple[int, int]] = None
        self._last_move_to: Optional[Tuple[int, int]] = None

        self._dragging: bool = False
        self._drag_start_x: int = -1
        self._drag_start_y: int = -1
        self._drag_pos: QPoint = QPoint()

        self._cell_size: int = 50
        self._margin: int = 30

        self.setMinimumSize(400, 450)
        self.setMouseTracking(True)

    def set_board(self, board: Board):
        self._board = board
        self.update()

    def set_night_mode(self, enabled: bool):
        self._night_mode = enabled
        self.update()

    def set_large_pieces(self, enabled: bool):
        self._large_pieces = enabled
        self.updateGeometry()
        self.update()

    def highlight_last_move(self, from_x: int, from_y: int, to_x: int, to_y: int):
        self._last_move_from = (from_x, from_y)
        self._last_move_to = (to_x, to_y)
        self.update()

    def highlight_moves(self, moves: List[Tuple[int, int]]):
        self._highlight_moves = moves
        self.update()

    def clear_selection(self):
        self._selected_x = -1
        self._selected_y = -1
        self._highlight_moves = []
        self.update()

    def _get_colors(self):
        if self._night_mode:
            return {
                'board_bg': QColor('#2B2B2B'),
                'line': QColor('#555555'),
                'river_text': QColor('#666666'),
                'red_text': QColor('#C41E3A'),
                'red_bg': QColor('#F5E6D3'),
                'black_text': QColor('#FFFFFF'),
                'black_bg': QColor('#3a3a3a'),
                'selected': QColor(255, 255, 0, 100),
                'move_dot': QColor(0, 200, 0, 160),
                'last_move': QColor(255, 200, 0, 80),
            }
        else:
            return {
                'board_bg': QColor('#E8C48F'),
                'line': QColor('#5D3A1A'),
                'river_text': QColor('#8B6914'),
                'red_text': QColor('#C41E3A'),
                'red_bg': QColor('#F5E6D3'),
                'black_text': QColor('#000000'),
                'black_bg': QColor('#8B4513'),
                'selected': QColor(255, 255, 0, 120),
                'move_dot': QColor(0, 180, 0, 150),
                'last_move': QColor(255, 200, 0, 70),
            }

    def _calculate_geometry(self):
        w = self.width()
        h = self.height()

        board_width = Board.WIDTH - 1
        board_height = Board.HEIGHT - 1

        available_w = w - 2 * self._margin
        available_h = h - 2 * self._margin

        cell_size_w = available_w / board_width
        cell_size_h = available_h / board_height

        self._cell_size = int(min(cell_size_w, cell_size_h))

        total_board_w = self._cell_size * board_width
        total_board_h = self._cell_size * board_height

        self._offset_x = (w - total_board_w) / 2
        self._offset_y = (h - total_board_h) / 2

    def _board_to_pixel(self, x: int, y: int) -> Tuple[int, int]:
        px = int(self._offset_x + x * self._cell_size)
        py = int(self._offset_y + y * self._cell_size)
        return px, py

    def _pixel_to_board(self, px: float, py: float) -> Tuple[int, int]:
        x = round((px - self._offset_x) / self._cell_size)
        y = round((py - self._offset_y) / self._cell_size)
        return x, y

    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < Board.WIDTH and 0 <= y < Board.HEIGHT

    def _get_piece_radius(self) -> int:
        base = self._cell_size * 0.42
        if self._large_pieces:
            base *= 1.2
        return int(min(base, self._cell_size * 0.48))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self._calculate_geometry()
        colors = self._get_colors()

        self._draw_board_background(painter, colors)
        self._draw_grid_lines(painter, colors)
        self._draw_river(painter, colors)
        self._draw_palace_lines(painter, colors)
        self._draw_last_move_highlight(painter, colors)
        self._draw_move_highlights(painter, colors)
        self._draw_selected_highlight(painter, colors)
        self._draw_pieces(painter, colors)
        self._draw_dragging_piece(painter, colors)

    def _draw_board_background(self, painter: QPainter, colors):
        painter.fillRect(self.rect(), colors['board_bg'])

    def _draw_grid_lines(self, painter: QPainter, colors):
        pen = QPen(colors['line'])
        pen.setWidth(1)
        painter.setPen(pen)

        for x in range(Board.WIDTH):
            x1, y1 = self._board_to_pixel(x, 0)
            x2, y2 = self._board_to_pixel(x, Board.HEIGHT - 1)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        for y in range(Board.HEIGHT):
            x1, y1 = self._board_to_pixel(0, y)
            x2, y2 = self._board_to_pixel(Board.WIDTH - 1, y)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _draw_river(self, painter: QPainter, colors):
        x1, y1 = self._board_to_pixel(0, 4)
        x2, y2 = self._board_to_pixel(Board.WIDTH - 1, 5)

        pen = QPen(colors['line'])
        pen.setWidth(1)
        painter.setPen(pen)

        for x in range(Board.WIDTH):
            px, _ = self._board_to_pixel(x, 0)
            if x == 0 or x == Board.WIDTH - 1:
                py_top = y1
                py_bottom = y2
                painter.drawLine(QPointF(px, py_top), QPointF(px, py_bottom))

        font_size = int(self._cell_size * 0.6)
        font = QFont('SimSun', font_size)
        painter.setFont(font)
        painter.setPen(colors['river_text'])

        text_y = (y1 + y2) / 2
        fm = QFontMetrics(font)
        text_height = fm.height()

        left_text = '楚 河'
        right_text = '汉 界'

        text_width_left = fm.width(left_text)
        text_width_right = fm.width(right_text)

        left_x = x1 + (x2 - x1) * 0.25 - text_width_left / 2
        right_x = x1 + (x2 - x1) * 0.75 - text_width_right / 2

        painter.drawText(QPointF(left_x, text_y + text_height / 4), left_text)
        painter.drawText(QPointF(right_x, text_y + text_height / 4), right_text)

    def _draw_palace_lines(self, painter: QPainter, colors):
        pen = QPen(colors['line'])
        pen.setWidth(1)
        painter.setPen(pen)

        tl_x, tl_y = self._board_to_pixel(3, 0)
        tr_x, tr_y = self._board_to_pixel(5, 0)
        bl_x, bl_y = self._board_to_pixel(3, 2)
        br_x, br_y = self._board_to_pixel(5, 2)
        painter.drawLine(QPointF(tl_x, tl_y), QPointF(br_x, br_y))
        painter.drawLine(QPointF(tr_x, tr_y), QPointF(bl_x, bl_y))

        tl_x, tl_y = self._board_to_pixel(3, 7)
        tr_x, tr_y = self._board_to_pixel(5, 7)
        bl_x, bl_y = self._board_to_pixel(3, 9)
        br_x, br_y = self._board_to_pixel(5, 9)
        painter.drawLine(QPointF(tl_x, tl_y), QPointF(br_x, br_y))
        painter.drawLine(QPointF(tr_x, tr_y), QPointF(bl_x, bl_y))

    def _draw_last_move_highlight(self, painter: QPainter, colors):
        if self._last_move_from is not None and self._last_move_to is not None:
            self._draw_position_highlight(painter, colors['last_move'],
                                          self._last_move_from[0], self._last_move_from[1])
            self._draw_position_highlight(painter, colors['last_move'],
                                          self._last_move_to[0], self._last_move_to[1])

    def _draw_position_highlight(self, painter: QPainter, color: QColor, x: int, y: int):
        px, py = self._board_to_pixel(x, y)
        size = self._cell_size * 0.9
        rect = QRectF(px - size / 2, py - size / 2, size, size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawRect(rect)

    def _draw_move_highlights(self, painter: QPainter, colors):
        for mx, my in self._highlight_moves:
            px, py = self._board_to_pixel(mx, my)
            radius = self._cell_size * 0.15

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(colors['move_dot']))
            painter.drawEllipse(QPointF(px, py), radius, radius)

    def _draw_selected_highlight(self, painter: QPainter, colors):
        if self._selected_x >= 0 and self._selected_y >= 0:
            self._draw_position_highlight(painter, colors['selected'],
                                          self._selected_x, self._selected_y)

    def _draw_pieces(self, painter: QPainter, colors):
        if self._board is None:
            return

        for y in range(Board.HEIGHT):
            for x in range(Board.WIDTH):
                piece = self._board.get_piece(x, y)
                if piece is not None:
                    if self._dragging and x == self._drag_start_x and y == self._drag_start_y:
                        continue
                    self._draw_piece(painter, colors, piece, x, y)

    def _draw_piece(self, painter: QPainter, colors, piece: Piece, x: int, y: int):
        px, py = self._board_to_pixel(x, y)
        radius = self._get_piece_radius()

        if piece.color == PieceColor.RED:
            bg_color = colors['red_bg']
            text_color = colors['red_text']
        else:
            bg_color = colors['black_bg']
            text_color = colors['black_text']

        painter.setPen(QPen(colors['line'], 2))
        painter.setBrush(QBrush(bg_color))
        painter.drawEllipse(QPointF(px, py), radius, radius)

        inner_radius = radius * 0.88
        pen = QPen(text_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(px, py), inner_radius, inner_radius)

        font_size = int(radius * 1.1)
        font = QFont('SimSun', font_size, QFont.Bold)
        painter.setFont(font)
        painter.setPen(text_color)

        text = piece.chinese_name
        fm = QFontMetrics(font)
        text_width = fm.width(text)
        text_height = fm.height()

        painter.drawText(QPointF(px - text_width / 2, py + text_height / 4), text)

    def _draw_dragging_piece(self, painter: QPainter, colors):
        if not self._dragging or self._board is None:
            return

        piece = self._board.get_piece(self._drag_start_x, self._drag_start_y)
        if piece is None:
            return

        px = self._drag_pos.x()
        py = self._drag_pos.y()
        radius = self._get_piece_radius()

        if piece.color == PieceColor.RED:
            bg_color = colors['red_bg']
            text_color = colors['red_text']
        else:
            bg_color = colors['black_bg']
            text_color = colors['black_text']

        painter.setPen(QPen(colors['line'], 2))
        painter.setBrush(QBrush(bg_color))
        painter.drawEllipse(QPointF(px, py), radius, radius)

        inner_radius = radius * 0.88
        pen = QPen(text_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(px, py), inner_radius, inner_radius)

        font_size = int(radius * 1.1)
        font = QFont('SimSun', font_size, QFont.Bold)
        painter.setFont(font)
        painter.setPen(text_color)

        text = piece.chinese_name
        fm = QFontMetrics(font)
        text_width = fm.width(text)
        text_height = fm.height()

        painter.drawText(QPointF(px - text_width / 2, py + text_height / 4), text)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or self._board is None:
            return

        x, y = self._pixel_to_board(event.x(), event.y())
        if not self._is_valid_position(x, y):
            return

        piece = self._board.get_piece(x, y)

        if self._selected_x >= 0 and self._selected_y >= 0:
            if (x, y) in self._highlight_moves:
                self.move_made.emit(self._selected_x, self._selected_y, x, y)
                self.clear_selection()
                return

        if piece is not None:
            self._dragging = True
            self._drag_start_x = x
            self._drag_start_y = y
            self._drag_pos = event.pos()

            if not (self._selected_x == x and self._selected_y == y):
                self._selected_x = x
                self._selected_y = y
                self.piece_selected.emit(x, y)
                self._highlight_moves = []

            self.update()
        else:
            if not (self._selected_x == x and self._selected_y == y):
                self.clear_selection()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._drag_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton or not self._dragging:
            return

        self._dragging = False

        x, y = self._pixel_to_board(event.x(), event.y())

        if self._is_valid_position(x, y):
            if (x, y) in self._highlight_moves:
                self.move_made.emit(self._drag_start_x, self._drag_start_y, x, y)
                self.clear_selection()
                self.update()
                return

        self.update()

    def sizeHint(self):
        base = 50 if not self._large_pieces else 65
        w = base * (Board.WIDTH - 1) + 2 * self._margin
        h = base * (Board.HEIGHT - 1) + 2 * self._margin
        from PyQt5.QtCore import QSize
        return QSize(w, h)

    def minimumSizeHint(self):
        base = 30
        w = base * (Board.WIDTH - 1) + 2 * self._margin
        h = base * (Board.HEIGHT - 1) + 2 * self._margin
        from PyQt5.QtCore import QSize
        return QSize(w, h)
