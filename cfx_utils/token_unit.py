import abc
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Type,
    Union,
    TypeVar,
    cast,
    overload,
    Generic,
    Callable,
    ClassVar,
)

import decimal
import numbers
import functools
from typing_extensions import (
    Self,
    ParamSpec,
    Literal,
)
import warnings
from cfx_utils.decorators import combomethod
from cfx_utils.exceptions import (
    DangerEqualWarning,
    InvalidTokenValueType,
    InvalidTokenValuePrecision,
    InvalidTokenOperation,
    TokenUnitNotMatch,
    FloatWarning,
    NegativeTokenValueWarning,
    TokenUnitNotFound,
)

BaseTokenUnit = TypeVar("BaseTokenUnit", bound="AbstractBaseTokenUnit")
AnyTokenUnit = TypeVar("AnyTokenUnit", bound="AbstractTokenUnit")

T = TypeVar("T")
P = ParamSpec("P")

# wraps exceptions took place when doing token operations
def token_operation_error(func: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except (
            InvalidTokenValueType,
            InvalidTokenValuePrecision,
            TokenUnitNotMatch,
        ) as e:
            if isinstance(e, InvalidTokenValueType):
                raise InvalidTokenOperation(
                    f"Not able to execute operation {func.__name__} on {args} due to invalid argument type"
                )
            elif isinstance(e, InvalidTokenValuePrecision):
                raise InvalidTokenOperation(
                    f"Not able to execute operation {func.__name__} on {args} due to unexpected precision"
                )
            else:  # isinstance(e, TokenUnitNotMatch):
                raise InvalidTokenOperation(TokenUnitNotMatch)

    return wrapper


# a decorator to warn float argument usage such as
# cls.classmethod(float_value)
# self.method(float_value)
def warn_float_value(func: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        assert len(args) == 2
        cls_or_self = args[0]
        cls_or_self._warn_float_value(args[1])  # type: ignore
        return func(*args, **kwargs)

    return wrapper


class AbstractTokenUnit(Generic[BaseTokenUnit], numbers.Number):
    """
    :class:`~AbstractTokenUnit` provides the implementation of token units computing operations,
    such as :meth:`__eq__`, :meth:`__le__`, :meth:`__add__`, etc.
    Token unit object can be directly used as transaction gas price or the value field of transaction.

    >>> from cfx_utils.token_unit import CFX, Drip
    >>> CFX(1)
    1 CFX
    >>> CFX(1).value
    1
    >>> Drip(1)
    1 Drip
    >>> CFX(1) == Drip(1) * 10**18
    True
    >>> Drip(1) / 2
    Traceback (most recent call last):
        ...
    cfx_utils.exceptions.InvalidTokenOperation: ...
    """

    _decimals: ClassVar[int]
    """
    The class variable to defining relation between current token unit and :attr:`~_base_unit`.
    
    >>> from cfx_utils import CFX, Drip
    >>> CFX._decimals
    18
    >>> Drip._decimals
    0
    """
    _base_unit: Type[BaseTokenUnit]
    """
    A class variable which is a class object referring to the base unit
    
    >>> from cfx_uitls import CFX
    >>> CFX._base_unit
    <class 'cfx_utils.token_unit.Drip'>
    """
    _value: Union[int, decimal.Decimal]

    @abc.abstractmethod
    def __init__(
        self,
        value: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float],
    ):
        if isinstance(value, AbstractTokenUnit):
            self._value = value.to_base_unit().value
            return
        elif isinstance(value, float):
            raise Exception("unreachable")
        else:
            self._value = value

    @property
    def value(self):
        return self._value

    @overload
    def to(self, target_unit: str) -> "AbstractTokenUnit[BaseTokenUnit]":
        ...

    @overload
    def to(self, target_unit: Type[AnyTokenUnit]) -> AnyTokenUnit:
        ...

    def to(
        self, target_unit: Union[str, Type[AnyTokenUnit]]
    ) -> Union[AnyTokenUnit, "AbstractTokenUnit[BaseTokenUnit]"]:
        """
        Return a new TokenUnit object in target_unit

        :param Union[str,Type[AnyTokenUnit]] target_unit: the target token unit to convert to
        :return: a new token unit object of target unit

        :examples:

        >>> from cfx_utils.token_unit import CFX, GDrip
        >>> val = CFX(1)
        >>> val.to(GDrip)
        1000000000 GDrip
        >>> val.to("Drip")
        1000000000000000000 Drip
        """
        # self -> base --> target
        if isinstance(target_unit, str):
            target_unit = cast(
                Type[AnyTokenUnit],
                self._base_unit.get_derived_units_dict().get(target_unit, target_unit),
            )
            # if no type object is found,
            if isinstance(target_unit, str):
                raise TokenUnitNotFound(
                    f"Cannot convert {type(self)} to {target_unit} because {target_unit} is not registered"
                )
        else:
            if target_unit._base_unit != self._base_unit:
                raise TokenUnitNotMatch(
                    f"Cannot convert {type(self)} to {target_unit} because of different token unit"
                )

        value = (
            decimal.Decimal(self._value)
            * decimal.Decimal(10**self._decimals)
            / decimal.Decimal(10**target_unit._decimals)
        )
        if issubclass(target_unit, AbstractBaseTokenUnit):
            if value % 1 != 0:
                # expected to be unreachable because check is done when self is inited
                raise InvalidTokenValuePrecision("Unreachable")

        # conversion_factor = self._base_unit.derived_units_conversions[target_unit]
        return cast(AnyTokenUnit, target_unit(value))

    def to_base_unit(self) -> BaseTokenUnit:
        """
        Return a new token unit object in :attr:`~_base_unit`

        :examples:

        >>> from cfx_utils import CFX
        >>> CFX(1).to_base_unit()
        1000000000000000000 Drip
        """
        return self.to(self._base_unit)

    @combomethod
    def _check_value(cls, value: Union[int, float, decimal.Decimal]) -> None:
        return decimal.Decimal(value) * (10**cls._decimals) % 1 == 0

    @combomethod
    def _warn_float_value(cls, value: Any) -> None:
        if isinstance(value, float):
            warnings.warn(
                f"{float} {value} is used to init token value, which might result in potential precision problem",
                FloatWarning,
            )

    @combomethod
    def _warn_negative_token_value(
        cls, value: Union[int, float, decimal.Decimal]
    ) -> None:
        if value < 0:
            warnings.warn(
                f"A negative value {value} is found to init token value, please check if it is expected.",
                NegativeTokenValueWarning,
            )

    @warn_float_value
    def __eq__(self, other: Union["AbstractTokenUnit[BaseTokenUnit]", Literal[0]]) -> bool:  # type: ignore
        """
        Whether self equals to other.
        other is supposed to be a token unit or :const:`0`. Other values are also viable but the result might be not as expected.
        If other is not a token unit nor :const:`0`, :const:`False` will always be returned.

        :raises DangerEqualWarning: when the compared param is not `0` nor token unit

        >>> CFX(0) == 0
        True
        >>> CFX(1) == 1 # will raise a warning
        False
        >>> CFX(1).value == 1
        True
        >>> CFX(1) == Drip(10**18)
        True
        """
        if isinstance(other, AbstractTokenUnit):
            return (self._base_unit is other._base_unit) and (
                self.to_base_unit().value == other.to_base_unit().value
            )
        if other == 0:
            return self._value == 0
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, decimal.Decimal)
        ):
            warnings.warn(
                f"{self} is compared to {other}, which is not a token unit nor zero, and __eq__ will always return False. It is suggested that you should compare by visiting `.value` such as `CFX(1).value == 1`",
                DangerEqualWarning,
            )
        return False

    @warn_float_value
    def __lt__(
        self,
        other: Union["AbstractTokenUnit[BaseTokenUnit]", Literal[0]],
    ) -> bool:
        if type(self) == type(other):
            return self._value < other._value  # type: ignore
        if isinstance(other, AbstractTokenUnit):
            if self._base_unit != other._base_unit:
                raise TokenUnitNotMatch(
                    f"Cannot compare token value with different base unit {other._base_unit} and {self._base_unit}"
                )
            return self._value < self.__class__(other)._value
        if other == 0:
            return self._value < 0
        raise InvalidTokenOperation(
            f"not able to compare {self} and {other} because {other} is not a token unit"
        )
        # return self._value < self.__class__(other)._value

    @warn_float_value
    def __le__(
        self,
        other: Union["AbstractTokenUnit[BaseTokenUnit]", Literal[0]],
    ) -> bool:
        return not (self > other)

    @warn_float_value
    def __gt__(
        self,
        other: Union["AbstractTokenUnit[BaseTokenUnit]", Literal[0]],
    ) -> bool:
        if type(self) == type(other):
            return self._value > other._value  # type: ignore
        if other == 0:
            return self._value > 0
        if isinstance(other, AbstractTokenUnit):
            if self._base_unit != other._base_unit:
                raise TokenUnitNotMatch(
                    f"Cannot compare token value with different base unit {other._base_unit} and {self._base_unit}"
                )
            return self._value > self.__class__(other)._value
        raise InvalidTokenOperation(
            f"not able to compare {self} and {other} because {other} is not a token unit"
        )
        # return self._value > self.__class__(other)._value

    @warn_float_value
    def __ge__(
        self,
        other: Union["AbstractTokenUnit[BaseTokenUnit]", Literal[0]],
    ) -> bool:
        return not (self < other)

    def __str__(self):
        return f"{self._value} {self.__class__.__name__}"

    def __repr__(self):
        return f"{self._value} {self.__class__.__name__}"

    @overload
    def __add__(self, other: Self) -> Self:
        ...

    @overload
    def __add__(self, other: "AbstractTokenUnit[Self]") -> Self:  # type: ignore
        ...

    @overload
    def __add__(self, other: "AbstractTokenUnit[BaseTokenUnit]") -> BaseTokenUnit:  # type: ignore
        ...

    # @overload
    # def __add__(self, other: Union[int, decimal.Decimal, float]) -> Self:
    #     ...

    @token_operation_error
    def __add__(  # type: ignore
        self,
        other: "AbstractTokenUnit[BaseTokenUnit]",
    ) -> Union[BaseTokenUnit, Self]:
        """
        Add 2 object of :class:`AbstractTokenUnit` with same :attr:`_base_unit`.

        :raises TokenUnitNotMatch: The 2 objects are not in same :attr:`_base_unit`
        :raises InvalidTokenValueType: The added object is not a :class:`AbstractTokenUnit` object
        :returns Union[BaseTokenUnit, Self]: If 2 units are in the same unit, return the same.
            Else, return the result in :attr:`_base_unit`

        >>> from cfx_utils.token_unit import CFX, Drip, GDrip
        >>> CFX(1) + Drip(1)
        1000000000000000001 Drip
        >>> CFX(1) + CFX(1)
        2 CFX
        >>> GDrip(1) + CFX(1)
        1000000001000000000 Drip
        """
        if isinstance(other, AbstractTokenUnit):
            if other._base_unit != self._base_unit:
                raise TokenUnitNotMatch(
                    f"Cannot add token value with different base token unit {other._base_unit} and {self._base_unit}"
                )
            if other.__class__ != self.__class__:
                return self.to_base_unit() + other.to_base_unit()
            return self.__class__(
                decimal.Decimal(self._value) + decimal.Decimal(other._value)
            )
        raise InvalidTokenValueType
        # return self + self.__class__(other)

    # int/float/decimal.Decimal + CFX(1)
    # @warn_float_value
    # @token_operation_error
    # def __radd__(self, other: Union[int, decimal.Decimal, float]) -> Self:
    #     return self + other

    @overload
    def __sub__(self, other: Self) -> Self:
        ...

    @overload
    def __sub__(self, other: "AbstractTokenUnit[Self]") -> Self:  # type: ignore
        # self is base token unit
        ...

    @overload
    def __sub__(self, other: "AbstractTokenUnit[BaseTokenUnit]") -> BaseTokenUnit:  # type: ignore
        ...

    # @overload
    # def __sub__(self, other: Union[int, decimal.Decimal, float]) -> Self:
    #     ...

    @token_operation_error
    def __sub__(  # type: ignore
        self,
        other: "AbstractTokenUnit[BaseTokenUnit]",
    ) -> Union[BaseTokenUnit, Self]:
        """
        Sub :obj:`other` from :obj:`self` with same :attr:`_base_unit`.

        :raises TokenUnitNotMatch: The 2 objects are not in same :attr:`_base_unit`
        :raises InvalidTokenValueType: :obj:`other` is not a :class:`AbstractTokenUnit` object
        :raises NegativeTokenValueWarning: The value of the result is less than :const:`0`
        :returns Union[BaseTokenUnit, Self]: If 2 units are in the same unit, return the same.
            Else, return the result in :attr:`_base_unit`

        >>> from cfx_utils.token_unit import CFX, Drip, GDrip
        >>> CFX(1) - Drip(1)
        999999999999999999 Drip
        >>> CFX(1) - CFX(1)
        0 CFX
        >>> GDrip(1) - CFX(1) # will raise a warning
        -999999999000000000 Drip
        """
        if isinstance(other, AbstractTokenUnit):
            if other._base_unit != self._base_unit:
                raise TokenUnitNotMatch(
                    f"Cannot add token value with different base token unit {other._base_unit} and {self._base_unit}"
                )
            if other.__class__ != self.__class__:
                return self.to_base_unit() - other.to_base_unit()
            return self.__class__(
                decimal.Decimal(self._value) - decimal.Decimal(other._value)
            )
        raise InvalidTokenValueType
        # return self.__class__(self._value - decimal.Decimal(other))

    # int/float/decimal.Decimal - CFX(1)
    # @warn_float_value
    # @token_operation_error
    # def __rsub__(self, other: Union[int, decimal.Decimal, float]) -> Self:
    #     return self.__class__(other) - self

    @warn_float_value
    @token_operation_error
    def __mul__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        """
        Multiply :obj:`self` with :obj:`other`.

        :raises InvalidTokenOperation: :obj:`other` is a :class:`AbstractTokenUnit` object
            or the returned result will not be in a valid value
        :raises NegativeTokenValueWarning: The value of the result is less than :const:`0`
        :raises FloatWarning: The multiplied time is a float
        :returns Self: Returns the result in :class:`Self`

        >>> from cfx_utils.token_unit import Drip
        >>> Drip(1) * 2
        2 Drip
        >>> Drip(1) * 0.5 # will raise a warning and an error
        Traceback (most recent call last):
        ...
        cfx_utils.exceptions.InvalidTokenOperation: Not able to execute operation __mul__ on (1 Drip, 0.5) due to invalid argument type
        """
        if isinstance(other, AbstractTokenUnit):
            raise InvalidTokenOperation(
                f"{self.__class__} is not allowed to multiply a token unit"
            )
        return self.__class__(self._value * decimal.Decimal(other))

    @warn_float_value
    @token_operation_error
    def __rmul__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        if isinstance(other, AbstractTokenUnit):
            raise InvalidTokenOperation(
                f"{self.__class__} is not allowed to multiply a token unit"
            )
        return self.__class__(self._value * decimal.Decimal(other))

    @overload
    def __truediv__(self, other: "AbstractTokenUnit[BaseTokenUnit]") -> decimal.Decimal:
        ...

    @overload
    def __truediv__(self, other: Union[int, decimal.Decimal, float]) -> Self:
        ...

    @warn_float_value
    @token_operation_error
    def __truediv__(
        self,
        other: Union["AbstractTokenUnit[BaseTokenUnit]", int, decimal.Decimal, float],
    ) -> Union[Self, decimal.Decimal]:
        """
        Divide :obj:`self` with :obj:`other`. The :obj:`other` could be a number or
        another :class:`AbstractTokenUnit` object sharing same :attr:`_base_unit`.

        :raises TokenUnitNotMatch: Another :class:`AbstractTokenUnit` object is not in same :attr:`_base_unit`
        :raises InvalidTokenOperation: The returned result will not be in a valid value
        :raises NegativeTokenValueWarning: The value of the result is less than :const:`0`
        :raises FloatWarning: :obj:`other` is a float
        :returns Union[Self, decimal.Decimal]: Returns the result depending on the type of :obj:`other`

        >>> from cfx_utils.token_unit import Drip
        >>> Drip(1) / Drip(2)
        Decimal('0.5')
        >>> Drip(2) / 2
        1 Drip
        """
        if isinstance(other, AbstractTokenUnit):
            if other._base_unit != self._base_unit:
                raise TokenUnitNotMatch(
                    f"Cannot operate __div__ on token values with different base token unit {other._base_unit} and {self._base_unit}"
                )
            if other.__class__ != self.__class__:
                return decimal.Decimal(
                    self.to_base_unit().value / other.to_base_unit().value
                )
            return decimal.Decimal(self._value) / decimal.Decimal(other._value)
        return self.__class__(self._value / decimal.Decimal(other))

    def __hash__(self):
        return hash(str(self))


class AbstractDerivedTokenUnit(AbstractTokenUnit[BaseTokenUnit]):
    _decimals: ClassVar[int]
    _value: decimal.Decimal

    def __init__(
        self,
        value: Union[
            int, decimal.Decimal, str, float, AbstractTokenUnit[BaseTokenUnit]
        ],
    ):
        if isinstance(value, AbstractTokenUnit):
            super().__init__(value)
            return
        # set using value setter
        self.value = value

    @property
    def value(self) -> decimal.Decimal:
        """
        Returns the token value as decimal.Decimal.

        :return decimal.Decimal: returns the token value

        Can be set using an int, decimal.Decimal, str or float

        :raises FloatWarning: it is recommended to use decimal.Decimal,
            when a float-typed value is used to set value, a warning will be raised
        :raises InvalidTokenValueType: the value type is not int, Decimal, str or float
        :raises InvalidTokenValuePrecision: the value cannot be divided
            exactly by its base unit

        :examples:

        >>> from cfx_utils import CFX
        >>> val = CFX(1)
        >>> val.value = 0.5 # will raise a FloatWarning
        >>> val
        0.5 CFX
        >>> val.value = 1/3
        Traceback (most recent call last):
            ...
        cfx_utils.exceptions.InvalidTokenValuePrecision: Not able to initialize <class 'cfx_utils.token_unit.CFX'>
        with <class 'decimal.Decimal'> 0.333333333333333314829616256247390992939472198486328125 due to unexpected precision.
        Try representing 0.333333333333333314829616256247390992939472198486328125 in <class 'decimal.Decimal'> properly,
        or init token value in int from <class 'cfx_utils.token_unit.Drip'>
        """
        return self._value

    @value.setter
    def value(self, value: Union[int, decimal.Decimal, str, float]) -> None:
        self._warn_float_value(value)
        cls = self.__class__
        try:
            value = decimal.Decimal(value)
        except:
            raise InvalidTokenValueType(
                f"Not able to initialize {cls} with {type(value)} {value}. "
                f"{int} or {decimal.Decimal} typed value is recommended"
            )

        # Token Value is of great importance, so we always check value validity
        if not self._check_value(value):
            raise InvalidTokenValuePrecision(
                f"Not able to initialize {cls} with {type(value)} {value} due to unexpected precision. "
                f"Try representing {value} in {decimal.Decimal} properly, or init token value in int from {cls._base_unit}"
            )
        self._warn_negative_token_value(value)
        self._value = value


class AbstractBaseTokenUnit(AbstractTokenUnit[Self], abc.ABC):
    _derived_units: Dict[str, Type["AbstractTokenUnit[Self]"]] = {}
    _decimals: ClassVar[int] = 0
    _base_unit: Type[Self]
    _value: int

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: Union[int, decimal.Decimal, float]) -> None:
        self._warn_float_value(value)
        if value % 1 != 0:
            raise InvalidTokenValueType(
                f"An integer is expected to init {self.__class__}, "
                f"received type {type(value)} argument: {value}"
            )
        value = int(value)
        self._warn_negative_token_value(value)
        self._value = value

    @overload
    def __init__(self, value: str, base: int = 10):
        ...

    @overload
    def __init__(
        self, value: Union[int, decimal.Decimal, float, AbstractTokenUnit[Self]]
    ):
        ...

    def __init__(
        self,
        value: Union[str, int, decimal.Decimal, float, AbstractTokenUnit[Self]],
        base: int = 10,
    ):
        """
        Initialize a token object of base unit (e.g. Drip). The minimum unit is 1.
        Error will be raised if `value` and `base` are not valid.

        :param Union[str,int,decimal.Decimal,float,AbstractTokenUnit[Self]] value:
            value to init the token, should be a number which can convert to int or
            another token unit which share the same
        :param int base: base to init a str-typed value, defaults to 10

        >>> from cfx_utils.token_unit import Drip
        >>> Drip(10)
        10 Drip
        >>> Drip("0x10", base=16)
        16 Drip
        >>> Drip(0.5)
        """
        if isinstance(value, AbstractTokenUnit):
            super().__init__(value)
            return
        if isinstance(value, str):
            value = int(value, base)
        self.value = value  # type: ignore

    @classmethod
    def register_derived_unit(
        cls, derived_unit: Type["AbstractDerivedTokenUnit[Self]"]
    ) -> None:
        """
        Register a new derived token unit to a base unit

        :raises ValueError: if a token unit with the same name is already registered

        >>> from cfx_utils import Drip, AbstractDerivedTokenUnit
        >>> # The AbstractDerivedTokenUnit[Drip] is used for type hints
        >>> class uCFX(AbstractDerivedTokenUnit[Drip]):
        ...     _decimals = 12
        ...
        >>> Drip.register_derived_unit(uCFX)
        >>> uCFX(1)
        1 uCFX
        >>> uCFX(1).to_base_unit()
        1000000000000 Drip
        """
        if derived_unit.__name__ in cls._derived_units:
            raise ValueError
        derived_unit._base_unit = cls
        cls._derived_units[derived_unit.__name__] = derived_unit

    @classmethod
    def get_derived_units_dict(cls) -> Dict[str, Type["AbstractTokenUnit[Self]"]]:
        """
        :return Dict: returns a dict object containing `token_name -> token_unit_class` mapping

        >>> from cfx_utils.token_unit import Drip
        >>> Drip.get_derived_units_dict()
        {'Drip': <class 'cfx_utils.token_unit.Drip'>,
        'CFX': <class 'cfx_utils.token_unit.CFX'>,
        'GDrip': <class 'cfx_utils.token_unit.GDrip'>}
        """
        return cls._derived_units


# This class is unused because type hint is not friendly if registered by factory
# Drip = TokenUnitFactory.factory_base_unit("Drip")
# CFX = TokenUnitFactory.factory_derived_unit("CFX", 18, Drip)
class TokenUnitFactory:
    @classmethod
    def factory_derived_unit(
        cls, unit_name: str, decimals: int, base_unit: Type[BaseTokenUnit]
    ) -> Type["AbstractDerivedTokenUnit[BaseTokenUnit]"]:
        derived_unit = cast(
            Type[AbstractDerivedTokenUnit[type(base_unit)]],
            type(
                unit_name,
                (AbstractDerivedTokenUnit[type(base_unit)],),
                {"_decimals": decimals, "_base_unit": base_unit},
            ),
        )
        base_unit.register_derived_unit(derived_unit)
        return derived_unit

    @classmethod
    def factory_base_unit(cls, unit_name: str) -> Type["AbstractBaseTokenUnit"]:
        """
        it is generally not recommended to use this function if the units to be produced is used frequently
        because the type hints generated will somewhat not work as expected
        """
        BaseUnit = cast(
            Type["AbstractBaseTokenUnit"],
            type(
                unit_name,
                (AbstractBaseTokenUnit,),
                {},
            ),
        )
        BaseUnit.register_derived_unit(BaseUnit)  # type: ignore
        return BaseUnit


# TODO: use metaclass to create class Drip, CFX and GDrip

if TYPE_CHECKING:

    class Drip(AbstractBaseTokenUnit["Drip"]):
        pass

else:

    class Drip(AbstractBaseTokenUnit):
        """
        The base token unit used in Conflux, corresponding to Ethereum's Wei.
        :class:`~Drip` inherits from :class:`~AbstractTokenUnit`
        so it supports :meth:`__eq__`, :meth:`__le__`, :meth:`__add__`, etc.
        """

        pass

    Drip.register_derived_unit(Drip)


class CFX(AbstractDerivedTokenUnit[Drip]):
    """
    A derived token unit from :class:`~Drip` in Conflux, corresponding to Ethereum's Ether.
    :class:`~CFX` inherits from :class:`~AbstractTokenUnit`
    so it supports :meth:`__eq__`, :meth:`__le__`, :meth:`__add__`, etc.
    1 CFX = 10**18 Drip.
    """

    _decimals: ClassVar[int] = 18


Drip.register_derived_unit(CFX)


class GDrip(AbstractDerivedTokenUnit[Drip]):
    """
    A derived token unit from :class:`~Drip` in Conflux, which corresponds to Ethereum's GWei.
    1 GDrip = 10**9 Drip
    """

    _decimals: ClassVar[int] = 9


Drip.register_derived_unit(GDrip)


@overload
def to_int_if_drip_units(value: AbstractTokenUnit) -> int:  # type: ignore
    ...


@overload
def to_int_if_drip_units(value: T) -> T:
    ...


def to_int_if_drip_units(value: Union[AbstractTokenUnit[Drip], T]) -> Union[int, T]:
    """
    | A util function to convert token units derived from :class:`~Drip` to :class:`~int`.
    | If the input is in token unit derived from :class:`~Drip`,
        then return a int corresponding to token value in Drip.
    | Else return the original input

    >>> from cfx.token_unit import to_int_if_drip_units, CFX
    >>> to_int_if_drip_units(CFX(1))
    1000000000000000000
    >>> to_int_if_drip_units(10**18)
    1000000000000000000
    >>> to_int_if_drip_units("a string")
    'a string'
    """
    if isinstance(value, AbstractTokenUnit):
        # TokenUnitNotMatch might arise
        return value.to(Drip).value
    return value
