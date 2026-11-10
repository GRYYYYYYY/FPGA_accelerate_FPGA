"""Strict six-input Vivado Boolean equation semantics, without eval()."""
import re

MASK = (1 << 64) - 1
INPUTS = {f'A{i}':sum(((n >> (i-1)) & 1) << n for n in range(64))
          for i in range(1,7)}


def truth_table(equation, output='O6'):
    """Return O6's 64-bit or O5's 32-bit table; reject unsupported syntax."""
    if output not in ('O6','O5'):raise ValueError('Unsupported LUT output')
    width=6 if output=='O6' else 5
    mask=(1 << (1 << width))-1
    text = re.sub(r'\s+', '', equation)
    if not text.startswith(output+'='):
        raise ValueError('Unexpected LUT output equation')
    text = text[3:]
    tokens = re.findall(r'A[1-6]|[01~*+()]', text)
    if ''.join(tokens) != text or not tokens or (width==5 and 'A6' in tokens):
        raise ValueError('Unsupported LUT equation token')
    position = 0

    def atom():
        nonlocal position
        if position >= len(tokens):raise ValueError('Missing operand')
        token = tokens[position];position += 1
        if token == '~':return mask ^ atom()
        if token == '(':
            value = disjunction()
            if position >= len(tokens) or tokens[position] != ')':
                raise ValueError('Unclosed parenthesis')
            position += 1
            return value
        if token in INPUTS:return INPUTS[token] & mask
        if token in ('0','1'):return mask if token == '1' else 0
        raise ValueError('Unexpected operand')

    def conjunction():
        nonlocal position
        value = atom()
        while position < len(tokens) and tokens[position] == '*':
            position += 1;value &= atom()
        return value

    def disjunction():
        nonlocal position
        value = conjunction()
        while position < len(tokens) and tokens[position] == '+':
            position += 1;value |= conjunction()
        return value

    value = disjunction()
    if position != len(tokens):raise ValueError('Trailing equation tokens')
    return value


def equivalent(a,b):
    return truth_table(a) == truth_table(b)
