g=3

(lambda f, g, x:
    f()
)(lambda: g(f, g), lambda f, g: x + 1, 4)