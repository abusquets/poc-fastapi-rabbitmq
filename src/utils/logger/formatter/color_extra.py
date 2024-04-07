import colorlog

from .standard_extra import FormatterExtra


class ColorFormatterExtra(colorlog.ColoredFormatter, FormatterExtra):
    pass
