from JestingLang.Misc.JLogic.LogicFunctions import variablesIntoIntegers
from JestingLang.Core.JParsing.JestingAST import operations as astOperations

def operationPlus(variables):
    variables_int, errors = variablesIntoIntegers(variables, "Plus(+)")
    answer = 0
    if len(errors) == 0:
        answer = variables_int[0] + variables_int[1]
    return errors, answer, "INT"


def operationMinus(variables):
    variables_int, errors = variablesIntoIntegers(variables, "Minus(-)")
    answer = 0
    if len(errors) == 0:
        if len(variables_int) == 1:
            answer = -variables_int[0]
        else:
            answer = variables_int[0] - variables_int[1]
    return errors, answer, "INT"


def operationTimes(variables):
    variables_int, errors = variablesIntoIntegers(variables, "Times(*)")
    answer = 0
    if len(errors) == 0:
        answer = variables_int[0] * variables_int[1]
    return errors, answer, "INT"


def operationDivide(variables):
    variables_int, errors = variablesIntoIntegers(variables, "Div(/)")
    answer = 0
    if str(variables[1]) == "0":
        errors.append("Divided by zero")
    if len(errors) == 0:
        answer = variables_int[0] / variables_int[1]
    return errors, answer, "INT"

def operationModulo(variables):
    variables_int, errors = variablesIntoIntegers(variables, "Modulo(MOD)")
    answer = 0
    if len(errors) == 0:
        answer = variables_int[0] % variables_int[1]
    return errors, answer, "INT"

def operationConcat(variables):
    return [], str(variables[0] if variables[0] is not None else '') + \
               str(variables[1] if variables[1] is not None else ''), "STR"


def operationEquals(variables):
    print(variables)
    return [], variables[0] == variables[1], "BOOL" # Needs further improving

def operationAnd(variables):
    return [], variables[0] and variables[1], "BOOL" # Needs further improving

def operationOr(variables):
    return [], variables[0] or variables[1], "BOOL" # Needs further improving

def operationBigger(variables):
    variables_int, errors = variablesIntoIntegers(variables, "Bigger(>)")
    answer = False
    if len(errors) == 0:
        answer = variables_int[0] > variables_int[1]
    return errors, answer, "BOOL"


def operationNot(variables):
    return [], not(variables[0]), "BOOL"

operations = {
                "+": operationPlus,
                "-": operationMinus,
                "u-": operationMinus,
                "*": operationTimes,
                "/": operationDivide,
                "&": operationConcat,
                "=": operationEquals,
                '>': operationBigger,
                'NOT': operationNot,
                'AND': operationAnd,
                'OR': operationOr,
                'MOD': operationModulo,
}

assert(astOperations == set(operations.keys()))