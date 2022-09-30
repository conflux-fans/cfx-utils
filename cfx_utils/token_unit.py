import abc
from typing import (
    Any,
    Dict,
    Type,
    Union,
    TypeVar,
    cast,
    overload,
    Generic
)

import decimal
import numbers
from typing_extensions import (
    Self
)
import warnings
from cfx_utils.decorators import (
    combomethod
)
from cfx_utils.exceptions import (
    InvalidTokenValueType,
    InvalidTokenValuePrecision,
    InvalidTokenOperation,
    MismatchTokenUnit,
    FloatWarning,
    NegativeTokenValueWarning,
    TokenUnitNotFound,
)

AnyTokenUnit = TypeVar("AnyTokenUnit", bound="AbstractTokenUnit")
BaseTokenUnit = TypeVar("BaseTokenUnit", bound="AbstractBaseTokenUnit")
T = TypeVar("T")

# wraps exceptions took place when doing token operations
def token_operation_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (InvalidTokenValueType, InvalidTokenValuePrecision, MismatchTokenUnit) as e:
            if isinstance(e, InvalidTokenValueType):
                raise InvalidTokenOperation(f"Not able to execute operation {func.__name__} on {args} due to invalid argument type")
            elif isinstance(e, InvalidTokenValuePrecision):
                raise InvalidTokenOperation(f"Not able to execute operation {func.__name__} on {args} due to unexpected precision")
            elif isinstance(e, MismatchTokenUnit):
                raise InvalidTokenOperation(MismatchTokenUnit)
    return wrapper

# a decorator to warn float argument usage such as
# cls.classmethod(float_value)
# self.method(float_value)
def warn_float_value(func):
    def wrapper(*args, **kwargs):
        assert len(args) == 2
        cls_or_self = args[0]
        cast(Type[AbstractTokenUnit], cls_or_self)
        cls_or_self._warn_float_value(args[1])
        return func(*args, **kwargs)
    return wrapper


class AbstractTokenUnit(Generic[BaseTokenUnit], numbers.Number):

    decimals: int
    base_unit: Type[BaseTokenUnit]
    _value: Union[int, decimal.Decimal]
    
    @abc.abstractmethod
    def __init__(self, value: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float]):
        if isinstance(value, AbstractTokenUnit):
            self._value = value.to_base_unit()._value
            return
        elif isinstance(value, float):
            raise Exception("unreachable")
        else:
            self._value = value
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    @abc.abstractmethod
    def value(self, value):
        self._value = value

    @overload
    def to(self, target_unit: str) -> "AbstractTokenUnit[BaseTokenUnit]":
        ...
    
    @overload
    def to(self, target_unit: Type[AnyTokenUnit]) -> AnyTokenUnit:
        ...
    
    def to(self, target_unit: Union[str, Type[AnyTokenUnit]]) -> AnyTokenUnit:
        """
        return a new TokenUnit object in target_unit

        :param Union[str, Type[AnyTokenUnit]] target_unit: _description_
        :raises ValueError: _description_
        :raises InvalidTokenValuePrecision: _description_
        :return AnyTokenUnit: _description_
        """        
        # self -> base --> target
        if isinstance(target_unit, str):
            target_unit = cast(Type[AnyTokenUnit], self.base_unit.derived_units.get(target_unit, target_unit))
            # if no type object is found, 
            if isinstance(target_unit, str):
                raise TokenUnitNotFound(f"Cannot convert {type(self)} to {target_unit} because {target_unit} is not registered")
        else:
            if target_unit.base_unit != self.base_unit:
                raise MismatchTokenUnit(f"Cannot convert {type(self)} to {target_unit} because of different token unit")
        
        value = decimal.Decimal(self._value) * decimal.Decimal(10**self.decimals) / decimal.Decimal(10**target_unit.decimals) # type: ignore
        if issubclass(target_unit, AbstractBaseTokenUnit):
            if value % 1 != 0:
                # expected to be unreachable because check is done when self is inited
                raise InvalidTokenValuePrecision("Unreachable")

        # conversion_factor = self.base_unit.derived_units_conversions[target_unit]
        return cast(AnyTokenUnit, target_unit(value))
    
    def to_base_unit(self) -> BaseTokenUnit:
        return self.to(self.base_unit)
    
    @combomethod
    def _check_value(cls, value):
        return decimal.Decimal(value) * (10**cls.decimals) % 1 == 0
    
    @combomethod
    def _warn_float_value(cls, value):
        if isinstance(value, float):
            warnings.warn(f"{float} {value} is used to init token value, which might result in potential precision problem", FloatWarning)
        
    @combomethod
    def _warn_negative_token_value(cls, value):
        if value < 0:
            warnings.warn(f"A negative value {value} is found to init token value, please check if it is expected.", NegativeTokenValueWarning)

    @warn_float_value
    def __eq__(self, other: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float]) -> bool:
        # note we use type() here
        if isinstance(other, AbstractTokenUnit):
            return self.base_unit == other.base_unit and self.to_base_unit()._value == other.to_base_unit()._value
        return self._value == other
    
    @warn_float_value
    def __lt__(self, other: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float]) -> bool:
        if type(self) == type(other):
            return self._value < other._value # type: ignore
        if isinstance(other, AbstractTokenUnit):
            if self.base_unit != other.base_unit:
                raise MismatchTokenUnit(f"Cannot compare token value with different base unit {other.base_unit} and {self.base_unit}")
        return self._value < self.__class__(other)._value
    
    @warn_float_value
    def __le__(self, other: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float]) -> bool:
        return not (self > other)
    
    @warn_float_value
    def __gt__(self, other: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float]) -> bool:
        if type(self) == type(other):
            return self._value < other._value # type: ignore
        if isinstance(other, AbstractTokenUnit):
            if self.base_unit != other.base_unit:
                raise MismatchTokenUnit(f"Cannot compare token value with different base unit {other.base_unit} and {self.base_unit}")
        return self._value > self.__class__(other)._value
    
    @warn_float_value
    def __ge__(self, other: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float]) -> bool:
        return not (self < other)
    
    def __str__(self):
        return f"{self._value} {self.__class__.__name__}"
    
    def __repr__(self):
        return f"{self._value} {self.__class__.__name__}"
    
    @overload
    def __add__(self, other: Self) -> Self:
        ...
    
    @overload
    def __add__(self, other: "AbstractTokenUnit[Self]") -> Self: # type: ignore
        # self is base token unit
        ...
        
    @overload
    def __add__(self, other: "AbstractTokenUnit[BaseTokenUnit]") -> BaseTokenUnit:
        ...
    
    @overload
    def __add__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        ...

    @warn_float_value
    @token_operation_error
    def __add__( # type: ignore
        self, 
        other: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float]
    ) -> Union[BaseTokenUnit, Self]:
        if isinstance(other, AbstractTokenUnit):
            if other.base_unit != self.base_unit:
                raise MismatchTokenUnit(f"Cannot add token value with different base token unit {other.base_unit} and {self.base_unit}")
            if other.__class__ != self.__class__:
                return self.to_base_unit() + other.to_base_unit()
            return self.__class__(
                    decimal.Decimal(self._value) + decimal.Decimal(other._value) 
                )
        return self + self.__class__(other)

    # int/float/decimal.Decimal + CFX(1)
    @warn_float_value
    @token_operation_error
    def __radd__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        return self + other
    
    @overload
    def __sub__(self, other: Self) -> Self:
        ...
    
    @overload
    def __sub__(self, other: "AbstractTokenUnit[Self]") -> Self: # type: ignore
        # self is base token unit
        ...
        
    @overload
    def __sub__(self, other: "AbstractTokenUnit[BaseTokenUnit]") -> BaseTokenUnit:
        ...
    
    @overload
    def __sub__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        ...

    @warn_float_value
    @token_operation_error
    def __sub__( # type: ignore
        self, 
        other: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float]
    ) -> Union[BaseTokenUnit, Self]:
        if isinstance(other, AbstractTokenUnit):
            if other.base_unit != self.base_unit:
                raise MismatchTokenUnit(f"Cannot add token value with different base token unit {other.base_unit} and {self.base_unit}")
            if other.__class__ != self.__class__:
                return self.to_base_unit() - other.to_base_unit()
            return self.__class__(
                    decimal.Decimal(self._value) - decimal.Decimal(other._value) 
                )
        return self.__class__(self._value - decimal.Decimal(other))

    # int/float/decimal.Decimal - CFX(1)
    @warn_float_value
    @token_operation_error
    def __rsub__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        return  self.__class__(other) - self
    
    @warn_float_value
    @token_operation_error
    def __mul__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        if isinstance(other, AbstractTokenUnit):
            raise InvalidTokenOperation(f"{self.__class__} is not allowed to multiply a token unit")
        return self.__class__(self._value * decimal.Decimal(other))
    
    @warn_float_value
    @token_operation_error
    def __rmul__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        if isinstance(other, AbstractTokenUnit):
            raise InvalidTokenOperation(f"{self.__class__} is not allowed to multiply a token unit")
        return self.__class__(self._value * decimal.Decimal(other))
    
    @overload
    def __truediv__(self, other: "AbstractTokenUnit") -> decimal.Decimal:
        ...
    
    @overload
    def __truediv__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        ...

    @warn_float_value
    @token_operation_error
    def __truediv__( # type: ignore
        self, 
        other: Union["AbstractTokenUnit", int, decimal.Decimal, float]
    ) -> Union[Self, decimal.Decimal]:
        if isinstance(other, AbstractTokenUnit):
            if other.base_unit != self.base_unit:
                raise MismatchTokenUnit(f"Cannot operate __div__ on token values with different base token unit {other.base_unit} and {self.base_unit}")
            if other.__class__ != self.__class__:
                return self.to_base_unit() / other.to_base_unit()
            return decimal.Decimal(self._value) / decimal.Decimal(other._value)
        return self.__class__(self._value / decimal.Decimal(other))
    
    def __hash__(self):
        return hash(str(self))

class AbstractDerivedTokenUnit(AbstractTokenUnit[BaseTokenUnit], abc.ABC):
    decimals: int
    _value: decimal.Decimal
    
    def __init__(self, value: Union[int, decimal.Decimal, str, float, AbstractTokenUnit[BaseTokenUnit]]):
        if isinstance(value, AbstractTokenUnit):
            super().__init__(value)
            return
        
        self.value = value

    @property
    def value(self) -> decimal.Decimal:
        return self._value

    @value.setter
    @warn_float_value
    def value(self, value: Union[int, decimal.Decimal, str, float]):
        cls = self.__class__
        try:
            value = decimal.Decimal(value)
        except:
            raise InvalidTokenValueType(f"Not able to initialize {cls} with {type(value)} {value}. "
                                        f"{int} or {decimal.Decimal} typed value is recommended")
        
        # Token Value is of great importance, so we always check value validity
        if not self._check_value(value):
            raise InvalidTokenValuePrecision(f"Not able to initialize {cls} with {type(value)} {value} due to unexpected precision. "
                                  f"Try represent {value} in {decimal.Decimal} properly, or init token value in int from {cls.base_unit}")
        self._warn_negative_token_value(value)
        self._value = value


class AbstractBaseTokenUnit(AbstractTokenUnit, abc.ABC):
    derived_units: Dict[str, Type["AbstractTokenUnit"]] = {}
    decimals: int = 0
    base_unit: Type[Self]
    _value: int

    @overload
    def __init__(self, value: str, base: int=10):
        ...
    
    @overload
    def __init__(self, value: Union[int, decimal.Decimal, float, AbstractTokenUnit]):
        ...
    
    def __init__(self, value: Union[str, int, decimal.Decimal, float, AbstractTokenUnit], base:int = 10):  # type: ignore
        cls = self.__class__
        if isinstance(value, AbstractTokenUnit):
            super().__init__(value)
            return
        if isinstance(value, str):
            value = int(value, base)
        self.value = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    @warn_float_value
    def value(self, value):
        if value % 1 != 0:
            raise InvalidTokenValueType(f"An integer is expected to init {self.__class__}, "
                             f"received type {type(value)} argument: {value}")
        value = int(value)
        self._warn_negative_token_value(value)
        self._value = value

    
    @classmethod
    def register_derived_units(cls, derived_unit: Type["AbstractDerivedTokenUnit"]):
        cls.derived_units[derived_unit.__name__] = derived_unit

# This class is unused because type hint is not friendly if registered by factory
# Drip = TokenUnitFactory.factory_base_unit("Drip")
# CFX = TokenUnitFactory.factory_derived_unit("CFX", 18, Drip)
class TokenUnitFactory:
    @classmethod
    def factory_derived_unit(cls, unit_name: str, decimals: int, base_unit: Type["AbstractBaseTokenUnit"]):
        DerivedUnit = type(
            unit_name, 
            (AbstractDerivedTokenUnit,), 
            {
                "decimals": decimals,
                "base_unit": base_unit
            }
        )
        base_unit.register_derived_units(DerivedUnit)
        return DerivedUnit
    
    @classmethod
    def factory_base_unit(cls, unit_name: str):
        BaseUnit = type(
            unit_name,
            (AbstractBaseTokenUnit,),
            {},
        )
        BaseUnit.derived_units[unit_name] = BaseUnit
        BaseUnit.base_unit = BaseUnit
        return BaseUnit


# TODO: use metaclass to create class Drip, CFX and GDrip
class Drip(AbstractBaseTokenUnit):
    pass
Drip.base_unit = Drip
Drip.derived_units["Drip"] = Drip

class CFX(AbstractDerivedTokenUnit[Drip]):
    decimals: int = 18
    base_unit = Drip
Drip.register_derived_units(CFX)

class GDrip(AbstractDerivedTokenUnit[Drip]):
    decimals: int = 9
    base_unit = Drip
Drip.register_derived_units(GDrip)

@overload
def to_int_if_drip_units(value: AbstractTokenUnit) -> int:
    ...

@overload
def to_int_if_drip_units(value: T) -> T:
    ...

def to_int_if_drip_units(value: Union[AbstractTokenUnit, T]) -> Union[int, T]:
    if isinstance(value, AbstractTokenUnit):
        # MismatchTokenUnit might arise
        return value.to(Drip).value
    return value
