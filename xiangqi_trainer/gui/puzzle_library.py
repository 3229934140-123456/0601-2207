from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from typing import List, Optional

from ..data.puzzles import Puzzle, KILL_TYPES, DIFFICULTIES


class PuzzleLibrary(QWidget):
    puzzle_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._all_puzzles: List[Puzzle] = []
        self._filtered_puzzles: List[Puzzle] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title_label = QLabel("残局题库")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QVBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.setSpacing(8)

        kill_type_layout = QHBoxLayout()
        kill_type_label = QLabel("杀法类型：")
        kill_type_label.setFixedWidth(70)
        self.kill_type_combo = QComboBox()
        self.kill_type_combo.addItem("全部")
        self.kill_type_combo.currentIndexChanged.connect(self._on_filter_changed)
        kill_type_layout.addWidget(kill_type_label)
        kill_type_layout.addWidget(self.kill_type_combo)
        filter_layout.addLayout(kill_type_layout)

        difficulty_layout = QHBoxLayout()
        difficulty_label = QLabel("难度：")
        difficulty_label.setFixedWidth(70)
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItem("全部")
        self.difficulty_combo.currentIndexChanged.connect(self._on_filter_changed)
        difficulty_layout.addWidget(difficulty_label)
        difficulty_layout.addWidget(self.difficulty_combo)
        filter_layout.addLayout(difficulty_layout)

        steps_layout = QHBoxLayout()
        steps_label = QLabel("步数：")
        steps_label.setFixedWidth(70)
        self.steps_combo = QComboBox()
        self._steps_options = [("全部", None, None)]
        self.steps_combo.addItem("全部")
        self.steps_combo.currentIndexChanged.connect(self._on_filter_changed)
        steps_layout.addWidget(steps_label)
        steps_layout.addWidget(self.steps_combo)
        filter_layout.addLayout(steps_layout)

        layout.addWidget(filter_frame)

        list_label = QLabel("残局列表：")
        list_label_font = QFont()
        list_label_font.setBold(True)
        list_label.setFont(list_label_font)
        layout.addWidget(list_label)

        self.puzzle_list = QListWidget()
        self.puzzle_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.puzzle_list, 1)

        self.count_label = QLabel("共 0 个残局")
        self.count_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.count_label)

    def load_puzzles(self, puzzles_list: List[Puzzle]):
        self._all_puzzles = puzzles_list
        self._refresh_filter_options()
        self._apply_filters()

    def _refresh_filter_options(self):
        """根据实际残局数据动态生成筛选项，避免空筛选"""
        kill_types = set()
        difficulties = set()
        steps_set = set()

        for puzzle in self._all_puzzles:
            if puzzle.kill_type:
                kill_types.add(puzzle.kill_type)
            if puzzle.difficulty:
                difficulties.add(puzzle.difficulty)
            if hasattr(puzzle, 'steps') and puzzle.steps:
                steps_set.add(puzzle.steps)
            elif hasattr(puzzle, 'min_steps') and puzzle.min_steps:
                steps_set.add(puzzle.min_steps)

        current_kill = self.kill_type_combo.currentText()
        self.kill_type_combo.blockSignals(True)
        self.kill_type_combo.clear()
        self.kill_type_combo.addItem("全部")
        for kt in sorted(kill_types, key=lambda x: KILL_TYPES.index(x) if x in KILL_TYPES else 999):
            self.kill_type_combo.addItem(kt)
        idx = self.kill_type_combo.findText(current_kill)
        self.kill_type_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.kill_type_combo.blockSignals(False)

        current_diff = self.difficulty_combo.currentText()
        self.difficulty_combo.blockSignals(True)
        self.difficulty_combo.clear()
        self.difficulty_combo.addItem("全部")
        for d in sorted(difficulties, key=lambda x: DIFFICULTIES.index(x) if x in DIFFICULTIES else 999):
            self.difficulty_combo.addItem(d)
        idx = self.difficulty_combo.findText(current_diff)
        self.difficulty_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.difficulty_combo.blockSignals(False)

        current_steps_idx = self.steps_combo.currentIndex()
        self.steps_combo.blockSignals(True)
        self.steps_combo.clear()
        self._steps_options = [("全部", None, None)]
        self.steps_combo.addItem("全部")
        for s in sorted(steps_set):
            self._steps_options.append((f"{s}步", s, s))
            self.steps_combo.addItem(f"{s}步")
        if current_steps_idx >= 0 and current_steps_idx < len(self._steps_options):
            self.steps_combo.setCurrentIndex(current_steps_idx)
        else:
            self.steps_combo.setCurrentIndex(0)
        self.steps_combo.blockSignals(False)

    def set_filter(
        self,
        kill_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        min_steps: Optional[int] = None,
        max_steps: Optional[int] = None
    ):
        if kill_type is not None:
            idx = self.kill_type_combo.findText(kill_type)
            if idx >= 0:
                self.kill_type_combo.setCurrentIndex(idx)
            else:
                self.kill_type_combo.setCurrentIndex(0)

        if difficulty is not None:
            idx = self.difficulty_combo.findText(difficulty)
            if idx >= 0:
                self.difficulty_combo.setCurrentIndex(idx)
            else:
                self.difficulty_combo.setCurrentIndex(0)

        if min_steps is not None and max_steps is not None:
            found = False
            for i, (label, mn, mx) in enumerate(self._steps_options):
                if mn == min_steps and mx == max_steps:
                    self.steps_combo.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.steps_combo.setCurrentIndex(0)
        else:
            self.steps_combo.setCurrentIndex(0)

    def _on_filter_changed(self):
        self._apply_filters()

    def _apply_filters(self):
        kill_type_text = self.kill_type_combo.currentText()
        difficulty_text = self.difficulty_combo.currentText()
        steps_idx = self.steps_combo.currentIndex()
        _, min_steps, max_steps = self._steps_options[steps_idx]

        self._filtered_puzzles = []
        for puzzle in self._all_puzzles:
            if kill_type_text != "全部" and puzzle.kill_type != kill_type_text:
                continue
            if difficulty_text != "全部" and puzzle.difficulty != difficulty_text:
                continue
            if min_steps is not None and max_steps is not None:
                puzzle_steps = getattr(puzzle, 'steps', None)
                if puzzle_steps is None:
                    puzzle_min = getattr(puzzle, 'min_steps', 1)
                    puzzle_max = getattr(puzzle, 'max_steps', 99)
                    if puzzle_max < min_steps or puzzle_min > max_steps:
                        continue
                else:
                    if puzzle_steps < min_steps or puzzle_steps > max_steps:
                        continue
            self._filtered_puzzles.append(puzzle)

        self._refresh_list()

    def _refresh_list(self):
        self.puzzle_list.clear()

        for puzzle in self._filtered_puzzles:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, puzzle.id)

            difficulty_color = {
                "简单": "#2ecc71",
                "中等": "#f39c12",
                "困难": "#e74c3c",
            }.get(puzzle.difficulty, "#333333")

            puzzle_steps = getattr(puzzle, 'steps', None)
            if puzzle_steps is None:
                min_s = getattr(puzzle, 'min_steps', 1)
                max_s = getattr(puzzle, 'max_steps', 1)
                steps_str = f"{min_s}-{max_s}步" if min_s != max_s else f"{min_s}步"
            else:
                steps_str = f"{puzzle_steps}步"

            widget_item = QWidget()
            widget_layout = QVBoxLayout(widget_item)
            widget_layout.setContentsMargins(8, 6, 8, 6)
            widget_layout.setSpacing(2)

            name_label = QLabel(puzzle.name)
            name_font = QFont()
            name_font.setBold(True)
            name_font.setPointSize(10)
            name_label.setFont(name_font)
            widget_layout.addWidget(name_label)

            info_label = QLabel()
            info_label.setTextFormat(Qt.RichText)
            info_text = (
                f"难度：<span style='color:{difficulty_color};font-weight:bold;'>{puzzle.difficulty}</span>"
                f"&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"步数：{steps_str}"
                f"&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"类型：{puzzle.kill_type}"
            )
            info_label.setText(info_text)
            info_label.setStyleSheet("color: #666666; font-size: 12px;")
            widget_layout.addWidget(info_label)

            self.puzzle_list.addItem(item)
            self.puzzle_list.setItemWidget(item, widget_item)
            item.setSizeHint(widget_item.sizeHint())

        self.count_label.setText(f"共 {len(self._filtered_puzzles)} 个残局")

    def _on_item_double_clicked(self, item: QListWidgetItem):
        puzzle_id = item.data(Qt.UserRole)
        if puzzle_id:
            self.puzzle_selected.emit(puzzle_id)
