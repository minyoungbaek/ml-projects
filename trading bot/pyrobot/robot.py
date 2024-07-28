import pandas as pd

from td.client import TDClient
from td.utils import milliseconds_since_epoch

from datetime import datetime
from datetime import time
from datetime import timezone

from typing import List
from typing import Dict
from typing import Union
from typing import Optional

from pyrobot.portfolio import Portfolio
from pyrobot.stock_frame import StockFrame

class PyRobot():
    def __init__(self, client_id: str, redirect_uri: str, credentials_path: str = None, trading_account: str = None, paper_trading: bool = True) -> None:

        self.trading_account: str = trading_account
        self.client_id: str = client_id
        self.redirect_uri: str = redirect_uri
        self.credentials_path: str = credentials_path
        self.session: TDClient = self._create_session()
        self.trades: dict = {}
        self.historical_prices: dict = {}
        self.stock_frame = None
        self.paper_trading = paper_trading

    def _create_session(self) -> TradingClient:

        trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        return trading_client
    
    @property
    def pre_market_open(self) -> bool:

        pre_market_start_time = datetime.now().replace(hour=12, minute=00, second=00, tzinfo=timezone.utc).timestamp()
        market_start_time = datetime.now().replace(hour=13, minute=30, second=00, tzinfo=timezone.utc).timestamp()
        right_now = datetime.now().replace(tzinfo=timezone.utc).timestamp()

        if market_start_time >= right_now >= pre_market_start_time:
            return True
        else:
            return False

    @property
    def post_market_open(self) -> bool:
         
        post_market_end_time = datetime.now().replace(hour=22, minute=30, second=00, tzinfo=timezone.utc).timestamp()
        market_end_time = datetime.now().replace(hour=20, minute=00, second=00, tzinfo=timezone.utc).timestamp()
        right_now = datetime.now().replace(tzinfo=timezone.utc).timestamp()

        if post_market_end_time >= right_now >= market_end_time:
            return True
        else:
            return False

    @property
    def regular_market_open(self) -> bool:
        
        market_start_time = datetime.now().replace(hour=13, minute=30, second=00, tzinfo=timezone.utc).timestamp()
        market_end_time = datetime.now().replace(hour=20, minute=00, second=00, tzinfo=timezone.utc).timestamp()
        right_now = datetime.now().replace(tzinfo=timezone.utc).timestamp()

        if market_end_time >= right_now >= market_start_time:
            return True
        else:
            return False
        
    def create_portfolio(self):
        
        # Initialize a new Portfolio object
        self.portfolio = Portfolio(account_number=self.trading_account)

        # Assign the client.
        self.portfolio.td_client = self.session

        return self.portfolio

    def create_trade(self):
        pass

    def grab_current_quotes(self) -> dict:
        
        # First grab all the symbols.
        symbols = self.portfolio.positions.keys()

        # Grab the quotes.
        quotes = self.session.get_quotes(instruments=list(symbols))

        return quotes

    def grab_historical_prices(self) -> List[Dict]:
        pass

    def create_stock_frame(self, data: List[dict]) -> StockFrame:
        
        self.stock_frame = StockFrame(data=data)

        return self.stock_frame

    def grab_historical_prices(self, start: datetime, end: datetime, bar_size: int = 1, bar_type: str = 'minute', symbols: Optional[List[str]] = None) -> dict:

        self._bar_size = bar_size
        self._bar_type = bar_type

        start = str(milliseconds_since_epoch(dt_object=start))
        end = str(milliseconds_since_epoch(dt_object=end))

        new_prices = []

        if not symbols:
            symbols = self.portfolio.positions

        for symbol in symbols:

            # TD Ameritrade API
            historical_prices_response = self.session.get_price_history(
                symbol=symbol,
                period_type='day',
                start_date=start,
                end_date=end,
                frequency_type=bar_type,
                frequency=bar_size,
                extended_hours=True
            )

            self.historical_prices[symbol] = {}
            self.historical_prices[symbol]['candles'] = historical_prices_response['candles']

            for candle in historical_prices_response['candles']:

                new_price_mini_dict = {}
                new_price_mini_dict['symbol'] = symbol
                new_price_mini_dict['open'] = candle['open']
                new_price_mini_dict['close'] = candle['close']
                new_price_mini_dict['high'] = candle['high']
                new_price_mini_dict['low'] = candle['low'] 
                new_price_mini_dict['volume'] = candle['volume']
                new_price_mini_dict['datetime'] = candle['datetime']
                new_prices.append(new_price_mini_dict)

        self.historical_prices['aggregated'] = new_prices

        return self.historical_prices