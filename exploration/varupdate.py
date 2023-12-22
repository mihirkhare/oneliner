f = (lambda: g())

try:
    print(f())
except:
    print('fail')

g = (lambda: 1)

try:
    print(f())
except:
    print('fail')