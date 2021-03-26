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
    data =  data.style.apply(color_passing_tests).render()
    return render_template('view.html',tables=[data],
    titles = ['Stock Screener Results'])

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
    df_final.to_csv("screener_results.csv")


scheduler = APScheduler()
scheduler.add_job(func=run_screener, args=None, trigger='cron', id='job', hour='6', minute='0')
scheduler.start()

if __name__ == "__main__":
    app.run()
    