from enum import Enum

CURSOR_SEPARATOR = "__"


class CursorPrefix(str, Enum):
    NEXT = "next"
    PREV = "prev"
