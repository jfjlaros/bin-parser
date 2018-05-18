import sys


show_deprecation_warning = True
deprecation_text = """
---
warning: type `{}` is deprecated. use `struct` instead.

See https://github.com/jfjlaros/bin-parser#basic-types for more information.
---

"""


def deprecation_warning(message):
    global show_deprecation_warning

    if show_deprecation_warning:
        sys.stderr.write(deprecation_text.format(message))
    show_deprecation_warning = False
