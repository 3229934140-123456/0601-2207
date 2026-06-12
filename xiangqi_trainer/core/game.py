import time
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from .board import Board
from .pieces import PieceColor, PieceType
from .move import Move
from .rules import generate_moves, is_check, is_checkmate, is_stalemate
from .utils import (
    board_from_grid, parse_move_str, find_solution_move,
    board_to_grid, PgnParseResult
)
from ..data.puzzles import Puzzle, create_empty_board
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
        all_moves = generate_moves(self.board, self.current_turn)
        return [m for m in all_moves if m.from_x == x and m.from_y == y]

    def get_mating_variations(self) -> List[Tuple[str, Move]]:
        """获取当前局面下所有能将死对方的走法（作为变着）"""
        from .rules import is_checkmate
        mating_moves = []
        all_moves = generate_moves(self.board, self.current_turn)
        for move in all_moves:
            temp_board = self.board.clone()
            temp_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)
            opponent = (PieceColor.BLACK if self.current_turn == PieceColor.RED
                       else PieceColor.RED)
            if is_checkmate(temp_board, opponent):
                mating_moves.append((move.to_chinese(), move))
        return mating_moves

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

    def load_imported_pgn(self, pgn_result: PgnParseResult, as_puzzle: bool = False) -> Puzzle:
        """加载导入的棋谱"""
        grid = board_to_grid(pgn_result.initial_board)

        if as_puzzle:
            solution = []
            for i, move in enumerate(pgn_result.moves):
                if move.color == pgn_result.first_move_color:
                    solution.append(move.to_chinese())
        else:
            solution = [m.to_chinese() for m in pgn_result.moves]

        puzzle_id = f"imported_{int(time.time())}"
        name = pgn_result.name or f"导入棋谱_{time.strftime('%Y%m%d_%H%M%S')}"

        puzzle = Puzzle(
            id=puzzle_id,
            name=name,
            description=f"从棋谱文件导入，共{len(pgn_result.moves)}步",
            difficulty="中等",
            kill_type="自定义",
            steps=len(solution) if solution else 1,
            initial_board=grid,
            solution=solution if as_puzzle else [],
            black_to_move=(pgn_result.first_move_color == PieceColor.BLACK)
        )

        self.load_puzzle(puzzle)

        if not as_puzzle:
            self.board_history = []
            self.move_history = []
            temp_board = pgn_result.initial_board.clone()
            current_color = pgn_result.first_move_color
            for move in pgn_result.moves:
                self.board_history.append(temp_board.clone())
                record = MoveRecord(move=move, is_correct=True, deviation_type="", time_taken=0.5)
                self.move_history.append(record)
                temp_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)
                current_color = (PieceColor.BLACK if current_color == PieceColor.RED
                                  else PieceColor.RED)

            if self.board_history:
                self.board = self.board_history[-1].clone()
                last_move = self.move_history[-1].move
                self.board.move_piece(last_move.from_x, last_move.from_y,
                                     last_move.to_x, last_move.to_y)
            self.current_turn = current_color
            self.is_game_over = False

        return puzzle

    def get_board_at_step(self, step_index: int) -> Optional[Board]:
        """获取指定步数的棋盘状态，用于复盘"""
        if step_index < -1 or step_index >= len(self.board_history):
            return None

        if step_index == -1:
            if self.current_puzzle:
                return board_from_grid(self.current_puzzle.initial_board)
            return None

        return self.board_history[step_index].clone()

    def save_current_as_custom_puzzle(self) -> Optional[Puzzle]:
        """保存当前棋盘为自定义残局"""
        grid = board_to_grid(self.board)

        has_red_king = False
        has_black_king = False
        for row in grid:
            for ch in row:
                if ch == 'K':
                    has_red_king = True
                elif ch == 'k':
                    has_black_king = True

        if not has_red_king or not has_black_king:
            return None

        puzzle_id = f"custom_{int(time.time())}"
        puzzle = Puzzle(
            id=puzzle_id,
            name=f"自定义残局_{time.strftime('%Y%m%d_%H%M%S')}",
            description="用户自定义保存的残局",
            difficulty="中等",
            kill_type="自定义",
            steps=3,
            initial_board=grid,
            solution=[],
            black_to_move=(self.current_turn == PieceColor.BLACK)
        )
        return puzzle
