import urwid

from sonnen import Sonnen
from sonnen_manager.ui import BatteryPile, HousePile, GridPile
from sonnen_manager.ui import Colors
from sonnen_manager.ui import UI_UPDATE_INTERVAL


class App:

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
        self.loop.set_alarm_in(UI_UPDATE_INTERVAL, self.grid_box.base_widget.update_grid)
        self.loop.set_alarm_in(UI_UPDATE_INTERVAL, self.battery_box.base_widget.update_battery)
        self.loop.set_alarm_in(UI_UPDATE_INTERVAL, self.house_box.base_widget.update_house)

        # API update loop
        self.loop.set_alarm_in(UI_UPDATE_INTERVAL, self.update_sonnen_data)

    def update_sonnen_data(self, _loop, _data):
        self.sonnen.update()
        self.loop.set_alarm_in(UI_UPDATE_INTERVAL, self.update_sonnen_data)

    def take_input(self, key):
        if key == 'q':
            raise urwid.ExitMainLoop