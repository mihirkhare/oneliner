from ast import *
import sys

def read_file() -> str:
    with open(sys.argv[1], 'r') as f:
        file = ''
        for line in f.readlines(): file += line
    return file

def transform_args(elts : list[Name]) -> list[arg]:
    match elts:
        case []:
            return []
        case _:
            return [arg(arg = elts[0].id)] + transform_args(elts[1:])

def transform_stmt(stmt : stmt, rest : list[stmt], acc: list[expr]) -> list[expr]:
    match stmt:
        # Transforming expression statement (already one line)
        case Expr(value = value):
            # TODO: if value is a tuple, can unpack to avoid unneeded nesting
            acc.append(value)
            return transform_stmts(rest, acc)

        # Single variable target assignment
        case Assign(targets = [Name(id = id)], value = value):
            acc.append(NamedExpr(target = Name(id = id), value = value))
            return transform_stmts(rest, acc)
        
        # TODO: add support for assigning to non-variable targets
            # non-variables can also appear in Tuple/List targets, handle using temp variables then the index/field attr update functions
        case Assign():
            raise NotImplementedError('Only single variable targets implemented for assignment')

        # case Assign(targets = [Name(id = id)], value = value):
        #     body = transform_stmts(rest)
        #     if len(body) == 1: body = body[0]
        #     else: body = Tuple(elts = body, ctx = Load())
            
        #     args = arguments(args = [arg(arg = id)], posonlyargs = [], kwonlyargs = [], kw_defaults = [], defaults = [])
        #     lam = Lambda(args = args, body = body)
        #     return [Call(func = lam, args = [value], keywords = [])]

        # Tuple/List variable target assignment
        # case Assign(targets = [Tuple(elts = elts)], value = value) | Assign(targets = [List(elts = elts)], value = value):
        #     body = transform_stmts(rest)
        #     if len(body) == 1: body = body[0]
        #     else: body = Tuple(elts = body, ctx = Load())

        #     args = arguments(args = transform_args(elts), posonlyargs = [], kwonlyargs = [], kw_defaults = [], defaults = [])
        #     lam = Lambda(args = args, body = body)
        #     # Unpack the arguments to pass into the function
        #     return [Call(func = lam, args = [Starred(value = value, ctx = Load())], keywords = [])]


def transform_stmts(stmts : list[stmt], acc: list[expr]) -> list[expr]:
    match stmts:
        case []:
            return acc
        case _:
            return transform_stmt(stmts[0], stmts[1:], acc)

def transform_module(module: Module) -> AST:
    body = transform_stmts(module.body, [])
    num_exprs = len(body)
    if num_exprs > 1:
        body_p = [Expr(value = Tuple(elts = body, ctx = Load()))]
    elif num_exprs == 1:
        body_p = [Expr(value = body[0])]
    else:
        body_p = []

    return Module(body = body_p, type_ignores = module.type_ignores)

if __name__ == '__main__':
    file = read_file()
    ast = parse(file)

    print('print("Old ------------")')
    print(unparse(ast))
    print('print()')
    print()

    print('print("New ------------")')
    print(unparse(transform_module(ast)))
    print('print()')