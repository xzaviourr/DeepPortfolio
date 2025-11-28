import os
import csv
from uuid import uuid4
import pandas as pd
import datetime
from typing import List, Dict
from collections import defaultdict as defaultDict

from src.models.trade import Trade
from src.models.stock_info import StockInfo

DATE_TODAY = datetime.datetime.now().date().strftime("%Y-%m-%d")

def load_manual_trades(file_path: str) -> List[Trade]:
    """
    Function to read the manual trades of the user. Manual trades consists of all the other ways
    in which user obtains or sells stocks, other than the trades recorded in the tradebook.
    This includes trades from IPOs, ESOPs, Gifts, etc.
    Args:
        file_path (str): Path to the CSV file containing manual trades
    Returns:
        List[Trade]: List of Trade objects representing manual trades
    """
    manual_trades_df = pd.read_csv(file_path)
    manual_trades_df['symbol'] = manual_trades_df['symbol'].str.split('-').str[0]     # Normalize symbols

    manual_trades = []
    for trade in manual_trades_df.iterrows():
        manual_trades.append(Trade(
            order_id = uuid4(),
            symbol = trade[1]['symbol'],
            quantity = abs(trade[1]['quantity']),
            price = trade[1]['price'],
            typ = 'buy' if trade[1]['quantity'] > 0 else 'sell',
            timestamp = datetime.datetime.strptime(trade[1]['trade_date'], "%Y-%m-%d").replace(hour=0, minute=0, second=0),
            remarks = trade[1]['remarks']
        ))
    return manual_trades

def load_tradebook(tradebook_files: List[str], manual_trades_file: str) -> List[Trade]:
    """
    Load the tradebook from the tradebook files and manual trades file.
    Args:
        tradebook_files (List[str]): List of paths to the tradebook files
        manual_trades_file (str): Path to the manual trades file
    Returns:
        List[Trade]: List of Trade objects representing the tradebook
    """
    fiscal_year_trades = [pd.read_csv(file) for file in tradebook_files]    # Read all tradebook files for individual fiscal year
    tradebook_df = pd.concat(fiscal_year_trades, ignore_index=True)    # Combine all tradebook files
    tradebook_df = tradebook_df.sort_values(by="order_execution_time")    # Sort by order execution time
    tradebook_df['symbol'] = tradebook_df['symbol'].str.split('-').str[0]     # Normalize symbols

    tradebook = []
    for trade in tradebook_df.iterrows():
        tradebook.append(Trade(
            order_id = trade[1]['order_id'],
            symbol = trade[1]['symbol'],
            quantity = trade[1]['quantity'],
            price = trade[1]['price'],
            typ = trade[1]['trade_type'],
            timestamp = datetime.datetime.strptime(trade[1]['order_execution_time'], "%Y-%m-%dT%H:%M:%S")
        ))

    if manual_trades_file != "":
        other_trades = load_manual_trades(manual_trades_file)
        tradebook.extend(other_trades)
        tradebook.sort(key=lambda t: t.timestamp)
    return tradebook

def generate_adjusted_tradebook(tradebook: List[Trade], stock_info_store: Dict[str, StockInfo]) -> List[Trade]:
    """
    Generate an adjusted tradebook by accounting for stock splits and bonus shares.
    Args:
        tradebook (List[Trade]): List of Trade objects representing the tradebook
        stock_info_store (Dict[str, StockInfo]): Dictionary containing stock info for each symbol
    Returns:
        List[Trade]: List of Trade objects representing the adjusted tradebook
    """
    if os.path.exists(f'metadata/adjusted_tradebook_{DATE_TODAY}.csv'):
        tradebook = pd.read_csv(f'metadata/adjusted_tradebook_{DATE_TODAY}.csv')
        adjusted_tradebook = []
        for entry in tradebook.iterrows():
            adjusted_tradebook.append(Trade(
                order_id = entry[1]['order_id'],
                symbol = entry[1]['symbol'],
                quantity = entry[1]['quantity'],
                price = entry[1]['price'],
                typ = entry[1]['type'],
                timestamp = datetime.datetime.strptime(entry[1]['date'], "%Y-%m-%d %H:%M:%S"),
                remarks = entry[1]['remarks'] if not pd.isna(entry[1]['remarks']) else ""
            ))
        return adjusted_tradebook

    tradebook_copy = tradebook.copy()
    for stock in stock_info_store.values():
        for split in stock.stock_splits:
            tradebook_copy.append(Trade(
                order_id = uuid4(), 
                symbol = stock.symbol, 
                quantity = 0, 
                price = split.ratio, 
                typ = 'bonus', 
                timestamp = datetime.datetime.combine(split.split_date, datetime.time(0, 0, 0))))
    
    tradebook_copy.sort(key=lambda t: t.timestamp)

    adjusted_tradebook = []
    holdings = defaultDict(int)  # Track current holdings for each symbol

    for trade in tradebook_copy:
        if trade.typ == 'buy':
            holdings[trade.symbol] += trade.quantity
            adjusted_tradebook.append(trade)
        
        elif trade.typ == 'sell':
            holdings[trade.symbol] -= trade.quantity
            adjusted_tradebook.append(trade)
        
        elif trade.typ == 'bonus':
            if holdings[trade.symbol] > 0:
                bonus_quantity = holdings[trade.symbol] * (trade.price - 1)     # Split ratio - 1
                holdings[trade.symbol] += bonus_quantity
                adjusted_tradebook.append(Trade(
                    order_id = uuid4(),
                    symbol = trade.symbol, 
                    quantity = bonus_quantity, 
                    price = 0, 
                    typ = 'bonus', 
                    timestamp = trade.timestamp, 
                    remarks="bonus shares"))

    # Save adjusted_tradebook to a CSV file
    with open(f'metadata/adjusted_tradebook_{DATE_TODAY}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['order_id', 'symbol', 'quantity', 'price', 'type', 'date', 'remarks'])
        for entry in adjusted_tradebook:
            writer.writerow([entry.order_id, entry.symbol, entry.quantity, entry.price, entry.typ, entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"), entry.remarks])

    return adjusted_tradebook