# Creates a list comp without a bound variable and uses it

l = [1 for _ in range(100)]
print(sum(l))