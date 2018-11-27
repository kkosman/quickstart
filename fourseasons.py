#!/usr/bin/python3

import math
from calendar import monthrange
from datetime import datetime, timedelta


class fourseasons():

	def quartic(x):
		# day length quartic - mardid
		# 0.00579473 x^4 - 0.146299 x^3 + 1.03703 x^2 - 1.48896 x + 10.5543
		# a                b              b             d           e
		x -= 1 # month number counted from 0

		return (0.00579473 * (x**4)) - (0.146299 * (x**3)) + (1.03703 * (x**2)) - (1.48896 * x) + 10.5543

	def get_today(current_date, day_length):
		time_format = "%y/%m/%d %H:%M:%S"
		start_date = datetime.strptime("18/11/10 00:00:00", time_format)

		hours_passed = (current_date - start_date).days * 24
		days_passed = hours_passed / day_length

		fast_forward_date = current_date + timedelta(days=days_passed)

		n = fast_forward_date
		days_in_month = monthrange(n.year, n.month)[1]
		current_day = n.day / days_in_month
		month_and_day = n.month + current_day

		return month_and_day

	def is_it_night_or_day(current_date, day_length = 20):
		today = get_today(current_date, day_length)

		duration = fourseasons.quartic() * (day_length / 24.0)
		night_length = day_length - duration

		current_hour = ( ( current_date.hour + ( current_date.minute / 60.0 ) ) / 24.0 ) * duration
		day_or_night = "night" if current_hour > duration else "day"

		return day_or_night


