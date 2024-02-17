from __future__ import annotations

from aqt.main import AnkiQt
from aqt.qt import *
from aqt.sound import av_player
from aqt.utils import showText

from ..consts import consts
from ..providers.tasklist import TranscriptionTask, tasklist
from .dialog import Dialog


class TaskWidgetIcon(QPushButton):
    def __init__(self, icon: QIcon, parent: QWidget):
        super().__init__(parent)
        self.setIcon(icon)
        self.setMaximumSize(32, 32)
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class TaskActionsWidget(QWidget):
    def __init__(
        self,
        task: TranscriptionTask,
        item: QTableWidgetItem,
        table_widget: QTableWidget,
    ):
        super().__init__(table_widget)
        self.setFixedWidth(75)
        self.task = task
        self.item = item
        self.table_widget = table_widget
        hbox = QHBoxLayout()
        play_button = TaskWidgetIcon(
            QIcon(str(consts.dir / "icons" / "play-fill.svg")), self
        )
        qconnect(play_button.clicked, self.on_play)
        hbox.addWidget(play_button)

        text_button = TaskWidgetIcon(
            QIcon(str(consts.dir / "icons" / "card-text.svg")), self
        )
        qconnect(text_button.clicked, self.on_text)
        hbox.addWidget(text_button)
        self.setLayout(hbox)

    def on_play(self) -> None:
        av_player.play_file(self.task.path)

    def on_text(self) -> None:
        showText(self.task.text(), self, copyBtn=True)


class TasklistDialog(Dialog):
    key = "tasklist"

    def __init__(self, mw: AnkiQt, parent: QWidget | None = None) -> None:
        self.mw = mw
        super().__init__(parent, Qt.WindowType.Window)

    def setup_ui(self) -> None:
        super().setup_ui()
        qconnect(self.finished, self.cleanup)
        self.setWindowTitle(f"{consts.name} - Task List")
        icon = QIcon()
        icon.addPixmap(QPixmap("icons:anki.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        table_widget = self.table_widget = QTableWidget(self)
        vbox.addWidget(self.table_widget)
        table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table_widget.setColumnCount(4)
        table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table_widget.setHorizontalHeaderLabels(["File", "Status", "Text", "Actions"])
        table_widget.verticalHeader().hide()
        table_widget.verticalHeader().setDefaultSectionSize(40)
        table_widget.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Fixed
        )
        table_widget.horizontalHeader().resizeSection(3, 75)

        self.add_tasks()
        self.update_timer = self.mw.progress.timer(
            1000, func=self.update_tasks, repeat=True, parent=self
        )

    def cleanup(self) -> None:
        av_player.clear_queue_and_maybe_interrupt()
        self.update_timer.deleteLater()

    def add_tasks(self, start: int = 0) -> None:
        self.table_widget.setRowCount(len(tasklist))
        for i, task in enumerate(tasklist[start:], start=start):
            filename_item = QTableWidgetItem()
            filename_item.setText(os.path.basename(task.path))
            filename_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(i, 0, filename_item)

            status_item = QTableWidgetItem()
            status_item.setText(task.status_text())
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(i, 1, status_item)

            text_item = QTableWidgetItem()
            text_item.setText(task.text())
            text_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(i, 2, text_item)

            actions_item = QTableWidgetItem()
            actions_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(i, 3, actions_item)
            actions_widget = TaskActionsWidget(task, actions_item, self.table_widget)
            actions_item.setSizeHint(QSize(75, 40))
            self.table_widget.setCellWidget(i, 3, actions_widget)

    def update_tasks(self) -> None:
        for i in range(self.table_widget.rowCount()):
            task = tasklist[i]
            status_item = self.table_widget.item(i, 1)
            status_item.setText(task.status_text())
            text_item = self.table_widget.item(i, 2)
            text_item.setText(task.text())

        self.add_tasks(self.table_widget.rowCount())
