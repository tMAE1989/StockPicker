import random

class Analyzer:
    def __init__(self, market_data):
        self.market_data = market_data

    def filter_stocks(self, tickers):
        """
        Filters stocks based on VOLUME and Volatility.
        """
        valid_stocks = []
        for ticker in tickers:
            data = self.market_data.get_stock_data(ticker)
            if data and 'full_history' in data:
                hist = data['full_history']
                
                # Volume Check: Current Volume > 1.5 * 20-day Avg Volume
                if len(hist) >= 20:
                    avg_vol = hist['Volume'].tail(20).mean()
                    current_vol = data['volume']
                    
                    if current_vol < 1.5 * avg_vol:
                        continue # Skip if volume is not high enough
                
                valid_stocks.append(data)
        
        # Sort by volatility (descending)
        valid_stocks.sort(key=lambda x: x['volatility'], reverse=True)
        return valid_stocks[:5]

    def determine_direction(self, stock_data):
        """
        Determines trade direction (Long/Short) based on 5-day trend.
        Returns: 'Long' or 'Short'
        """
        history = stock_data.get('history', [])
        if len(history) >= 2:
            start_price = history[0]
            end_price = history[-1]
            if end_price < start_price:
                return 'Short'
        return 'Long'

    def estimate_winnings(self, stock_data):
        """
        Estimates potential winnings using a heuristic (Volatility * Leverage).
        This is a SIMULATION.
        """
        volatility = stock_data['volatility']
        current_price = stock_data['price']
        direction = self.determine_direction(stock_data)
        
        # Simulation assumptions
        stock_leverage = 1
        option_leverage = 5  # Simulated 5x leverage for options
        
        # Optimistic daily move prediction (based on current volatility)
        daily_move_pct = volatility / (252**0.5) # Daily vol
        
        # Apply a "hype factor"
        hype_factor = random.uniform(0.8, 1.5)
        projected_move = daily_move_pct * hype_factor
        
        stock_win_pct = projected_move * 100
        option_win_pct = projected_move * option_leverage * 100
        
        if direction == 'Long':
            projected_price = current_price * (1 + projected_move)
        else: # Short
            projected_price = current_price * (1 - projected_move)
        
        return {
            "direction": direction,
            "stock_win_pct": round(stock_win_pct, 2),
            "option_win_pct": round(option_win_pct, 2),
            "projected_price": round(projected_price, 2)
        }
