"""Parse a Loaf .kicad_pcb (stdin) and print outline, footprints, NPTH/mounting holes.
Usage: git -C <repo> show <rev>:hardware/BREAD_Loaf.kicad_pcb | python3 -I loafparse.py
"""
import sys, math, re

def tokenize(s):
    for m in re.finditer(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s):
        yield m.group(0)

def parse(s):
    stack = [[]]
    for t in tokenize(s):
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t.strip('"') if t.startswith('"') else t)
    return stack[0][0]

def kids(n, name):
    return [c for c in n if isinstance(c, list) and c and c[0] == name]

def kid(n, name):
    k = kids(n, name); return k[0] if k else None

def rot(x, y, deg):
    # KiCad: positive angle rotates CCW on screen (y down) -> use -deg in math frame
    a = math.radians(-deg)
    return x*math.cos(a) - y*math.sin(a), x*math.sin(a) + y*math.cos(a)

