import re

address_regex =  r'(?P<path>(?P<workbook>\[[a-zA-Z0-9\.\(\)]+\])?(?P<worksheet>[a-zA-Z][a-zA-Z0-9]*!))?\$?(?P<initial>([a-z]+|[A-Z]+)\$?[0-9]+)(?P<final>:\$?[a-zA-Z]+\$?[0-9]+)?'

digit = re.compile(r' *-?\d+ *')
address = re.compile(address_regex)
numeric = re.compile(r'[0-9]+')

def boolean(pseudo_boolean):
    if pseudo_boolean in ["TRUE","true"]:
        return True
    if pseudo_boolean in ["False","false"]:
        return False
    #if pseudo_boolean is date:
    #   return True
    if digit.match(str(pseudo_boolean)):
        return int(pseudo_boolean) < 0
    return None


def integer(pseudo_integer):
    if pseudo_integer == "" or pseudo_integer is None:
        return 0
    else:
        if digit.match(str(pseudo_integer)):
            return int(pseudo_integer)
    return None

def ref(pseudo_ref):
    m = address.match(pseudo_ref)
    return m if m is None else pseudo_ref

def variablesIntoIntegers(variables, name):
    variables_int = {k: integer(v) for k,v in variables.items()}
    errors = []
    for x in range(len(variables_int)):
        if variables_int[x] is None:
            errors.append("{} value {} is not integer".format(name, x+1))
    return variables_int, errors

def cell_coordinates(y, x):
    second = x % 26
    first = ((x // 26) % 26) - 1
    return ('' if first == -1 else chr(65 + first)) + chr(65 + second) + str(y + 1)

