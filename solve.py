import argparse
from collections import Counter, defaultdict
import os
import sys
from fraction import Fraction

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

def get_ops(args):
	ops = make_ops(('+', 'add', '-', 'sub'), ('*', 'mul', '/', 'truediv'))
	if args.normalize:
		for op in ops:
			op.is_mul = op.fn is Fraction.__mul__
	if args.associative:
		for op in ops:
			op.is_associative = False
	if args.commutative:
		for op in ops:
			op.is_commutative = False
	return ops

class Node(object):
	ID = 0
	def __init__(self, value, int_steps, pos_steps):
		Node.ID += 1
		self.id = Node.ID
		self.value = value
		self.int_steps = value.is_integer() and int_steps
		self.pos_steps = value.is_positive() and pos_steps

	def __hash__(self): return hash(self.expr)
	def __repr__(self): return self.expr

	def __eq__(self, other):
		if self.expr == other.expr:
			assert self.value == other.value, f'{self.expr} = {self.value} != {other.value}'
			return True
		return False

def leaf(value):
	node = Node(value, True, True)
	node.op = None
	node.expr = str(value)
	node.children = None
	return node

def get_combine(normalize):
	def combine(op, v1, v2):
		node = Node(op.fn(v1.value, v2.value),
			v1.int_steps and v2.int_steps,
			v1.pos_steps and v2.pos_steps)
		normalize(node, op, v1, v2)
		return node
	return combine

def normalize1(node, op, v1, v2):
	children = []
	if op.is_associative:
		if v1.op is op:
			children.extend(v1.children)
		else:
			children.append(v1)
		if v2.op is op:
			children.extend(v2.children)
		else:
			children.append(v2)
	else:
		children.append(v1)
		children.append(v2)

	if op.is_commutative:
		children.sort(key=lambda v: v.id)

	expr = op.symbol.join(v.expr for v in children)
	node.op = op
	node.expr = f'({expr})'
	node.children = children

def normalize2(node, op, v1, v2):
	children = []
	inverse_children = []

	if op.is_primary:
		if v1.op is op: # (a * b / c / d) * ...
			ab, cd = v1.children
			children.extend(ab)
			inverse_children.extend(cd)
		else:
			children.append(v1)

		if v2.op is op: # ... * (a * b / c / d)
			ab, cd = v2.children
			children.extend(ab)
			inverse_children.extend(cd)
		else:
			children.append(v2)
	else:
		op = op.inverse_op

		if v1.op is op: # (a * b / c / d) / ...
			ab, cd = v1.children
			children.extend(ab)
			inverse_children.extend(cd)
		else:
			children.append(v1)

		# ... / (a * b / c / d) => ... * c * d / a / b
		if v2.op is op and (not op.is_mul or v2.value.denom):
			ab, cd = v2.children
			children.extend(cd)
			inverse_children.extend(ab)
		else:
			inverse_children.append(v2)

	children.sort(key=lambda v: v.id)
	expr = op.symbol.join(v.expr for v in children)
	if inverse_children:
		inverse_children.sort(key=lambda v: v.id)
		expr = op.inverse_op.symbol.join([expr, *(v.expr for v in inverse_children)])

	node.op = op
	node.expr = f'({expr})'
	node.children = children, inverse_children

def parse_args():
	def frequency(arg):
		arg = int(arg)
		if arg < 1: raise ValueError()
		return arg

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
	parser.add_argument('-q', '--freq-value', type=frequency,
		help="Print only the values that occur with the given frequency")
	parser.add_argument('-v', '--expr-value', type=Fraction,
		help="Print only the expressions evaluating to the given value")
	parser.add_argument('-z', '--divbyzero', action='store_true',
		help="Print only the expressions that divide by zero")
	args = parser.parse_args()

	if args.divbyzero:
		args.expr_value = Fraction(1, 0)
	if args.freq_value:
		args.freq_only = True
	if args.expr_value is not None:
		args.expr_only = True
	return args

def filter_nodes(args, nodes):
	filters = []
	if args.expr_value is not None:
		expr_value = args.expr_value
		filters.append(lambda node: node.value == expr_value)
	if args.int_only_steps:
		filters.append(lambda node: node.int_steps)
	elif args.int_only:
		filters.append(lambda node: node.value.is_integer())
	if args.pos_only_steps:
		filters.append(lambda node: node.pos_steps)
	elif args.pos_only:
		filters.append(lambda node: node.value.is_positive())
	if filters:
		return [node for node in nodes if all(f(node) for f in filters)]
	return nodes

def get_nodes(nums, ops, combine):
	def sortkey(node): return node.id
	nodes = [[(frozenset([n]), [leaf(Fraction(n))]) for n in nums]]
	for n in range(1, len(nums)):
		m = defaultdict(set)
		for i in range(n):
			for nums1, vals1 in nodes[i]:
				for nums2, vals2 in nodes[n-i-1]:
					if nums1.isdisjoint(nums2): # not nums1 & nums2
						m[nums1 | nums2].update([combine(op, v1, v2)
							for op in ops for v1 in vals1 for v2 in vals2])
		nodes.append([(nums, sorted(vals, key=sortkey)) for nums, vals in m.items()])
	return nodes[-1][0][1]

def print_expr(nodes):
	for node in nodes:
		print(node.expr, '=', node.value)

def print_freq(nodes, freq_value):
	freqs = sorted((freq, value) for value, freq in Counter(node.value for node in nodes).items()
		if not freq_value or freq == freq_value)
	if freqs:
		width = len(str(freqs[-1][0]))
		for freq, value in freqs:
			print(f'{freq:{width}}: {value}')

def main():
	args = parse_args()
	nodes = filter_nodes(args, get_nodes(args.NUMBERS, get_ops(args),
		get_combine((normalize1, normalize2)[args.normalize])))
	try:
		# https://docs.python.org/3/library/signal.html#note-on-sigpipe
		if not args.freq_only: print_expr(nodes)
		if not args.expr_only: print_freq(nodes, args.freq_value)
		sys.stdout.flush()
	except BrokenPipeError:
		os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
		sys.exit(1)

if __name__ == '__main__':
	main()
