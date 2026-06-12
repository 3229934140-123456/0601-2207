from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QScrollArea,
    QSpinBox, QToolButton, QSizePolicy, QGridLayout
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from typing import Optional, List, Tuple, Dict


class ReviewPanel(QWidget):
    step_changed = pyqtSignal(int)
    review_closed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._move_list: List[Tuple[str, bool, str]] = []
        self._current_step = -1
        self._solution: List[str] = []
        self._solution_expanded = True
        self._analysis: Dict = {}
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        title_layout = QHBoxLayout()
        title_label = QLabel("复盘分析")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.close_button = QPushButton("关闭")
        self.close_button.setFixedWidth(60)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.close_button.clicked.connect(self._on_close_clicked)
        title_layout.addWidget(self.close_button)
        main_layout.addLayout(title_layout)

        analysis_frame = QFrame()
        analysis_frame.setFrameShape(QFrame.StyledPanel)
        analysis_layout = QGridLayout(analysis_frame)
        analysis_layout.setContentsMargins(10, 10, 10, 10)
        analysis_layout.setHorizontalSpacing(15)
        analysis_layout.setVerticalSpacing(8)

        accuracy_label = QLabel("正确率")
        accuracy_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.accuracy_value = QLabel("0%")
        accuracy_value_font = QFont()
        accuracy_value_font.setPointSize(18)
        accuracy_value_font.setBold(True)
        self.accuracy_value.setFont(accuracy_value_font)
        self.accuracy_value.setStyleSheet("color: #27ae60;")
        analysis_layout.addWidget(accuracy_label, 0, 0)
        analysis_layout.addWidget(self.accuracy_value, 1, 0)

        total_steps_label = QLabel("总步数")
        total_steps_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.total_steps_value = QLabel("0")
        total_steps_value_font = QFont()
        total_steps_value_font.setPointSize(18)
        total_steps_value_font.setBold(True)
        self.total_steps_value.setFont(total_steps_value_font)
        self.total_steps_value.setStyleSheet("color: #2980b9;")
        analysis_layout.addWidget(total_steps_label, 0, 1)
        analysis_layout.addWidget(self.total_steps_value, 1, 1)

        avg_time_label = QLabel("平均用时")
        avg_time_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.avg_time_value = QLabel("0秒")
        avg_time_value_font = QFont()
        avg_time_value_font.setPointSize(18)
        avg_time_value_font.setBold(True)
        self.avg_time_value.setFont(avg_time_value_font)
        self.avg_time_value.setStyleSheet("color: #9b59b6;")
        analysis_layout.addWidget(avg_time_label, 0, 2)
        analysis_layout.addWidget(self.avg_time_value, 1, 2)

        main_layout.addWidget(analysis_frame)

        error_types_frame = QFrame()
        error_types_frame.setFrameShape(QFrame.StyledPanel)
        error_types_layout = QVBoxLayout(error_types_frame)
        error_types_layout.setContentsMargins(10, 8, 10, 8)
        error_types_layout.setSpacing(4)

        error_types_title = QLabel("错误类型统计")
        error_types_title.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        error_types_layout.addWidget(error_types_title)

        self.error_types_content = QLabel("暂无数据")
        self.error_types_content.setStyleSheet("color: #999999; font-size: 12px;")
        self.error_types_content.setWordWrap(True)
        error_types_layout.addWidget(self.error_types_content)

        main_layout.addWidget(error_types_frame)

        moves_frame = QFrame()
        moves_frame.setFrameShape(QFrame.StyledPanel)
        moves_layout = QVBoxLayout(moves_frame)
        moves_layout.setContentsMargins(0, 0, 0, 0)
        moves_layout.setSpacing(0)

        moves_header = QWidget()
        moves_header_layout = QHBoxLayout(moves_header)
        moves_header_layout.setContentsMargins(10, 8, 10, 8)
        moves_header_layout.setSpacing(10)

        moves_title = QLabel("走法列表")
        moves_title.setStyleSheet("font-weight: bold; color: #333;")
        moves_header_layout.addWidget(moves_title)
        moves_header_layout.addStretch()

        self.step_info_label = QLabel("0 / 0")
        self.step_info_label.setStyleSheet("color: #666666; font-size: 12px;")
        moves_header_layout.addWidget(self.step_info_label)

        moves_layout.addWidget(moves_header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        moves_layout.addWidget(line)

        self.move_list_widget = QListWidget()
        self.move_list_widget.setFrameShape(QFrame.NoFrame)
        self.move_list_widget.itemClicked.connect(self._on_item_clicked)
        moves_layout.addWidget(self.move_list_widget, 1)

        main_layout.addWidget(moves_frame, 1)

        nav_frame = QFrame()
        nav_frame.setFrameShape(QFrame.NoFrame)
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(6)

        self.prev_button = QPushButton("◀ 上一步")
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.prev_button.clicked.connect(self._on_prev_clicked)
        nav_layout.addWidget(self.prev_button)

        nav_layout.addStretch()

        jump_label = QLabel("跳转到：")
        jump_label.setStyleSheet("color: #666666; font-size: 12px;")
        nav_layout.addWidget(jump_label)

        self.jump_spin = QSpinBox()
        self.jump_spin.setRange(1, 1)
        self.jump_spin.setFixedWidth(60)
        self.jump_spin.valueChanged.connect(self._on_jump_changed)
        nav_layout.addWidget(self.jump_spin)

        step_label = QLabel("步")
        step_label.setStyleSheet("color: #666666; font-size: 12px;")
        nav_layout.addWidget(step_label)

        nav_layout.addStretch()

        self.next_button = QPushButton("下一步 ▶")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.next_button.clicked.connect(self._on_next_clicked)
        nav_layout.addWidget(self.next_button)

        main_layout.addWidget(nav_frame)

        solution_frame = QFrame()
        solution_frame.setFrameShape(QFrame.StyledPanel)
        solution_layout = QVBoxLayout(solution_frame)
        solution_layout.setContentsMargins(10, 8, 10, 8)
        solution_layout.setSpacing(6)

        solution_header = QHBoxLayout()
        solution_title = QLabel("标准解法")
        solution_title.setStyleSheet("font-weight: bold; color: #333;")
        solution_header.addWidget(solution_title)
        solution_header.addStretch()

        self.toggle_solution_btn = QToolButton()
        self.toggle_solution_btn.setText("收起 ▲")
        self.toggle_solution_btn.setStyleSheet("""
            QToolButton {
                color: #2980b9;
                border: none;
                font-size: 12px;
                padding: 2px 6px;
            }
            QToolButton:hover {
                color: #1f618d;
            }
        """)
        self.toggle_solution_btn.clicked.connect(self._toggle_solution)
        solution_header.addWidget(self.toggle_solution_btn)
        solution_layout.addLayout(solution_header)

        self.solution_scroll = QScrollArea()
        self.solution_scroll.setWidgetResizable(True)
        self.solution_scroll.setFrameShape(QFrame.NoFrame)
        self.solution_scroll.setMaximumHeight(120)

        self.solution_content = QWidget()
        self.solution_content_layout = QVBoxLayout(self.solution_content)
        self.solution_content_layout.setContentsMargins(4, 4, 4, 4)
        self.solution_content_layout.setSpacing(2)

        self.solution_scroll.setWidget(self.solution_content)
        solution_layout.addWidget(self.solution_scroll)

        main_layout.addWidget(solution_frame)

    def load_review(self, move_list: List[Tuple[str, bool, str]], analysis: Dict):
        self._move_list = move_list
        self._analysis = analysis
        self._current_step = -1
        self._refresh_move_list()
        self._refresh_analysis()
        self._update_nav_buttons()
        self._update_step_info()

        total_steps = analysis.get('total_steps', len(move_list))
        self.jump_spin.setRange(1, max(1, total_steps))
        self.jump_spin.setValue(1)

    def set_current_step(self, index: int):
        if 0 <= index < len(self._move_list):
            self._current_step = index
            self._highlight_current_step()
            self._update_nav_buttons()
            self._update_step_info()
            self.jump_spin.blockSignals(True)
            self.jump_spin.setValue(index + 1)
            self.jump_spin.blockSignals(False)
            self.step_changed.emit(index)

    def set_solution(self, solution_list: List[str]):
        self._solution = solution_list
        self._refresh_solution()

    def _refresh_move_list(self):
        self.move_list_widget.clear()
        for i, (move_chinese, is_correct, deviation_type) in enumerate(self._move_list):
            self._add_move_item(i, move_chinese, is_correct, deviation_type)

    def _add_move_item(self, index: int, move_chinese: str, is_correct: bool, deviation_type: str):
        item = QListWidgetItem()
        item.setData(Qt.UserRole, index)

        widget_item = QWidget()
        widget_layout = QHBoxLayout(widget_item)
        widget_layout.setContentsMargins(10, 6, 10, 6)
        widget_layout.setSpacing(10)

        step_num_label = QLabel(f"第{index + 1}步")
        step_num_label.setFixedWidth(50)
        step_num_label.setStyleSheet("color: #666666; font-size: 12px;")
        widget_layout.addWidget(step_num_label)

        move_label = QLabel(move_chinese)
        move_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold;")
        widget_layout.addWidget(move_label, 1)

        status_label = QLabel()
        status_label.setFixedWidth(30)
        status_label.setAlignment(Qt.AlignCenter)
        if is_correct:
            status_label.setText("✓")
            status_label.setStyleSheet("color: #27ae60; font-size: 16px; font-weight: bold;")
        elif deviation_type == "deviation":
            status_label.setText("⚠")
            status_label.setStyleSheet("color: #f39c12; font-size: 16px; font-weight: bold;")
        else:
            status_label.setText("✗")
            status_label.setStyleSheet("color: #e74c3c; font-size: 16px; font-weight: bold;")
        widget_layout.addWidget(status_label)

        self.move_list_widget.addItem(item)
        self.move_list_widget.setItemWidget(item, widget_item)
        item.setSizeHint(widget_item.sizeHint())

    def _highlight_current_step(self):
        if self._current_step >= 0:
            self.move_list_widget.setCurrentRow(self._current_step)
            self.move_list_widget.scrollToItem(
                self.move_list_widget.currentItem(),
                QListWidget.PositionAtCenter
            )

    def _refresh_analysis(self):
        total_steps = self._analysis.get('total_steps', len(self._move_list))
        correct_count = self._analysis.get('correct_count', 0)
        avg_time = self._analysis.get('avg_time', 0.0)
        error_types = self._analysis.get('error_types', {})

        self.total_steps_value.setText(str(total_steps))

        if total_steps > 0:
            accuracy = (correct_count / total_steps) * 100
            self.accuracy_value.setText(f"{accuracy:.1f}%")
        else:
            self.accuracy_value.setText("0%")

        if avg_time < 60:
            self.avg_time_value.setText(f"{avg_time:.1f}秒")
        else:
            minutes = int(avg_time // 60)
            secs = avg_time % 60
            self.avg_time_value.setText(f"{minutes}分{secs:.0f}秒")

        if error_types:
            error_text = ""
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                error_text += f"• {error_type}：{count}次　　"
            self.error_types_content.setText(error_text.strip())
            self.error_types_content.setStyleSheet("color: #333333; font-size: 12px;")
        else:
            self.error_types_content.setText("暂无错误记录")
            self.error_types_content.setStyleSheet("color: #999999; font-size: 12px;")

    def _refresh_solution(self):
        for i in reversed(range(self.solution_content_layout.count())):
            widget = self.solution_content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self._solution:
            label = QLabel("暂无标准解法")
            label.setStyleSheet("color: #999999; font-size: 12px;")
            self.solution_content_layout.addWidget(label)
            return

        for i, move in enumerate(self._solution):
            move_label = QLabel(f"第{i + 1}步：{move}")
            move_label.setStyleSheet("color: #2c3e50; font-size: 12px;")
            self.solution_content_layout.addWidget(move_label)

    def _toggle_solution(self):
        self._solution_expanded = not self._solution_expanded
        if self._solution_expanded:
            self.solution_scroll.show()
            self.toggle_solution_btn.setText("收起 ▲")
        else:
            self.solution_scroll.hide()
            self.toggle_solution_btn.setText("展开 ▼")

    def _on_item_clicked(self, item: QListWidgetItem):
        index = item.data(Qt.UserRole)
        if index is not None:
            self.set_current_step(index)

    def _on_prev_clicked(self):
        if self._current_step > 0:
            self.set_current_step(self._current_step - 1)

    def _on_next_clicked(self):
        if self._current_step < len(self._move_list) - 1:
            self.set_current_step(self._current_step + 1)

    def _on_jump_changed(self, value: int):
        self.set_current_step(value - 1)

    def _on_close_clicked(self):
        self.review_closed.emit()

    def _update_nav_buttons(self):
        self.prev_button.setEnabled(self._current_step > 0)
        self.next_button.setEnabled(self._current_step < len(self._move_list) - 1)

    def _update_step_info(self):
        total = len(self._move_list)
        current = self._current_step + 1 if self._current_step >= 0 else 0
        self.step_info_label.setText(f"{current} / {total}")
