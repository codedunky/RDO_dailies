import inspect

import os
import sys

# Enable ANSI color rendering in Windows console
if os.name == 'nt':
    os.system('')

import textwrap
from config import settings

COLORS = {
    "ireset":          "\033[0m",
    "idarkred":        "\033[31m",
    "idarkgreen":      "\033[32m",
    "idarkyellow":     "\033[33m",
    "idarkblue":       "\033[34m",
    "idarkpurple":     "\033[35m",
    "idarkcyan":       "\033[36m",
    "iblack":          "\033[90m",
    "ired":            "\033[91m",
    "igreen":          "\033[92m",
    "iyellow":         "\033[93m",
    "iblue":           "\033[94m",
    "ipurple":         "\033[95m",
    "icyan":           "\033[96m",
    "iwhite":          "\033[97m",
    "bblack":          "\033[40m",
    "bred":            "\033[41m",
    "bgreen":          "\033[42m",
    "byellow":         "\033[43m\033[30m",
    "bblue":           "\033[44m",
    "bpurple":         "\033[45m",
    "bcyan":           "\033[46m",
    "bwhite":          "\033[47m\033[30m",
    "bRESET":          "\033[49m",
    "bbrightblack":    "\033[100m",
    "bbrightred":      "\033[101m",
    "bbrightgreen":    "\033[102m\033[30m",
    "bbrightyellow":   "\033[103m\033[30m",
    "bbrightblue":     "\033[104m",
    "bbrightpurple":   "\033[105m",
    "bbrightcyan":     "\033[106m\033[30m",
    "bbrightwhite":    "\033[107m\033[30m"
}

LEVEL_MAP = {
    'L0': 0,
    'L1': 1,
    'L2': 2,
    'L3': 3,
    'L4': 4
}

DEFAULT_LEVEL_COLORS = {
    'L1': 'bwhite',
    'L2': 'bblue',
    'L3': 'idarkgreen',
    'L4': 'ipurple'
}

# Status badge formatting helpers for final terminal report
BG_RED = "\033[101m"
BG_YELLOW = "\033[30;43m"
BG_GREEN = "\033[30;42m"
BG_RESET = "\033[0m"


def debug_print(*args, debug: bool = True):
    """
    Print debug messages with level and color filtering.
    Usage:
      debug_print('L1', 'message')
      debug_print('L1', 'bgreen', 'message')
    """
    if not debug or len(args) == 0:
        return

    level_str = args[0]
    if isinstance(level_str, str):
        level_upper = level_str.upper()
        level_num = LEVEL_MAP.get(level_upper, 3)
    else:
        level_upper = 'L4'
        level_num = 4

    if level_num > settings.CURRENT_DEBUG_LEVEL:
        return

    color = None
    if len(args) > 1:
        second_arg = args[1]
        if isinstance(second_arg, str) and second_arg.lower() in COLORS:
            color = second_arg.lower()
            message_parts = args[2:]
        else:
            message_parts = args[1:]
    else:
        message_parts = []

    default_color_name = DEFAULT_LEVEL_COLORS.get(level_upper, 'iblue')
    color_code = COLORS.get(color, COLORS.get(default_color_name, COLORS["iblue"]))

    frame = inspect.currentframe()
    caller_frame = frame.f_back
    line_number = caller_frame.f_lineno

    combined_message = " ".join(str(msg) for msg in message_parts)
    if not combined_message.strip():
        return

    wrap_width = 125
    max_indent = 12
    line_info = f"LINE {line_number}: "
    line_info_length = len(line_info)

    wrapped_message = textwrap.fill(combined_message, width=wrap_width)
    indent_str = ' ' * max(0, max_indent - line_info_length)

    lines = wrapped_message.splitlines()
    print(f"{line_info}{indent_str}{color_code}{lines[0]}{COLORS['ireset']}")

    full_indent = ' ' * max_indent
    for line in lines[1:]:
        print(f"{full_indent}{color_code}{line}{COLORS['ireset']}")