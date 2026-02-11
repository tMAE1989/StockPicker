# Volatile Stock Picker App

This application suggests volatile stocks daily at 9:00 AM MEZ and compares the estimation with actual results at the end of the day.

## Prerequisites

You need to have Python installed. It seems it might not be in your system PATH.
You also need the following libraries:
- `beautifulsoup4`
- `requests`
- `yfinance`
- `schedule`
- `python-dotenv`
- `pandas`

## Installation

1.  Open a terminal in this directory.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *If `pip` is not recognized, try `python -m pip install -r requirements.txt` or `py -m pip install -r requirements.txt`.*

## Configuration

1.  Rename `.env.example` to `.env` (if you haven't already).
2.  The Reddit API keys are **NO LONGER REQUIRED** as we switched to scraping ApeWisdom.io.

## Usage

### Manual Test
To test the "Morning" job immediately (finding stocks):
```bash
python main.py --test-morning
```

To test the "Evening" job immediately (comparing results):
```bash
python main.py --test-evening
```

### Running the Scheduler
To run the app continuously (it will check the time and run at 9:00 AM and 10:00 PM):
```bash
python main.py
```
*Keep the terminal window open.*
