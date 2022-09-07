import decimal

class Drip(int):
    # def __new__(cls, val) -> "Drip":
    #     return int.__new__(cls, val)
    
    def to_cfx(self, decimals=18) -> "CFX":
        return CFX(self) / 10**decimals

class CFX(decimal.Decimal):
    # def __new__(cls, *args, **kwargs) -> decimal.Decimal:
    #     return decimal.Decimal.__new__(cls, *args, **kwargs)
    
    def to_drip(self, decimals=18) -> "Drip":
        return Drip()