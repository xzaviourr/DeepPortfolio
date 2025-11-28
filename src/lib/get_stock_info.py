import yfinance as yf
from typing import Dict
import datetime
import pandas as pd

from src.models.stock_info import StockInfo, StockSplit, Dividend
from src.database.stock_info import insert_stock_info_into_db, get_stock_info_from_db
from src.database.stock_split import insert_stock_split_into_db, get_stock_splits_from_db
from src.database.dividend import insert_dividend_into_db, get_dividends_from_db
from src.database.index import insert_index_into_db, get_index_from_db

DATE_TODAY = datetime.datetime.now().date().strftime("%Y-%m-%d")

def get_stock_splits(symbol: str, stock: yf.Ticker) -> list[StockSplit]:
    """
    Fetch stock split data for a given stock symbol and store it in the database.

    Args:
        symbol (str): Stock symbol.
        stock (yf.Ticker): yfinance Ticker object.

    Returns:
        list[StockSplit]: List of StockSplit objects.
    """
    try:
        stock_splits_df = stock.get_splits().to_frame()
        stock_splits = []
        for row in stock_splits_df.iterrows():
            stock_splits.append(StockSplit(split_date=row[0].date(), ratio=row[1]['Stock Splits']))
            insert_stock_split_into_db(symbol=symbol, split_date=row[0].date(), ratio=row[1]['Stock Splits'])
        return stock_splits
    except Exception as e:
        print(f"Error fetching stock splits for {symbol}: {e}")
        return []

def get_dividends(symbol: str, stock: yf.Ticker) -> list[Dividend]:
    """
    Fetch dividend data for a given stock symbol and store it in the database.

    Args:
        symbol (str): Stock symbol.
        stock (yf.Ticker): yfinance Ticker object.

    Returns:
        list[Dividend]: List of Dividend objects.
    """
    try:
        dividends_df = stock.get_dividends().to_frame()
        dividends = []
        for row in dividends_df.iterrows():
            insert_dividend_into_db(symbol=symbol, ex_date=row[0].date(), amount=row[1]['Dividends'])
            dividends.append(Dividend(ex_date=row[0].date(), amount=row[1]['Dividends']))
        return dividends
    except Exception as e:
        print(f"Error fetching dividends for {symbol}: {e}")
        return []

def get_stock_info(symbol: str) -> StockInfo:
    """
    Fetch stock information for a given symbol. First, check the database; if not found, fetch from yfinance.

    Args:
        symbol (str): Stock symbol.

    Returns:
        StockInfo: StockInfo object containing stock details, or None if data could not be fetched.
    """
    def get_value(key, default=None):
        return stock_info.get(key, default)

    # Check if data exists in the database
    try:
        stock_info = get_stock_info_from_db(symbol)
        if stock_info:
            stock_info.stock_splits = get_stock_splits_from_db(symbol)
            stock_info.dividends = get_dividends_from_db(symbol)
            print(f"Fetching {symbol} from database")
            return stock_info
    except Exception as e:
        print(f"Error fetching {symbol} from database: {e}")

    # If data does not exist, fetch from yfinance
    stock_info = None
    stock = None
    try:
        stock = yf.Ticker(f"{symbol}.NS")  # NSE
        stock_info = stock.info
    except Exception as e:
        print(f"Error fetching {symbol} from NSE: {e}")

    if not stock_info:
        try:
            stock = yf.Ticker(f"{symbol}.BO")  # BSE
            stock_info = stock.info
        except Exception as e:
            print(f"Error fetching {symbol} from BSE: {e}")
            return None

    print(f"Fetched {symbol} from yfinance")
    # Create StockInfo object with all required fields
    try:
        info = StockInfo(
            symbol=symbol,
            symbol_yf=get_value('symbol', symbol),
            name=get_value('longName', 'Unknown'),
            city=get_value('city', 'Unknown'),
            industry=get_value('industry', 'Unknown'),
            sector=get_value('sector', 'Unknown'),
            stock_splits=get_stock_splits(symbol, stock),
            dividends=get_dividends(symbol, stock),
            previous_close=get_value('previousClose', 0.0),
            volume=get_value('volume', 0),
            average_volume_10days=get_value('averageVolume10days', 0),
            average_volume_3months=get_value('averageDailyVolume3Month', 0),
            fifty_two_week_low=get_value('fiftyTwoWeekLow', 0.0),
            fifty_two_week_high=get_value('fiftyTwoWeekHigh', 0.0),
            fifty_two_week_change=get_value('52WeekChange', 0.0),
            market_cap=get_value('marketCap', 0),
            book_value=get_value('bookValue', 0.0),
            price_to_sales_trailing_12_months=get_value('priceToSalesTrailing12Months', 0.0),
            price_to_book=get_value('priceToBook', 0.0),
            trailing_pe=get_value('trailingPE', 0.0),
            forward_pe=get_value('forwardPE', 0.0),
            trailing_eps=get_value('trailingEps', 0.0),
            forward_eps=get_value('forwardEps', 0.0),
            price_eps_current_year=get_value('priceEpsCurrentYear', 0.0),
            fifty_day_average=get_value('fiftyDayAverage', 0.0),
            two_hundred_day_average=get_value('twoHundredDayAverage', 0.0),
            beta=get_value('beta', 0.0),
            debt_to_equity=get_value('debtToEquity', 0.0),
            enterprise_to_revenue=get_value('enterpriseToRevenue', 0.0),
            enterprise_to_ebitda=get_value('enterpriseToEbitda', 0.0),
            ebitda=get_value('ebitda', 0),
            total_debt=get_value('totalDebt', 0),
            total_revenue=get_value('totalRevenue', 0),
            revenue_per_share=get_value('revenuePerShare', 0.0),
            gross_profit=get_value('grossProfits', 0),
            revenue_growth=get_value('revenueGrowth', 0.0),
            gross_margins=get_value('grossMargins', 0.0),
            ebitda_margins=get_value('ebitdaMargins', 0.0),
            operating_margins=get_value('operatingMargins', 0.0),
            eps_trailing_12months=get_value('trailingEps', 0.0),
            eps_forward=get_value('forwardEps', 0.0),
            eps_current_year=get_value('epsCurrentYear', 0.0),
            target_high_price=get_value('targetHighPrice', 0.0),
            target_low_price=get_value('targetLowPrice', 0.0),
            target_mean_price=get_value('targetMeanPrice', 0.0),
            dividend_yield=get_value('dividendYield', 0.0),
            five_year_average_dividend_yield=get_value('fiveYearAvgDividendYield', 0.0)
        )
        insert_stock_info_into_db(info)
        return info
    except Exception as e:
        print(f"Error creating StockInfo object for {symbol}: {e}")
        return None

def get_stock_info_store(symbols: list[str]) -> Dict[str, StockInfo]:
    """
    Fetch stock information for multiple symbols and store them in a dictionary.

    Args:
        symbols (list[str]): List of stock symbols.

    Returns:
        Dict[str, StockInfo]: Dictionary mapping symbols to StockInfo objects.
    """
    stock_info_store = {}
    for symbol in symbols:
        stock_info = get_stock_info(symbol)
        if stock_info:
            stock_info_store[symbol] = stock_info
    return stock_info_store

def get_index_data() -> pd.DataFrame:
    """
    Fetch index data from the database. If not available, fetch from yfinance and store in the database.

    Returns:
        pd.DataFrame: DataFrame containing index data.
    """
    try:
        index_data = get_index_from_db()
        if index_data.empty:
            nifty50 = yf.Ticker("^NSEI").history(period="5y").reset_index()[["Date", "Close"]]
            bsesensex = yf.Ticker("^BSESN").history(period="5y").reset_index()[["Date", "Close"]]
            niftybank = yf.Ticker("^NSEBANK").history(period="5y").reset_index()[["Date", "Close"]]

            index_data = pd.concat([
                nifty50.set_index('Date').rename(columns={'Close': 'nifty50'}),
                bsesensex.set_index('Date').rename(columns={'Close': 'bsesensex'}),
                niftybank.set_index('Date').rename(columns={'Close': 'niftybank'})
            ], axis=1).reset_index().drop_duplicates(subset=['Date']).set_index('Date').reset_index()

            # Convert Date column to date type
            index_data['Date'] = index_data['Date'].dt.date
            index_data.rename(columns={'Date': 'date'}, inplace=True)

            insert_index_into_db(index_data)
        return index_data
    except Exception as e:
        print(f"Error fetching index data: {e}")
        return pd.DataFrame()