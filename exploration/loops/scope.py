# Original

# scopes = 1
# globals = 5
# while globals >= scopes:
#     if globals == scopes: break
#     z = scopes
#     globals -= 1
# print(scopes, globals, z)

# new
scopes = [globals()]
scopes

scopes[-1]['scopes'] = 1
scopes[-1]['globals'] = 5
while scopes[-1][]