"""6.009 Lab 8A: carlae Interpreter"""

import sys


class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    # add spaces in between parens
    source = source.replace('(',' ( ')
    source = source.replace(')',' ) ')
    new_source = ""
    
    # when there are comments, ignore everything until there is a new line
    i=0
    while i != len(source):
        if source[i] == ';':
            while source[i] != '\n' and i != len(source)-1:
                i+=1
        else:
            new_source += source[i]
        i+=1
            
    # ignore '\n', split into list, and ignore any ""
    new_source = new_source.replace('\n',' ')
    source_list = new_source.split(' ')
    new_source_list = []
    for i in range(len(source_list)):
        if source_list[i] != "" and source_list[i] != "\n":
            new_source_list.append(source_list[i])
            
    return new_source_list


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    def isValid(tokens):
        paren_count=0
        for i in range(len(tokens)):
            if tokens[i] == '(':
                paren_count+=1
            if tokens[i] == ')':
                paren_count-=1
            if paren_count < 0:
                raise(SyntaxError)
        if paren_count != 0:
            raise(SyntaxError)
    
    
    def parse_num_sym(token):
        if '.' not in token:
            try:
                token = int(token)
            except:
                token = str(token)
        else:
            try:
                token = float(token)
            except:
                token = str(token)
                
        return token
    
    
    def parse_helper(tokens):
        parsed = []
        i=0
        while i != len(tokens):
            if tokens[i] == '(':
                i+=1
                start = i
                paren_count = 1
                while paren_count > 0:
                    if tokens[i] == '(':
                        paren_count+=1
                    if tokens[i] == ')':
                        paren_count-=1
                    i+=1
                end = i-1
                parsed.append(parse_helper(tokens[start:end]))
            
            else:
                parsed.append(parse_num_sym(tokens[i]))
                i+=1
        return parsed
    
    
    isValid(tokens)
    
    if len(tokens) == 1:
        return parse_num_sym(tokens[0])
    
    elif tokens[0] != '(':
        raise(SyntaxError)
        
    return parse_helper(tokens)[0]
    
#    
#    
#    if len(tokens) == 1:
#        return parse_num_sym(tokens[0])
#    
#    
#    def parse_helper(tokens):
#        parsed_list = []
#        current = None
#        
#        i = 0
#        while i != len(tokens):
#            print(tokens)
#            if tokens[i] == '(':
#                i+=1
#                end_i = i+1
#                paren_count = 1
#                while end_i != len(tokens) and paren_count>0:
#                    if tokens[end_i] == ')':
#                        paren_count-=1
#                    if tokens[end_i] == '(':
#                        paren_count+=1
#                    end_i += 1
#                
#                current=parse_helper(tokens[i:end_i-1])
#                i = end_i-1
#                
#            
#            if current != None:
#                parsed_list.append(current)
#                current = None
#            else:
#                parsed_list.append(parse_num_sym(tokens[i]))
#                
#            i+=1
#    
#        if len(parsed_list) > 1:
#            return parsed_list
#        else:
#            return parsed_list[0]
#
#    return parse_helper(tokens)

class function:
    def __init__(self, body, params, enviro):
        self.body = body
        self.params = params
        self.enviro = enviro


class environment:
    
    def __init__(self, parent):
        self.parent = parent
        self.vars = {}
        
    def define(self, NAME, EXPR):
        self.vars[NAME] = EXPR
        return EXPR
    


carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': lambda args: args[0] if len(args) == 1 else (args[0] * carlae_builtins['*'](args[1:])),
    '/': lambda args: args[0] if len(args) == 1 else (carlae_builtins['/'](args[:-1]) / args[-1]),
} 


builtins = environment(None)
builtins.define('+', carlae_builtins['+'])
builtins.define('-', carlae_builtins['-'])
builtins.define('*', carlae_builtins['*'])
builtins.define('/', carlae_builtins['/'])



def evaluate(tree, enviro = None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    expression = tree
    
    if enviro == None:
        enviro = environment(builtins)


    # if expression is a list, make a recursive call
    if isinstance(expression, list):
        
        # if current expression has keyword define
        if expression[0] == "define":
            return enviro.define(expression[1],evaluate(expression[2], enviro))
        else:
            for i in range(len(expression)):
                expression[i] = evaluate(expression[i], enviro)
            if callable(expression[0]):
                return expression[0](expression[1:])
            else:
                raise EvaluationError
    

    # if current expression is a built-in
    elif isinstance(expression, str) and expression in carlae_builtins:
        return carlae_builtins[expression]
    
    # if current expression is a number
    elif isinstance(expression,(float,int)):
        return expression
    
    # look up variable in current environment, if not found, look in parent environments
    elif isinstance(expression, str):
        if expression in enviro.vars:
            return enviro.vars[expression]
        elif enviro.parent != None:
            return evaluate(expression, enviro.parent)
        else:
            raise EvaluationError

    # if nothing else works, raise an error
    else:
        raise EvaluationError


def REPL():
    inp = None
    enviro = environment(builtins)
    while inp != "QUIT":
        inp = input ("in> ")
        try:
            print("out> " + str(result_and_env(parse(tokenize(inp)),enviro)[0]))
        except Exception as e:
            if inp == "QUIT":
                break
            print('error> ', e)
        
def result_and_env(inp, enviro = None):
    if enviro == None:
        enviro = environment(builtins)
    return (evaluate(inp,enviro),enviro)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    
        
    REPL()
    

  