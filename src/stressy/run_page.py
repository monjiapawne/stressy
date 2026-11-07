from asyncio import AbstractEventLoop
from typing import ClassVar

from gi.repository import GLib, Gtk

from stressy.base_page import Page
from stressy.worker import RequestJob


class RunPage(Page):
    def __init__(self, worker_loop: AbstractEventLoop):
        super().__init__()
        self.worker_loop = worker_loop
        self.job: RequestJob | None = None
        self.total = 0

        self.grid = Gtk.Grid(row_spacing=6, column_spacing=12)
        self.append(self.grid)

        self.grid.attach(Gtk.Label(label="Url"), column=0, row=0, width=1, height=1)
        self.url_field = Gtk.Entry(hexpand=True, text="https://google.ca")
        self.grid.attach(self.url_field, column=1, row=0, width=1, height=1)

        self.grid.attach(Gtk.Label(label="Requests"), column=0, row=1, width=1, height=1)
        self.count_field = Gtk.SpinButton.new_with_range(1, 100000, 1)
        self.count_field.set_value(15)
        self.grid.attach(self.count_field, column=1, row=1, width=1, height=1)

        self.run_button = Gtk.Button(label="Submit")
        self.run_button.connect("clicked", self.on_run_clicked)
        self.append(self.run_button)

        self.progress_bar = Gtk.ProgressBar()
        self.append(self.progress_bar)

        self.stats = Stats()
        self.append(self.stats)

    def prefill(self, url: str, total: int):
        self.url_field.set_text(url)
        self.count_field.set_value(total)

    def on_run_clicked(self, _):
        if self.job is None:
            self.total = self.count_field.get_value_as_int()
            job = RequestJob(
                loop=self.worker_loop,
                url=self.url_field.get_text(),
                total_requests=self.total,
                callback=self._update_progress,
            )
            job.submit()
            self.job = job

            self.run_button.set_label("Cancel")
            self.progress_bar.set_fraction(0)
            self.stats.reset()
        else:
            self.job.cancel()
            self.toast(f"Canceled at {int(self.progress_bar.get_fraction() * 100)}%")
            self.run_button.set_label("Submit")
            self.job = None

    def _update_progress(self, done: int, failed: int, error_codes: set[int]):
        GLib.idle_add(self._apply_progress, done, failed, error_codes)

    def _apply_progress(self, done: int, failed: int, error_codes: set[int]):
        prev = int(self.progress_bar.get_fraction() * 100)
        curr = int((done / self.total) * 100)
        if curr != prev:
            self.progress_bar.set_fraction(done / self.total)

        self.stats.set("success", str(done - failed))
        self.stats.set("failed", str(failed))
        if error_codes:
            self.stats.set("codes", ", ".join(map(str, error_codes)))

        if done == self.total:
            self.run_button.set_label("Submit")
            self.toast("Done")
            self.job = None


class Stats(Gtk.Box):
    FIELDS: ClassVar = {"success": "0", "failed": "0", "codes": "n/a"}

    def __init__(self):
        super().__init__(homogeneous=True)
        self._labels: dict[str, Gtk.Label] = {}
        for name, default in self.FIELDS.items():
            self._labels[name], box = self.stat_box(name.title(), default)
            self.append(box)

    def set(self, label_name: str, value: str):
        self._labels[label_name].set_label(value)

    def reset(self):
        for name, default in self.FIELDS.items():
            self.set(name, default)

    @staticmethod
    def stat_box(caption: str, default: str) -> tuple[Gtk.Label, Gtk.Box]:
        value = Gtk.Label(label=default, ellipsize="end", max_width_chars=10)
        box = Gtk.Box(orientation="vertical", hexpand=True)
        box.append(Gtk.Label(label=caption))
        box.append(value)
        return value, box
