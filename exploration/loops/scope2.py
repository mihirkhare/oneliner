# # Original
# def x():
#     a = 1
#     def y():
#         nonlocal a
#         a += 1
#         return a
#     def z():
#         nonlocal a
#         a += 1
#         return a
#     return y, z
# a, b = x()
# print(a())
# print(b())
# print(a())
# print(b())
# c, d = x()
# print(c())
# print(d())
# print(c())
# print(d())

# Translated
temp0 = [locals()]
def x():
    temp1 = temp0 + [locals()]
    # scopes = temp1
    temp1[-1]['a'] = 1
    def y():
        print(temp1)
        temp2 = temp1 + [locals()]
        # scopes = temp2
        temp2[-2]['a'] += 1
        return temp2[-2]['a']
    def z():
        print(temp1)
        temp3 = temp1 + [locals()]
        # scopes = temp3
        temp3[-2]['a'] += 1
        return temp3[-2]['a']
    return y, z
a, b = x()
print(a())
print(b())
# print(a())
# print(b())
# c, d = x()
# print(c())
# print(d())
# print(c())
# print(d())