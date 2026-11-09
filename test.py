res = 1
def test_fun1():
    global res
    res = 2

print(res)
test_fun1()
print(res)