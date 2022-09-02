import sys
from typing import (
    TYPE_CHECKING,
    Any,
    NewType,
    TypedDict,
    Union,
    Literal
)
# from eth_typing import AnyAddress
from hexbytes import HexBytes
from eth_typing.evm import (
    # Address,
    HexAddress,
    # ChecksumAddress,
    BlockNumber,
    ChecksumAddress,
    Hash32
)
from eth_typing.encoding import (
    HexStr,
)

# from web3.types import (
#     Nonce,
#     _Hash32,
# )
from decimal import Decimal

if TYPE_CHECKING:
    # avoid recursive import
    from cfx_address import Base32Address

### copy-paste definition from web3 
_Hash32 = Union[Hash32, bytes, HexStr, str]
Nonce = NewType("Nonce", int)
# copy-paste ended

Drip = NewType("Drip", int)
CFX = NewType("CFX", Decimal)
Storage = NewType("Storage", int)

AddressParam = Union["Base32Address", str]

EpochLiteral = Literal["earliest", "latest_checkpoint", "latest_finalized", "latest_confirmed", "latest_state", "latest_mined"]
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
        "gasPrice": Drip,
        "nonce": Nonce,
        "to": AddressParam,
        "value": Drip,
        "epochHeight": int,
        "storageLimit": Storage
    },
    total=False,
)

if sys.version_info >= (3,9):
    TxParam = Union[TxDict, dict[str, Any]]
else:
    TxParam = Union[TxDict, dict]

# __all__ = [
#     "HexAddress",
#     "ChecksumAddress",
#     "Storage",
#     "Drip",
#     "Nonce",
#     "Hash32"
#     "_Hash32",
#     "EpochLiteral",
    
#     "AddressParam",
#     "EpochNumberParam",
#     "BlockNumber",
#     "TxDict",
#     "TxParam",
# ]
