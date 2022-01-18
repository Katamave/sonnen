from sonnen_manager import App
from sonnen import Sonnen

from sonnen_manager.config import IP, AUTH_TOKEN


def main():
    # Authentication token for the battery
    if not AUTH_TOKEN:
        print('AUTH_TOKEN env variable not set!')
        exit()
    sonnen_battery = Sonnen(AUTH_TOKEN, IP)
    sonnen_battery.update()

    app = App(sonnen_battery)
    app.loop.run()

    print(sonnen_battery.latest_details_data)
    print(sonnen_battery.status_data)

