import sys


show_deprication_warning = True
deprication_text = """
---
warning: type `{}` is depricated. use `struct` instead.

See https://github.com/jfjlaros/bin-parser/blob/master/README.md#struct for
more information.
---

"""


def deprication_warning(message):
    global show_deprication_warning

    if show_deprication_warning:
        sys.stderr.write(deprication_text.format(message))
    show_deprication_warning = False
