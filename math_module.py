# === This is my math module ===
import math


# --- This will be used someday ----
"[√] <-- This is square root"


# --- Fraction ---
class Fraction:
	def __init__(self, a: int, b: int):
		# a/b
		self.a = a
		self.b = b
	def simplify(self) -> None:
		gcd = math.gcd(self.a, self.b)
		self.a = self.a // gcd
		self.b = self.b // gcd
		if self.a < 0 and self.b < 0:
			self.a = -self.a
			self.b = -self.b
	def add(self, to_add) -> None:
		self.a = self.a*to_add.b + to_add.a*self.b
		self.b = self.b*to_add.b
		self.simplify()
	def minus(self, to_minus) -> None:
		self.a = self.a*to_minus.b - to_minus.a*self.b
		self.b = self.b*to_minus.b
		self.simplify()
	def multiply(self, to_multiply) -> None:
		self.a *= to_multiply.a
		self.b *= to_multiply.b
		self.simplify()
	def divide(self, to_divide) -> None:
		self.a *= to_divide.b
		self.b *= to_divide.a
		self.simplify()
	def to_float(self) -> float:
		return self.a / self.b
	def to_percentage(self) -> float:
		return self.a / self.b * 100


# --- 整理方程式 ---
def cleanup(eq: str) -> list:
	# 3x-5+2y+6=7 -> [{'x': 3.0, 'y': 2},6]
	
	# find variables
	vars = []
	non_vars = "1234567890=+-*/×÷<>"
	for i in eq:
		if i not in non_vars and i not in vars:
			vars.append(i)
	if len(vars) in [1,2,3]:
		pass
	elif len(vars) == 0:
		raise TypeError("No variables entered into the function")
	else:
		raise TypeError("Too many variables (Maximum three, and the max length of a var is 1)")
	
	# seperate left and right
	left = []
	right = []
	is_left = True
	r = ""
	skip = False
	for x in eq:
		if (skip): skip = False ; continue
		if(x == "+"):
			if (is_left):
				left.append(r)
			else:
				right.append(r)
			r = ""
		elif (x == "-"):
			if (is_left):
				left.append(r)
			else:
				right.append(r)
			r = "-"
		elif (x in "><="):
			left.append(r)
			is_left = False
			if ("<=" in eq or ">=" in eq):
				skip = True
			r = ""
		else:
			r += x
	right.append(r)
	try: left.remove("")
	except: pass
	try: right.remove("")
	except: pass

	# deg1/deg2 to left and deg0 to right
	for i in range(len(left)):
		try:
			left[i] = -int(left[i])
			right.append(left[i])
			left[i] = '&' # Placeholder
		except: pass
	for i in range(len(right)):
		try:
			right[i] = int(right[i])
		except:
			left.append(f"-{right[i]}" if right[i][0] != '-' else right[i][1:])
			right[i] = '&' # Placeholder
	try: left.remove('&')
	except: pass
	try: right.remove('&')
	except: pass

	# add up everything in deg0
	r = 0
	for i in right:
		r += i
	
	# finish deg1 and deg2
	l = {}
	for i in vars:
		l[f"{i}"] = 0
	for i in left:
		for j in vars:
			if j in i:
				temp = i
				temp = temp.replace(f'{j}','')
				if temp == '': temp = 1
				if temp == '-': temp = -1
				temp = float(temp)
				l[f"{j}"] += temp

	return [l, r]
				

# --- 二元一次聯立方程式 ---
def solve_21(eq1: str, eq2: str) -> dict:
	e1 = cleanup(eq1)
	e2 = cleanup(eq2)
	# cleanup example: [{'x': 3, 'y': 2}, 5]

	# { a1x + b1y = c1
	# { a2x + b2y = c2
	# 
	# D=|a1 b1|, Dx=|c1 b1|, Dy=|a1 c1|
	#   |a2 b2|     |c2 b2|     |a2 c2|
	# 
	# D!=0 -> x=Dx/D, y=Dy/D
	# D=0, Dx=0, Dy=0 -> 無限多解
	# D=0, Dx^2+Dy^2 != 0 -> 無解
	
	for i in list(e1[0].keys()):
		if i not in list(e2[0].keys()): e2[0][f"{i}"] = 0
	for i in list(e2[0].keys()):
		if i not in list(e1[0].keys()): e1[0][f"{i}"] = 0
	if len(e1[0]) != 2 and len(e2[0]) != 2:
		raise TypeError("Too many variables")
	v = list(e1[0].keys())
	a1 = e1[0][v[0]]
	b1 = e1[0][v[1]]
	c1 = e1[1]
	a2 = e2[0][v[0]]
	b2 = e2[0][v[1]]
	c2 = e2[1]
	d = int(a1*b2-b1*a2)
	dx = int(c1*b2-b1*c2)
	dy = int(a1*c2-c1*a2)

	if d == 0 and dx*dx + dy*dy != 0:
		return {f'{v[0]}': False, f'{v[1]}': False}
	elif d == 0 and dx ==0 and dy == 0:
		return {f'{v[0]}': True, f'{v[1]}': True}
	else:
		if dx % d == 0: x = dx/d
		else: x = Fraction(dx, d); x.simplify()
		if dy % d == 0: y = dy/d
		else: y = Fraction(dy, d); y.simplify()
		return {f'{v[0]}': x, f'{v[1]}': y}


# --- 三元一次聯立方程式 ---
def solve_31(eq1: str, eq2: str, eq3: str) -> dict:
	e1 = cleanup(eq1)
	e2 = cleanup(eq2)
	e3 = cleanup(eq3)
	# cleanup example: [{'x': 3, 'y': 2, 'z': 1}, 6]

	# { a1x + b1y + c1z = d1
	# { a2x + b2y + c2z = d2
	# { a3x + b3y + c3z = d3
	# 
	# D=|a1 b1 c1|, Dx=|d1 b1 c1|, Dy=|a1 d1 c1|, Dz=|a1 b1 d1|
	#   |a2 b2 c2|     |d2 b2 c2|     |a2 d2 c2|     |a2 b2 d2|
	#   |a3 b3 c3|     |d3 b3 c3|     |a3 d3 c3|     |a3 b3 d3|
	# 
	# D!=0 -> x=Dx/D, y=Dy/D, z=Dz/D
	# D=0, Dx=0, Dy=0, Dz=0 -> 無限多解
	# D=0, Dx^2+Dy^2+Dz^2 != 0 -> 無解
	for i in list(e1[0].keys()):
		if i not in list(e2[0].keys()): e2[0][f"{i}"] = 0
		if i not in list(e3[0].keys()): e3[0][f"{i}"] = 0
	for i in list(e2[0].keys()):
		if i not in list(e1[0].keys()): e1[0][f"{i}"] = 0
		if i not in list(e3[0].keys()): e3[0][f"{i}"] = 0
	for i in list(e3[0].keys()):
		if i not in list(e1[0].keys()): e1[0][f"{i}"] = 0
		if i not in list(e2[0].keys()): e2[0][f"{i}"] = 0
	if len(e1[0]) != 3 and len(e2[0]) != 3 and len(e3[0]) != 3:
		raise TypeError("Too many variables")
	v = list(e1[0].keys())
	a1 = e1[0][v[0]]
	b1 = e1[0][v[1]]
	c1 = e1[0][v[2]]
	d1 = e1[1]
	a2 = e2[0][v[0]]
	b2 = e2[0][v[1]]
	c2 = e2[0][v[2]]
	d2 = e2[1]
	a3 = e3[0][v[0]]
	b3 = e3[0][v[1]]
	c3 = e3[0][v[2]]
	d3 = e3[1]
	d = int(a1*b2*c3+b1*c2*a3+c1*a2*b3-c1*b2*a3-b1*a2*c3-a1*c2*b3)
	dx = int(d1*b2*c3+b1*c2*d3+c1*d2*b3-c1*b2*d3-b1*d2*c3-d1*c2*b3)
	dy = int(a1*d2*c3+d1*c2*a3+c1*a2*d3-c1*d2*a3-d1*a2*c3-a1*c2*d3)
	dz = int(a1*b2*d3+b1*d2*a3+d1*a2*b3-d1*b2*a3-b1*a2*d3-a1*d2*b3)

	if d == 0 and dx*dx + dy*dy + dz*dz != 0:
		return {f'{v[0]}': False, f'{v[1]}': False, f'{v[2]}': True}
	elif d == 0 and dx ==0 and dy == 0 and dz == 0:
		return {f'{v[0]}': True, f'{v[1]}': True, f'{v[2]}': True}
	else:
		if dx % d == 0: x = dx/d
		else: x = Fraction(dx, d); x.simplify()
		if dy % d == 0: y = dy/d
		else: y = Fraction(dy, d); y.simplify()
		if dy % d == 0: z = dz/d
		else: z = Fraction(dz, d); z.simplify()
		return {f'{v[0]}': x, f'{v[1]}': y, f'{v[2]}': z}


# --- 質因數分解 ---
def factorize(num) -> list:
	i = 2
	f = []
	while i * i <= num:
		if num % i == 0:
			num //= i
			f.append(i)
		else:
			i += 1
	if num > 1:
		f.append(num)
	return f


# --- 簡化根號 ---
def sim_sqrt(num: int) -> list:
	# return s [a,b] means a√b
	f = factorize(num)
	if len(f) == 1:
		return [1, num]
	else:
		s = [1,1]
		i = 0
		while i < len(f):
			current_amount = f.count(f[i])
			if current_amount % 2 == 0:
				# ex: 4
				for _ in range(current_amount // 2): s[0] *= f[i]
				i += current_amount
			elif (current_amount-1) % 2 == 0:
				# ex: 3
				s[1] *= f[i]
				for _ in range((current_amount-1) // 2): s[0] *= f[i]
				i += current_amount
			else:
				i += 1
	return s
