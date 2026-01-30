from collections import defaultdict
from fastapi import BackgroundTasks


BACKGROUND_TASKS_DICT = defaultdict(BackgroundTasks)
