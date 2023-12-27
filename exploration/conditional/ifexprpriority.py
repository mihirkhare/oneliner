def f():
    print('lol')
    return 0

def g():
    print('hihihi')
    return 0

print('Larger!') if f() > 4 else (print('Equal!') if g() == 4 else print('Smaller!'))