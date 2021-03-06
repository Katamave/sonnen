import os

# Auth token of the battery
AUTH_TOKEN = os.getenv('AUTH_TOKEN')


# IP address of the battery
IP = 'sonnenbatterie'

# Battery and inverter
BATTERY_MAX_LOAD_W = 4800

# Grid
GRID_MAX_LOAD = 3300

# Inverter
INVERTER_MAX_LOAD = 8300

# House max load without inverter
HOUSE_MAX_LOAD = BATTERY_MAX_LOAD_W + GRID_MAX_LOAD
