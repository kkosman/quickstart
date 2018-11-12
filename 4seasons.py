#!/usr/bin/python3

import math

# day length quartic - mardid
# 0.00579473 x^4 - 0.146299 x^3 + 1.03703 x^2 - 1.48896 x + 10.5543
# a                b              b             d           e


def quartic(x):
	a = 0.00579473
	b = -0.146299
	c = 1.03703
	d = -1.48896
	e = 10.5543

	return a * math.pow(x,4) + b * math.pow(x,3) + c * math.pow(x,2) + d * math.pow(x,1) + e


x = 0
while x < 12:
	print(x, quartic(x))
	x+=1