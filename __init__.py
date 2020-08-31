# This Anki add-on limits the number of new cards, depending on the
# days "workload", which is the number of cards studied plus the
# nubers or new and review cards scheduled for the day.
#
# It only works with the V2 scheduler.
#
# There are two implementations: a new one that works with Anki 2.1.22 and
# later, and an old one that works on older versions of Anki. This loads
# one or the other, depending on Anki version.
#
from anki import version as anki_version

# print("anki_version ", anki_version)
if anki_version < '2.1.22':
    if anki_version < '2.1.17':
        from aqt.utils import showWarning
        title = "Warning: unsupported Anki version"
        msg = (
            "<b>WARNING:</b> This plugin has not been tested on Anki versions "
            "older than 2.1.17. If you experience problems, please upgrade "
            "Anki to at least version 2.1.17"
        )
        showWarning(msg, title=title, textFormat="rich")
    from .versions import monkey_patch
else:
    from .versions import new_hook
