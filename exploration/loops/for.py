

class ForIter:
    stop = StopIteration
    def __init__(self, iterator, indicator, scope) -> None:
        self.iterator = iterator.__iter__()
        self.indicator = indicator
        self.scope = scope
    
    def __iter__(self):
        return self

    def __next__(self):
        # if self.scope[self.indicator]: raise StopIteration
        if self.scope[self.indicator]: raise self.stop
        return self.scope, self.iterator.__next__()
    
locals()['0'] = False
# must set iterator vars in scope to match behavior of for loop not having a new scope
# must also delete vars from local lambda scope, so that

# translation of:
# for ind, i in enumerate(range(3, 54)):
#     if i > 30: break
#     print(i, ind)

__builtins__.StopIteration = Exception
[(scope.__setitem__('ind', ind), scope.__setitem__('i', i), (scope.__setitem__('0', True) if i > 30 else ()), (print(scope['i'], scope['ind']) if not scope['0'] else ())) for scope, (ind, i) in ForIter(enumerate(range(3, 54)), '0', locals())]