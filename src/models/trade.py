import datetime
from dataclasses import dataclass

@dataclass
class Trade:
    order_id: str
    symbol: str
    quantity: int
    price: float
    typ: str
    timestamp: datetime.datetime
    remarks: str = ""