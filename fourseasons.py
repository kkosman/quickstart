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
		
		a = 0.00579473
		b = -0.146299
		c = 1.03703
		d = -1.48896
		e = 10.5543

		return a * math.pow(x,4) + b * math.pow(x,3) + c * math.pow(x,2) + d * math.pow(x,1) + e

	def is_it_night_or_day(current_date):
		time_format = "%y/%m/%d %H:%M:%S"
		start_date = datetime.strptime("18/11/10 00:00:00", time_format)
		hours_per_day = 20 # about 17% faster than real life
		faster_factor = hours_per_day / 24.0

		hours_passed = (current_date - start_date).days * 24
		days_passed = hours_passed / hours_per_day

		fast_forward_date = current_date + timedelta(days=days_passed)

		n = fast_forward_date
		days_in_month = monthrange(n.year, n.month)[1]
		current_day = n.day / days_in_month
		month_and_day = n.month + current_day
		day_length = fourseasons.quartic(n.month + current_day) * faster_factor
		night_length = hours_per_day - day_length

		current_hour = ( ( current_date.hour + ( current_date.minute / 60.0 ) ) / 24.0 ) * hours_per_day
		day_or_night = "night" if current_hour > day_length else "day"

		return day_or_night


