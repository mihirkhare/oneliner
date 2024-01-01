from ast import *
import sys

def read_file() -> str:
    with open(sys.argv[1], 'r') as f: return f.read()

# TODO: to avoid having a crazy amount of temps, delete temps when not needed anymore
    # potentially use a list variable as a stack
temp_count = 0
def get_new_temp() -> str:
    global temp_count
    temp_count += 1
    return str(temp_count)

def get_attribute(obj: expr, attr: str) -> expr:
    return Attribute(value = obj, attr = attr, ctx = Load())

def set_attribute(obj: expr, attr: str, value: expr) -> expr:
    return Call(
        func = get_attribute(obj, '__setattr__'),
        args = [Constant(value = attr), value],
        keywords = []
    )

def get_item(obj: expr, item: None | str | bytes | bool | int | float | complex) -> expr:
    return Subscript(value = obj, slice = Constant(value = item), ctx = Load())

def set_item(obj: expr, item: None | str | bytes | bool | int | float | complex, value: expr) -> expr:
    return Call(
        func = get_attribute(obj, '__setitem__'),
        args = [Constant(value = item), value],
        keywords = []
    )

def get_globals() -> expr:
    return Call(
        func = Name(id = 'globals', ctx = Load()),
        args = [],
        keywords = []
    )

def get_locals() -> expr:
    return Call(
        func = Name(id = 'locals', ctx = Load()),
        args = [],
        keywords = []
    )

def set_global_variable(id: str, value: expr) -> expr:
    return set_item(get_globals(), id, value)

def get_global_variable(id: str) -> expr:
    return get_item(get_globals(), id)

def get_scope(scope: str) -> expr:
    return get_global_variable(scope)

def set_variable(id: str, value: expr, scope: str) -> expr:
    return set_item(get_scope(scope), id, value)

def get_variable(id: str, scope: str) -> expr:
    return get_item(get_scope(scope), id)

# TODO: make scopes be a list during runtime as well for pushing/popping
def add_scope(scopes: list[str], acc: list[expr]):
    scope = get_new_temp()
    scopes.append(scope)
    acc.append(set_global_variable(scope, get_locals()))

def rem_scope(scopes: list[str], acc: list[expr]):
    scopes.pop()

def wrap_exprs(exprs: list[expr]) -> expr:
    num_exprs = len(exprs)
    if num_exprs > 1:
        res = Tuple(elts = exprs, ctx = Load())
    elif num_exprs == 1:
        res = exprs[0]
    else:
        res = Tuple(elts = [], ctx = Load())

    return res

def transform_args(elts : list[Name]) -> list[arg]:
    return [arg(arg = elt.id) for elt in elts]

# TODO: add support for assigning to non-variable targets
    # non-variables can also appear in Tuple/List targets, handle using temp variables then the index/field attr update functions
def transform_assign(target: expr, value: expr, scopes: list[str], acc: list[expr]):
    match target:
        case Name(id = id):
            acc.append(set_variable(id, value, scopes[-1]))

        case Tuple(elts = elts) | List(elts = elts):
            if len(elts) > 1:
                temp = get_new_temp()
                acc.append(set_variable(temp, value, scopes[-1]))
                value = get_variable(temp)

            for i, elt in enumerate(elts):
                transform_assign(elt, get_item(value, i), scopes, acc)

def transform_assign_list(targets: list[expr], value: expr, scopes: list[str], acc: list[expr]):
    if len(targets) > 1:
        temp = get_new_temp()
        acc.append(set_variable(temp, value, scopes[-1]))
        value = get_variable(temp)

    for target in targets:
        transform_assign(target, value, scopes, acc)

def transform_import(names: list[alias], scopes: list[str], acc: list[expr]):
    for name in names:
        keywords = [
            keyword(
                arg = 'fromlist',
                value = List(elts = [Constant(value = None)], ctx = Load())
            ),
            keyword(
                arg = 'globals',
                value = get_globals()
            )
        ] if name.asname else [keyword(
            arg = 'globals',
            value = get_globals()
        )]
        bind = name.asname if name.asname else name.name
        module = Call(func = Name(id = '__import__', ctx = Load()), args = [Constant(value = name.name)], keywords = keywords)

        acc.append(set_variable(bind, module, scopes[-1]))

def transform_import_from(module: str | None, names: list[alias], level: int, scopes: list[str], acc: list[expr]):
    module_name = module if module else ''
    fromlist = [Constant(value = name.name) for name in names]
    keywords = [
        keyword(
            arg = 'fromlist',
            value = List(elts = fromlist, ctx = Load())
        ),
        keyword(
            arg = 'globals',
            value = get_globals()
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
    acc.append(set_variable(temp, module, scopes[-1]))
    for name in names:
        bind = name.asname if name.asname else name.name
        attr = get_attribute(get_variable(temp, scopes[-1]), name.name)
        acc.append(set_variable(bind, attr, scopes[-1]))

def transform_if(test: expr, body: list[stmt], orelse: list[stmt], scopes: list[str], acc: list[expr]):
    acc.append(IfExp(
        test = test,
        body = wrap_exprs(transform_stmts(body, 0, scopes, [])),
        orelse = wrap_exprs(transform_stmts(orelse, 0, scopes, []))
    ))

def transform_for(target: expr, iter: expr, body: list[stmt], orelse: list[stmt], scopes: list[str], acc: list[expr]):
    pass

def transform_while(test: expr, body: list[stmt], orelse: list[stmt], scopes: list[str], acc: list[expr]):
    pass

def transform_stmt(stmts: list[stmt], pos: int, scopes: list[str], acc: list[expr]) -> list[expr]:
    match stmts[pos]:
        # Transforming expression statement (already one line)
        case Expr(value = value):
            # TODO: if value is a tuple, can unpack to avoid unneeded nesting
            acc.append(value)
            return transform_stmts(stmts, pos + 1, scopes, acc)

        # Transforming any assignment statement
        case Assign(targets = targets, value = value):
            transform_assign_list(targets, value, scopes, acc)
            return transform_stmts(stmts, pos + 1, scopes, acc)
        
        # Transforming basic imports with optional aliases
        case Import(names = names):
            transform_import(names, scopes, acc)
            return transform_stmts(stmts, pos + 1, scopes, acc)
        
        # Transforming from imports with optional aliases
        # TODO: implement *; this can happen after iteration is implemented
        case ImportFrom(module = module, names = names, level = level):
            transform_import_from(module, names, level, scopes, acc)
            return transform_stmts(stmts, pos + 1, scopes, acc)
        
        # Transforming if-elif-else statements
        case If(test = test, body = body, orelse = orelse):
            transform_if(test, body, orelse, scopes, acc)
            return transform_stmts(stmts, pos + 1, scopes, acc)
        
        case For(target = target, iter = iter, body = body, orelse = orelse):
            transform_for(target, iter, body, orelse, scopes, acc)
            return transform_stmts(stmts, pos + 1, scopes, acc)

        case While(test = test, body = body, orelse = orelse):
            transform_while(test, body, orelse, scopes, acc)
            return transform_stmts(stmts, pos + 1, scopes, acc)

def transform_stmts(stmts: list[stmt], start: int, scopes: list[str], acc: list[expr]) -> list[expr]:
    if start == len(stmts): return acc
    return transform_stmt(stmts, start, scopes, acc)

def transform_module(module: Module) -> AST:
    acc = []
    scopes = []
    add_scope(scopes, acc)
    add_loops(acc)
    body = wrap_exprs(transform_stmts(module.body, 0, scopes, acc))
    rem_scope(scopes, acc)
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
    print()