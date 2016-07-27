#!/usr/bin/python

class Operator(object):
	def __init__(self, symbol, isAssociative, isCommutative, fn):
		self.symbol = ' {} '.format(symbol)
		self.isAssociative = isAssociative
		self.isCommutative = isCommutative
		self.fn = fn

ops = [
	Operator('+', True,  True,  lambda a, b: a + b),
	Operator('-', False, False, lambda a, b: a - b),
	Operator('*', True,  True,  lambda a, b: a * b),
	Operator('/', False, False, lambda a, b: None if b == 0 else float(a) / float(b)),
]

tree = []
valueFrequency = {}
expressionValue = {}

def parseTree(i):
	node = tree[i]
	if isinstance(node, int):
		return str(node), node, i + 1, None, None

	expr1, value1, j, op1, op1children = parseTree(i + 1)
	expr2, value2, j, op2, op2children = parseTree(j)

	value = None if value1 is None or value2 is None else node.fn(value1, value2)

	children = []
	if node.isAssociative:
		if op1 == node:
			children.extend(op1children)
		else:
			children.append(expr1)
		if op2 == node:
			children.extend(op2children)
		else:
			children.append(expr2)
	else:
		children.append(expr1)
		children.append(expr2)

	if node.isCommutative:
		children.sort()

	expression = '({})'.format(node.symbol.join(children))

	return expression, value, j, node, children

def printExpressionAndValue():
	expression, value, nextIndex, lastOperator, lastOpChildren = parseTree(0)

	assert nextIndex == len(tree)

	if value is not None:
		value = round(value, 10)
		if value == int(value):
			value = int(value)

	if args.int_only and type(value) is not int:
		return
	if args.expr_value is not None and value != args.expr_value:
		return
	if args.divbyzero and value is not None:
		return

	if expression in expressionValue:
		assert value == expressionValue[expression]
	else:
		expressionValue[expression] = value

		if not args.freq_only:
			print expression, '=', value

		valueFrequency[value] = valueFrequency.get(value, 0) + 1

def solve():
	n = numops.pop()
	if n == 0:
		for i in xrange(len(numbers)):
			x = numbers.pop(i)
			tree.append(x)
			if numops:
				solve()
			else:
				printExpressionAndValue()
			tree.pop()
			numbers.insert(i, x)
	else:
		for op in ops:
			tree.append(op)
			for i in xrange(n):
				numops.append(n - i - 1)
				numops.append(i)
				solve()
				numops.pop()
				numops.pop()
			tree.pop()
	numops.append(n)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('integers', metavar='N', type=int, nargs='*', default=[1, 3, 4, 6])
	parser.add_argument('-a', '--associative', action='store_true', help="Don't discard associative equivalents")
	parser.add_argument('-c', '--commutative', action='store_true', help="Don't discard commutative equivalents")
	parser.add_argument('-e', '--expr-only', action='store_true', help="Print only expressions (not frequencies)")
	parser.add_argument('-f', '--freq-only', action='store_true', help="Print only frequencies (not expressions)")
	parser.add_argument('-i', '--int-only', action='store_true',
		help="Print only expressions and frequencies corresponding to integer values")
	parser.add_argument('-q', '--freq-value', type=int,
		help="Print only the values corresponding to the given frequency")
	parser.add_argument('-v', '--expr-value', type=float,
		help="Print only the expressions evaluating to the given value")
	parser.add_argument('-z', '--divbyzero', action='store_true',
		help="Print only the expressions that divide by zero")
	args = parser.parse_args()

	numbers = args.integers
	numops = [len(numbers) - 1]

	if args.associative:
		for op in ops:
			op.isAssociative = False
	if args.commutative:
		for op in ops:
			op.isCommutative = False
	if args.freq_value is not None:
		args.freq_only = True
	if args.expr_value is not None or args.divbyzero:
		args.expr_only = True

	solve()

	if not args.expr_only:
		if args.freq_value is None:
			frequencies = [(freq, value) for value, freq in valueFrequency.iteritems()]
		else:
			frequencies = [(freq, value) for value, freq in valueFrequency.iteritems()
				if freq == args.freq_value]
		frequencies.sort()
		for freq, value in frequencies:
			print '{:4}: {}'.format(freq, value)
