from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    NewType,
    TypedDict,
    Union,
    Literal
)

from hexbytes import (
    HexBytes,
)
from eth_typing.evm import (
    # Address,
    HexAddress,
    # ChecksumAddress,
    BlockNumber,
    ChecksumAddress,
    Hash32,
)
from eth_typing.encoding import (
    HexStr,
)

from cfx_utils.token_unit import (
    CFX,
    Drip,
    GDrip,
    AbstractDerivedTokenUnit,
)


if TYPE_CHECKING:
    # avoid recursive import
    from cfx_address import Base32Address

### copy-paste definition from web3
_Hash32 = Union[Hash32, bytes, HexStr, str]
Nonce = NewType("Nonce", int)
# copy-paste ended

Storage = NewType("Storage", int)

AddressParam = Union["Base32Address", str]

EpochLiteral = Literal[
    "earliest",
    "latest_checkpoint",
    "latest_finalized",
    "latest_confirmed",
    "latest_state",
    "latest_mined",
]
EpochNumber = NewType("EpochNumber", int)
EpochNumberParam = Union[EpochLiteral, EpochNumber, int]
"""Epoch param could be either EpochLiteral, or Epoch Number
"""

# ChainId = Union[int, HexStr]

# syntax b/c "from" keyword not allowed w/ class construction
TxDict = TypedDict(
    "TxDict",
    {
        "chainId": int,
        "data": Union[bytes, HexStr],
        # addr or ens
        "from": AddressParam,
        "gas": int,
        "gasPrice": Union[Drip, AbstractDerivedTokenUnit[Drip], int],
        "nonce": Nonce,
        "to": AddressParam,
        "value": Union[Drip, AbstractDerivedTokenUnit[Drip], int],
        "epochHeight": int,
        "storageLimit": Storage,
    },
    total=False,
)

TxParam = Union[TxDict, Dict[str, Any]]

__all__ = [
    "HexAddress",
    "HexBytes",
    "BlockNumber",
    "ChecksumAddress",
    "Hash32",
    "HexStr",
    "CFX",
    "Drip",
    "GDrip",
    "AbstractDerivedTokenUnit",
    "_Hash32",
    "Nonce",
    "Storage",
    "AddressParam",
    "EpochLiteral",
    "EpochNumber",
    "EpochNumberParam",
    "TxDict",
    "TxParam",
]
