#!/usr/bin/python

numbers = [1, 3, 4, 6]

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

numops = [len(numbers) - 1]

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

	if expression in expressionValue:
		assert value == expressionValue[expression]
	else:
		expressionValue[expression] = value

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
	solve()

	for freq, value in sorted([(freq, value) for value, freq in valueFrequency.iteritems()]):
		print '{:4}: {}'.format(freq, value)
