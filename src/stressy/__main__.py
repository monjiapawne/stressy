import sys
from asyncio import new_event_loop
from threading import Thread

from stressy.window import StressyApp


def main():
    worker_loop = new_event_loop()
    Thread(target=worker_loop.run_forever, daemon=True).start()
    app = StressyApp(worker_loop=worker_loop, application_id="io.github.monjiapawne.Stressy")
    sys.exit(app.run())


if __name__ == "__main__":
    main()
