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
                
                # Volume Check: Current (or last closed) Volume > 1.5 * 20-day Avg Volume
                if len(hist) >= 20:
                    # Get average of last 20 TRADING days (excluding the very last row if it's current/incomplete)
                    avg_vol = hist['Volume'].iloc[-21:-1].mean()
                    
                    # Current volume - if we are before open, this might be 0 or pre-market.
                    # We use the latest available volume.
                    current_vol = data['volume']
                    
                    if current_vol < 1.3 * avg_vol:
                        print(f"DEBUG: Skipping {ticker} - Volume ({current_vol:.0f}) below 1.3x average ({avg_vol:.0f})")
                        continue # Skip if volume is not high enough
                
                valid_stocks.append(data)
        
        # Sort by volatility (descending)
        valid_stocks.sort(key=lambda x: x['volatility'], reverse=True)
        return valid_stocks[:5]

    def determine_direction(self, stock_data):
        """
        Determines trade direction based on volume pressure.
        - Days where price went UP: volume counts as buying pressure.
        - Days where price went DOWN: volume counts as selling pressure.
        If buying volume > selling volume -> Long (bulls in control).
        If selling volume > buying volume -> Short (bears in control).
        """
        hist = stock_data.get('full_history')
        if hist is not None and len(hist) >= 5:
            recent = hist.tail(5)
            
            buying_volume = 0
            selling_volume = 0
            
            closes = recent['Close'].values
            volumes = recent['Volume'].values
            
            for i in range(1, len(closes)):
                if closes[i] > closes[i - 1]:
                    buying_volume += volumes[i]
                elif closes[i] < closes[i - 1]:
                    selling_volume += volumes[i]
                # Flat days are ignored
            
            if selling_volume > buying_volume:
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
