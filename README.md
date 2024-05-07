# Taricha

**solve.py** is a Python script that generates all possible arithmetic expressions in which each number from a list (by default 1, 3, 4, and 6) occurs exactly once.

```
> python3 solve.py
(1 + 3 + 4 + 6) = 14
((4 - 6) + 1 + 3) = 2
((6 - 4) + 1 + 3) = 6
((4 * 6) + 1 + 3) = 28
((4 / 6) + 1 + 3) = 14/3
((6 / 4) + 1 + 3) = 11/2
((3 - 6) + 1 + 4) = 2
((6 - 3) + 1 + 4) = 8
((3 * 6) + 1 + 4) = 23
((3 / 6) + 1 + 4) = 11/2
...
(((6 / 4) / 1) / 3) = 1/2
(((6 / 4) / 3) / 1) = 1/2
  1: -71
  1: -69
  1: -68
  1: -66
  1: -60
  1: -54
  1: -48
  1: -41
...
 72: -1
 77: 5
 79: 7
 82: 0
 87: 9/2
 91: 8
 99: -6
107: 2
109: 1
134: 6
>
```

```
> python3 solve.py --expr-value 96
((1 + 3) * 4 * 6) = 96
>
```

```
> python3 solve.py --divbyzero
(6 / ((3 - 4) + 1)) = None
(6 / ((1 - 4) + 3)) = None
(6 / (1 - (4 - 3))) = None
(6 / (3 - (4 - 1))) = None
(6 / (4 - (1 + 3))) = None
(6 / ((1 + 3) - 4)) = None
(6 / ((4 - 1) - 3)) = None
(6 / ((4 - 3) - 1)) = None
> python3 solve.py --divbyzero --normalize
(6 / (1 + 3 - 4)) = None
(6 / (4 - 1 - 3)) = None
>
```

```
> python3 solve.py 7 22
(22 + 7) = 29
(7 - 22) = -15
(22 - 7) = 15
(22 * 7) = 154
(7 / 22) = 7/22
(22 / 7) = 22/7
1: -15
1: 7/22
1: 22/7
1: 15
1: 29
1: 154
>
```

```
> python3 solve.py --int-only 7 22
(22 + 7) = 29
(7 - 22) = -15
(22 - 7) = 15
(22 * 7) = 154
1: -15
1: 15
1: 29
1: 154
>
```

## Command-line Options

| Short | Long | Description |
|-------|------|-------------|
-h | --help        | Show help message and exit
-a | --associative | Don't discard associative equivalents
-c | --commutative | Don't discard commutative equivalents
-e | --expr-only   | Print only expressions (not frequencies)
-f | --freq-only   | Print only frequencies (not expressions)
-i | --int-only    | Print only expressions and frequencies corresponding to integer values
-p | --pos-only    | Print only expressions and frequencies corresponding to positive values
-I | --int-only-steps | Discard expressions with any non-integer intermediate (or final) values
-P | --pos-only-steps | Discard expressions with any non-positive intermediate (or final) values
-n | --normalize   | Fully normalize expressions
-q | --freq-value  | Print only the values that occur with the given frequency
-v | --expr-value  | Print only the expressions evaluating to the given value
-z | --divbyzero   | Print only the expressions that divide by zero

See also [https://nightjuggler.com/taricha/](https://nightjuggler.com/taricha/)
