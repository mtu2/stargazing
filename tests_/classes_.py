class A:

    def __init__(self):
        self.val = "testing"

    def test(self):
        return self.val


if __name__ == "__main__":
    a = A()
    print(a.test())
