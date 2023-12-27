def f():
    return g()

try:
    print(f())
except:
    print('fail')

def g():
    return 1

try:
    print(f())
except:
    print('fail')