from flask import *
import pandas as pd
from flask_apscheduler import APScheduler
from Screener import StockScreener
import sys
from datetime import datetime
import pathlib

app = Flask(__name__)
date = datetime.now()

@app.route("/")
def show_tables():
    data = pd.read_csv('screener_results.csv')
    data.set_index(['Unnamed: 0'], inplace=True)
    data.index.name=None

    cols = data.columns
    cols_first_rules = [col for col in cols if "(1st)" in col]
    cols_second_rules = [col for col in cols if "(2nd)" in col]
    cols_patterns = [col for col in cols if "Pattern" in col]
    cols_order = ['Ticker', 'N-Value Rating', 'Lwowski Rating', 'Primary Passed Tests', 'Secondary Passed Tests'] + cols_first_rules + cols_second_rules + cols_patterns
    remaining_cols = list(set(cols) - set(cols_order))
    print(cols_order+remaining_cols)
    data = data[cols_order+remaining_cols]
    data = data.sort_values(by=['N-Value Rating', 'Lwowski Rating'], ascending=False)
    data =  data.style.apply(color_passing_tests).render()

    fname = pathlib.Path('screener_results.csv')
    date = datetime.now()
    return render_template('view.html',tables=[data], date=date, titles = ['Stock Screener Results'])

def color_passing_tests(s):
    out = []
    for idx,v in enumerate(s):
        if type(v) == bool and v:
            out.append('background-color: #77dd77')
        else:
            if idx % 2 == 0:
                out.append('background-color: #eee')
            else:
                out.append('background-color: #fff')
    return out

def run_screener():
    print("Running Screener", file=sys.stdout)
    screener = StockScreener()
    df_final = screener.screen()
    date = datetime.now()
    df_final.to_csv("screener_results.csv")


scheduler = APScheduler()
scheduler.add_job(func=run_screener, args=None, trigger='cron', id='job', hour='6', minute='0')
scheduler.start()

if __name__ == "__main__":
    app.run()
    