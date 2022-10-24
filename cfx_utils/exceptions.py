class InvalidNetworkId(ValueError):
    """
    An invaid network id is found to be used, which should be a positive integer
    """
    pass

class InvalidAddress(ValueError):
    """
    The supplied address is an illegal address
    """
    pass

class InvalidBase32Address(InvalidAddress):
    """
    The supplied address is not a valid Base32 address, as defined in CIP-37
    """
    pass

class InvalidHexAddress(InvalidAddress):
    """
    The supplied address is not a valid hex address
    """
    pass

class InvalidConfluxHexAddress(InvalidHexAddress):
    """
    The supplied hex address doesn't start with 0x0, 0x1 or 0x8, which is required by conflux
    """
    pass

class InvalidEpochNumebrParam(ValueError):
    """
    The epoch number param is invalid, which is supposed to be a non-negative integer or literal ['earliest', 'latest_checkpoint', 'latest_finalized', 'latest_confirmed', 'latest_state', 'latest_mined']
    """
    pass

class AddressNotMatch(ValueError):
    """
    The supplied address is legal, but does not satisfy some specific requirements, e.g. a Base32Address is expected 
    """
    pass

# class HexAddressNotMatch(AddressNotMatch):
#     pass

class Base32AddressNotMatch(AddressNotMatch):
    """
    The supplied Base32 address is legal, but does not satisfy some specific requirements, e.g. network id or address type
    """
    pass

class TokenError(ValueError):
    pass

class InvalidTokenValueType(TokenError):
    """
    Type of the supplied value is not valid, should be `int`/`float`/`decimal.Decimal` or `str` with base
    """
    pass

class TokenUnitNotMatch(TokenError):
    """
    Incompaible token units are operated together, which is not expected, e.g., Drip(1).to(Wei)
    """
    pass

# TODO: remove this line in formal release
MismatchTokenUnit = TokenUnitNotMatch

class TokenUnitNotFound(TokenError):
    """
    The supplied target unit is not found or not registered
    """
    pass

class InvalidTokenValuePrecision(TokenError):
    """
    The supplied variable value is invalid because a invalid float is used, e.g., CFX(1/3)
    """
    pass

class InvalidTokenOperation(TokenError):
    """
    Exception occured when operating token invalidly, typically it will wrap `InvalidTokenValueType`, `InvalidTokenValuePrecision`, and `TokenUnitNotMatch`. e.g. CFX(1) / 3
    """
    pass

class TokenValueWarning(UserWarning):
    pass

class DangerEqualWarning(UserWarning):
    """
    Token unit is compared to another number which is not a token unit
    """

class FloatWarning(TokenValueWarning):
    """
    `float` type number is found to be used, which should be avoided by using `decimal.Decimal`
    """
    pass

class NegativeTokenValueWarning(TokenValueWarning):
    """
    negative number is found to be used with token value, which is typically illegal and should be checked
    """
    pass
