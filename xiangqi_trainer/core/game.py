import time
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from .board import Board
from .pieces import PieceColor, PieceType
from .move import Move
from .rules import generate_moves, is_check, is_checkmate, is_stalemate
from .utils import board_from_grid, parse_move_str, find_solution_move
from ..data.puzzles import Puzzle
from ..data.storage import Statistics, record_puzzle_result


@dataclass
class MoveRecord:
    move: Move
    is_correct: bool = True
    deviation_type: str = ""
    time_taken: float = 0.0


class GameController:
    def __init__(self):
        self.board: Board = Board()
        self.current_puzzle: Optional[Puzzle] = None
        self.current_turn: PieceColor = PieceColor.RED
        self.move_history: List[MoveRecord] = []
        self.board_history: List[Board] = []
        self.solution_step_index: int = 0
        self.hints_used: int = 0
        self.score: int = 100
        self.start_time: float = 0
        self.total_time: float = 0
        self.is_game_over: bool = False
        self.game_result: str = ""
        self.last_move_time: float = 0

    def load_puzzle(self, puzzle: Puzzle) -> None:
        self.current_puzzle = puzzle
        self.board = board_from_grid(puzzle.initial_board)
        self.current_turn = PieceColor.BLACK if puzzle.black_to_move else PieceColor.RED
        self.move_history = []
        self.board_history = []
        self.solution_step_index = 0
        self.hints_used = 0
        self.score = 100
        self.start_time = time.time()
        self.last_move_time = self.start_time
        self.total_time = 0
        self.is_game_over = False
        self.game_result = ""

    def get_valid_moves(self, x: int, y: int) -> List[Move]:
        piece = self.board.get_piece(x, y)
        if piece is None or piece.color != self.current_turn:
            return []
        return generate_moves(self.board, self.current_turn)

    def make_move(self, from_x: int, from_y: int, to_x: int, to_y: int) -> Tuple[bool, str]:
        if self.is_game_over:
            return False, "游戏已结束"

        piece = self.board.get_piece(from_x, from_y)
        if piece is None:
            return False, "没有棋子"

        if piece.color != self.current_turn:
            return False, "不是你的回合"

        valid_moves = self.get_valid_moves(from_x, from_y)
        target_move = None
        for m in valid_moves:
            if m.to_x == to_x and m.to_y == to_y and m.from_x == from_x and m.from_y == from_y:
                target_move = m
                break

        if target_move is None:
            return False, "不合法的走法"

        current_time = time.time()
        time_taken = current_time - self.last_move_time
        self.last_move_time = current_time

        self.board_history.append(self.board.clone())

        captured = self.board.move_piece(from_x, from_y, to_x, to_y)
        target_move.captured_piece = captured

        is_correct, deviation = self._evaluate_move(target_move)

        record = MoveRecord(
            move=target_move,
            is_correct=is_correct,
            deviation_type=deviation,
            time_taken=time_taken
        )
        self.move_history.append(record)

        self._switch_turn()

        self._check_game_end()

        return True, ""

    def _evaluate_move(self, move: Move) -> Tuple[bool, str]:
        if self.current_puzzle is None:
            return True, ""

        player_color = PieceColor.BLACK if self.current_puzzle.black_to_move else PieceColor.RED

        if self.current_turn != player_color:
            return True, ""

        solution = self.current_puzzle.solution
        if self.solution_step_index >= len(solution):
            return True, ""

        expected_move_str = solution[self.solution_step_index]
        expected_move = parse_move_str(
            self.board_history[-1] if self.board_history else
            board_from_grid(self.current_puzzle.initial_board),
            expected_move_str,
            player_color
        )

        if expected_move is None:
            self.solution_step_index += 1
            return True, ""

        if move.from_x == expected_move.from_x and move.to_x == expected_move.to_x \
           and move.from_y == expected_move.from_y and move.to_y == expected_move.to_y:
            self.solution_step_index += 1
            return True, ""
        else:
            deviation = "偏离解法"
            return False, deviation

    def _switch_turn(self):
        self.current_turn = PieceColor.BLACK if self.current_turn == PieceColor.RED else PieceColor.RED

    def _check_game_end(self):
        opponent = PieceColor.BLACK if self.current_turn == PieceColor.RED else PieceColor.RED

        if is_checkmate(self.board, self.current_turn):
            self.is_game_over = True
            self.total_time = time.time() - self.start_time
            player_color = PieceColor.BLACK if self.current_puzzle.black_to_move else PieceColor.RED
            if self.current_turn != player_color:
                self.game_result = "胜利！成功将死对方"
            else:
                self.game_result = "失败"
            return

        if is_stalemate(self.board, self.current_turn):
            self.is_game_over = True
            self.total_time = time.time() - self.start_time
            self.game_result = "和棋（困毙）"
            return

        kings_red = 0
        kings_black = 0
        for y in range(Board.HEIGHT):
            for x in range(Board.WIDTH):
                p = self.board.get_piece(x, y)
                if p and p.type == PieceType.KING:
                    if p.color == PieceColor.RED:
                        kings_red += 1
                    else:
                        kings_black += 1

        if kings_red == 0 or kings_black == 0:
            self.is_game_over = True
            self.total_time = time.time() - self.start_time
            self.game_result = "胜利" if kings_black == 0 else "失败"

    def undo_move(self) -> bool:
        if len(self.move_history) == 0:
            return False

        if self.is_game_over:
            self.is_game_over = False
            self.game_result = ""

        self.move_history.pop()
        if self.board_history:
            self.board = self.board_history.pop()

        self._switch_turn()

        if self.current_puzzle:
            player_color = PieceColor.BLACK if self.current_puzzle.black_to_move else PieceColor.RED
            if self.current_turn == player_color and self.solution_step_index > 0:
                self.solution_step_index -= 1

        return True

    def restart_puzzle(self) -> None:
        if self.current_puzzle:
            self.load_puzzle(self.current_puzzle)

    def get_solution_hint(self, level: int) -> Optional[str]:
        if self.current_puzzle is None:
            return None

        player_color = PieceColor.BLACK if self.current_puzzle.black_to_move else PieceColor.RED
        if self.current_turn != player_color:
            return "等对方走完再提示"

        solution = self.current_puzzle.solution
        if self.solution_step_index >= len(solution):
            return "已完成所有解法步骤"

        move_str = solution[self.solution_step_index]
        current_board = self.board_history[-1] if self.board_history else \
            board_from_grid(self.current_puzzle.initial_board)
        move = parse_move_str(current_board, move_str, player_color)

        if move is None:
            return None

        self.hints_used += 1
        points = 10 * level
        self.score = max(0, self.score - points)

        if level == 1:
            return f"提示：走 {move.piece.chinese_name}"
        elif level == 2:
            return f"提示：{move.piece.chinese_name} 从 {move.from_x + 1} 路走到 {move.to_x + 1} 路"
        else:
            return f"提示：{move.to_chinese()}"

    def get_total_time(self) -> float:
        if self.is_game_over:
            return self.total_time
        return time.time() - self.start_time

    def get_current_step_solution(self) -> Optional[str]:
        if self.current_puzzle is None:
            return None
        if self.solution_step_index >= len(self.current_puzzle.solution):
            return None
        return self.current_puzzle.solution[self.solution_step_index]

    def get_solution_moves(self) -> List[str]:
        if self.current_puzzle is None:
            return []
        return self.current_puzzle.solution

    def save_result(self, stats: Statistics) -> None:
        if self.current_puzzle is None:
            return

        correct = self.game_result.startswith("胜利")
        steps = len([m for m in self.move_history
                     if m.move.color == (PieceColor.BLACK if self.current_puzzle.black_to_move else PieceColor.RED)])
        total_time = self.get_total_time()

        error_type = ""
        if not correct:
            if self.hints_used > 3:
                error_type = "过度依赖提示"
            elif any(not m.is_correct for m in self.move_history):
                error_type = "走法偏离"
            else:
                error_type = "未能成杀"

        record_puzzle_result(
            stats,
            self.current_puzzle.id,
            correct,
            steps,
            total_time,
            self.hints_used,
            error_type
        )
