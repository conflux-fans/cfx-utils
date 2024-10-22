from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    NewType,
    Union,
)

from typing_extensions import (
    Literal,
    TypedDict,
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

### copy-paste definition from web3
_Hash32 = Union[Hash32, bytes, HexStr, str]
Nonce = NewType("Nonce", int)
# copy-paste ended

Storage = NewType("Storage", int)

AddressParam = str

EpochLiteral = Literal[
    "earliest",
    "latest_checkpoint",
    "latest_finalized",
    "latest_confirmed",
    "latest_state",
    "latest_mined",
    "pending",
]
EpochNumber = NewType("EpochNumber", int)
EpochNumberParam = Union[EpochLiteral, EpochNumber, int]
"""Epoch param could be either EpochLiteral, or Epoch Number
"""

# ChainId = Union[int, HexStr]

# syntax b/c "from" keyword not allowed w/ class construction
BaseTxDict = TypedDict(
    "BaseTxDict",
    {
        "chainId": int,
        "data": Union[bytes, HexStr],
        # addr or ens
        "from": AddressParam,
        "gas": int,
        "nonce": Nonce,
        "to": AddressParam,
        "value": Union[Drip, AbstractDerivedTokenUnit[Drip], int],
        "epochHeight": int,
        "storageLimit": Storage,
    },
    total=False,
)

class LegacyTxDict(BaseTxDict, total=False):
    gasPrice: Union[Drip, AbstractDerivedTokenUnit[Drip], int]
    
class TypedTxDict(BaseTxDict, total=False):
    type: Union[int, HexStr]
    
class CIP1559TxDict(TypedTxDict, total=False):
    maxFeePerGas: Union[Drip, AbstractDerivedTokenUnit[Drip], int]
    maxPriorityFeePerGas: Union[Drip, AbstractDerivedTokenUnit[Drip], int]

TxDict = Union[LegacyTxDict, TypedTxDict, CIP1559TxDict]
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
