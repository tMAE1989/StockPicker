import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class MarketData:
    def __init__(self):
        pass

    def get_current_price(self, ticker):
        """Fetches the current price of a stock."""
        try:
            ticker_obj = yf.Ticker(ticker)
            # data = ticker_obj.history(period="1d")
            # if not data.empty:
            #     return data['Close'].iloc[-1]
            # Fallback to fast_info or regular info
            price = ticker_obj.fast_info.last_price
            return price
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return None

    def get_stock_data(self, ticker):
        """Fetches detailed stock data including volatility."""
        try:
            ticker_obj = yf.Ticker(ticker)
            # Need 3mo for accurate RSI-14 calculation + volatility
            hist = ticker_obj.history(period="3mo")
            
            if hist.empty:
                return None
            
            current_price = ticker_obj.fast_info.last_price
            
            # Use 'Volume' if available, otherwise fallback
            if 'Volume' in hist.columns and not hist['Volume'].empty:
                volume = hist['Volume'].iloc[-1]
            else:
                volume = ticker_obj.fast_info.last_volume
            
            # Calculate volatility (standard deviation of daily returns)
            hist['Returns'] = hist['Close'].pct_change()
            volatility = hist['Returns'].std() * (252 ** 0.5) # Annualized volatility based on daily returns
            
            # Get 5-day history for trend analysis
            history_5d = hist['Close'].tail(5).tolist() if not hist.empty else []

            return {
                "ticker": ticker,
                "price": current_price,
                "volume": volume,
                "volatility": volatility,
                "history": history_5d,
                "full_history": hist # Return full DF for RSI calculation
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def get_closing_price(self, ticker):
        """Fetches the closing price for the day (or most recent close)."""
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period="1d")
            if not hist.empty:
                return hist['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error fetching closing price for {ticker}: {e}")
            return None
