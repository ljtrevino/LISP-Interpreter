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
        """
        Uses open and closing of parens to determine 
        if a given list of tokens has balanced ( and )
        """
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
        """
        Casts token to float if it is a number
        """
        try:
            token = float(token)
        except:
            token = str(token)
        return token
    
    
    def parse_helper(tokens):
        """
        Input: a list of tokens (from the tokenize function above)
        Output: a parsed expression in list form
        """
        parsed = []
        i=0
        while i != len(tokens):
            
            # if there are parens, we find indices of starting ( and ending )
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
                
                # adds this subexpression as its own list
                # recursively calls helper function in case there are more () inside
                parsed.append(parse_helper(tokens[start:end]))
            
            else:
                # try casting as a number, otherwise make it a string
                parsed.append(parse_num_sym(tokens[i]))
                i+=1
                
        return parsed
    
    
    ###########################
    #   ACTUAL FUNCTION CALL  #
    ###########################
    
    # First make sure the parentheses are balanced, otherwise raise exception
    isValid(tokens)
    
    # base case
    if len(tokens) == 1:
        return parse_num_sym(tokens[0])
    
    # raise error if not in proper S-expression format
    elif tokens[0] != '(':
        raise(SyntaxError)
        
    # call helper function to parse tokens (which ends up having an
    # extra list around it so we add [0] to get rid of this extra list)
    return parse_helper(tokens)[0]
    

###############################################################################

class function:
    
    def __init__(self, body, params, enviro):
        """
        A function object consists of a body, parameters, 
        and the environment in which it was defined
        """
        self.body = body
        self.params = params
        self.enviro = enviro


class environment:
    
    def __init__(self, parent):
        """
        An environment object has a parent and the variables that have been
        defined in that environment (implemented as a dictionary)
        """
        self.parent = parent
        self.vars = {}
    
    def define(self, NAME, EXPR):
        """
        Creates a new variable with given NAME and sets it equal to EXPR
        Returns the expression after variable has been assigned
        """
        self.vars[NAME] = EXPR
        return EXPR
    
    

# Define built in operators (+, -, *, /) and initalize an environment with these operators
# This environment is called "builtins" and will be the parent of new environments
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




def evaluate(expression, enviro = None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    
    # No current environment, so we must create a new one (whos parent is builtins)
    if enviro == None:
        enviro = environment(builtins)

    if isinstance(expression, list):
        
        if expression == []:
            raise EvaluationError
        
        # IMPROVE THIS CHECK... WHAT IS THE TEST CASE: ((lambda (x) x) 2 3) TRYING TO GET AT?
        if isinstance(expression[0], list) and expression[0][0] == 'lambda':
            if len(expression[0][1]) != len(expression[1:]):
                raise EvaluationError
        
        
        if expression[0] == "define":
            
            if isinstance(expression[1], str):
                return enviro.define(expression[1],evaluate(expression[2], enviro))
            
            # if "Easier Function Definitions" format is used (7.6.5), recursively create function
            if isinstance(expression[1], list):
                return enviro.define(expression[1][0],evaluate(['lambda', expression[1][1:], expression[2]], enviro))
                
    
        if expression[0] == "lambda":
            # create new function with respect to the body, params, and current environment
            func = function(expression[2], expression[1], enviro)
            return func
        
        else:
            new_expression = []
            for i in range(len(expression)):
                # recursively evaluate each element of the expression with respect to current environment
                new_expression.append(evaluate(expression[i], enviro))
                
            # if the first value of the expression is a function we made previously:
            if isinstance(new_expression[0],function):
                
                # create a new environment whose parent is the environment in which the function was defined
                new_enviro = environment(new_expression[0].enviro)
                
                # in the new environment bind the function's parameters to the values that are passed to it
                for param,val in zip(new_expression[0].params,new_expression[1:]):
                    new_enviro.define(param,val)
                    
                # evaluate the body of the function in that new environment
                return evaluate(new_expression[0].body, new_enviro)
            
            # if we renamed a builtin and the first element is callable
            elif callable(new_expression[0]):
                return new_expression[0](new_expression[1:])
            
            # if all else fails, raise an error
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


def REPL():
    """
    Read, Evaluate, Print Loop
    
    Continually prompts the user for input until they type QUIT
    
    It accepts input from the user, tokenizes and parses it, 
    evaluates it (by calling result_and_env), and prints the result
    """
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
    """
    Inputs: user input, current environment
    Output: result of the evaluation and environment
            in which the expression was evaluated
    """
    if enviro == None:
        enviro = environment(builtins)
    return (evaluate(inp,enviro),enviro)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
        
    REPL()
    

  