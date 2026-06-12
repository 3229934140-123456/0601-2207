from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QListWidget, QListWidgetItem, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from typing import Optional, List, Tuple

from ..data.storage import Statistics, BestRecord


class BarChartWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._data: List[Tuple[str, int]] = []
        self.setMinimumHeight(160)

    def set_data(self, data: List[Tuple[str, int]]):
        self._data = data
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        padding_left = 10
        padding_right = 10
        padding_top = 20
        padding_bottom = 30

        chart_width = width - padding_left - padding_right
        chart_height = height - padding_top - padding_bottom

        if not self._data:
            painter.setPen(QColor("#999999"))
            painter.drawText(
                QRect(padding_left, padding_top, chart_width, chart_height),
                Qt.AlignCenter,
                "暂无数据"
            )
            return

        max_value = max(v for _, v in self._data) if self._data else 1
        if max_value == 0:
            max_value = 1

        bar_count = len(self._data)
        bar_spacing = 8
        bar_width = (chart_width - bar_spacing * (bar_count - 1)) / bar_count
        bar_width = min(bar_width, 50)

        colors = [
            QColor("#e74c3c"), QColor("#e67e22"), QColor("#f39c12"),
            QColor("#f1c40f"), QColor("#2ecc71")
        ]

        for i, (label, value) in enumerate(self._data):
            bar_height = (value / max_value) * (chart_height - 20)
            bar_height = max(bar_height, 2)

            x = padding_left + i * (bar_width + bar_spacing)
            y = padding_top + chart_height - bar_height

            color = colors[i % len(colors)]
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 1))
            painter.drawRoundedRect(
                int(x), int(y), int(bar_width), int(bar_height), 4, 4
            )

            painter.setPen(QColor("#333333"))
            value_font = QFont()
            value_font.setPixelSize(11)
            value_font.setBold(True)
            painter.setFont(value_font)
            value_rect = QRect(
                int(x), int(y) - 18, int(bar_width), 16
            )
            painter.drawText(value_rect, Qt.AlignCenter, str(value))

            painter.setPen(QColor("#666666"))
            label_font = QFont()
            label_font.setPixelSize(11)
            painter.setFont(label_font)
            label_rect = QRect(
                int(x) - 10, int(padding_top + chart_height), int(bar_width) + 20, 20
            )
            painter.drawText(label_rect, Qt.AlignCenter, label)


class StatsPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._stats = Statistics()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        title_label = QLabel("学习成绩")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.StyledPanel)
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(12, 12, 12, 12)
        stats_layout.setHorizontalSpacing(15)
        stats_layout.setVerticalSpacing(10)

        total_label = QLabel("总完成题数")
        total_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.total_value = QLabel("0")
        total_value_font = QFont()
        total_value_font.setPointSize(18)
        total_value_font.setBold(True)
        self.total_value.setFont(total_value_font)
        self.total_value.setStyleSheet("color: #2c3e50;")
        stats_layout.addWidget(total_label, 0, 0)
        stats_layout.addWidget(self.total_value, 1, 0)

        accuracy_label = QLabel("正确率")
        accuracy_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.accuracy_value = QLabel("0%")
        accuracy_value_font = QFont()
        accuracy_value_font.setPointSize(18)
        accuracy_value_font.setBold(True)
        self.accuracy_value.setFont(accuracy_value_font)
        self.accuracy_value.setStyleSheet("color: #27ae60;")
        stats_layout.addWidget(accuracy_label, 0, 1)
        stats_layout.addWidget(self.accuracy_value, 1, 1)

        streak_label = QLabel("连续天数")
        streak_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.streak_value = QLabel("0天")
        streak_value_font = QFont()
        streak_value_font.setPointSize(24)
        streak_value_font.setBold(True)
        self.streak_value.setFont(streak_value_font)
        self.streak_value.setStyleSheet("color: #e74c3c;")
        stats_layout.addWidget(streak_label, 2, 0)
        stats_layout.addWidget(self.streak_value, 3, 0, 1, 2, Qt.AlignCenter)

        main_layout.addWidget(stats_frame)

        error_title = QLabel("常错类型（前5名）")
        error_title_font = QFont()
        error_title_font.setBold(True)
        error_title.setFont(error_title_font)
        main_layout.addWidget(error_title)

        error_frame = QFrame()
        error_frame.setFrameShape(QFrame.StyledPanel)
        error_layout = QVBoxLayout(error_frame)
        error_layout.setContentsMargins(8, 8, 8, 8)

        self.bar_chart = BarChartWidget()
        error_layout.addWidget(self.bar_chart)

        main_layout.addWidget(error_frame)

        best_title = QLabel("最佳记录")
        best_title_font = QFont()
        best_title_font.setBold(True)
        best_title.setFont(best_title_font)
        main_layout.addWidget(best_title)

        best_frame = QFrame()
        best_frame.setFrameShape(QFrame.StyledPanel)
        best_layout = QVBoxLayout(best_frame)
        best_layout.setContentsMargins(0, 0, 0, 0)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 8, 10, 8)
        header_layout.setSpacing(10)

        name_header = QLabel("残局名称")
        name_header.setStyleSheet("font-weight: bold; color: #333;")
        name_header.setMinimumWidth(120)
        steps_header = QLabel("最佳步数")
        steps_header.setStyleSheet("font-weight: bold; color: #333;")
        steps_header.setAlignment(Qt.AlignCenter)
        steps_header.setFixedWidth(70)
        time_header = QLabel("用时")
        time_header.setStyleSheet("font-weight: bold; color: #333;")
        time_header.setAlignment(Qt.AlignCenter)
        time_header.setFixedWidth(70)
        hints_header = QLabel("提示")
        hints_header.setStyleSheet("font-weight: bold; color: #333;")
        hints_header.setAlignment(Qt.AlignCenter)
        hints_header.setFixedWidth(50)

        header_layout.addWidget(name_header)
        header_layout.addWidget(steps_header)
        header_layout.addWidget(time_header)
        header_layout.addWidget(hints_header)
        best_layout.addWidget(header_widget)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        best_layout.addWidget(line)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.best_list = QListWidget()
        self.best_list.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self.best_list)

        best_layout.addWidget(scroll, 1)

        main_layout.addWidget(best_frame, 1)

    def update_stats(self, stats_obj: Statistics):
        self._stats = stats_obj
        self._update_display()

    def _update_display(self):
        stats = self._stats

        self.total_value.setText(str(stats.total_puzzles))

        if stats.total_puzzles > 0:
            accuracy = (stats.correct_count / stats.total_puzzles) * 100
            self.accuracy_value.setText(f"{accuracy:.1f}%")
        else:
            self.accuracy_value.setText("0%")

        self.streak_value.setText(f"{stats.streak_days}天")

        self._update_error_chart()
        self._update_best_records()

    def _update_error_chart(self):
        error_types = self._stats.error_types
        sorted_items = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        top5 = sorted_items[:5]
        self.bar_chart.set_data(top5)

    def _update_best_records(self):
        self.best_list.clear()

        best_records = self._stats.best_records
        sorted_records = sorted(best_records.items())

        if not sorted_records:
            item = QListWidgetItem("暂无最佳记录")
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor("#999999"))
            self.best_list.addItem(item)
            return

        for puzzle_id, record in sorted_records:
            self._add_best_record_item(puzzle_id, record)

    def _add_best_record_item(self, puzzle_id: str, record: BestRecord):
        item = QListWidgetItem()
        item.setData(Qt.UserRole, puzzle_id)

        widget_item = QWidget()
        widget_layout = QHBoxLayout(widget_item)
        widget_layout.setContentsMargins(10, 6, 10, 6)
        widget_layout.setSpacing(10)

        name_label = QLabel(puzzle_id)
        name_label.setStyleSheet("color: #333; font-size: 13px;")
        name_label.setMinimumWidth(120)
        name_label.setWordWrap(True)
        widget_layout.addWidget(name_label)

        steps_label = QLabel(str(record.steps))
        steps_label.setAlignment(Qt.AlignCenter)
        steps_label.setStyleSheet(
            "color: #27ae60; font-weight: bold; font-size: 13px;"
        )
        steps_label.setFixedWidth(70)
        widget_layout.addWidget(steps_label)

        time_str = self._format_time(record.time)
        time_label = QLabel(time_str)
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setStyleSheet("color: #2980b9; font-size: 13px;")
        time_label.setFixedWidth(70)
        widget_layout.addWidget(time_label)

        hints_label = QLabel(str(record.hints_used))
        hints_label.setAlignment(Qt.AlignCenter)
        hints_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        hints_label.setFixedWidth(50)
        widget_layout.addWidget(hints_label)

        self.best_list.addItem(item)
        self.best_list.setItemWidget(item, widget_item)
        item.setSizeHint(widget_item.sizeHint())

    def _format_time(self, seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.1f}秒"
        else:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}分{secs:.0f}秒"
