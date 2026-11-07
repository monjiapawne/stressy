from gi.repository import Adw, Gtk


class Page(Gtk.Box):
    TOAST_TIMEOUT = 1
    PAGE_PADDING = 15

    def __init__(self):
        super().__init__(
            orientation="vertical",
            spacing=10,
            margin_start=self.PAGE_PADDING,
            margin_end=self.PAGE_PADDING,
            margin_top=self.PAGE_PADDING,
            margin_bottom=self.PAGE_PADDING,
        )

    def toast(self, title: str, timeout: int | None = None):
        if not timeout:
            timeout = self.TOAST_TIMEOUT
        if overlay := self.get_ancestor(Adw.ToastOverlay):
            overlay.add_toast(Adw.Toast(title=title, timeout=timeout))
