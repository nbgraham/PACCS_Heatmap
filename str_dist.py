import difflib

def str_distance(a,b):
    count = 0
    for i, s in enumerate(difflib.ndiff(a, b)):
        if s[0] != ' ':
            count += 1
    return count