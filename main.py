#!/home/katamave/PycharmProjects/sonnenProject/venv/bin/python
from app import App
from sonnen import Sonnen

from config import AUTH_TOKEN, IP


def main():
    sonnen_battery = Sonnen(AUTH_TOKEN, IP)
    sonnen_battery.update()

    app = App(sonnen_battery)
    app.loop.run()

    print(sonnen_battery.latest_details_data)
    print(sonnen_battery.status_data)
    print(sonnen_battery.time_since_full)


if __name__ == '__main__':
    main()
