#!/home/katamave/PycharmProjects/sonnenProject/venv/bin/python
import requests
import urwid

# Configuration
from config import AUTH_TOKEN
from config import IP
from config import BATTERY_MAX_LOAD_W
from config import INVERTER_MAX_LOAD
from config import HOUSE_MAX_LOAD


class Sonnen:
    """Class for managing Sonnen API data"""
    # API Groups
    IC_STATUS = 'ic_status'

    # API Item keys
    CONSUMPTION_KEY = 'Consumption_W'
    PRODUCTION_KEY = 'Production_W'
    GRID_FEED_IN_WATT_KEY = 'GridFeedIn_W'
    USOC_KEY = 'USOC'
    RSOC_KEY = 'RSOC'
    BATTERY_CHARGE_OUTPUT_KEY = 'Apparent_output'
    REM_CON_WH_KEY = 'RemainingCapacity_Wh'
    PAC_KEY = 'Pac_total_W'
    SECONDS_SINCE_FULL_KEY = 'secondssincefullcharge'
    MODULES_INSTALLED_KEY = 'nrbatterymodules'
    CONSUMPTION_AVG_KEY = 'Consumption_Avg'
    FULL_CHARGE_CAPACITY_KEY = 'FullChargeCapacity'

    def __init__(self, auth_token: str, ip: str):
        self.ip = ip
        self.auth_token = auth_token
        self.url = f'http://{ip}'
        self.header = {'Auth-Token': self.auth_token}

        # read api endpoints
        self.status_api_endpoint = f'{self.url}/api/v2/status'
        self.latest_details_api_endpoint = f'{self.url}/api/v2/latestdata'

        # api data
        self._latest_details_data = None
        self._status_data = None

    def fetch_latest_details(self) -> None:
        """ Fetches latest details api """
        response = requests.get(self.latest_details_api_endpoint, headers=self.header)
        self._latest_details_data = response.json()

    def fetch_status(self) -> None:
        """ Fetches status api """
        response = requests.get(self.status_api_endpoint, headers=self.header)
        self._status_data = response.json()

    def update(self) -> None:
        """ Updates data from apis of the sonnenBatterie """
        self.fetch_latest_details()
        self.fetch_status()

    @property
    def consumption_average(self) -> str:
        """Average consumption in watt
           Returns:
               average consumption in watt
        """
        return self._status_data[self.CONSUMPTION_AVG_KEY]

    @property
    def time_to_empty(self) -> str:
        """Time until battery discharged
            Returns:
                Time in string format HH MM
        """
        hours = int(self.remaining_capacity_wh / self.discharging)if self.discharging else 0
        rest_w = self.remaining_capacity_wh % self.discharging if self.discharging else 0
        minutes = int(rest_w / self.discharging * 60) if rest_w > 0 else 0
        return f'{hours}:{minutes}'

    @property
    def seconds_since_full(self) -> int:
        """Seconds passed since full charge
            Returns:
                seconds as integer
        """
        return self._latest_details_data[self.IC_STATUS][self.SECONDS_SINCE_FULL_KEY]

    @property
    def installed_modules(self) -> int:
        """Battery modules installed in the system
            Returns:
                Number of modules
        """
        return self._latest_details_data[self.IC_STATUS][self.MODULES_INSTALLED_KEY]

    @property
    def minutes_since_full(self) -> int:
        """Minutes passed since full charge
            Returns:
                minutes as integer
        """
        return int(self.seconds_since_full / 60)

    @property
    def hours_since_full(self) -> int:
        """Hours passed since full charge
            Returns:
                hours as integer
        """
        return int(self.minutes_since_full / 60)

    @property
    def time_since_full(self) -> str:
        """Calculates time since full charge.
           Returns:
               Time in format days hours minutes seconds
        """
        seconds = self.seconds_since_full % 60
        minutes = int((self.seconds_since_full / 60) % 60)
        hours = int((self.minutes_since_full / 60) % 24)
        days = int(self.hours_since_full / 24)
        hours_str = f'{"0" if hours < 10 else ""}{hours}'
        minutes_str = f'{"0" if minutes < 10 else ""}{minutes}'
        seconds_str = f'{"0" if seconds < 10 else ""}{seconds}'
        return f'{days} days - {hours_str}:{minutes_str}:{seconds_str}'

    @property
    def latest_details_data(self) -> dict:
        """Latest details data dict saved from the battery api
            Returns:
                last dictionary data saved
        """
        return self._latest_details_data

    @property
    def status_data(self) -> dict:
        """Latest status data dict saved from the battery api
            Returns:
                last dictionary data saved
        """
        return self._status_data

    @property
    def consumption(self) -> str:
        """Consumption of the household
            Returns:
                house consumption in Watt
        """
        return self._latest_details_data[self.CONSUMPTION_KEY]

    @property
    def production(self) -> str:
        """Power production of the household
            Returns:
                house production in Watt
        """
        return self._latest_details_data[self.PRODUCTION_KEY]

    @property
    def u_soc(self) -> str:
        """User state of charge
            Returns:
                User SoC in percent
        """
        return self._latest_details_data[self.USOC_KEY]

    @property
    def remaining_capacity_wh(self) -> int:
        """ Remaining capacity in watt hours
            IMPORTANT NOTE: it seems that sonnen have made a mistake
            in the API. The value should be the half.
            I have made the simple division hack here
            2300W reserve is removed as well
            Returns:
                 Remaining USABLE capacity of the battery in Wh
        """
        return self._status_data[self.REM_CON_WH_KEY] / 2 - 2300

    @property
    def full_charge_capacity(self) -> int:
        """Full charge capacity of the battery system
            Returns:
                Capacity in Wh
        """
        return self._latest_details_data[self.FULL_CHARGE_CAPACITY_KEY]

    @property
    def time_remaining_to_fully_charged(self) -> str:
        """Time remaining until fully charged
            Returns:
                Time in HH MM format
        """
        remaining_charge = self.full_charge_capacity - self.remaining_capacity_wh
        hours = int(remaining_charge / self.charging) if self.charging else 0
        minutes = int((remaining_charge % self.charging) / self.charging * 60) if self.charging else 0
        return f'{hours}:{minutes}'

    @property
    def pac_total(self) -> int:
        """ Battery inverter load
            Negative if charging
            Positive if discharging
            Returns:
                  Inverter load value in watt
        """
        return self._latest_details_data[self.PAC_KEY]

    @property
    def charging(self) -> int:
        """Actual battery charging value
            Returns:
                Charging value in watt
        """
        if self.pac_total < -1:
            return abs(self.pac_total)
        return 0

    @property
    def discharging(self) -> int:
        """Actual battery discharging value
            Returns:
                Discharging value in watt
        """
        if self.pac_total > 0:
            return abs(self.pac_total)
        return 0

    @property
    def grid_in(self) -> int:
        """Actual grid feed in value
            Returns:
                Value in watt
        """
        if self._status_data[self.GRID_FEED_IN_WATT_KEY] > 0:
            return self._status_data[self.GRID_FEED_IN_WATT_KEY]
        return 0

    @property
    def grid_out(self) -> int:
        """Actual grid out value
            Returns:
                Value in watt
        """
        if self._status_data[self.GRID_FEED_IN_WATT_KEY] < 0:
            return abs(self._status_data[self.GRID_FEED_IN_WATT_KEY])
        return 0


class Colors:
    # Combination nicks
    NORMAL = 'normal'
    COMPLETE = 'complete'
    ECO = 'eco'
    CRITICAL = 'critical'
    LOW = 'low'

    # Colors
    WHITE = 'white'
    BLACK = 'black'
    RED = 'red'
    DARK_RED = 'dark red'
    BLUE = 'blue'
    GRAY = 'gray'
    LIGHT_GRAY = 'light gray'
    DARK_GREEN = 'dark green'
    DARK_BLUE = 'dark blue'

    def __init__(self):
        self.palette = [
            (Colors.NORMAL, Colors.BLACK, Colors.LIGHT_GRAY),
            (Colors.COMPLETE, Colors.BLACK, Colors.DARK_RED),
            (Colors.ECO, Colors.WHITE, Colors.DARK_GREEN),
            (Colors.CRITICAL, Colors.BLACK, Colors.DARK_RED),
            (Colors.LOW, Colors.BLACK, Colors.DARK_BLUE)

        ]


class HousePile(urwid.Pile):

    def __init__(self, sonnen, app):
        self.sonnen = sonnen
        self.app = app

        # Production widget
        self.txt_production = urwid.Text('Power production')
        self.pb_power_production = WattLoadProgressBar(Colors.NORMAL, Colors.ECO, done=INVERTER_MAX_LOAD)
        self.pb_power_production.current = self.sonnen.production

        # Consumption widget
        self.txt_consumption = urwid.Text('House consumption')
        self.pb_house_consumption = WattLoadProgressBar(Colors.NORMAL, Colors.COMPLETE, done=HOUSE_MAX_LOAD)
        self.pb_house_consumption.current = self.sonnen.consumption

        self.data_pile_list = [
            self.txt_production,
            self.pb_power_production,
            self.txt_consumption,
            self.pb_house_consumption
        ]
        super().__init__(self.data_pile_list)

    def update_house(self, _loop, _data):
        self.pb_house_consumption.current = self.sonnen.consumption
        self.pb_power_production.current = self.sonnen.production
        self.app.loop.set_alarm_in(App.UPDATE_INTERVAL, self.update_house)


class GridPile(urwid.Pile):

    def __init__(self, sonnen, app):

        self.app = app
        self.sonnen = sonnen

        # Widgets
        self.txt_grid_feed_in = urwid.Text('Grid feed in')
        self.pb_grid_feed_in = WattLoadProgressBar(Colors.NORMAL, Colors.COMPLETE, done=BATTERY_MAX_LOAD_W)
        self.pb_grid_feed_in.current = sonnen.grid_in
        self.txt_power_from_grid = urwid.Text('Power from grid')
        self.pb_power_from_grid = WattLoadProgressBar(Colors.NORMAL, Colors.COMPLETE, done=INVERTER_MAX_LOAD)
        self.pb_power_from_grid.current = sonnen.grid_out
        pile_list = [
            self.txt_grid_feed_in,
            self.pb_grid_feed_in,
            self.txt_power_from_grid,
            self.pb_power_from_grid
        ]
        super().__init__(pile_list)

    def update_grid(self, _loop, _data):
        self.pb_grid_feed_in.current = self.sonnen.grid_in
        self.pb_power_from_grid.current = self.sonnen.grid_out
        self.app.loop.set_alarm_in(App.UPDATE_INTERVAL, self.update_grid)


class BetterProgressBar(urwid.ProgressBar):

    def __init__(self, normal, complete, **kwargs):
        super().__init__(normal, complete, **kwargs)

    def update_complete_color(self, colors: list):
        if self.current > (self.done * 0.5):
            self.complete = colors[0]
        elif self.current > (self.done * 0.2):
            self.complete = colors[1]
        else:
            self.complete = colors[2]


class WattLoadProgressBar(BetterProgressBar):

    def __init__(self, normal, complete, **kwargs):
        super().__init__(normal, complete, **kwargs)

    def get_text(self):
        return f'{str(self.current)} W'


class BatteryPile(urwid.Pile):

    def __init__(self, sonnen, app):
        self.sonnen = sonnen
        self.app = app

        # Full charge capacity
        self.txt_remaining_capacity = urwid.Text(self.battery_remaining_wh_str)
        # Installed modules in the system
        self.txt_modules_installed = urwid.Text(self.modules_installed_str)
        # Time until battery discharged
        self.txt_time_to_discharge = urwid.Text(self.time_to_discharge_str)
        # Time until fully charged
        self.txt_time_to_fully_charged = urwid.Text(self.time_to_fully_charged)
        # Battery SoC
        self.txt_progress_soc_u = urwid.Text('Battery SoC')
        self.pb_soc_u = BetterProgressBar(Colors.NORMAL, Colors.COMPLETE)
        self.pb_soc_u.current = sonnen.u_soc
        self.pb_soc_u.update_complete_color([Colors.ECO, Colors.LOW, Colors.CRITICAL])

        # Battery discharging
        self.txt_battery_discharge = urwid.Text('Battery discharge')
        self.pb_battery_discharge = WattLoadProgressBar(Colors.NORMAL,
                                                        Colors.COMPLETE, current=0,
                                                        done=BATTERY_MAX_LOAD_W)
        self.pb_battery_discharge.current = sonnen.discharging

        # Battery charging
        self.txt_battery_charge = urwid.Text('Battery charging')
        self.pb_battery_charge = WattLoadProgressBar(Colors.NORMAL, Colors.COMPLETE, current=0, done=BATTERY_MAX_LOAD_W)
        self.pb_battery_charge.current = sonnen.charging

        pile_list = [
            self.txt_remaining_capacity,
            self.txt_modules_installed,
            self.txt_time_to_discharge,
            self.txt_time_to_fully_charged,
            self.txt_progress_soc_u,
            self.pb_soc_u,
            self.txt_battery_discharge,
            self.pb_battery_discharge,
            self.txt_battery_charge,
            self.pb_battery_charge
        ]
        super().__init__(pile_list)

    def update_battery(self, _loop, _data):
        self.pb_battery_discharge.current = self.sonnen.discharging
        self.pb_battery_charge.current = self.sonnen.charging
        self.pb_soc_u.current = self.sonnen.u_soc
        self.pb_soc_u.update_complete_color([Colors.ECO, Colors.LOW, Colors.CRITICAL])
        self.txt_time_to_discharge.set_text(self.time_to_discharge_str)
        self.txt_time_to_fully_charged.set_text(self.time_to_fully_charged)
        self.txt_remaining_capacity.set_text(self.battery_remaining_wh_str)

        self.app.loop.set_alarm_in(App.UPDATE_INTERVAL, self.update_battery)

    @property
    def battery_remaining_wh_str(self):
        return f'Remaining power in battery: {self.sonnen.remaining_capacity_wh} Wh'

    @property
    def modules_installed_str(self):
        return f'Installed modules: {self.sonnen.installed_modules}'

    @property
    def time_to_discharge_str(self):
        return f'Time to discharged: {self.sonnen.time_to_empty}'

    @property
    def time_to_fully_charged(self):
        return f'Time to fully charged: {self.sonnen.time_remaining_to_fully_charged}'


class App:

    UPDATE_INTERVAL = 3

    def __init__(self, sonnen_object: Sonnen):
        self.sonnen = sonnen_object

        # Right UI frame
        txt_battery_box_title = urwid.Text('Battery details')
        self.battery_box = urwid.LineBox(BatteryPile(sonnen=self.sonnen, app=self))
        right_ui_frame_list = [
            txt_battery_box_title,
            self.battery_box
        ]
        right_ui_frame = urwid.Pile(right_ui_frame_list)

        # Left UI frame
        txt_house_box_title = urwid.Text('Household details')
        self.house_box = urwid.LineBox(HousePile(sonnen=self.sonnen, app=self))
        txt_grid_box_title = urwid.Text('Grid details')
        self.grid_box = urwid.LineBox(GridPile(sonnen=self.sonnen, app=self))
        left_ui_frame_list = [
            txt_house_box_title,
            self.house_box,
            txt_grid_box_title,
            self.grid_box
        ]
        left_ui_frame = urwid.Pile(left_ui_frame_list)

        # Setting up main column widget
        col_list = [
            left_ui_frame,
            right_ui_frame
        ]
        frame_col = urwid.Columns(col_list)

        # Colors
        self.palette = Colors().palette

        # MainFrame
        self.main_frame = urwid.Filler(frame_col, 'top')
        self.loop = urwid.MainLoop(self.main_frame, palette=self.palette, unhandled_input=self.take_input)

        # interface update loops
        self.loop.set_alarm_in(App.UPDATE_INTERVAL, self.grid_box.base_widget.update_grid)
        self.loop.set_alarm_in(App.UPDATE_INTERVAL, self.battery_box.base_widget.update_battery)
        self.loop.set_alarm_in(App.UPDATE_INTERVAL, self.house_box.base_widget.update_house)

        # API update loop
        self.loop.set_alarm_in(App.UPDATE_INTERVAL, self.update_sonnen_data)

    def update_sonnen_data(self, _loop, _data):
        self.sonnen.update()
        self.loop.set_alarm_in(App.UPDATE_INTERVAL, self.update_sonnen_data)

    def take_input(self, key):
        if key == 'q':
            raise urwid.ExitMainLoop


def main():
    sonnen_battery = Sonnen(AUTH_TOKEN, IP)
    sonnen_battery.update()

    app = App(sonnen_battery)
    app.loop.run()

    print(sonnen_battery.latest_details_data)
    print(sonnen_battery.status_data)


if __name__ == '__main__':
    main()
