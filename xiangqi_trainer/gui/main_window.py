import sys
import time
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QAction, QActionGroup, QToolBar, QLabel, QPushButton, QFrame,
    QMessageBox, QFileDialog, QInputDialog, QMenu, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

from .board_widget import BoardWidget
from .puzzle_library import PuzzleLibrary
from .hint_panel import HintPanel
from .review_panel import ReviewPanel
from .stats_panel import StatsPanel

from ..core.game import GameController
from ..core.ai import AIOpponent
from ..core.board import Board
from ..core.pieces import PieceColor
from ..core.rules import is_check
from ..core.utils import (
    board_to_grid, board_from_grid, parse_move_str, parse_pgn_text
)

from ..data.puzzles import get_all_puzzles, get_puzzle_by_id, Puzzle
from ..data.storage import (
    load_stats, save_stats, get_custom_puzzles, add_custom_puzzle,
    Statistics
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("象棋残局训练")
        self.resize(1200, 800)

        self.game = GameController()
        self.ai = AIOpponent("中等")
        self.stats: Statistics = load_stats()
        self.night_mode = False
        self.large_pieces = False
        self.ai_thinking = False
        self.review_mode = False

        self._saved_board = None
        self._saved_board_history = []
        self._saved_move_history = []
        self._saved_turn = PieceColor.RED
        self._saved_solution_index = 0
        self._saved_is_game_over = False
        self._saved_game_result = ""
        self._saved_black_to_move = False
        self._current_record = None
        self._record_step_notes = {}
        self._record_step_deviations = {}

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)
        self.elapsed_seconds = 0

        self._init_ui()
        self._init_menu()
        self._init_toolbar()
        self._connect_signals()
        self._load_default_puzzle()
        self._update_stats_display()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        left_splitter = QSplitter(Qt.Vertical)

        self.puzzle_library = PuzzleLibrary()
        self.puzzle_library.setMinimumWidth(280)

        self.stats_panel = StatsPanel()

        left_tab = QTabWidget()
        left_tab.addTab(self.puzzle_library, "题库")
        left_tab.addTab(self.stats_panel, "成绩")

        left_splitter.addWidget(left_tab)

        center_layout = QVBoxLayout()
        center_layout.setSpacing(8)

        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_layout.setSpacing(15)

        self.puzzle_name_label = QLabel("未选择残局")
        puzzle_name_font = QFont()
        puzzle_name_font.setPointSize(13)
        puzzle_name_font.setBold(True)
        self.puzzle_name_label.setFont(puzzle_name_font)
        info_layout.addWidget(self.puzzle_name_label)

        info_layout.addStretch()

        self.turn_label = QLabel("红方走")
        self.turn_label.setStyleSheet(
            "color: #C41E3A; font-weight: bold; font-size: 14px;"
        )
        info_layout.addWidget(self.turn_label)

        self.check_label = QLabel("")
        self.check_label.setStyleSheet(
            "color: #e74c3c; font-weight: bold; font-size: 14px;"
        )
        info_layout.addWidget(self.check_label)

        self.time_label = QLabel("00:00")
        time_font = QFont()
        time_font.setPointSize(14)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        self.time_label.setStyleSheet("color: #2c3e50;")
        info_layout.addWidget(self.time_label)

        center_layout.addWidget(info_frame)

        self.board_widget = BoardWidget()
        self.board_widget.setMinimumSize(500, 550)
        center_layout.addWidget(self.board_widget, 1)

        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.StyledPanel)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(12, 8, 12, 8)
        control_layout.setSpacing(8)

        self.undo_btn = QPushButton("撤回")
        self.restart_btn = QPushButton("重来")
        self.hint_btn = QPushButton("提示")
        self.review_btn = QPushButton("复盘")
        self.next_puzzle_btn = QPushButton("下一题")

        for btn in [self.undo_btn, self.restart_btn, self.hint_btn,
                    self.review_btn, self.next_puzzle_btn]:
            btn.setMinimumHeight(36)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                    color: #7f8c8d;
                }
            """)

        self.undo_btn.clicked.connect(self._on_undo)
        self.restart_btn.clicked.connect(self._on_restart)
        self.hint_btn.clicked.connect(self._on_hint)
        self.review_btn.clicked.connect(self._on_review)
        self.next_puzzle_btn.clicked.connect(self._on_next_puzzle)

        control_layout.addWidget(self.undo_btn)
        control_layout.addWidget(self.restart_btn)
        control_layout.addWidget(self.hint_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.review_btn)
        control_layout.addWidget(self.next_puzzle_btn)

        center_layout.addWidget(control_frame)

        center_widget = QWidget()
        center_widget.setLayout(center_layout)

        right_tab = QTabWidget()
        right_tab.setMinimumWidth(300)

        self.hint_panel = HintPanel()
        right_tab.addTab(self.hint_panel, "提示")

        self.review_panel = ReviewPanel()
        right_tab.addTab(self.review_panel, "复盘")

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_tab)
        main_splitter.addWidget(center_widget)
        main_splitter.addWidget(right_tab)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setStretchFactor(2, 1)

        main_layout.addWidget(main_splitter)

    def _init_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件")

        save_puzzle_action = QAction("保存当前残局为自定义...", self)
        save_puzzle_action.triggered.connect(self._on_save_custom_puzzle)
        file_menu.addAction(save_puzzle_action)

        save_record_action = QAction("保存当前对局记录...", self)
        save_record_action.triggered.connect(self._on_save_game_record)
        file_menu.addAction(save_record_action)

        edit_record_action = QAction("编辑对局备注与标签...", self)
        edit_record_action.triggered.connect(self._on_edit_record_info)
        file_menu.addAction(edit_record_action)

        import_pgn_action = QAction("导入棋谱文本...", self)
        import_pgn_action.triggered.connect(self._on_import_pgn)
        file_menu.addAction(import_pgn_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        game_menu = menubar.addMenu("游戏")

        undo_action = QAction("撤回一步", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._on_undo)
        game_menu.addAction(undo_action)

        restart_action = QAction("重新开始", self)
        restart_action.setShortcut("Ctrl+R")
        restart_action.triggered.connect(self._on_restart)
        game_menu.addAction(restart_action)

        game_menu.addSeparator()

        hint_action = QAction("获取提示", self)
        hint_action.setShortcut("H")
        hint_action.triggered.connect(self._on_hint)
        game_menu.addAction(hint_action)

        view_menu = menubar.addMenu("视图")

        night_mode_action = QAction("夜间模式", self)
        night_mode_action.setCheckable(True)
        night_mode_action.toggled.connect(self._toggle_night_mode)
        view_menu.addAction(night_mode_action)

        large_pieces_action = QAction("大棋子模式", self)
        large_pieces_action.setCheckable(True)
        large_pieces_action.toggled.connect(self._toggle_large_pieces)
        view_menu.addAction(large_pieces_action)

        help_menu = menubar.addMenu("帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _init_toolbar(self):
        toolbar = QToolBar("工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        undo_action = QAction("撤回", self)
        undo_action.triggered.connect(self._on_undo)
        toolbar.addAction(undo_action)

        restart_action = QAction("重来", self)
        restart_action.triggered.connect(self._on_restart)
        toolbar.addAction(restart_action)

        toolbar.addSeparator()

        hint_action = QAction("提示", self)
        hint_action.triggered.connect(self._on_hint)
        toolbar.addAction(hint_action)

        toolbar.addSeparator()

        night_action = QAction("夜间模式", self)
        night_action.setCheckable(True)
        night_action.toggled.connect(self._toggle_night_mode)
        toolbar.addAction(night_action)

        large_action = QAction("大棋子", self)
        large_action.setCheckable(True)
        large_action.toggled.connect(self._toggle_large_pieces)
        toolbar.addAction(large_action)

    def _connect_signals(self):
        self.board_widget.piece_selected.connect(self._on_piece_selected)
        self.board_widget.move_made.connect(self._on_move_made)
        self.puzzle_library.puzzle_selected.connect(self._on_puzzle_selected)
        self.hint_panel.hint_requested.connect(self._on_hint_requested)
        self.review_panel.step_changed.connect(self._on_review_step_changed)
        self.review_panel.review_closed.connect(self._on_review_closed)
        self.review_panel.note_changed.connect(self._on_review_note_changed)

    def _load_default_puzzle(self):
        all_puzzles = get_all_puzzles()
        custom_puzzles = get_custom_puzzles()
        self.puzzle_library.load_puzzles(all_puzzles + custom_puzzles)

        if all_puzzles:
            self._load_puzzle(all_puzzles[0].id)

    def _load_puzzle(self, puzzle_id: str):
        puzzle = get_puzzle_by_id(puzzle_id)
        if puzzle is None:
            custom_puzzles = get_custom_puzzles()
            for p in custom_puzzles:
                if p.id == puzzle_id:
                    puzzle = p
                    break

        if puzzle is None:
            return

        self.game.load_puzzle(puzzle)
        self.board_widget.set_board(self.game.board)
        self.board_widget.clear_selection()
        self.puzzle_name_label.setText(puzzle.name)

        self.hint_panel.reset()
        self.hint_panel.set_score(self.game.score)

        self.elapsed_seconds = 0
        self.timer.start(1000)
        self._update_turn_label()
        self._update_check_status()
        self._update_buttons()

        self.review_mode = False

        self._update_review_panel()

    def _refresh_after_load(self, puzzle: Puzzle):
        """加载残局或导入棋谱后刷新界面"""
        self.board_widget.set_board(self.game.board)
        self.board_widget.clear_selection()
        self.puzzle_name_label.setText(puzzle.name)

        self.hint_panel.reset()
        self.hint_panel.set_score(self.game.score)

        self.elapsed_seconds = 0
        if not self.review_mode:
            self.timer.start(1000)
        self._update_turn_label()
        self._update_check_status()
        self._update_buttons()
        self._update_review_panel()

    def _on_puzzle_selected(self, puzzle_id: str):
        self._load_puzzle(puzzle_id)

    def _on_piece_selected(self, x: int, y: int):
        if self.review_mode or self.ai_thinking:
            return

        valid_moves = self.game.get_valid_moves(x, y)
        move_positions = [(m.to_x, m.to_y) for m in valid_moves]
        self.board_widget.highlight_moves(move_positions)

    def _on_move_made(self, from_x: int, from_y: int, to_x: int, to_y: int):
        if self.review_mode or self.ai_thinking:
            return

        player_color = PieceColor.BLACK if self.game.current_puzzle.black_to_move else PieceColor.RED

        if self.game.current_turn != player_color:
            return

        success, msg = self.game.make_move(from_x, from_y, to_x, to_y)
        if not success:
            QMessageBox.warning(self, "提示", msg)
            return

        self.board_widget.set_board(self.game.board)
        self.board_widget.highlight_last_move(from_x, from_y, to_x, to_y)
        self.board_widget.clear_selection()

        self._update_turn_label()
        self._update_check_status()
        self._update_buttons()
        self._update_review_panel()

        if self.game.is_game_over:
            self._on_game_over()
            return

        if self.game.current_turn != player_color:
            QTimer.singleShot(500, self._ai_move)

    def _ai_move(self):
        if self.game.is_game_over or self.review_mode:
            return

        self.ai_thinking = True
        self.turn_label.setText("电脑思考中...")

        ai_color = self.game.current_turn
        move = self.ai.get_best_move(self.game.board, ai_color)

        if move is None:
            self.ai_thinking = False
            self._update_turn_label()
            return

        success, _ = self.game.make_move(move.from_x, move.from_y, move.to_x, move.to_y)

        if success:
            self.board_widget.set_board(self.game.board)
            self.board_widget.highlight_last_move(
                move.from_x, move.from_y, move.to_x, move.to_y
            )
            self._update_turn_label()
            self._update_check_status()
            self._update_buttons()
            self._update_review_panel()

            if self.game.is_game_over:
                self._on_game_over()

        self.ai_thinking = False
        self._update_turn_label()

    def _on_undo(self):
        if self.review_mode:
            return

        player_color = PieceColor.BLACK if self.game.current_puzzle.black_to_move else PieceColor.RED

        if self.game.current_turn == player_color:
            if self.game.undo_move():
                self.game.undo_move()

                self.board_widget.set_board(self.game.board)
                self.board_widget.clear_selection()
                self._update_turn_label()
                self._update_check_status()
                self._update_buttons()
                self._update_review_panel()

                if self.game.is_game_over:
                    self.timer.stop()

                self.hint_panel.reset()
                self.hint_panel.set_score(self.game.score)
                self.hint_panel.set_hints_used(self.game.hints_used)
        else:
            self.game.undo_move()
            self.game.undo_move()
            self.board_widget.set_board(self.game.board)
            self.board_widget.clear_selection()
            self._update_turn_label()
            self._update_check_status()
            self._update_buttons()
            self._update_review_panel()

    def _on_restart(self):
        if self.game.current_puzzle:
            self.game.restart_puzzle()
            self.board_widget.set_board(self.game.board)
            self.board_widget.clear_selection()
            self.hint_panel.reset()
            self.hint_panel.set_score(self.game.score)

            self.elapsed_seconds = 0
            self.timer.start(1000)
            self._update_turn_label()
            self._update_check_status()
            self._update_buttons()
            self._update_review_panel()

            self.review_mode = False

    def _on_hint(self):
        if self.game.is_game_over or self.review_mode:
            return

        player_color = PieceColor.BLACK if self.game.current_puzzle.black_to_move else PieceColor.RED
        if self.game.current_turn != player_color:
            QMessageBox.information(self, "提示", "请等待电脑走棋后再获取提示")
            return

        next_level = self.hint_panel._current_level + 1
        self._on_hint_requested(next_level)

    def _on_hint_requested(self, level: int):
        hint_text = self.game.get_solution_hint(level)
        if hint_text:
            self.hint_panel.use_hint(level, hint_text)

    def _on_review(self):
        if not self.game.move_history:
            QMessageBox.information(self, "提示", "还没有走棋记录，无法复盘")
            return

        self.review_mode = True
        self.timer.stop()

        self._saved_board = self.game.board.clone()
        self._saved_board_history = [b.clone() for b in self.game.board_history]
        self._saved_move_history = list(self.game.move_history)
        self._saved_turn = self.game.current_turn
        self._saved_solution_index = self.game.solution_step_index
        self._saved_is_game_over = self.game.is_game_over
        self._saved_game_result = self.game.game_result
        self._saved_black_to_move = self.game.current_puzzle.black_to_move

        self._enter_review_mode(len(self.game.move_history) - 1)

    def _enter_review_mode(self, step_index: int):
        self.review_mode = True

        move_list = []
        for record in self._saved_move_history:
            move_list.append((
                record.move.to_chinese(),
                record.is_correct,
                record.deviation_type
            ))

        player_color = PieceColor.BLACK if self.game.current_puzzle.black_to_move else PieceColor.RED
        player_moves = [m for m in self._saved_move_history if m.move.color == player_color]
        correct_count = sum(1 for m in player_moves if m.is_correct)
        total_time = sum(m.time_taken for m in player_moves)
        avg_time = total_time / len(player_moves) if player_moves else 0

        error_types = {}
        for m in player_moves:
            if not m.is_correct and m.deviation_type:
                error_types[m.deviation_type] = error_types.get(m.deviation_type, 0) + 1

        analysis = {
            'total_steps': len(player_moves),
            'correct_count': correct_count,
            'avg_time': avg_time,
            'error_types': error_types
        }

        self.review_panel.load_review(move_list, analysis)
        self.review_panel.set_solution(self.game.get_solution_moves())
        self.review_panel.set_step_notes(self._record_step_notes)
        self.review_panel.set_step_deviations(self._record_step_deviations)
        self.review_panel.set_current_step(step_index)

        self._show_board_at_step(step_index)

        self._update_buttons()

    def _show_board_at_step(self, step_index: int):
        if step_index < -1 or step_index >= len(self._saved_move_history):
            return

        from ..core.pieces import PieceColor as PC
        first_is_black = self._saved_black_to_move

        if step_index == -1:
            if self.game.current_puzzle:
                from ..core.utils import board_from_grid
                display_board = board_from_grid(self.game.current_puzzle.initial_board)
                current_turn = PC.BLACK if first_is_black else PC.RED
            else:
                return
        else:
            if step_index < len(self._saved_board_history):
                display_board = self._saved_board_history[step_index].clone()
                last_move = self._saved_move_history[step_index].move
                display_board.move_piece(last_move.from_x, last_move.from_y,
                                         last_move.to_x, last_move.to_y)
            else:
                display_board = self._saved_board.clone()

            last_color = self._saved_move_history[step_index].move.color
            current_turn = PC.BLACK if last_color == PC.RED else PC.RED

        self.board_widget.set_board(display_board)
        if step_index >= 0 and step_index < len(self._saved_move_history):
            record = self._saved_move_history[step_index]
            self.board_widget.highlight_last_move(
                record.move.from_x, record.move.from_y,
                record.move.to_x, record.move.to_y
            )
        self.board_widget.clear_selection()

        from ..core.rules import is_check as _is_check
        if _is_check(display_board, current_turn):
            self.check_label.setText("将军！")
        else:
            self.check_label.setText("")
        if current_turn == PC.RED:
            self.turn_label.setText("红方走")
            self.turn_label.setStyleSheet(
                "color: #C41E3A; font-weight: bold; font-size: 14px;"
            )
        else:
            self.turn_label.setText("黑方走")
            self.turn_label.setStyleSheet(
                "color: #333333; font-weight: bold; font-size: 14px;"
            )

    def _on_review_step_changed(self, step_index: int):
        self._show_board_at_step(step_index)

        is_player_turn = (step_index % 2 == 0)
        if is_player_turn and 0 <= step_index < len(self._saved_board_history):
            board_before = self._saved_board_history[step_index]
            player_color = (PieceColor.BLACK if self.game.current_puzzle.black_to_move
                           else PieceColor.RED)

            from ..core.rules import generate_moves, is_checkmate
            from ..core.pieces import PieceColor as PC
            mating_moves = []
            all_moves = generate_moves(board_before, player_color)
            for move in all_moves:
                temp_board = board_before.clone()
                temp_board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)
                opponent = PC.BLACK if player_color == PC.RED else PC.RED
                if is_checkmate(temp_board, opponent):
                    mating_moves.append(move.to_chinese())
            self.review_panel.set_variations(mating_moves)
        else:
            self.review_panel.set_variations([])

    def _on_review_note_changed(self, step_index: int, note_text: str):
        if note_text:
            self._record_step_notes[step_index] = note_text
        elif step_index in self._record_step_notes:
            del self._record_step_notes[step_index]

    def _on_review_closed(self):
        self._record_step_notes = self.review_panel.get_step_notes()

        self.game.board = self._saved_board
        self.game.board_history = self._saved_board_history
        self.game.move_history = self._saved_move_history
        self.game.current_turn = self._saved_turn
        self.game.solution_step_index = self._saved_solution_index
        self.game.is_game_over = self._saved_is_game_over
        self.game.game_result = self._saved_game_result

        self.review_mode = False
        self.board_widget.set_board(self.game.board)
        self.board_widget.clear_selection()
        self._update_turn_label()
        self._update_check_status()
        self._update_buttons()
        self._update_review_panel()
        self.timer.start(1000)

    def _on_next_puzzle(self):
        all_puzzles = get_all_puzzles() + get_custom_puzzles()
        if not all_puzzles:
            return

        current_id = self.game.current_puzzle.id if self.game.current_puzzle else ""
        found = False
        for i, puzzle in enumerate(all_puzzles):
            if puzzle.id == current_id:
                if i < len(all_puzzles) - 1:
                    self._load_puzzle(all_puzzles[i + 1].id)
                    found = True
                break

        if not found and all_puzzles:
            self._load_puzzle(all_puzzles[0].id)

    def _on_game_over(self):
        self.timer.stop()

        self.game.save_result(self.stats)
        save_stats(self.stats)
        self._update_stats_display()

        result = self.game.game_result
        total_time = self.game.get_total_time()
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        time_str = f"{minutes}分{seconds}秒"

        msg = f"{result}\n\n用时：{time_str}\n得分：{self.game.score}\n使用提示：{self.game.hints_used}次"

        if "胜利" in result:
            QMessageBox.information(self, "恭喜", msg)
        else:
            QMessageBox.information(self, "游戏结束", msg)

        self._update_buttons()

    def _update_timer(self):
        self.elapsed_seconds += 1
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def _update_turn_label(self):
        if self.game.current_turn == PieceColor.RED:
            self.turn_label.setText("红方走")
            self.turn_label.setStyleSheet(
                "color: #C41E3A; font-weight: bold; font-size: 14px;"
            )
        else:
            self.turn_label.setText("黑方走")
            self.turn_label.setStyleSheet(
                "color: #333333; font-weight: bold; font-size: 14px;"
            )

    def _update_check_status(self):
        if is_check(self.game.board, self.game.current_turn):
            self.check_label.setText("将军！")
        else:
            self.check_label.setText("")

    def _update_buttons(self):
        has_history = len(self.game.move_history) > 0
        self.undo_btn.setEnabled(has_history and not self.review_mode)
        self.restart_btn.setEnabled(self.game.current_puzzle is not None)
        self.hint_btn.setEnabled(
            not self.game.is_game_over and not self.review_mode
            and self.game.current_puzzle is not None
        )
        self.review_btn.setEnabled(has_history)

    def _update_review_panel(self):
        if self.game.current_puzzle is None:
            return

        move_list = []
        for record in self.game.move_history:
            move_list.append((
                record.move.to_chinese(),
                record.is_correct,
                record.deviation_type
            ))

        player_color = PieceColor.BLACK if self.game.current_puzzle.black_to_move else PieceColor.RED
        player_moves = [m for m in self.game.move_history if m.move.color == player_color]
        correct_count = sum(1 for m in player_moves if m.is_correct)
        total_time = sum(m.time_taken for m in player_moves)
        avg_time = total_time / len(player_moves) if player_moves else 0

        error_types = {}
        for m in player_moves:
            if not m.is_correct and m.deviation_type:
                error_types[m.deviation_type] = error_types.get(m.deviation_type, 0) + 1

        analysis = {
            'total_steps': len(player_moves),
            'correct_count': correct_count,
            'avg_time': avg_time,
            'error_types': error_types
        }

        self.review_panel.load_review(move_list, analysis)
        self.review_panel.set_solution(self.game.get_solution_moves())

    def _update_stats_display(self):
        self.stats_panel.update_stats(self.stats)

    def _toggle_night_mode(self, enabled: bool):
        self.night_mode = enabled
        self.board_widget.set_night_mode(enabled)

        if enabled:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QFrame[frameShape="1"] {
                    background-color: #3a3a3a;
                    border: 1px solid #555555;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                }
                QTabBar::tab {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    padding: 8px 16px;
                }
                QTabBar::tab:selected {
                    background-color: #2b2b2b;
                }
                QListWidget {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
                QComboBox {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    padding: 4px;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QToolBar {
                    background-color: #3a3a3a;
                    border: none;
                }
                QMenuBar {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                }
                QMenuBar::item:selected {
                    background-color: #555555;
                }
                QMenu {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                }
                QMenu::item:selected {
                    background-color: #555555;
                }
            """)
        else:
            self.setStyleSheet("")

    def _toggle_large_pieces(self, enabled: bool):
        self.large_pieces = enabled
        self.board_widget.set_large_pieces(enabled)

    def _on_save_custom_puzzle(self):
        if self.game.current_puzzle is None:
            QMessageBox.warning(self, "提示", "请先选择一个残局")
            return

        name, ok = QInputDialog.getText(self, "保存残局", "请输入残局名称：")
        if not ok or not name:
            return

        grid = board_to_grid(self.game.board)
        custom_id = f"custom_{int(time.time())}"

        puzzle = Puzzle(
            id=custom_id,
            name=name,
            description="自定义残局",
            difficulty="中等",
            kill_type="自定义",
            steps=1,
            initial_board=grid,
            solution=[],
            black_to_move=(self.game.current_turn == PieceColor.BLACK)
        )

        add_custom_puzzle(puzzle)
        all_puzzles = get_all_puzzles() + get_custom_puzzles()
        self.puzzle_library.load_puzzles(all_puzzles)

        QMessageBox.information(self, "成功", "残局已保存到自定义题库")

    def _build_record_from_current(self) -> Optional['GameRecord']:
        from ..data.storage import GameRecord
        if self.game.current_puzzle is None or not self.game.move_history:
            return None

        move_strings = [r.move.to_chinese() for r in self.game.move_history]
        first_black = self.game.current_puzzle.black_to_move

        if self._current_record is not None:
            self._current_record.move_strings = move_strings
            self._current_record.first_color_black = first_black
            self._current_record.initial_board = self.game.current_puzzle.initial_board
            self._current_record.step_notes = dict(self._record_step_notes)
            return self._current_record

        return GameRecord(
            id=f"record_{int(time.time())}",
            name=self.game.current_puzzle.name,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            move_strings=move_strings,
            first_color_black=first_black,
            initial_board=self.game.current_puzzle.initial_board,
            notes="",
            tags=[],
            step_notes=dict(self._record_step_notes),
            step_deviations=dict(self._record_step_deviations),
            puzzle_id=self.game.current_puzzle.id
        )

    def _on_save_game_record(self):
        from ..data.storage import save_game_record, GameRecord

        if self.game.current_puzzle is None or not self.game.move_history:
            QMessageBox.warning(self, "提示", "没有可保存的对局记录，请先走几步棋")
            return

        if self._current_record is None:
            name, ok = QInputDialog.getText(
                self, "保存对局记录", "请输入对局名称：",
                text=self.game.current_puzzle.name
            )
            if not ok or not name:
                return
        else:
            name = self._current_record.name

        record = self._build_record_from_current()
        if record is None:
            return
        record.name = name

        save_game_record(record)
        self._current_record = record

        tag_info = ""
        if record.tags:
            tag_info = f"\n标签：{'、'.join(record.tags)}"

        QMessageBox.information(
            self, "成功",
            f"对局记录已保存：\n\n  名称：{record.name}\n  步数：{len(record.move_strings)} 步"
            f"{tag_info}\n  备注：{record.notes or '（无）'}\n\n可在题库中搜索此对局名称或标签查看。"
        )

    def _on_edit_record_info(self):
        from ..data.storage import save_game_record
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QLabel, QDialogButtonBox

        record = self._build_record_from_current()
        if record is None:
            QMessageBox.warning(self, "提示", "没有可编辑的对局记录，请先走几步棋或保存对局")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("编辑对局信息")
        dlg.setMinimumWidth(400)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel("对局名称："))
        name_edit = QLineEdit(record.name)
        layout.addWidget(name_edit)

        layout.addWidget(QLabel("标签（用空格或逗号分隔，如：中局 错招）："))
        tags_edit = QLineEdit(" ".join(record.tags))
        layout.addWidget(tags_edit)

        layout.addWidget(QLabel("整体备注："))
        notes_edit = QTextEdit(record.notes)
        notes_edit.setMinimumHeight(100)
        layout.addWidget(notes_edit)

        if self._record_step_notes:
            info = "当前已写心得的步数：" + "、".join(
                f"第{i+1}步" for i in sorted(self._record_step_notes.keys())
            )
            layout.addWidget(QLabel(info))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        if dlg.exec_() == QDialog.Accepted:
            record.name = name_edit.text().strip() or record.name
            tags_raw = tags_edit.text().replace(",", " ").replace("，", " ")
            record.tags = [t.strip() for t in tags_raw.split() if t.strip()]
            record.notes = notes_edit.toPlainText().strip()

            save_game_record(record)
            self._current_record = record

            tag_text = f"\n标签：{'、'.join(record.tags)}" if record.tags else ""
            note_text = f"\n备注：{record.notes[:30]}{'...' if len(record.notes) > 30 else ''}" if record.notes else ""
            QMessageBox.information(self, "已保存", f"对局信息已更新：{record.name}{tag_text}{note_text}")

    def _on_import_pgn(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入棋谱文本", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except Exception as e:
                QMessageBox.critical(
                    self, "导入失败",
                    f"无法读取文件：文件编码不是 UTF-8 或 GBK\n\n详细错误：{str(e)}"
                )
                return
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"读取文件出错：{str(e)}")
            return

        result = parse_pgn_text(content)

        if not result.success:
            help_text = (
                "\n\n支持的棋谱格式说明：\n"
                "  1. 中文记谱：每行一个走法，如 炮二平五、马8进7\n"
                "  2. 简写记谱：R2+5、C2=5、N8+7\n"
                "  3. 可加标签 [Name \"名称\"] [Puzzle \"1\"]\n"
                "  4. 自定义初始局面：[Board \"rnbakabnr/9/1c5c1/...\"]\n\n"
                "  红方：帅车马相仕炮兵 (中文数字 一二三四五六七八九)\n"
                "  黑方：将车马象士卒砲 (阿拉伯数字 1-9)"
            )
            QMessageBox.critical(self, "导入失败", result.error_message + help_text)
            return

        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QDialogButtonBox, QLabel

        choice_dialog = QDialog(self)
        choice_dialog.setWindowTitle("导入棋谱")
        dialog_layout = QVBoxLayout(choice_dialog)

        info_label = QLabel(
            f"成功解析棋谱：\n"
            f"  名称：{result.name or '未命名'}\n"
            f"  总步数：{len(result.moves)} 步\n"
            f"  初始局面：{'标准开局' if not result.name else '自定义局面'}\n\n"
            f"请选择导入方式："
        )
        info_label.setWordWrap(True)
        dialog_layout.addWidget(info_label)

        radio_review = QRadioButton("作为完整对局导入（可复盘走法）")
        radio_puzzle = QRadioButton("作为残局题库保存（红方招法为解法）")
        radio_review.setChecked(True)
        dialog_layout.addWidget(radio_review)
        dialog_layout.addWidget(radio_puzzle)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(choice_dialog.accept)
        btn_box.rejected.connect(choice_dialog.reject)
        dialog_layout.addWidget(btn_box)

        if choice_dialog.exec_() != QDialog.Accepted:
            return

        as_puzzle = radio_puzzle.isChecked()

        puzzle = self.game.load_imported_pgn(result, as_puzzle=as_puzzle)

        if as_puzzle:
            add_custom_puzzle(puzzle)
            all_puzzles = get_all_puzzles() + get_custom_puzzles()
            self.puzzle_library.load_puzzles(all_puzzles)
            QMessageBox.information(
                self, "导入成功",
                f"已保存到自定义题库：\n\n  {puzzle.name}\n  共 {len(puzzle.solution)} 步解法"
            )
        else:
            self._refresh_after_load(puzzle)
            QMessageBox.information(
                self, "导入成功",
                f"已加载对局，可在复盘面板中查看 {len(result.moves)} 步走法"
            )

    def _on_about(self):
        QMessageBox.about(
            self, "关于",
            "象棋残局训练 v1.0\n\n"
            "一款供象棋爱好者离线练习和复盘的残局训练软件\n\n"
            "功能：\n"
            "• 题库筛选（按杀法、难度、步数）\n"
            "• 拖拽走子，自动判断合法性\n"
            "• 将军、胜负提示\n"
            "• 逐步提示，扣除成绩\n"
            "• 撤回、重来功能\n"
            "• 标准解法变着展示\n"
            "• 自定义残局保存\n"
            "• 复盘分析每步得失\n"
            "• 学习成绩统计\n"
            "• 夜间模式、大棋子模式"
        )

    def closeEvent(self, event):
        save_stats(self.stats)
        event.accept()
