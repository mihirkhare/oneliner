# NOTE: THESE MUST GO BEFORE ALL IMPORTS (at start of module translation)
# globals()['0'] = {'StopIteration': StopIteration}
class WhileIter:
    stop = StopIteration
    def __init__(self, guard, indicator, scope) -> None:
        self.guard = guard
        self.indicator = indicator
        self.scope = scope
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.scope[self.indicator] or not self.guard(self.scope): raise self.stop
        return self.scope

import builtins
old_iter = iter
def new_iter(iterable):
    print(333)
    return old_iter(iterable)
builtins.iter = new_iter
builtins.StopIteration = None

x = 0
locals()['0'] = False
[(scope.__setitem__('x', scope['x'] + 1), print(scope['x'])) for scope in WhileIter((lambda scope: scope['x'] < 5), '0', locals())]
# [(scope.__setitem__('x', scope['x'] + 1), print(scope['x'])) for scope in WhileIter((lambda scope: True), '0', locals())]
# loop = lambda scope: (scope.__setitem__('x', scope['x'] + 1), print(scope['x']), False)[-1] if scope['x'] < 5 else (True, )[-1]

# trial = WhileIter(loop, locals())

# [None for _ in trial]