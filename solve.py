import argparse

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

class Operator(object):
	def __init__(self, symbol, fn, is_primary):
		self.symbol = f' {symbol} '
		self.fn = Fraction.__dict__[f'__{fn}__']
		self.is_primary = is_primary
		self.is_associative = is_primary
		self.is_commutative = is_primary

def make_ops(*spec):
	ops = []
	for sym1, fn1, sym2, fn2 in spec:
		op1 = Operator(sym1, fn1, True)
		op2 = Operator(sym2, fn2, False)
		op1.inverse_op = op2
		op2.inverse_op = op1
		ops.append(op1)
		ops.append(op2)
	return ops

def parse_tree2(tree, i):
	node = tree[i]
	if isinstance(node, Fraction):
		return str(node), node, (), i + 1, None, None, None

	expr1, value1, steps1, j, op1, op1children, inverse_children1 = parse_tree2(tree, i + 1)
	expr2, value2, steps2, j, op2, op2children, inverse_children2 = parse_tree2(tree, j)
	value = node.fn(value1, value2)

	children = []
	inverse_children = []

	if node.is_primary:
		if op1 is node: # (a * b / c / d) * ...
			children.extend(op1children)
			inverse_children.extend(inverse_children1)
		else:
			children.append(expr1)

		if op2 is node: # ... * (a * b / c / d)
			children.extend(op2children)
			inverse_children.extend(inverse_children2)
		else:
			children.append(expr2)
	else:
		node = node.inverse_op

		if op1 is node: # (a * b / c / d) / ...
			children.extend(op1children)
			inverse_children.extend(inverse_children1)
		else:
			children.append(expr1)

		# ... / (a * b / c / d) => ... * c * d / a / b
		if op2 is node and (not node.is_mul or value2.denom):
			children.extend(inverse_children2)
			inverse_children.extend(op2children)
		else:
			inverse_children.append(expr2)

	children.sort()
	expression = node.symbol.join(children)
	if inverse_children:
		inverse_children.sort()
		expression = node.inverse_op.symbol.join([expression, *inverse_children])

	return f'({expression})', value, (*steps1, *steps2, value), j, node, children, inverse_children

def parse_tree1(tree, i):
	node = tree[i]
	if isinstance(node, Fraction):
		return str(node), node, (), i + 1, None, None

	expr1, value1, steps1, j, op1, op1children = parse_tree1(tree, i + 1)
	expr2, value2, steps2, j, op2, op2children = parse_tree1(tree, j)
	value = node.fn(value1, value2)

	children = []
	if node.is_associative:
		if op1 is node:
			children.extend(op1children)
		else:
			children.append(expr1)
		if op2 is node:
			children.extend(op2children)
		else:
			children.append(expr2)
	else:
		children.append(expr1)
		children.append(expr2)

	if node.is_commutative:
		children.sort()

	expression = node.symbol.join(children)

	return f'({expression})', value, (*steps1, *steps2, value), j, node, children

def parse_args():
	parser = argparse.ArgumentParser(allow_abbrev=False)
	parser.add_argument('NUMBERS', type=int, nargs='*', default=[1, 3, 4, 6])
	parser.add_argument('-a', '--associative', action='store_true', help="Don't discard associative equivalents")
	parser.add_argument('-c', '--commutative', action='store_true', help="Don't discard commutative equivalents")
	parser.add_argument('-e', '--expr-only', action='store_true', help="Print only expressions (not frequencies)")
	parser.add_argument('-f', '--freq-only', action='store_true', help="Print only frequencies (not expressions)")
	parser.add_argument('-i', '--int-only', action='store_true',
		help="Print only expressions and frequencies corresponding to integer values")
	parser.add_argument('-p', '--pos-only', action='store_true',
		help="Print only expressions and frequencies corresponding to positive values")
	parser.add_argument('-I', '--int-only-steps', action='store_true',
		help="Discard expressions with any non-integer intermediate (or final) values")
	parser.add_argument('-P', '--pos-only-steps', action='store_true',
		help="Discard expressions with any non-positive intermediate (or final) values")
	parser.add_argument('-n', '--normalize', action='store_true', help="Fully normalize expressions")
	parser.add_argument('-q', '--freq-value', type=int,
		help="Print only the values that occur with the given frequency")
	parser.add_argument('-v', '--expr-value', type=Fraction,
		help="Print only the expressions evaluating to the given value")
	parser.add_argument('-z', '--divbyzero', action='store_true',
		help="Print only the expressions that divide by zero")
	args = parser.parse_args()

	if args.divbyzero:
		args.expr_value = Fraction(1, 0)
	if args.freq_value is not None:
		args.freq_only = True
	if args.expr_value is not None:
		args.expr_only = True
	return args

def main():
	ops = make_ops(('+', 'add', '-', 'sub'), ('*', 'mul', '/', 'truediv'))
	for op in ops:
		op.is_mul = op.fn is Fraction.__mul__

	args = parse_args()
	if args.associative:
		for op in ops:
			op.is_associative = False
	if args.commutative:
		for op in ops:
			op.is_commutative = False

	value_freq = {}
	expr_value = {}
	numbers = list(map(Fraction, args.NUMBERS))
	num_ops = [len(numbers) - 1]
	parse_tree = parse_tree2 if args.normalize else parse_tree1

	def print_expression(tree):
		expression, value, steps, next_index = parse_tree(tree, 0)[:4]
		assert next_index == len(tree)
		if args.expr_value is not None and value != args.expr_value: return
		if args.int_only and not value.is_integer(): return
		if args.pos_only and not value.is_positive(): return
		if args.int_only_steps and not all(map(Fraction.is_integer, steps)): return
		if args.pos_only_steps and not all(map(Fraction.is_positive, steps)): return
		if expression in expr_value:
			assert expr_value[expression] == value, f'{expression} = {expr_value[expression]} != {value}'
			return
		expr_value[expression] = value
		if not args.freq_only:
			print(expression, '=', value)
		value_freq[value] = value_freq.get(value, 0) + 1

	def solve(tree):
		n = num_ops.pop()
		if n == 0:
			for i in range(len(numbers)):
				x = numbers.pop(i)
				tree.append(x)
				if num_ops:
					solve(tree)
				else:
					print_expression(tree)
				tree.pop()
				numbers.insert(i, x)
		else:
			for op in ops:
				tree.append(op)
				for i in range(n):
					num_ops.append(n - i - 1)
					num_ops.append(i)
					solve(tree)
					num_ops.pop()
					num_ops.pop()
				tree.pop()
		num_ops.append(n)

	solve([])

	if not args.expr_only:
		if args.freq_value:
			freq_value = args.freq_value
			freqs = [(freq, value) for value, freq in value_freq.items() if freq == freq_value]
		else:
			freqs = [(freq, value) for value, freq in value_freq.items()]
		if freqs:
			freqs.sort()
			width = len(str(freqs[-1][0]))
			for freq, value in freqs:
				print(f'{freq:{width}}: {value}')

if __name__ == '__main__':
	main()
