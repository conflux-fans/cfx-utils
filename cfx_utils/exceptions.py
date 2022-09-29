class InvalidNetworkId(ValueError):
    pass

class InvalidAddress(ValueError):
    pass

class InvalidBase32Address(InvalidAddress):
    """
    The supplied address is not a valid Base32 address, as defined in CIP-37
    """
    pass

class InvalidHexAddress(InvalidAddress):
    pass

class InvalidConfluxHexAddress(InvalidHexAddress):
    """
    The supplied hex address starts without 0x0, 0x1 or 0x8, which is required by conflux
    """
    pass

class InvalidEpochNumebrParam(ValueError):
    pass

class AddressNotMatch(ValueError):
    pass

class HexAddressNotMatch(AddressNotMatch):
    pass

class Base32AddressNotMatch(AddressNotMatch):
    """
    the supplied Base32Address does not satisfy some specific requirements, e.g. network id or address type
    """
    pass

class TokenError(ValueError):
    pass

class InvalidTokenValueType(TokenError):
    pass

class MismatchTokenUnit(TokenError):
    pass

class TokenUnitNotFound(TokenError):
    pass

class InvalidTokenValuePrecision(TokenError):
    """
    problem 
    """
    pass

class InvalidTokenOperation(TokenError):
    pass

class FloatWarning(UserWarning):
    pass

class NegativeTokenValueWarning(UserWarning):
    pass
