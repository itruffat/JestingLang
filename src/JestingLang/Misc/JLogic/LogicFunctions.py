import re

address_regex_str =  r'(?P<path>(?P<workbook>\[[a-zA-Z0-9\.\(\)]+\])?(?P<worksheet>[a-zA-Z][a-zA-Z0-9]*!))?\$?(?P<initial>([a-z]+|[A-Z]+)\$?[0-9]+)(?P<final>:\$?[a-zA-Z]+\$?[0-9]+)?'

digit = re.compile(r' *-?\d+ *')
address = re.compile(address_regex_str)
boolean_true = re.compile(r'TRUE|true')
boolean_false = re.compile(r'FALSE|false')
#numeric = re.compile(r'[0-9]+')

def extract_address(t):
    match = address.match(t)
    if match is None:
        return None, None, None, None, None
    else:
        matches = match.groupdict()
        return matches['path'], matches['workbook'], matches['worksheet'], matches['initial'], matches['final']

def label_data(data):
    sdata = str(data)
    if boolean_true.match(sdata) or boolean_false.match(sdata):
        return "BOOL"
    if digit.match(sdata):
        return "INT"
    #if address.match(sdata):
    #    return "REF"
    return "STR"

def boolean(pseudo_boolean):
    sboolean = str(pseudo_boolean)
    if boolean_true.match(sboolean):
        return True
    if boolean_false.match(sboolean):
        return False
    #if pseudo_boolean is date:
    #   return True
    if digit.match(sboolean):
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

