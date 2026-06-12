from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from typing import Optional


HINT_POINTS = [10, 20, 30]
MAX_HINT_LEVEL = 3


class HintPanel(QWidget):
    hint_requested = pyqtSignal(int)
    hint_used = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_level = 0
        self._score = 100
        self._hints_used = 0
        self._hint_texts = ["", "", ""]
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        title_label = QLabel("提示")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(8)

        score_layout = QHBoxLayout()
        score_label = QLabel("当前分数：")
        score_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.score_value = QLabel("100")
        score_value_font = QFont()
        score_value_font.setPointSize(16)
        score_value_font.setBold(True)
        self.score_value.setFont(score_value_font)
        self.score_value.setStyleSheet("color: #27ae60;")
        score_layout.addWidget(score_label)
        score_layout.addWidget(self.score_value)
        score_layout.addStretch()
        info_layout.addLayout(score_layout)

        hints_layout = QHBoxLayout()
        hints_label = QLabel("已用提示：")
        hints_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.hints_value = QLabel("0 次")
        self.hints_value.setStyleSheet("color: #e67e22; font-size: 13px; font-weight: bold;")
        hints_layout.addWidget(hints_label)
        hints_layout.addWidget(self.hints_value)
        hints_layout.addStretch()
        info_layout.addLayout(hints_layout)

        main_layout.addWidget(info_frame)

        level_frame = QFrame()
        level_frame.setFrameShape(QFrame.StyledPanel)
        level_layout = QVBoxLayout(level_frame)
        level_layout.setContentsMargins(10, 10, 10, 10)
        level_layout.setSpacing(8)

        level_title_layout = QHBoxLayout()
        level_title_label = QLabel("提示等级")
        level_title_label.setStyleSheet("font-weight: bold; color: #333;")
        level_title_layout.addWidget(level_title_label)
        level_title_layout.addStretch()
        self.level_label = QLabel("第 0 / 3 级")
        self.level_label.setStyleSheet("color: #2980b9; font-weight: bold;")
        level_title_layout.addWidget(self.level_label)
        level_layout.addLayout(level_title_layout)

        self.level_progress = QProgressBar()
        self.level_progress.setRange(0, MAX_HINT_LEVEL)
        self.level_progress.setValue(0)
        self.level_progress.setTextVisible(False)
        self.level_progress.setFixedHeight(8)
        self.level_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        level_layout.addWidget(self.level_progress)

        self.hint_display = QLabel("点击下方按钮获取提示")
        self.hint_display.setAlignment(Qt.AlignCenter)
        self.hint_display.setWordWrap(True)
        self.hint_display.setMinimumHeight(60)
        self.hint_display.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px dashed #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                color: #7f8c8d;
                font-size: 13px;
            }
        """)
        level_layout.addWidget(self.hint_display)

        main_layout.addWidget(level_frame)

        cost_frame = QFrame()
        cost_frame.setFrameShape(QFrame.StyledPanel)
        cost_layout = QVBoxLayout(cost_frame)
        cost_layout.setContentsMargins(10, 8, 10, 8)
        cost_layout.setSpacing(4)

        cost_title = QLabel("提示消耗")
        cost_title.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        cost_layout.addWidget(cost_title)

        cost_items_layout = QHBoxLayout()
        cost_items_layout.setSpacing(6)
        for i, points in enumerate(HINT_POINTS):
            cost_item = QFrame()
            cost_item.setStyleSheet("""
                QFrame {
                    background-color: #fef9e7;
                    border: 1px solid #f1c40f;
                    border-radius: 4px;
                }
            """)
            item_layout = QVBoxLayout(cost_item)
            item_layout.setContentsMargins(6, 4, 6, 4)
            item_layout.setSpacing(2)

            level_tag = QLabel(f"第{i+1}级")
            level_tag.setAlignment(Qt.AlignCenter)
            level_tag.setStyleSheet("color: #b7950b; font-size: 11px; font-weight: bold;")
            item_layout.addWidget(level_tag)

            points_tag = QLabel(f"-{points}分")
            points_tag.setAlignment(Qt.AlignCenter)
            points_tag.setStyleSheet("color: #e74c3c; font-size: 12px; font-weight: bold;")
            item_layout.addWidget(points_tag)

            cost_items_layout.addWidget(cost_item)

        cost_layout.addLayout(cost_items_layout)
        main_layout.addWidget(cost_frame)

        self.hint_button = QPushButton("获取提示")
        self.hint_button.setMinimumHeight(40)
        self.hint_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
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
        self.hint_button.clicked.connect(self._on_hint_clicked)
        main_layout.addWidget(self.hint_button)

        main_layout.addStretch()

    def _on_hint_clicked(self):
        if self._current_level >= MAX_HINT_LEVEL:
            return

        next_level = self._current_level + 1
        points_deducted = HINT_POINTS[next_level - 1]

        if self._score < points_deducted:
            self.hint_display.setText("分数不足，无法获取提示")
            self.hint_display.setStyleSheet("""
                QLabel {
                    background-color: #fdedec;
                    border: 1px dashed #e74c3c;
                    border-radius: 6px;
                    padding: 10px;
                    color: #c0392b;
                    font-size: 13px;
                }
            """)
            return

        self.hint_requested.emit(next_level)

    def set_hint_text(self, text: str, level: int):
        if 1 <= level <= MAX_HINT_LEVEL:
            self._hint_texts[level - 1] = text

        if level > self._current_level:
            self._current_level = level
            self._update_display()

    def set_score(self, score: int):
        self._score = score
        self._update_score_display()

    def set_hints_used(self, count: int):
        self._hints_used = count
        self.hints_value.setText(f"{count} 次")

    def reset(self):
        self._current_level = 0
        self._hint_texts = ["", "", ""]
        self._update_display()
        self.hint_button.setEnabled(True)

    def _update_display(self):
        self.level_label.setText(f"第 {self._current_level} / {MAX_HINT_LEVEL} 级")
        self.level_progress.setValue(self._current_level)

        if self._current_level == 0:
            self.hint_display.setText("点击下方按钮获取提示")
            self.hint_display.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 1px dashed #bdc3c7;
                    border-radius: 6px;
                    padding: 10px;
                    color: #7f8c8d;
                    font-size: 13px;
                }
            """)
            self.hint_button.setText("获取提示")
        else:
            hint_text = self._hint_texts[self._current_level - 1]
            self.hint_display.setText(hint_text)
            self.hint_display.setStyleSheet("""
                QLabel {
                    background-color: #eafaf1;
                    border: 1px solid #27ae60;
                    border-radius: 6px;
                    padding: 10px;
                    color: #1e8449;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)

            if self._current_level >= MAX_HINT_LEVEL:
                self.hint_button.setText("已达最高提示等级")
                self.hint_button.setEnabled(False)
            else:
                next_points = HINT_POINTS[self._current_level]
                self.hint_button.setText(f"获取第{self._current_level + 1}级提示（-{next_points}分）")

    def _update_score_display(self):
        self.score_value.setText(str(self._score))
        if self._score >= 80:
            self.score_value.setStyleSheet("color: #27ae60;")
        elif self._score >= 50:
            self.score_value.setStyleSheet("color: #f39c12;")
        else:
            self.score_value.setStyleSheet("color: #e74c3c;")

    def use_hint(self, level: int, text: str):
        points_deducted = HINT_POINTS[level - 1]
        self._score -= points_deducted
        self._hints_used += 1

        self.set_hint_text(text, level)
        self._update_score_display()
        self.hints_value.setText(f"{self._hints_used} 次")

        self.hint_used.emit(points_deducted)
