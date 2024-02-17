from __future__ import annotations

from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, overload


@dataclass
class TranscriptionTask:
    path: str
    future: Future
    started: datetime

    def status_text(self) -> str:
        if self.future.running():
            duration = datetime.now() - self.started
            return f"Running for {duration.total_seconds():.2f} s"
        elif self.future.exception():
            return f"Error: {self.future.exception()}"
        else:
            return "Finished"

    def text(self) -> str:
        if self.future.done():
            try:
                return self.future.result().strip()
            except:
                return ""
        return ""


class TaskList:
    def __init__(self) -> None:
        self.tasks: list[TranscriptionTask] = []

    def add_task(self, path: str, future: Future) -> None:
        task = TranscriptionTask(path, future, datetime.now())
        task_idx = next(
            (i for i, task in enumerate(self.tasks) if task.path == path), -1
        )
        if task_idx != -1:
            self.tasks[task_idx] = task
        else:
            self.tasks.append(task)

    def __iter__(self) -> Iterator[TranscriptionTask]:
        return iter(self.tasks)

    def __len__(self) -> int:
        return len(self.tasks)

    @overload
    def __getitem__(self, idx: int) -> TranscriptionTask:
        pass

    @overload
    def __getitem__(self, idx: slice) -> list[TranscriptionTask]:
        pass

    def __getitem__(
        self, idx: int | slice
    ) -> TranscriptionTask | list[TranscriptionTask]:
        return self.tasks[idx]


tasklist = TaskList()
