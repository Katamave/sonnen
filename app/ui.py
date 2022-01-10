import urwid

# configuration
from app.config import BATTERY_MAX_LOAD_W
from app.config import INVERTER_MAX_LOAD
from app.config import HOUSE_MAX_LOAD

UI_UPDATE_INTERVAL = 3


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
        self.app.loop.set_alarm_in(UI_UPDATE_INTERVAL, self.update_house)


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
        self.app.loop.set_alarm_in(UI_UPDATE_INTERVAL, self.update_grid)


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

        self.app.loop.set_alarm_in(UI_UPDATE_INTERVAL, self.update_battery)

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