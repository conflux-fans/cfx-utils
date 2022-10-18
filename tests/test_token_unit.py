import decimal
import numbers
from typing import (
    Any,
    Type,
    Union,
)
import pytest
from cfx_utils.token_unit import (
    AbstractTokenUnit, Drip, CFX, GDrip, TokenUnitFactory
)
from cfx_utils.exceptions import (
    InvalidTokenOperation,
    InvalidTokenValueType,
    InvalidTokenValuePrecision,
    MismatchTokenUnit,
    FloatWarning,
    NegativeTokenValueWarning,
    TokenUnitNotFound
)

Wei = TokenUnitFactory.factory_base_unit("Wei")

def assert_type_and_value(instance: object, typ: Type[Any], val: Union[int, decimal.Decimal, float, AbstractTokenUnit[Drip]]) -> None:
    assert type(instance) == typ
    assert instance == val
    assert val == instance

def test_init():
    Drip(1)
    Drip.base_unit
    Drip(10**18)
    Drip(1)
    Drip("0x1f4515", 16)
    CFX(1)
    CFX(decimal.Decimal(1) / 10**18)
    CFX("0.000000001")
    
    with pytest.warns(FloatWarning):
        CFX(1.5)
    with pytest.warns(FloatWarning):
        Drip(1.0)
    with pytest.warns(NegativeTokenValueWarning):
        CFX(-100)

    with pytest.raises(InvalidTokenValueType):
        with pytest.warns(FloatWarning):
            Drip(1.5) # type: ignore
    with pytest.raises(InvalidTokenValueType):
        CFX("a") # type: ignore
    with pytest.raises(InvalidTokenValuePrecision):
        with pytest.warns(FloatWarning):
            CFX(10**(-18)) # type: ignore
    
def test_to():
    instance1 = Drip(1).to(CFX)
    assert_type_and_value(instance1, CFX, decimal.Decimal(1) / 10 ** 18)
    instance2 = CFX(1).to(Drip)
    assert_type_and_value(instance2, Drip, 10 ** 18)
    
    with pytest.raises(TokenUnitNotFound):
        CFX(3).to("ETH")
        
    with pytest.raises(MismatchTokenUnit):
        CFX(3).to(Wei)
        
def test_add_float():
    with pytest.raises(InvalidTokenOperation):
        with pytest.warns(FloatWarning):
            tmp = Drip(1) + 1.5
        
    with pytest.raises(InvalidTokenOperation):
        with pytest.warns(FloatWarning):
            tmp = 1.5 + Drip(1)
    
    with pytest.warns(FloatWarning):
        tmp = CFX(1) + 0.5
        assert_type_and_value(tmp, CFX, 1 + decimal.Decimal(0.5))
        assert_type_and_value(tmp, CFX, 1.5)

    with pytest.warns(FloatWarning):
        tmp =  0.5 + CFX(1)
        assert_type_and_value(tmp, CFX, 1 + decimal.Decimal(0.5))
        assert_type_and_value(tmp, CFX, 1.5)

    with pytest.raises(InvalidTokenOperation) as e:
        with pytest.warns(FloatWarning):
            tmp = CFX(1) + 1e-18

    with pytest.raises(InvalidTokenOperation) as e:
        with pytest.warns(FloatWarning):
            tmp = 1e-18 + CFX(1)

def test_add_different_unit():
    tmp = Drip(1) + CFX(1)

    assert_type_and_value(tmp, Drip, 1 + 10**18)
    tmp = Drip(1) + Drip(1)
    
    tmp =  CFX(1) + Drip(1)
    assert_type_and_value(tmp, Drip, 1 + 10**18)
    
    tmp = GDrip(1) + CFX(1)
    assert_type_and_value(tmp, Drip, 10**9 + 10**18)
    
    with pytest.raises(InvalidTokenOperation):
        m =  Wei(1) + CFX(1) # type: ignore

def test_equal():
    assert Drip(1) == CFX(1 / decimal.Decimal(10**18))
    assert GDrip(10**9) == CFX(1)
    
def test_mul():
    assert_type_and_value(CFX(2) * 2, CFX, 4)
    assert_type_and_value(2 * CFX(2), CFX, 4)
    with pytest.warns(FloatWarning):
        assert_type_and_value(CFX(2) * 0.5, CFX, 1)
    with pytest.raises(InvalidTokenOperation) as e:
        with pytest.warns(FloatWarning):
            tmp = CFX(2) * 1e-18
    assert "due to unexpected precision" in str(e)
    
    with pytest.raises(InvalidTokenOperation):
        tmp = CFX(2) * Drip(3) # type: ignore

def test_div():
    assert_type_and_value(CFX(1) / Drip(1), decimal.Decimal, 10**18)
    assert_type_and_value(CFX(1) / 10**18, CFX, Drip(1))
    with pytest.raises(InvalidTokenOperation):
        tmp = Drip(1) / Wei(1)

def test_repr():
    assert repr(CFX(1)) == "1 CFX"
    
def test_str():
    assert str(CFX(1)) == "1 CFX"
    with pytest.warns(FloatWarning):
        assert str(CFX(0.5)) == "0.5 CFX"
    assert str(CFX(1/decimal.Decimal(10**18))) == f"{1/decimal.Decimal(10**18)} CFX"

def test_sub():
    assert_type_and_value(CFX(2) - CFX(1), CFX, 1)
    assert_type_and_value(CFX(2) - 1, CFX, 1)
    assert_type_and_value(CFX(2) / 10**18 - Drip(1), Drip, 1)
    with pytest.warns(NegativeTokenValueWarning):
        assert_type_and_value(1 - CFX(2), CFX, -1)
        
    with pytest.raises(InvalidTokenOperation):
        tmp = Drip(1) - Wei(1)

def test_compare():
    assert CFX(2) < 5
    assert CFX(2) <= 3
    assert CFX(2) <= 2
    assert CFX(2) > 0
    
    assert 5 >= CFX(2)
    assert 3 > CFX(2)
    assert 2 >= CFX(2)
    assert 0 < CFX(2)
    
    assert Drip(10**19) >= CFX(1)
    assert Drip(10**19) > CFX(1)
    assert Drip(10**17) < CFX(1)
    assert Drip(10**18) <= CFX(1)
    assert CFX(1) != Wei(10**18)
    
    # NOTE: this is valid operation because python will interpret the follow to
    # Drip(10) > 5 and 5 > CFX(2)
    # However, 5 has different meanings in different context, Users should be careful to use chained comparison on token values
    assert Drip(10) > 5 > CFX(2)

def test_value():
    assert_type_and_value(CFX(2).value, decimal.Decimal, 2)
    assert_type_and_value(Drip(2).value, int, 2)
    tmp = Drip(2)
    tmp.value = 3
    assert_type_and_value(tmp, Drip, 3)
    with pytest.warns(FloatWarning):
        tmp.value = 3.0
    with pytest.raises(InvalidTokenValueType):
        tmp.value = 0.5