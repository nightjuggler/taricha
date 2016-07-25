#!/usr/bin/python

numbers = [1, 3, 4, 6]

class Operator(object):
	def __init__(self, symbol, fn):
		self.symbol = symbol
		self.fn = fn

ops = [
	Operator('+', lambda a, b: a + b),
	Operator('-', lambda a, b: a - b),
	Operator('*', lambda a, b: a * b),
	Operator('/', lambda a, b: None if b == 0 else float(a) / float(b)),
]

resultHash = {}
numops = [len(numbers) - 1]
tree = []

def parseTree(i):
	v = tree[i]
	if isinstance(v, int):
		return v, v, i + 1

	t1, n1, j = parseTree(i + 1)
	t2, n2, j = parseTree(j)
	n = None if n1 is None or n2 is None else v.fn(n1, n2)
	t = '({} {} {})'.format(t1, v.symbol, t2)

	return t, n, j

def printResult():
	t, n, j = parseTree(0)

	if n is not None:
		n = round(n, 10)
		if n == int(n):
			n = int(n)

	print t, '=', n

	resultHash[n] = resultHash.get(n, 0) + 1

def solve():
	n = numops.pop()
	if n == 0:
		for i in xrange(len(numbers)):
			x = numbers.pop(i)
			tree.append(x)
			if numops:
				solve()
			else:
				printResult()
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

	for count, result in sorted([(count, result) for result, count in resultHash.iteritems()]):
		print '{:4}: {}'.format(count, result)
