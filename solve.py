#!/usr/bin/python

numbers = [1, 3, 4, 6]

class Operator(object):
	def __init__(self, symbol, isAssociative, isCommutative, fn):
		self.symbol = symbol
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
haveExpression = {}
valueFrequency = {}

def parseTree(i):
	node = tree[i]
	if isinstance(node, int):
		return node, node, i + 1

	expr1, value1, j = parseTree(i + 1)
	expr2, value2, j = parseTree(j)

	value = None if value1 is None or value2 is None else node.fn(value1, value2)
	expression = '({} {} {})'.format(expr1, node.symbol, expr2)

	return expression, value, j

def printExpressionAndValue():
	expression, value, nextIndex = parseTree(0)

	assert nextIndex == len(tree)

	if value is not None:
		value = round(value, 10)
		if value == int(value):
			value = int(value)

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
