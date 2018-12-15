#!/usr/bin/python3


from datetime import datetime, timedelta
# from fourseasons import fourseasons
from sensormodules import fourseasons
from tabulate import tabulate


results = []

x = 0
while x < 10:
	current_date_time = datetime.now() + timedelta(hours=30*24*x)
	# current_date_time = datetime.now() + timedelta(hours=4*x)
	season = fourseasons.fourseasons(current_date_time)
	today = season.get_today()
	day_length = season.get_daylength()
	light_status = season.is_it_night_or_day()
	results.append([current_date_time,light_status,today, day_length])
	x+=1


print(tabulate(results,headers=['date', 'light', 'today', 'day_length']))