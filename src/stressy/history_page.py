from typing import ClassVar

from gi.repository import Adw, GObject, Gtk

from stressy.base_page import Page

DUMMY = []


class HistoryPage(Page):
    __gsignals__: ClassVar = {
        "load_requested": (GObject.SignalFlags.RUN_FIRST, None, (str, int)),
    }

    def __init__(self):
        super().__init__()
        self.list_box = Gtk.ListBox(css_classes=["boxed-list"], selection_mode="single")
        for url, total, status in DUMMY:
            row = Adw.ActionRow(title=url, subtitle=f"{total} requests - {status}")
            retry = Gtk.Button(
                icon_name="view-refresh-symbolic",
                valign="center",
            )
            retry.connect("clicked", lambda _btn, url, total: self.emit("load_requested", url, total), url, total)
            row.add_suffix(retry)
            self.list_box.append(row)

        scroller = Gtk.ScrolledWindow(vexpand=True, hscrollbar_policy="never")
        scroller.set_child(self.list_box)
        self.append(scroller)
