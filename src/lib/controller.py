import json

from src.lib.get_tradebook import generate_adjusted_tradebook, load_tradebook
from src.lib.get_stock_info import get_stock_info_store, get_index_data
from src.lib.generate_holdings import generate_holdings_from_tradebook
from src.lib.get_holdings import load_holdings

class Controller:
    def __init__(self):
        user_data = json.loads(open("metadata/user_data.json").read())
        self.name = user_data["name"]
        self.email = user_data["email"]
        self.tradebook_files = user_data["tradebook"]
        self.manual_trades_file = user_data["manual_tradebook"]
        self.holdings_file = user_data["holdings"]
        
        self.tradebook = load_tradebook(self.tradebook_files, self.manual_trades_file)
        self.symbols = set(entry.symbol for entry in self.tradebook)
        self.stock_info_store = get_stock_info_store(self.symbols)
        self.adjusted_tradebook = generate_adjusted_tradebook(self.tradebook, self.stock_info_store)
        self.index_returns = get_index_data()
        self.calculated_holdings = generate_holdings_from_tradebook(self.symbols, self.adjusted_tradebook, self.index_returns, self.stock_info_store)
        self.actual_holdings = load_holdings(self.holdings_file)
        
        # Separate holdings into current and past holdings
        self.current_holdings = [holding for holding in self.calculated_holdings if holding.quantity != 0]
        self.past_holdings = [holding for holding in self.calculated_holdings if len(holding.realized_profit_history) != 0]