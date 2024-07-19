# import asyncio
import aiohttp
import aiomoex
import pandas as pd
import plotly.graph_objects as go  # type: ignore
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request

app = Flask(__name__)


async def fetch_data(ticker, interval, start, end):
    async with aiohttp.ClientSession() as session:
        try:
            data = await aiomoex.get_market_candles(session, security=ticker, interval=interval, start=start, end=end)
            df = pd.DataFrame(data)
            if df.empty:
                return None
            df.set_index('begin', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None


@app.route('/', methods=['GET', 'POST'])
async def index():
    ticker = 'SNGSP'
    error = None
    if request.method == 'POST':
        ticker = request.form['ticker']

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    df_daily = await fetch_data(ticker, 24, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    start_date = end_date - timedelta(days=30)
    df_hourly = await fetch_data(ticker, 60, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    start_date = end_date - timedelta(days=7)
    df_10min = await fetch_data(ticker, 10, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    start_date = end_date - timedelta(days=1)
    df_1min = await fetch_data(ticker, 1, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    if df_daily is None or df_hourly is None or df_10min is None or df_1min is None:
        error = "Invalid ticker or no data available."

    fig_daily = go.Figure(data=[go.Candlestick(x=df_daily.index,
                                               open=df_daily['open'],
                                               high=df_daily['high'],
                                               low=df_daily['low'],
                                               close=df_daily['close'])])
    fig_daily.update_layout(
        title=f'{ticker} Daily Prices Over Last Year', height=400, xaxis_rangeslider_visible=False)

    fig_hourly = go.Figure(data=[go.Candlestick(x=df_hourly.index,
                                                open=df_hourly['open'],
                                                high=df_hourly['high'],
                                                low=df_hourly['low'],
                                                close=df_hourly['close'])])
    fig_hourly.update_layout(
        title=f'{ticker} Hourly Prices Over Last Month', height=400, xaxis_rangeslider_visible=False)

    fig_10min = go.Figure(data=[go.Candlestick(x=df_10min.index,
                                               open=df_10min['open'],
                                               high=df_10min['high'],
                                               low=df_10min['low'],
                                               close=df_10min['close'])])
    fig_10min.update_layout(
        title=f'{ticker} 10-Min Prices Over Last Week', height=400, xaxis_rangeslider_visible=False)

    fig_1min = go.Figure(data=[go.Candlestick(x=df_1min.index,
                                              open=df_1min['open'],
                                              high=df_1min['high'],
                                              low=df_1min['low'],
                                              close=df_1min['close'])])
    fig_1min.update_layout(
        title=f'{ticker} 1-Min Prices Over Last Day', height=400, xaxis_rangeslider_visible=False)

    graph_html_daily = fig_daily.to_html(full_html=False)
    graph_html_hourly = fig_hourly.to_html(full_html=False)
    graph_html_10min = fig_10min.to_html(full_html=False)
    graph_html_1min = fig_1min.to_html(full_html=False)

    html_template = """
    <html>
        <head>
            <title>Screener</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                .chart-container {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: space-between;
                }
                .chart {
                    width: 48%;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Screener</h1>
            <form method="post">
                <label for="ticker">Enter Ticker:</label>
                <input type="text" id="ticker" name="ticker" value="{{ ticker }}">
                <input type="submit" value="Submit">
            </form>
            {% if error %}
                <p style="color:red;">{{ error }}</p>
            {% endif %}
            <div class="chart-container">
                <div class="chart">
                    {{ graph_html_daily|safe }}
                </div>
                <div class="chart">
                    {{ graph_html_hourly|safe }}
                </div>
                <div class="chart">
                    {{ graph_html_10min|safe }}
                </div>
                <div class="chart">
                    {{ graph_html_1min|safe }}
                </div>
            </div>
        </body>
    </html>
    """

    return render_template_string(html_template,
                                  graph_html_daily=graph_html_daily,
                                  graph_html_hourly=graph_html_hourly,
                                  graph_html_10min=graph_html_10min,
                                  graph_html_1min=graph_html_1min,
                                  ticker=ticker,
                                  error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
