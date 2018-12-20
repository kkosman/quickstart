#!/usr/bin/python3

import math
from calendar import monthrange
from datetime import datetime, timedelta


class fourseasons():
	day_length = 24
	month_length = 30
	time_format = "%y/%m/%d %H:%M:%S"

	def __init__(self, current_date):
		self.current_date = current_date
		self.start_date = datetime.strptime("18/05/01 09:00:00", self.time_format)
		self.start_month = self.start_date.month
		# start_date = datetime.strptime("18/11/10 00:00:00", time_format)

	def quartic(self, x):
		# day length quartic - mardid - january is x == 0
		# 0.00579473 x^4 - 0.146299 x^3 + 1.03703 x^2 - 1.48896 x + 10.5543
		# a                b              b             d           e
		return (0.00579473 * (x**4)) - (0.146299 * (x**3)) + (1.03703 * (x**2)) - (1.48896 * x) + 10.5543

	def get_today(self):
		diff = (self.current_date - self.start_date)
		hours_passed = diff.seconds / 60 / 60 / 24
		days_passed = diff.days

		month_and_day = (days_passed + hours_passed) / self.day_length
		month_and_day += self.start_month

		while month_and_day > 13:
			month_and_day -= 13

		return month_and_day

	def get_daylength(self):
		today = self.get_today()

		duration = self.quartic(today) * (self.day_length / 24.0)
		night_length = self.day_length - duration
		
		return duration

	def is_it_night_or_day(self):
		daylength = self.get_daylength()
		current_hour = ( ( self.current_date.hour + ( self.current_date.minute / 60.0 ) ) / 24.0 ) * self.day_length
		day_or_night = "night" if current_hour >= daylength else "day"

		return day_or_night
