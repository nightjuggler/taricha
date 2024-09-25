class Fraction(object):
	#
	# Note that, by design, any Fraction with denominator 0 will compare equal to any other
	# Fraction with denominator 0 and greater than any Fraction with a non-zero denominator.
	# The two instance attributes "num" and "denom" should only ever be set by the constructor
	# so that "denom" is never negative, and if "denom" is 0, "num" is 1.
	#
	def __init__(self, num=0, denom=1):
		if isinstance(num, str):
			num, *rest = num.split('/')
			num = int(num)
			if rest:
				if len(rest) > 1:
					raise ValueError('Not a valid fraction!')
				denom = int(rest[0])
		if not isinstance(num, int) or not isinstance(denom, int):
			raise ValueError('Not a valid fraction!')
		if not denom:
			self.num = 1
			self.denom = 0
			return
		if denom < 0:
			num = -num
			denom = -denom
		gcd, x = num, denom
		while x:
			gcd, x = x, gcd % x
		self.num = num // gcd
		self.denom = denom // gcd

	def is_integer(self): return self.denom == 1
	def is_positive(self): return self.num > 0 and self.denom

	def __hash__(self):
		return hash((self.num, self.denom))

	def __bool__(self):
		return self.num != 0

	def __repr__(self):
		if self.denom == 1:
			return str(self.num)
		if not self.denom:
			return 'None'
		return f'{self.num}/{self.denom}'

	def __add__(self, other):
		return Fraction(self.num*other.denom + other.num*self.denom, self.denom*other.denom)
	def __sub__(self, other):
		return Fraction(self.num*other.denom - other.num*self.denom, self.denom*other.denom)
	def __mul__(self, other):
		return Fraction(self.num*other.num, self.denom*other.denom)
	def __truediv__(self, other):
		return Fraction(self.num*other.denom, self.denom*other.num) if other.denom else Fraction(1, 0)

	def __lt__(self, other): return self.num*other.denom < other.num*self.denom
	def __le__(self, other): return self.num*other.denom <= other.num*self.denom
	def __eq__(self, other): return self.denom == other.denom and self.num == other.num
	def __ne__(self, other): return self.denom != other.denom or self.num != other.num
	def __gt__(self, other): return self.num*other.denom > other.num*self.denom
	def __ge__(self, other): return self.num*other.denom >= other.num*self.denom

