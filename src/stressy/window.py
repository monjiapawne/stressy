from asyncio import AbstractEventLoop

from gi.repository import Adw

from stressy.history_page import HistoryPage
from stressy.run_page import RunPage


class Win(Adw.ApplicationWindow):
    def __init__(self, worker_loop: AbstractEventLoop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_size_request(width=200, height=-1)
        self.set_resizable(False)

        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        self.stack = Adw.ViewStack()
        self.view = Adw.ToolbarView(content=self.stack)
        self.toast_overlay.set_child(self.view)
        self.switcher = Adw.InlineViewSwitcher(stack=self.stack, display_mode="icons")
        self.header = Adw.HeaderBar(title_widget=self.switcher)
        self.view.add_top_bar(self.header)

        self.run_page = RunPage(worker_loop=worker_loop)
        self.history_page = HistoryPage()
        self.history_page.connect(
            "load_requested",
            lambda _page, url, total: [
                self.run_page.prefill(url, total),
                self.stack.set_visible_child_name("run"),
                self.run_page.toast("Loaded"),
            ],
        )

        self.stack.add_titled_with_icon(self.run_page, "run", "Run", "media-playback-start-symbolic")
        self.stack.add_titled_with_icon(self.history_page, "history", "History", "document-open-recent-symbolic")


class StressyApp(Adw.Application):
    def __init__(self, worker_loop, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)
        self._worker_loop = worker_loop

    def on_activate(self, app):
        self.win = Win(self._worker_loop, application=app)
        self.win.present()
