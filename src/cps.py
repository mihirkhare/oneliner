# variables: dict[int, set[str]] = {1: set({**globals()}.keys())}  # initializing to names defined at module start
# scopes: list[int] = []
global_vars: set[str] = set({**globals()}.keys())

from ast import *
import sys

def read_file() -> str:
    with open(sys.argv[1], 'r') as f: return f.read()

def get_expr_defs(expr: expr, in_assign: bool, acc: set[str]):
    match expr:
        case BoolOp(values = values):
            get_exprs_defs(values, False, acc)
        
        case BinOp(left = left, right = right):
            get_expr_defs(left, False, acc)
            get_expr_defs(right, False, acc)

        case UnaryOp(operand = operand):
            get_expr_defs(operand, False, acc)
                
        case Lambda():
            return
                
        case IfExp(test = test, body = body, orelse = orelse):
            get_expr_defs(test, False, acc)
            get_expr_defs(body, False, acc)
            get_expr_defs(orelse, False, acc)
                
        case Dict(keys = keys, values = values):
            for key in keys:
                if key != None: get_expr_defs(key, False, acc)
            for value in values: get_expr_defs(value, False, acc)
                
        case Set(elts = elts):
            for elt in elts: get_expr_defs(elt, False, acc)
                
        case ListComp(elt = elt, generators = generators):
            get_expr_defs(elt, False, acc)
            for generator in generators: get_exprs_defs(generator.ifs, False, acc)
        
        case SetComp(elt = elt, generators = generators):
            get_expr_defs(elt, False, acc)
            for generator in generators: get_exprs_defs(generator.ifs, False, acc)
                
        case DictComp(key = key, value = value, generators = generators):
            get_expr_defs(key, False, acc)
            get_expr_defs(value, False, acc)
            for generator in generators: get_exprs_defs(generator.ifs, False, acc)
                
        case GeneratorExp(elt = elt, generators = generators):
            get_expr_defs(elt, False, acc)
            for generator in generators: get_exprs_defs(generator.ifs, False, acc)

        case Await(value = value):
            get_expr_defs(value, False, acc)

        case Yield(value = value):
            if value != None: get_expr_defs(value, False, acc)

        case YieldFrom(value = value):
            get_expr_defs(value, False, acc)
                
        case Compare(left = left, comparators = comparators):
            get_expr_defs(left, False, acc)
            get_exprs_defs(comparators, False, acc)
            
        case Call(func = func, args = args, keywords = keywords):
            get_expr_defs(func, False, acc)
            get_exprs_defs(args, False, acc)
            for keyword in keywords: get_expr_defs(keyword.value, False, acc)

        case FormattedValue(value = value, format_spec = format_spec):
            get_expr_defs(value, False, acc)
            if format_spec != None: get_expr_defs(format_spec, False, acc)
        
        case JoinedStr(values = values):
            get_exprs_defs(values, False, acc)
        
        case Constant():
            return
        
        case NamedExpr(target = target, value = value):
            acc.add(target.id)
            get_expr_defs(value, False, acc)

        case Attribute(value = value):
            get_expr_defs(value, False, acc)
        
        case Slice(lower = lower, upper = upper, step = step):
            get_expr_defs(lower, False, acc)
            get_expr_defs(upper, False, acc)
            get_expr_defs(step, False, acc)

        case Subscript(value = value, slice = slice):
            get_expr_defs(value, False, acc)
            get_expr_defs(slice, False, acc)

        case Starred(value = value):
            get_expr_defs(value, False, acc)

        case Name(id = id):
            if in_assign: acc.add(id)
        
        case List(elts = elts):
            get_exprs_defs(elts, in_assign, acc)

        case Tuple(elts = elts):
            get_exprs_defs(elts, in_assign, acc)

def get_exprs_defs(exprs: list[expr], in_assign: bool, acc: set[str]):
    for expr in exprs: get_expr_defs(expr, in_assign, acc)

def get_stmt_defs(stmt: stmt, acc: set[str]):
    match stmt:
        case FunctionDef():
            raise NotImplementedError('function definitions not yet implemented')
        
        case AsyncFunctionDef():
            raise NotImplementedError('async function definitions not yet implemented')
        
        case ClassDef():
            raise NotImplementedError('class definitions not yet implemented')
        
        case Return():
            raise NotImplementedError('return not yet implemented')
        
        case Delete():
            raise NotImplementedError('delete not yet implemented')

        # Transforming any assignment statement
        case Assign(targets = targets, value = value):
            get_exprs_defs(targets, True, acc)
            get_expr_defs(value, False, acc)
        
        case AugAssign():
            raise NotImplementedError('augmented assign not yet implemented')
        
        case AnnAssign():
            raise NotImplementedError('annotated assign not yet implemented')
        
        case For(target = target, iter = iter, body = body, orelse = orelse):
            get_expr_defs(target, True, acc)
            get_expr_defs(iter, False, acc)
            get_stmts_defs(body, acc)
            get_stmts_defs(orelse, acc)

        case AsyncFor():
            raise NotImplementedError('async for not yet implemented')

        case While(test = test, body = body, orelse = orelse):
            get_expr_defs(test, False, acc)
            get_stmts_defs(body, acc)
            get_stmts_defs(orelse, acc)
        
        # Transforming if-elif-else statements
        case If(test = test, body = body, orelse = orelse):
            get_expr_defs(test, False, acc)
            get_stmts_defs(body, acc)
            get_stmts_defs(orelse, acc)

        case With():
            raise NotImplementedError('with not yet implemented')
        
        case AsyncWith():
            raise NotImplementedError('async with not yet implemented')
        
        case Raise():
            raise NotImplementedError('raise not yet implemented')
        
        case Try():
            raise NotImplementedError('try not yet implemented')
        
        case TryStar():
            raise NotImplementedError('try* not yet implemented')
        
        case Assert():
            raise NotImplementedError('assert not yet implemented')
        
        # Transforming basic imports with optional aliases
        case Import(names = names):
            for name in names:
                if name.asname != None: acc.add(name.asname)
                else: acc.add(name.name)
        
        # Transforming from imports with optional aliases
        # TODO: implement *; this can happen after iteration is implemented
        case ImportFrom(names = names):
            for name in names:
                if name.asname != None: acc.add(name.asname)
                else: acc.add(name.name)

        case Global():
            raise NotImplementedError('global not yet implemented')
        
        case Nonlocal():
            raise NotImplementedError('nonlocal not yet implemented')

        # Transforming expression statement (already one line)
        case Expr(value = value):
            get_expr_defs(value, False, acc)

        case Pass():
            return
        
        case Break():
            return
        
        case Continue():
            return

def get_stmts_defs(stmts: list[stmt], acc: set[str]):
    for stmt in stmts: get_stmt_defs(stmt, acc)

# # TODO: to avoid having a crazy amount of temps, delete temps when not needed anymore
#     # potentially use a list variable as a stack
# temp_count = 0
# def get_new_temp() -> str:
#     global temp_count
#     temp_count += 1
#     return str(temp_count)

# def get_attribute(obj: expr, attr: str) -> expr:
#     return Attribute(value = obj, attr = attr, ctx = Load())

# def set_attribute(obj: expr, attr: str, value: expr) -> expr:
#     return Call(
#         func = get_attribute(obj, '__setattr__'),
#         args = [Constant(value = attr), value],
#         keywords = []
#     )

# def get_item(obj: expr, item: None | str | bytes | bool | int | float | complex) -> expr:
#     return Subscript(value = obj, slice = Constant(value = item), ctx = Load())

# def set_item(obj: expr, item: None | str | bytes | bool | int | float | complex, value: expr) -> expr:
#     return Call(
#         func = get_attribute(obj, '__setitem__'),
#         args = [Constant(value = item), value],
#         keywords = []
#     )

# def get_globals() -> expr:
#     return Call(
#         func = Name(id = 'globals', ctx = Load()),
#         args = [],
#         keywords = []
#     )

# def get_locals() -> expr:
#     return Call(
#         func = Name(id = 'locals', ctx = Load()),
#         args = [],
#         keywords = []
#     )

# def set_global_variable(id: str, value: expr) -> expr:
#     return set_item(get_globals(), id, value)

# def get_global_variable(id: str) -> expr:
#     return get_item(get_globals(), id)

# def get_scope(scope: str) -> expr:
#     return get_global_variable(scope)

# def set_variable(id: str, value: expr, scope: str) -> expr:
#     return set_item(get_scope(scope), id, value)

# def get_variable(id: str, scope: str) -> expr:
#     return get_item(get_scope(scope), id)

# # TODO: make scopes be a list during runtime as well for pushing/popping
# def add_scope(scopes: list[str], acc: list[expr]):
#     scope = get_new_temp()
#     scopes.append(scope)
#     acc.append(set_global_variable(scope, get_locals()))

# def rem_scope(scopes: list[str], acc: list[expr]):
#     scopes.pop()

# def wrap_exprs(exprs: list[expr]) -> expr:
#     num_exprs = len(exprs)
#     if num_exprs > 1:
#         res = Tuple(elts = exprs, ctx = Load())
#     elif num_exprs == 1:
#         res = exprs[0]
#     else:
#         res = Tuple(elts = [], ctx = Load())

#     return res

# while_temp = '-1'
# for_temp = '-2'
# def add_loops(acc: list[expr]):
#     base = Tuple(elts = [Name(id = 'object', ctx = Load())], ctx = Load())
#     attr_names = [Constant(value = 'stop'), Constant(value = '__init__'), Constant(value = '__iter__'), Constant(value = '__next__')]
#     stop = Name(id = 'StopIteration')
#     iter_body = parse('lambda self: self').body[0].value

#     # while
#     while_init_body = parse('lambda self, guard, indicator, scope: (self.__setattr__("guard", guard), self.__setattr__("indicator", indicator), self.__setattr__("scope", scope), None)[-1]').body[0].value
#     while_next_body = parse('lambda self: ([] for [] in []).throw(self.stop) if self.scope[self.indicator] or not self.guard(self.scope) else self.scope').body[0].value
#     while_dict = Dict(
#         keys = attr_names,
#         values = [stop, while_init_body, iter_body, while_next_body]
#     )
#     while_type = Call(
#         func = Name(id = 'type'),
#         args = [Constant(value = while_temp), base, while_dict],
#         keywords = []
#     )
#     acc.append(while_type)

#     # for
#     for_init_body = parse('lambda self, iterator, indicator, scope: (self.__setattr__("iterator", iterator.__iter__()), self.__setattr__("indicator", indicator), self.__setattr__("scope", scope), None)[-1]').body[0].value
#     for_next_body = parse('lambda self: ([] for [] in []).throw(self.stop) if self.scope[self.indicator] else (self.scope, self.iterator.__next__())').body[0].value
#     for_dict = Dict(
#         keys = attr_names,
#         values = [stop, for_init_body, iter_body, for_next_body]
#     )
#     for_type = Call(
#         func = Name(id = 'type'),
#         args = [Constant(value = for_temp), base, for_dict],
#         keywords = []
#     )
#     acc.append(for_type)

# def transform_expr(expr: expr | None, scopes: list[str]) -> expr | None:
#     # Dict keys may be none in the case of a dictionary unpacking inside a literal
#     if expr == None: return None

#     match expr:
#         case BoolOp(op = op, values = values):
#             return BoolOp(op = op, values = transform_exprs(values, scopes))
        
#         case BinOp(left = left, op = op, right = right):
#             return BinOp(left = transform_expr(left, scopes), op = op, right = transform_expr(right, scopes))
        
#         case UnaryOp(op = op, operand = operand):
#             return UnaryOp(op = op, operand = transform_expr(operand, scopes))
        
#         case Lambda():
#             return expr
        
#         case IfExp(test = test, body = body, orelse = orelse):
#             return IfExp(test = transform_expr(test, scopes), body = transform_expr(body, scopes), orelse = transform_expr(orelse, scopes))
        
#         case Dict(keys = keys, values = values):
#             return Dict(keys = transform_exprs(keys, scopes), values = transform_exprs(values, scopes))
        
#         case Set(elts = elts):
#             return Set(elts = transform_exprs(elts, scopes))
        
#         case ListComp(elt = elt, generators = generators):
#             raise NotImplementedError('Not Yet Implemented')
        
#         case DictComp(key = key, value = value, generators = generators):
#             raise NotImplementedError('Not Yet Implemented')
        
#         case GeneratorExp(elt = elt, generators = generators):
#             raise NotImplementedError('Not Yet Implemented')
        
#         case Await() | Yield() | YieldFrom():
#             raise NotImplementedError('Not Yet Implemented')
        
#         case Compare(left = left, ops = ops, comparators = comparators):
#             return Compare(left = transform_expr(left, scopes), ops = ops, comparators = transform_exprs(comparators, scopes))
        
#         case Call(func = func, )

# def transform_exprs(exprs: list[expr], scopes: list[str]) -> list[expr]:
#     return [transform_expr(expr, scopes) for expr in exprs]

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
        
        # case Break():
        #     acc.append(set_variable(kwargs['break'], Constant(value = True), scopes[-1]))

def transform_stmts(stmts: list[stmt], start: int, scopes: list[str], acc: list[expr]) -> list[expr]:
    if start == len(stmts): return acc
    return transform_stmt(stmts, start, scopes, acc)

def transform_module(module: Module) -> AST:
    acc = []
    get_stmts_defs(module, global_vars)
    variables: dict[int, set[str]] = {0: global_vars}
    scopes: list[int] = [0]
    # scopes = init_global(module_init_vars)
    # add_scope(scopes, acc)
    # add_loops(acc)
    # body = wrap_exprs(transform_stmts(module.body, 0, scopes, acc))
    # rem_scope(scopes, acc)
    # return Module(body = [Expr(value = body)], type_ignores = module.type_ignores)

if __name__ == '__main__':
    file = read_file()
    ast = parse(file)
    # res = set()
    # get_stmts_defs(ast.body, res)
    # print(res)


    print('print("Old ------------")')
    print(unparse(ast))
    print('print()')
    print()

    print('print("New ------------")')
    print(unparse(transform_module(ast)))
    print('print()')
    print()