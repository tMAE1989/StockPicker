import requests
from bs4 import BeautifulSoup
import re

class ApeWisdomScraper:
    def __init__(self):
        self.base_url = "https://apewisdom.io/all-stocks/"

    def get_trending_stocks(self, limit=10):
        """
        Scrapes apewisdom.io/all-stocks/ to get trending stocks.
        Returns a list of ticker symbols.
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(self.base_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            tickers = []
            # Find links like https://apewisdom.io/stocks/SYMBOL/
            # The text inside the link or the href itself contains the ticker.
            # Based on the view_content_chunk, we saw links like: [SPDR S&P 500 ETF Trust](https://apewisdom.io/stocks/SPY/)
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                match = re.search(r'/stocks/([A-Z]+)/', href)
                if match:
                    ticker = match.group(1)
                    if ticker not in tickers:
                        tickers.append(ticker)
                        if len(tickers) >= limit:
                            break
            
            return tickers
            
        except Exception as e:
            print(f"Error scraping ApeWisdom: {e}")
            return []

if __name__ == "__main__":
    scraper = ApeWisdomScraper()
    print(scraper.get_trending_stocks())
