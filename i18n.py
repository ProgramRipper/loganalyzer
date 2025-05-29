import gettext
import locale
import os.path

lang = locale.getlocale(getattr(locale, "LC_MESSAGES"))[0]
t = gettext.translation(
    "loganalyzer",
    localedir=os.path.join(os.path.dirname(__file__), "locale"),
    languages=[lang] if lang else None,
    fallback=True,
)
_ = t.gettext
