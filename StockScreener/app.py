from flask import *
import pandas as pd
from flask_apscheduler import APScheduler
from Screener import StockScreener
import sys
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def show_tables():
    data = pd.read_csv('screener_results.csv')
    data.set_index(['Unnamed: 0'], inplace=True)
    data.index.name=None
    data = data.sort_values(by=['Primary Passed Tests', 'Secondary Passed Tests'], ascending=False)
    return render_template('view.html',tables=[data.to_html()],
    titles = ['Stock Screener Results'])


def run_screener():
    print("Running Screener", file=sys.stdout)
    screener = StockScreener()
    df_final = screener.screen()
    df_final.to_csv("screener_results.csv")


scheduler = APScheduler()
scheduler.add_job(func=run_screener, args=None, trigger='interval', id='job', seconds=14400, next_run_time=datetime.now())
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
    