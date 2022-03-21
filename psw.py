def koren(x, n):
    for i in range(x):
        if i ** n == x:
            return i
print(koren(27, 3))