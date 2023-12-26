from ast import *
import sys

def read_file() -> str:
    with open(sys.argv[1], 'r') as f: return f.read()

temp_count = 0
def get_new_temp() -> str:
    global temp_count
    temp_count += 1
    return str(temp_count)

def read_temp(temp: str) -> expr:
    return Subscript(
        value = Call(
            func = Name(id = 'globals', ctx = Load()),
            args = [],
            keywords = []
        ),
        slice = Constant(value = temp),
        ctx = Load()
    )

def transform_args(elts : list[Name]) -> list[arg]:
    match elts:
        case []:
            return []
        case _:
            return [arg(arg = elts[0].id)] + transform_args(elts[1:])
        
def set_global_variable(id: str, value: expr) -> expr:
    return Call(
        func = Attribute(
            value = Call(
                func = Name(id = 'globals', ctx = Load()),
                args = [],
                keywords = []
            ),
            attr = '__setitem__',
            ctx = Load()
        ),
        args = [Constant(value = id), value],
        keywords = []
    )

def set_local_variable(id: str, value: expr) -> expr:
    return Call(
        func = Attribute(
            value = Call(
                func = Name(id = 'locals', ctx = Load()),
                args = [],
                keywords = []
            ),
            attr = '__setitem__',
            ctx = Load()
        ),
        args = [Constant(value = id), value],
        keywords = []
    )

def transform_assign(target: expr, value: expr, acc: list[expr]):
    match target:
        case Name(id = id):
            acc.append(set_local_variable(id, value))

        case Tuple(elts = elts) | List(elts = elts):
            if len(elts) > 1:
                temp = get_new_temp()
                acc.append(set_local_variable(temp, value))
                value = read_temp(temp)

            for i, elt in enumerate(elts):
                transform_assign(elt, Subscript(value = value, slice = Constant(value = i), ctx = Load()), acc)

def transform_assign_list(targets: list[expr], value: expr, acc: list[expr]):
    if len(targets) > 1:
        temp = get_new_temp()
        acc.append(set_local_variable(temp, value))
        value = read_temp(temp)

    for target in targets:
        transform_assign(target, value, acc)

def transform_stmt(stmt: stmt, rest: list[stmt], acc: list[expr]) -> list[expr]:
    match stmt:
        # Transforming expression statement (already one line)
        case Expr(value = value):
            # TODO: if value is a tuple, can unpack to avoid unneeded nesting
            acc.append(value)
            return transform_stmts(rest, acc)

        # Single variable target assignment
        case Assign(targets = targets, value = value):
            transform_assign_list(targets, value, acc)
            return transform_stmts(rest, acc)
        
        # TODO: add support for assigning to non-variable targets
            # non-variables can also appear in Tuple/List targets, handle using temp variables then the index/field attr update functions
        case Assign():
            raise NotImplementedError('Only single variable targets implemented for assignment')

def transform_stmts(stmts: list[stmt], acc: list[expr]) -> list[expr]:
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