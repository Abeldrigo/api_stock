import requests
from datetime import datetime, timedelta
from twilio.rest import Client

# Load the dotenv and os modules
# load_dotenv will be used to load the .env file to the environment variables.
from dotenv import load_dotenv
# os will be used to refer to those variables in the code
import os

# Credentials
load_dotenv(".env")  # This will load the .env file

STOCK_NAME = "TSLA"
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_ENDPOINT = "https://www.alphavantage.co/query"

STOCK_PARAMS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": ALPHAVANTAGE_API_KEY,
}

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWSAPI_PARAMS = {
    # "q": "Tesla Inc",
    # "from": datetime.today().strftime('%Y-%m-%d'),
    # "sortBy": "publishedAt",
    "qInTitle": "Tesla Inc",
    "apiKey": os.getenv("NEWSAPI_KEY"),
}

#  twilio API Parameters
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

stock_response = requests.get(url=ALPHAVANTAGE_ENDPOINT, params=STOCK_PARAMS)
stock_response.raise_for_status()
stock = stock_response.json()["Time Series (Daily)"]

# Gets the dates for today - 1 day and today - 2 days as string
today_minus_one_day = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
today_minus_two_days = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')

# Gets the close price from two previous days and converts to float
yesterday_close = float(stock[today_minus_one_day]["4. close"])
before_yesterday_close = float(stock[today_minus_two_days]["4. close"])

# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
change_percent = round(((yesterday_close - before_yesterday_close) / before_yesterday_close) * 100)
print(change_percent)
if change_percent >= 0:
    stock_icon = "🔺"
else:
    stock_icon = "🔻"

abs_change_percent = abs(change_percent)
if abs_change_percent >= 5:
    news_response = requests.get(url=NEWS_ENDPOINT, params=NEWSAPI_PARAMS)
    news_response.raise_for_status()
    news = news_response.json()["articles"][:3]
    for idx, x in enumerate(news):
        # twilio client. To send SMS
        client = Client(ACCOUNT_SID, AUTH_TOKEN)

        message = client.messages.create(
            body=f"TSLA: {stock_icon}{abs_change_percent}%\n"
                 f"Headline: {news[idx]['title']}\n"
                 f"Brief: {news[idx]['description']}\n",
            from_="+18782192133",
            to="+525611779621",
        )

        print(message.status)
