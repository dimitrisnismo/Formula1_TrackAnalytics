import fastf1 
import numpy as np
import matplotlib as mpl

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection


fastf1.Cache.enable_cache('C:\\Cachef1') 

quali = fastf1.get_session(2021, 'Spanish Grand Prix', 'Q')
laps = quali.load_laps()


# Get telemetry data
x = lap.telemetry['X']              # values for x-axis
y = lap.telemetry['Y']              # values for y-axis
color = lap.telemetry['Speed'] 
