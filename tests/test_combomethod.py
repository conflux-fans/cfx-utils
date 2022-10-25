from cfx_utils.decorators import combomethod

class A:
    @combomethod
    def a(self, i: int) -> int:
        return 1

def test_combomethod_type_hint():
    f1 = A.a
    f2 = A().a
    f1(1)
    f2(1)
