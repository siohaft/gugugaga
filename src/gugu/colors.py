from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass


class ANSI:
    """
    ANSI escape sequences used by the Gugu terminal renderer.

    This class contains raw escape sequences only. Higher-level
    semantic colors are provided by the ColorTheme class below.
    """

    RESET = "\033[0m"

    # Text styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"

    # Reset individual styles
    RESET_BOLD = "\033[22m"
    RESET_DIM = "\033[22m"
    RESET_ITALIC = "\033[23m"
    RESET_UNDERLINE = "\033[24m"
    RESET_BLINK = "\033[25m"
    RESET_REVERSE = "\033[27m"
    RESET_HIDDEN = "\033[28m"
    RESET_STRIKETHROUGH = "\033[29m"

    # Standard foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Standard background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Bright background colors
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"

    # Cursor / terminal control
    CLEAR_SCREEN = "\033[2J"
    CLEAR_LINE = "\033[2K"
    CURSOR_HOME = "\033[H"
    CURSOR_HIDE = "\033[?25l"
    CURSOR_SHOW = "\033[?25h"


@dataclass(frozen=True)
class RGB:
    """Simple RGB color representation."""

    red: int
    green: int
    blue: int

    def __post_init__(self):
        for name, value in (
            ("red", self.red),
            ("green", self.green),
            ("blue", self.blue),
        ):
            if not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")

            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be between 0 and 255.")


class Colors:
    """
    General-purpose ANSI color helper for Gugu.

    Supports:
        - standard ANSI colors
        - bright colors
        - 256-color mode
        - true-color RGB
        - text styles
        - semantic Gugu colors
        - global enable/disable
        - terminal detection
        - Windows ANSI support
    """

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        stream=None,
    ):
        self.stream = stream or sys.stderr

        if enabled is None:
            enabled = self._detect_color_support()

        self.enabled = enabled

    # ------------------------------------------------------------------
    # Environment / terminal detection
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_color_support() -> bool:
        """
        Determine whether ANSI colors should be enabled.

        Rules:

        1. NO_COLOR disables colors.
        2. GUGU_NO_COLOR disables colors.
        3. GUGU_COLORS=1/true/yes/on forces colors.
        4. GUGU_COLORS=0/false/no/off disables colors.
        5. Non-TTY streams disable colors by default.
        6. Windows consoles are initialized for ANSI support when possible.
        """

        if "NO_COLOR" in os.environ:
            return False

        if os.environ.get("GUGU_NO_COLOR", "").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }:
            return False

        forced = os.environ.get("GUGU_COLORS", "").lower()

        if forced in {"0", "false", "no", "off"}:
            return False

        if forced in {"1", "true", "yes", "on"}:
            Colors.enable_windows_ansi()
            return True

        stream = sys.stderr

        try:
            is_tty = stream.isatty()
        except (AttributeError, OSError):
            is_tty = False

        if not is_tty:
            return False

        if os.name == "nt":
            return Colors.enable_windows_ansi()

        return True

    @staticmethod
    def enable_windows_ansi() -> bool:
        """
        Enable ANSI/VT processing on Windows consoles.

        Returns True when ANSI output should be usable.
        """

        if os.name != "nt":
            return True

        try:
            kernel32 = ctypes.windll.kernel32

            stdout_handle = kernel32.GetStdHandle(-11)
            stderr_handle = kernel32.GetStdHandle(-12)

            success = False

            for handle in (
                stdout_handle,
                stderr_handle,
            ):
                if handle in (0, -1):
                    continue

                mode = ctypes.c_uint32()

                if not kernel32.GetConsoleMode(
                    handle,
                    ctypes.byref(mode),
                ):
                    continue

                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

                new_mode = mode.value | (ENABLE_VIRTUAL_TERMINAL_PROCESSING)

                if kernel32.SetConsoleMode(
                    handle,
                    new_mode,
                ):
                    success = True

            return success

        except (
            AttributeError,
            OSError,
            ctypes.ArgumentError,
        ):
            return False

    # ------------------------------------------------------------------
    # Core color formatting
    # ------------------------------------------------------------------

    def apply(
        self,
        text: object,
        *styles: str,
    ) -> str:
        """
        Apply one or more ANSI styles to text.
        """

        value = str(text)

        if not self.enabled or not styles:
            return value

        return "".join(styles) + value + ANSI.RESET

    def style(
        self,
        text: object,
        *styles: str,
    ) -> str:
        """Alias for apply()."""
        return self.apply(text, *styles)

    # ------------------------------------------------------------------
    # Standard foreground colors
    # ------------------------------------------------------------------

    def black(self, text: object) -> str:
        return self.apply(text, ANSI.BLACK)

    def red(self, text: object) -> str:
        return self.apply(text, ANSI.RED)

    def green(self, text: object) -> str:
        return self.apply(text, ANSI.GREEN)

    def yellow(self, text: object) -> str:
        return self.apply(text, ANSI.YELLOW)

    def blue(self, text: object) -> str:
        return self.apply(text, ANSI.BLUE)

    def magenta(self, text: object) -> str:
        return self.apply(text, ANSI.MAGENTA)

    def cyan(self, text: object) -> str:
        return self.apply(text, ANSI.CYAN)

    def white(self, text: object) -> str:
        return self.apply(text, ANSI.WHITE)

    # ------------------------------------------------------------------
    # Bright foreground colors
    # ------------------------------------------------------------------

    def bright_black(self, text: object) -> str:
        return self.apply(text, ANSI.BRIGHT_BLACK)

    def bright_red(self, text: object) -> str:
        return self.apply(text, ANSI.BRIGHT_RED)

    def bright_green(self, text: object) -> str:
        return self.apply(text, ANSI.BRIGHT_GREEN)

    def bright_yellow(self, text: object) -> str:
        return self.apply(text, ANSI.BRIGHT_YELLOW)

    def bright_blue(self, text: object) -> str:
        return self.apply(text, ANSI.BRIGHT_BLUE)

    def bright_magenta(self, text: object) -> str:
        return self.apply(text, ANSI.BRIGHT_MAGENTA)

    def bright_cyan(self, text: object) -> str:
        return self.apply(text, ANSI.BRIGHT_CYAN)

    def bright_white(self, text: object) -> str:
        return self.apply(text, ANSI.BRIGHT_WHITE)

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------

    def bold(self, text: object) -> str:
        return self.apply(text, ANSI.BOLD)

    def dim(self, text: object) -> str:
        return self.apply(text, ANSI.DIM)

    def italic(self, text: object) -> str:
        return self.apply(text, ANSI.ITALIC)

    def underline(self, text: object) -> str:
        return self.apply(text, ANSI.UNDERLINE)

    def reverse(self, text: object) -> str:
        return self.apply(text, ANSI.REVERSE)

    def strikethrough(self, text: object) -> str:
        return self.apply(text, ANSI.STRIKETHROUGH)

    # ------------------------------------------------------------------
    # 256-color support
    # ------------------------------------------------------------------

    def color256(
        self,
        text: object,
        color: int,
    ) -> str:
        """
        Apply an ANSI 256-color foreground color.

        color must be between 0 and 255.
        """

        if not isinstance(color, int):
            raise TypeError("256-color value must be an integer.")

        if not 0 <= color <= 255:
            raise ValueError("256-color value must be between 0 and 255.")

        return self.apply(
            text,
            f"\033[38;5;{color}m",
        )

    def background256(
        self,
        text: object,
        color: int,
    ) -> str:
        """Apply an ANSI 256-color background."""

        if not isinstance(color, int):
            raise TypeError("256-color value must be an integer.")

        if not 0 <= color <= 255:
            raise ValueError("256-color value must be between 0 and 255.")

        return self.apply(
            text,
            f"\033[48;5;{color}m",
        )

    # ------------------------------------------------------------------
    # True-color RGB support
    # ------------------------------------------------------------------

    def rgb(
        self,
        text: object,
        color: RGB | tuple[int, int, int],
    ) -> str:
        """Apply a 24-bit RGB foreground color."""

        if not isinstance(color, RGB):
            if isinstance(color, tuple) and len(color) == 3:
                color = RGB(*color)
            else:
                raise TypeError("color must be RGB or " "(red, green, blue).")

        return self.apply(
            text,
            (f"\033[38;2;" f"{color.red};" f"{color.green};" f"{color.blue}m"),
        )

    def background_rgb(
        self,
        text: object,
        color: RGB | tuple[int, int, int],
    ) -> str:
        """Apply a 24-bit RGB background."""

        if not isinstance(color, RGB):
            if isinstance(color, tuple) and len(color) == 3:
                color = RGB(*color)
            else:
                raise TypeError("color must be RGB or " "(red, green, blue).")

        return self.apply(
            text,
            (f"\033[48;2;" f"{color.red};" f"{color.green};" f"{color.blue}m"),
        )

    # ------------------------------------------------------------------
    # Semantic Gugu colors
    # ------------------------------------------------------------------

    def error(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_RED,
            ANSI.BOLD,
        )

    def warning(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_YELLOW,
            ANSI.BOLD,
        )

    def success(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_GREEN,
            ANSI.BOLD,
        )

    def info(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_CYAN,
        )

    def debug(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_MAGENTA,
        )

    def trace(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.DIM,
        )

    def filename(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_CYAN,
        )

    def line_number(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_YELLOW,
        )

    def source_code(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.WHITE,
        )

    def exception_name(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_RED,
            ANSI.BOLD,
        )

    def suggestion(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_YELLOW,
        )

    def caret(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_RED,
        )

    def keyword(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_MAGENTA,
        )

    def builtin(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_CYAN,
        )

    def string(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_GREEN,
        )

    def number(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_BLUE,
        )

    def operator(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.BRIGHT_YELLOW,
        )

    # ------------------------------------------------------------------
    # Composite helpers
    # ------------------------------------------------------------------

    def traceback_header(self, text: object) -> str:
        return self.apply(
            text,
            ANSI.DIM,
        )

    def exception_header(
        self,
        exception_name: object,
        message: object,
    ) -> str:
        return (
            f"{self.exception_name(exception_name)}"
            f": "
            f"{self.bright_white(message)}"
        )

    def location(
        self,
        path: object,
        line: int | None = None,
        column: int | None = None,
    ) -> str:
        """
        Format a source location in a consistent Gugu style.

        Example:
            file.gugu:12:5
        """

        result = self.filename(path)

        if line is not None:
            result += ":" + self.line_number(line)

        if column is not None:
            result += ":" + self.line_number(column)

        return result

    def traceback_location(
        self,
        path: object,
        line: int,
        function: str | None = None,
    ) -> str:
        result = (
            f"  File "
            f"{self.filename(repr(str(path)))}"
            f", line "
            f"{self.line_number(line)}"
        )

        if function:
            result += f", in " f"{self.keyword(function)}"

        return result

    def source_with_caret(
        self,
        source: str,
        caret_position: int | None = None,
    ) -> str:
        """
        Render source code and an optional caret.

        caret_position is a zero-based character position.
        """

        result = self.source_code(f"    {source}")

        if caret_position is not None:
            result += "\n"

            if caret_position < 0:
                caret_position = 0

            result += "    " + " " * caret_position + self.caret("^")

        return result

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def write(
        self,
        text: object = "",
        *,
        end: str = "\n",
        file=None,
        flush: bool = False,
    ) -> None:
        """
        Write text using the configured stream.
        """

        output = file or self.stream

        print(
            text,
            end=end,
            file=output,
            flush=flush,
        )

    def print_error(
        self,
        title: object,
        message: object,
    ) -> None:
        self.write(
            self.exception_header(
                title,
                message,
            )
        )

    def print_warning(
        self,
        title: object,
        message: object,
    ) -> None:
        self.write(f"{self.warning(title)}: " f"{message}")

    def print_success(
        self,
        message: object,
    ) -> None:
        self.write(
            self.success("Success"),
            " ",
            message,
        )

    # ------------------------------------------------------------------
    # Runtime control
    # ------------------------------------------------------------------

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def copy(self) -> "Colors":
        """
        Return an independent Colors instance with the
        same configuration.
        """

        return Colors(
            enabled=self.enabled,
            stream=self.stream,
        )


# ----------------------------------------------------------------------
# Default Gugu color theme
# ----------------------------------------------------------------------

COLORS = Colors()


# ----------------------------------------------------------------------
# Convenience functions
# ----------------------------------------------------------------------


def color(
    text: object,
    *styles: str,
) -> str:
    return COLORS.apply(
        text,
        *styles,
    )


def red(text: object) -> str:
    return COLORS.red(text)


def green(text: object) -> str:
    return COLORS.green(text)


def yellow(text: object) -> str:
    return COLORS.yellow(text)


def blue(text: object) -> str:
    return COLORS.blue(text)


def magenta(text: object) -> str:
    return COLORS.magenta(text)


def cyan(text: object) -> str:
    return COLORS.cyan(text)


def white(text: object) -> str:
    return COLORS.white(text)


def bold(text: object) -> str:
    return COLORS.bold(text)


def dim(text: object) -> str:
    return COLORS.dim(text)


def error(text: object) -> str:
    return COLORS.error(text)


def warning(text: object) -> str:
    return COLORS.warning(text)


def success(text: object) -> str:
    return COLORS.success(text)


def info(text: object) -> str:
    return COLORS.info(text)


def suggestion(text: object) -> str:
    return COLORS.suggestion(text)


def filename(text: object) -> str:
    return COLORS.filename(text)


def line_number(text: object) -> str:
    return COLORS.line_number(text)
