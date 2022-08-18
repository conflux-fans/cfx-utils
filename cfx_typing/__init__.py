from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NewType,
    Optional,
    Sequence,
    Type,
    TypeVar,
    TypedDict,
    Union,
    Literal
)
# from eth_typing import AnyAddress
from hexbytes import HexBytes

from eth_typing.evm import (
    # Address,
    # HexAddress,
    # ChecksumAddress,
    BlockNumber,
    ChecksumAddress,
)
from eth_typing.encoding import (
    HexStr,
)

from web3.types import (
    Nonce,
    _Hash32,
)
from cfx_address import Base32Address

Drip = NewType("Drip", int)
CFX = NewType("CFX", int)
AddressParam = Union[Base32Address, str]

EpochLiteral = Literal["latest_checkpoint", "earliest", "latest_finalized", "latest_confirmed", "latest_state", "latest_mined"]
EpochNumberParam = Union[EpochLiteral, _Hash32, int]
ChainId = Union[int, HexStr]
Storage = NewType("Storage", int)

class NodeStatus(TypedDict):
    bestHash: _Hash32
    chainId: int
    networkId: int
    blockNumber: int
    epochNumber: int
    latestCheckpoint: int
    latestConfirmed: int
    latestState: int
    latestFinalized: int
    ethereumSpaceChainId: int
    pendingTxNumber: int

class EstimateResult(TypedDict):    
    gasLimit: int
    gasUsed: int
    storageCollateralized: Storage


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

class FilterParams(TypedDict, total=False):
    fromEpoch: EpochNumberParam
    toEpoch: EpochNumberParam
    blockHashes: Sequence[_Hash32]
    address: Union[Base32Address, List[Base32Address]]
    topics: Sequence[Optional[Union[_Hash32, Sequence[_Hash32]]]]
    limit: int
    offset: int


class LogReceipt(TypedDict):
    address: Base32Address
    topics: Sequence[HexBytes]
    data: HexBytes
    blockHash: HexBytes
    epochNumber: int
    transactionHash: HexBytes
    transactionIndex: int
    logIndex: int
    transactionLogIndex: int

# syntax b/c "from" keyword not allowed w/ class construction
TxReceipt = TypedDict(
    "TxReceipt",
    {
        "transactionHash": _Hash32,
        "index": int,
        "blockHash": _Hash32,
        "epochNumber": int,
        "from": AddressParam,
        "to": AddressParam,
        "gasUsed": Drip,
        "gasFee": Drip,
        "gasCoveredBySponsor": bool,
        "storageCollateralized": Storage,
        "storageCoveredBySponsor": bool,
        "storageReleased": List[Storage],
        "contractCreated": Union[AddressParam, None],
        
        "stateRoot": _Hash32,
        "outcomeStatus": int,
        "logsBloom": HexBytes,
        
        "logs": List[LogReceipt]
    },
)

# syntax b/c "from" keyword not allowed w/ class construction
TxData = TypedDict(
    "TxData",
    {
        "blockHash": Union[None, HexBytes],
        "chainId": int,
        "contractCreated": Union[None, AddressParam],
        "data": HexBytes,
        "epochHeight": int,
        "from": AddressParam,
        "gas": int,
        "gasPrice": Drip,
        "hash": _Hash32,
        "nonce": Nonce,
        "r": HexBytes,
        "s": HexBytes,
        "status": Union[None, int],
        "storageLimit": Storage,
        "to": Union[None, AddressParam],
        "transactionIndex": Union[None, int],
        "v": int,
        "value": Drip,
    },
    total=False,
)

TxParam = Union[TxDict, dict[str, Any]]

class BlockData(TypedDict):
    hash: _Hash32
    parentHash: _Hash32
    height: int
    miner: Base32Address
    deferredStateRoot: _Hash32
    deferredReceiptsRoot: _Hash32
    deferredLogsBloomHash: _Hash32
    blame: int
    transactionsRoot: _Hash32
    epochNumber: Union[int, None]
    blockNumber: Union[int, None]
    gasLimit: int
    gasUsed: Union[int, None]
    timestamp: int
    difficulty: int
    powQuality: Union[HexBytes, None]
    refereeHashes: Sequence[_Hash32]
    adaptive: bool
    nonce: HexBytes
    size: int
    custom: Sequence[HexBytes]
    posReference: _Hash32
    transactions: Sequence[Union[_Hash32, TxData]]
