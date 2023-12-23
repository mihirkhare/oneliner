class X:
    a: int
    b: str

v = X()

v.a, v.b = 3, 4
v.a, v.b = v.b, v.a

print(v.a, v.b)