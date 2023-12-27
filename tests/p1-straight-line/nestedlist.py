# ((x, y), z) = ((3, 4), 5)
# t, z = ((3, 4), 5)
# x, y = t

# print(x, y, z)

i = ((3, 4), 5)

(lambda t, z: (lambda x, y: print(x, y, z))(*t))(*i)