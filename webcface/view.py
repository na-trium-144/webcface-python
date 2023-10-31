from enum import IntEnum


class ViewComponentType(IntEnum):
    TEXT = 0
    NEW_LINE = 1
    BUTTON = 2


class ViewColor(IntEnum):
    INHERIT = 0
    BLACK = 1
    WHITE = 2
    GRAY = 4
    RED = 8
    ORANGE = 9
    YELLOW = 11
    GREEN = 13
    TEAL = 15
    CYAN = 16
    BLUE = 18
    INDIGO = 19
    PURPLE = 21
    PINK = 23
