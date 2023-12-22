from ast import *
import sys

with open(sys.argv[1], 'r') as f:
    file = ''
    for line in f.readlines(): file += line

def transform_stmt(stmt : stmt, rest : list[stmt]) -> list[expr]:
    match stmt:
        # TODO: if value is a tuple, can unpack to avoid unneeded nesting
        case Expr(value = value):
            return [value] + transform_stmts(rest)
        
        case Assign():
            raise NotImplementedError('Assignment has not yet been implemented')


def transform_stmts(stmts : list[stmt]) -> list[expr]:
    match stmts:
        case []:
            return []
        case _:
            return transform_stmt(stmts[0], stmts[1:])

def transform_module(module : Module) -> AST:
    # print(dump(module, indent=2))
    body = transform_stmts(module.body)
    num_exprs = len(body)
    if num_exprs > 1:
        res = Module(body = [Expr(value = Tuple(elts = transform_stmts(module.body), ctx = Load()))], type_ignores = module.type_ignores)
    elif num_exprs == 1:
        res = Module(body = [Expr(value = body[0])], type_ignores = module.type_ignores)
    else:
        res = Module(body = [], type_ignores = module.type_ignores)
    # print(dump(res, indent=2))
    return res

ast = parse(file)
print(unparse(ast))
print(unparse(transform_module(ast)))
# print(unparse(transform_module(Module(body = [], type_ignores = []))))
# print(transform_module(parse(file)))