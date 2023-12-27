class X:
    def __init__(self, h : int) -> None:
        self.h = h

x = X(4)
x.h = 3

x.__setattr__('h', 43)

a = ['42', 4]
a.__setitem__(0, 34)

print(a)