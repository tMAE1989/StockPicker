import time
import schedule
import argparse
import datetime
from market_data import MarketData
from apewisdom_scraper import ApeWisdomScraper
from analyzer import Analyzer
from database import Database
from telegram_notifier import TelegramNotifier
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()

def job_morning():
    print(f"\n--- Running Morning Job: {datetime.datetime.now()} ---")
    
    # 1. Scrape Trending Stocks
    scraper = ApeWisdomScraper()
    print("Scraping ApeWisdom...")
    tickers = scraper.get_trending_stocks(limit=15)
    print(f"Found tickers: {tickers}")
    
    # 2. Market Data & Filtering
    md = MarketData()
    analyzer = Analyzer(md)
    
    print("Fetching market data and analyzing...")
    filtered_stocks = analyzer.filter_stocks(tickers)
    
    # 3. Estimation & Saving
    db = Database()
    
    print("\n--- Daily Volatile Stock Suggestions ---")
    msg_lines = ["🚀 *Daily Volatile Stocks* 🚀", f"_{datetime.date.today().isoformat()}_", ""]

    for stock in filtered_stocks:
        estimation = analyzer.estimate_winnings(stock)
        
        # Merge data for DB
        suggestion = {
            "ticker": stock['ticker'],
            "price": stock['price'],
            "direction": estimation['direction'],
            "projected_price": estimation['projected_price'],
            "stock_win_pct": estimation['stock_win_pct'],
            "option_win_pct": estimation['option_win_pct']
        }
        
        db.save_suggestion(suggestion)
        
        print(f"Ticker: {stock['ticker']} ({estimation['direction']})")
        print(f"  Current Price: ${stock['price']:.2f}")
        print(f"  Volatility: {stock['volatility']:.4f}")
        print(f"  Est. Stock Win: {estimation['stock_win_pct']}%")
        print(f"  Est. Option Win (5x): {estimation['option_win_pct']}%")
        print("-" * 30)

        # Build message part
        msg_lines.append(f"*{stock['ticker']}* ({estimation['direction']})")
        msg_lines.append(f"Price: ${stock['price']:.2f} | Vol: {stock['volatility']:.2f}")
        msg_lines.append(f"Est Win: Stock {estimation['stock_win_pct']}% | Opt {estimation['option_win_pct']}%")
        msg_lines.append("---")

    # Send Telegram
    if msg_lines:
        notifier = TelegramNotifier()
        full_msg = "\n".join(msg_lines)
        notifier.send_message(full_msg)

def job_evening():
    print(f"\n--- Running Evening Job: {datetime.datetime.now()} ---")
    
    db = Database()
    md = MarketData()
    
    suggestions = db.get_todays_suggestions()
    # suggestions row structure: (id, date, ticker, direction, sugg_price, proj_price, est_stock_win, est_opt_win, act_close, act_win)
    
    print("\n--- End of Day Comparison ---")
    msg_lines = ["🌙 *End of Day Results* 🌙", f"_{datetime.date.today().isoformat()}_", ""]

    for row in suggestions:
        # Adjustment for schema change: row indices might shift if table was recreated.
        # Assuming new schema: 0:id, 1:date, 2:ticker, 3:direction, 4:sugg_price...
        
        if len(row) < 10:
             print(f"Skipping old format record for {row[2]}")
             continue

        ticker = row[2]
        direction = row[3]
        suggested_price = row[4]
        estimated_win = row[6]
        
        actual_close = md.get_closing_price(ticker)
        
        if actual_close:
            # Calculate actual win based on direction
            if direction == 'Short':
                actual_win_pct = ((suggested_price - actual_close) / suggested_price) * 100
            else:
                actual_win_pct = ((actual_close - suggested_price) / suggested_price) * 100
            
            db.update_actuals(ticker, actual_close, actual_win_pct)
            
            print(f"Ticker: {ticker} ({direction})")
            print(f"  Suggested Price: ${suggested_price:.2f}")
            print(f"  Actual Close:    ${actual_close:.2f}")
            print(f"  Est. Win: {estimated_win:.2f}%")
            print(f"  Act. Win: {actual_win_pct:.2f}%")
            
            diff = actual_win_pct - estimated_win
            print(f"  Difference: {diff:.2f}%")
            print("-" * 30)
            
            # Build message part
            icon = "✅" if actual_win_pct > 0 else "❌"
            msg_lines.append(f"{icon} *{ticker}* ({direction})")
            msg_lines.append(f"Sugg: ${suggested_price:.2f} -> Close: ${actual_close:.2f}")
            msg_lines.append(f"Act Win: {actual_win_pct:.2f}% (Est: {estimated_win:.2f}%)")
            msg_lines.append("---")

        else:
            print(f"Could not fetch closing price for {ticker}")

    # Send Telegram
    if len(msg_lines) > 3: # Check if we have actual content
        notifier = TelegramNotifier()
        full_msg = "\n".join(msg_lines)
        notifier.send_message(full_msg)

def main():
    parser = argparse.ArgumentParser(description="Volatile Stock Picker")
    parser.add_argument("--test-morning", action="store_true", help="Run morning job immediately")
    parser.add_argument("--test-evening", action="store_true", help="Run evening job immediately")
    args = parser.parse_args()

    if args.test_morning:
        job_morning()
        return

    if args.test_evening:
        job_evening()
        return

    # Schedule
    # Changed to 09:30 as requested
    schedule.every().day.at("09:30").do(job_morning)
    
    # Evening job (Close)
    # Market close is usually 16:00 EST. 
    # In MEZ (Germany), that is 22:00 (10 PM).
    schedule.every().day.at("22:00").do(job_evening)

    print("Scheduler started. Waiting for jobs...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
