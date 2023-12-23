from ast import *
import sys

with open(sys.argv[1], 'r') as f:
    file = ''
    for line in f.readlines(): file += line

def transform_args(elts : list[Name]) -> list[arg]:
    match elts:
        case []:
            return []
        case _:
            return [arg(arg = elts[0].id)] + transform_args(elts[1:])

def transform_stmt(stmt : stmt, rest : list[stmt]) -> list[expr]:
    match stmt:
        # Transforming expression statement (already one line)
        case Expr(value):
            # TODO: if value is a tuple, can unpack to avoid unneeded nesting
            return [value] + transform_stmts(rest)
        
        # TODO: add support for assigning to non-variable targets
            # non-variables can also appear in Tuple/List targets, handle using temp variables then the index/field attr update functions

        # Single variable target assignment
        case Assign(targets = [Name(id = id)], value = value):
            body = transform_stmts(rest)
            if len(body) == 1: body = body[0]
            else: body = Tuple(elts = body, ctx = Load())
            
            args = arguments(args = [arg(arg = id)], posonlyargs = [], kwonlyargs = [], kw_defaults = [], defaults = [])
            lam = Lambda(args = args, body = body)
            return [Call(func = lam, args = [value], keywords = [])]

        # Tuple/List variable target assignment
        case Assign(targets = [Tuple(elts = elts)], value = value) | Assign(targets = [List(elts = elts)], value = value):
            body = transform_stmts(rest)
            if len(body) == 1: body = body[0]
            else: body = Tuple(elts = body, ctx = Load())

            args = arguments(args = transform_args(elts), posonlyargs = [], kwonlyargs = [], kw_defaults = [], defaults = [])
            lam = Lambda(args = args, body = body)
            return [Call(func = lam, args = [Starred(value = value, ctx = Load())], keywords = [])]


def transform_stmts(stmts : list[stmt]) -> list[expr]:
    match stmts:
        case []:
            return []
        case _:
            return transform_stmt(stmts[0], stmts[1:])

def transform_module(module : Module) -> AST:
    body = transform_stmts(module.body)
    num_exprs = len(body)
    if num_exprs > 1: res = Module(body = [Expr(value = Tuple(elts = transform_stmts(module.body), ctx = Load()))], type_ignores = module.type_ignores)
    elif num_exprs == 1: res = Module(body = [Expr(value = body[0])], type_ignores = module.type_ignores)
    else: res = Module(body = [], type_ignores = module.type_ignores)
    return res

ast = parse(file)

print('print("Old ------------")')
print(unparse(ast))
print('print()')

print('print("New ------------")')
print(unparse(transform_module(ast)))
print('print()')