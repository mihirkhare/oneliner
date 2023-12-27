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
    return [arg(arg = elt.id) for elt in elts]

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

def wrap_exprs(exprs: list[expr]) -> expr:
    num_exprs = len(exprs)
    if num_exprs > 1:
        res = Tuple(elts = exprs, ctx = Load())
    elif num_exprs == 1:
        res = exprs[0]
    else:
        res = Tuple(elts = [], ctx = Load())

    return res

# TODO: add support for assigning to non-variable targets
    # non-variables can also appear in Tuple/List targets, handle using temp variables then the index/field attr update functions
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

def transform_import(names: list[alias], acc: list[expr]):
    for name in names:
        keywords = [
            keyword(
                arg = 'fromlist',
                value = List(elts = [Constant(value = None)], ctx = Load())
            ),
            keyword(
                arg = 'globals',
                value = Call(func = Name(id = 'globals', ctx = Load()), args = [], keywords = [])
            )
        ] if name.asname else [keyword(
            arg = 'globals',
            value = Call(func = Name(id = 'globals', ctx = Load()), args = [], keywords = [])
        )]
        bind = name.asname if name.asname else name.name
        module = Call(func = Name(id = '__import__', ctx = Load()), args = [Constant(value = name.name)], keywords = keywords)

        acc.append(set_local_variable(bind, module))

def transform_import_from(module: str | None, names: list[alias], level: int, acc: list[expr]):
    module_name = module if module else ''
    fromlist = [Constant(value = name.name) for name in names]
    keywords = [
        keyword(
            arg = 'fromlist',
            value = List(elts = fromlist, ctx = Load())
        ),
        keyword(
            arg = 'globals',
            value = Call(func = Name(id = 'globals', ctx = Load()), args = [], keywords = [])
        ),
        keyword(
            arg = 'level',
            value = Constant(value = level)
        )
    ]
    module = Call(
        func = Name(id = '__import__', ctx = Load()),
        args = [Constant(value = module_name)],
        keywords = keywords
    )

    temp = get_new_temp()
    acc.append(set_local_variable(temp, module))
    for name in names:
        bind = name.asname if name.asname else name.name
        attr = Attribute(value = read_temp(temp), attr = name.name, ctx = Load())
        acc.append(set_local_variable(bind, attr))

def transform_if(test: expr, body: list[stmt], orelse: list[stmt], acc: list[expr]):
    acc.append(IfExp(
        test = test,
        body = wrap_exprs(transform_stmts(body, 0, [])),
        orelse = wrap_exprs(transform_stmts(orelse, 0, []))
    ))

def transform_stmt(stmts: list[stmt], pos: int, acc: list[expr]) -> list[expr]:
    match stmts[pos]:
        # Transforming expression statement (already one line)
        case Expr(value = value):
            # TODO: if value is a tuple, can unpack to avoid unneeded nesting
            acc.append(value)
            return transform_stmts(stmts, pos + 1, acc)

        # Transforming any assignment statement
        case Assign(targets = targets, value = value):
            transform_assign_list(targets, value, acc)
            return transform_stmts(stmts, pos + 1, acc)
        
        # Transforming basic imports with optional aliases
        case Import(names = names):
            transform_import(names, acc)
            return transform_stmts(stmts, pos + 1, acc)
        
        # Transforming from imports with optional aliases
        # TODO: implement *; this can happen after iteration is implemented
        case ImportFrom(module = module, names = names, level = level):
            transform_import_from(module, names, level, acc)
            return transform_stmts(stmts, pos + 1, acc)
        
        # Transforming if-elif-else statements
        case If(test = test, body = body, orelse = orelse):
            transform_if(test, body, orelse, acc)
            return transform_stmts(stmts, pos + 1, acc)

def transform_stmts(stmts: list[stmt], start: int, acc: list[expr]) -> list[expr]:
    if start == len(stmts): return acc
    return transform_stmt(stmts, start, acc)

def transform_module(module: Module) -> AST:
    body = wrap_exprs(transform_stmts(module.body, 0, []))
    return Module(body = [Expr(value = body)], type_ignores = module.type_ignores)

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