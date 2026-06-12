import random
from typing import Optional, List
from ..core.board import Board
from ..core.pieces import PieceColor, PieceType
from ..core.move import Move
from ..core.rules import generate_moves, is_check, is_checkmate


class AIOpponent:
    def __init__(self, difficulty: str = "中等"):
        self.difficulty = difficulty

    def get_best_move(self, board: Board, color: PieceColor) -> Optional[Move]:
        moves = generate_moves(board, color)
        if not moves:
            return None

        if self.difficulty == "简单":
            return self._random_strategy(board, color, moves)
        elif self.difficulty == "困难":
            return self._aggressive_strategy(board, color, moves)
        else:
            return self._balanced_strategy(board, color, moves)

    def _random_strategy(self, board: Board, color: PieceColor, moves: List[Move]) -> Optional[Move]:
        check_moves = []
        capture_moves = []
        other_moves = []

        for move in moves:
            test_board = board.clone()
            test_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)
            opp_color = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
            if is_check(test_board, opp_color):
                check_moves.append(move)
            elif move.captured_piece is not None:
                capture_moves.append(move)
            else:
                other_moves.append(move)

        if check_moves and random.random() < 0.4:
            return random.choice(check_moves)
        if capture_moves and random.random() < 0.3:
            return random.choice(capture_moves)
        return random.choice(moves)

    def _balanced_strategy(self, board: Board, color: PieceColor, moves: List[Move]) -> Optional[Move]:
        scored_moves = []

        for move in moves:
            score = self._evaluate_move(board, move, color)
            scored_moves.append((score, move))

        scored_moves.sort(key=lambda x: x[0], reverse=True)

        top_moves = scored_moves[:min(5, len(scored_moves))]
        return random.choice(top_moves)[1]

    def _aggressive_strategy(self, board: Board, color: PieceColor, moves: List[Move]) -> Optional[Move]:
        best_score = -99999
        best_move = None

        for move in moves:
            test_board = board.clone()
            test_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)

            score = self._evaluate_position(test_board, color)

            opp_color = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
            opp_moves = generate_moves(test_board, opp_color)
            if opp_moves:
                min_reply_score = 99999
                for opp_move in opp_moves[:10]:
                    reply_board = test_board.clone()
                    reply_board.move_piece(opp_move.from_x, opp_move.from_y, opp_move.to_x, opp_move.to_y)
                    reply_score = self._evaluate_position(reply_board, color)
                    if reply_score < min_reply_score:
                        min_reply_score = reply_score
                score = min_reply_score

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _evaluate_move(self, board: Board, move: Move, color: PieceColor) -> int:
        score = 0

        if move.captured_piece is not None:
            piece_values = {
                PieceType.KING: 10000,
                PieceType.CHARIOT: 900,
                PieceType.HORSE: 400,
                PieceType.CANNON: 450,
                PieceType.ADVISOR: 200,
                PieceType.ELEPHANT: 200,
                PieceType.PAWN: 100,
            }
            score += piece_values.get(move.captured_piece.type, 0) * 10

        test_board = board.clone()
        test_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)

        opp_color = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
        if is_checkmate(test_board, opp_color):
            score += 5000
        elif is_check(test_board, opp_color):
            score += 50

        center_x = 4
        center_y = 4.5
        dist_to_center = abs(move.to_x - center_x) + abs(move.to_y - center_y)
        score += (16 - dist_to_center)

        if move.piece.type == PieceType.PAWN:
            if board.is_river_crossed(move.to_x, move.to_y, color):
                score += 30

        return score

    def _evaluate_position(self, board: Board, color: PieceColor) -> int:
        score = 0

        piece_values = {
            PieceType.KING: 10000,
            PieceType.CHARIOT: 900,
            PieceType.HORSE: 400,
            PieceType.CANNON: 450,
            PieceType.ADVISOR: 200,
            PieceType.ELEPHANT: 200,
            PieceType.PAWN: 100,
        }

        for y in range(Board.HEIGHT):
            for x in range(Board.WIDTH):
                piece = board.get_piece(x, y)
                if piece is not None:
                    value = piece_values.get(piece.type, 0)
                    if piece.color == color:
                        score += value
                    else:
                        score -= value

        opp_color = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
        if is_check(board, opp_color):
            score += 30
        if is_checkmate(board, opp_color):
            score += 5000

        if is_check(board, color):
            score -= 50

        return score
