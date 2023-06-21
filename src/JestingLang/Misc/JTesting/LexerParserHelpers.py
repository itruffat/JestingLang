
helper_lexer_pointer = []

def unmap_token(token):
    return (token.type, token.value, token.lineno, token.lexpos)

def squeeze_lexer(_input, _lexer = None, indirect_lexer = helper_lexer_pointer):
    if _lexer is None:
        _lexer = helper_lexer_pointer[0]
    _lexer.input(_input)
    return [unmap_token(token) for token in _lexer]