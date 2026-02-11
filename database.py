import sqlite3
import datetime

class Database:
    def __init__(self, db_path="volatile_stocks.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            ticker TEXT,
            direction TEXT,
            suggested_price REAL,
            projected_price REAL,
            estimated_stock_win_pct REAL,
            estimated_option_win_pct REAL,
            actual_close_price REAL,
            actual_win_pct REAL
        )''')
        conn.commit()
        conn.close()

    def clear_todays_suggestions(self):
        """Deletes all suggestions for the current date. useful for re-runs."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        date_str = datetime.date.today().isoformat()
        c.execute("DELETE FROM suggestions WHERE date = ?", (date_str,))
        conn.commit()
        conn.close()

    def save_suggestion(self, suggestion):
        """
        Saves a suggestion to the database.
        suggestion: dict with ticker, price, projected_price, etc.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        date_str = datetime.date.today().isoformat()
        
        # Check if exists and remove if so (overwrite)
        c.execute("SELECT id FROM suggestions WHERE date = ? AND ticker = ?", (date_str, suggestion['ticker']))
        existing = c.fetchone()
        if existing:
             c.execute("DELETE FROM suggestions WHERE id = ?", (existing[0],))
        
        c.execute('''INSERT INTO suggestions (
            date, ticker, direction, suggested_price, projected_price, 
            estimated_stock_win_pct, estimated_option_win_pct
        ) VALUES (?, ?, ?, ?, ?, ?, ?)''', (
            date_str, 
            suggestion['ticker'], 
            suggestion['direction'],
            suggestion['price'], 
            suggestion['projected_price'],
            suggestion['stock_win_pct'], 
            suggestion['option_win_pct']
        ))
        conn.commit()
        conn.close()

    def get_todays_suggestions(self):
        """Returns suggestions made today."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        date_str = datetime.date.today().isoformat()
        c.execute("SELECT * FROM suggestions WHERE date = ?", (date_str,))
        rows = c.fetchall()
        conn.close()
        return rows

    def update_actuals(self, ticker, actual_close, actual_win_pct):
        """Updates the actual close price and win percentage for a ticker suggesting today."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        date_str = datetime.date.today().isoformat()
        c.execute('''UPDATE suggestions 
                     SET actual_close_price = ?, actual_win_pct = ? 
                     WHERE date = ? AND ticker = ?''', 
                  (actual_close, actual_win_pct, date_str, ticker))
        conn.commit()
        conn.close()
