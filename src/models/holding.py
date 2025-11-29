from typing import List, Tuple
import datetime
from dataclasses import dataclass, field

from src.models.trade import Trade
from src.models.stock_info import StockInfo


@dataclass
class Holding:
    # Current status
    symbol: str = ""
    quantity: int = 0
    buy_average: float = 0
    investment: float = 0
    current_price: float = 0
    unrealized_profit: float = 0

    # Running trades
    running_trades: List[Trade] = field(default_factory=list)
    running_ltcg: float = 0
    running_stcg: float = 0

    # Trade history
    trades: List[Trade] = field(default_factory=list)
    investment_trend: List[Tuple[datetime.date, float]] = field(default_factory=list)
    quantity_trend: List[Tuple[datetime.date, float]] = field(default_factory=list)
    realized_profit_history: List[Tuple[datetime.datetime, float]] = field(default_factory=list)
    dividend_history: List[Tuple[datetime.date, float]] = field(default_factory=list)

    # Past performance
    realized_profit: float = 0
    dividend_income: float = 0

    # Performance metrics
    risk_free_return_trend: List[Tuple[datetime.date, float]] = field(default_factory=list)
    nifty50_return_trend: List[Tuple[datetime.date, float]] = field(default_factory=list)
    bsesensex_return_trend: List[Tuple[datetime.date, float]] = field(default_factory=list)
    niftybank_return_trend: List[Tuple[datetime.date, float]] = field(default_factory=list)
    
    # Stock information
    stock_info: StockInfo = None