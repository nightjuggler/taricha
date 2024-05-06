import argparse
import operator

def gcd(a, b):
	while b:
		a, b = b, a % b
	return a

class Fraction(object):
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
		d = gcd(num, denom)
		self.num = num // d
		self.denom = denom // d

	def is_integer(self):
		return self.denom == 1

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
	def __init__(self, symbol, is_associative, is_commutative, fn):
		self.symbol = f' {symbol} '
		self.is_associative = is_associative
		self.is_commutative = is_commutative
		self.fn = fn

	def set_inverse(self, inverse_op, is_primary):
		self.inverse_op = inverse_op
		self.is_primary = is_primary

def parse_tree2(tree, i):
	node = tree[i]
	if isinstance(node, Fraction):
		return str(node), node, i + 1, None, None, None

	expr1, value1, j, op1, op1children, inverse_children1 = parse_tree2(tree, i + 1)
	expr2, value2, j, op2, op2children, inverse_children2 = parse_tree2(tree, j)
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

		if op2 is node: # ... / (a * b / c / d) => ... * c * d / a / b
			children.extend(inverse_children2)
			inverse_children.extend(op2children)
		else:
			inverse_children.append(expr2)

	children.sort()
	expression = node.symbol.join(children)
	if inverse_children:
		inverse_children.sort()
		expression = node.inverse_op.symbol.join([expression, *inverse_children])

	return f'({expression})', value, j, node, children, inverse_children

def parse_tree1(tree, i):
	node = tree[i]
	if isinstance(node, Fraction):
		return str(node), node, i + 1, None, None

	expr1, value1, j, op1, op1children = parse_tree1(tree, i + 1)
	expr2, value2, j, op2, op2children = parse_tree1(tree, j)
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

	return f'({expression})', value, j, node, children

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('integers', metavar='N', type=int, nargs='*', default=[1, 3, 4, 6])
	parser.add_argument('-a', '--associative', action='store_true', help="Don't discard associative equivalents")
	parser.add_argument('-c', '--commutative', action='store_true', help="Don't discard commutative equivalents")
	parser.add_argument('-e', '--expr-only', action='store_true', help="Print only expressions (not frequencies)")
	parser.add_argument('-f', '--freq-only', action='store_true', help="Print only frequencies (not expressions)")
	parser.add_argument('-i', '--int-only', action='store_true',
		help="Print only expressions and frequencies corresponding to integer values")
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
	ops = [
		Operator('+', True,  True,  operator.add),
		Operator('-', False, False, operator.sub),
		Operator('*', True,  True,  operator.mul),
		Operator('/', False, False, operator.truediv),
	]
	ops[0].set_inverse(ops[1], True)
	ops[1].set_inverse(ops[0], False)
	ops[2].set_inverse(ops[3], True)
	ops[3].set_inverse(ops[2], False)

	args = parse_args()
	if args.associative:
		for op in ops:
			op.is_associative = False
	if args.commutative:
		for op in ops:
			op.is_commutative = False

	value_freq = {}
	expr_value = {}
	numbers = list(map(Fraction, args.integers))
	num_ops = [len(numbers) - 1]
	parse_tree = parse_tree2 if args.normalize else parse_tree1

	def print_expression_and_value(expression, value):
		if args.int_only and not value.is_integer():
			return
		if args.expr_value is not None and value != args.expr_value:
			return
		if expression in expr_value:
			assert expr_value[expression] == value
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
					expression, value, next_index = parse_tree(tree, 0)[:3]
					assert next_index == len(tree)
					print_expression_and_value(expression, value)
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

		freqs.sort()
		width = len(str(freqs[-1][0]))
		for freq, value in freqs:
			print(f'{freq:{width}}: {value}')

if __name__ == '__main__':
	main()
