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
