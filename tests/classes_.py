class A:

    def __init__(self):
        self.val = "testing"

    def test(self):
        return self.val


class B(A):

    def __init__(self):
        super().__init__()

    def test_b(self):
        return self.val


if __name__ == "__main__":
    a = A()
    b = B()
    print(b.test_b())
