from finviz.screener import Screener
import nest_asyncio
import finviz
import pandas_datareader as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)

import datetime
import stockquotes
import pandas as pd
import tqdm
nest_asyncio.apply()

import time
from tqdm.contrib.concurrent import process_map

class StockScreener:

  @staticmethod
  def initial_screen():
    eps_5year_over0pct = False
    eps_qoq_over0pct = False
    eps_yoy_over0pct = False
    sales_5years_over0pct = False
    sales_qoq_over0pct = True

    filters = []
    if eps_5year_over0pct:
      filters.append('fa_eps5years_pos')
    if eps_qoq_over0pct:
      filters.append('fa_epsqoq_pos')
    if eps_yoy_over0pct:
      filters.append('fa_epsyoy_pos')
    if sales_5years_over0pct:
      filters.append('fa_sales5years_pos')
    if sales_qoq_over0pct:
      filters.append('fa_salesqoq_pos')

    stock_list = Screener(filters=filters, table='Performance', order='price')
    return stock_list
  
  @staticmethod
  def moving_average(yahoo_df, days, delta=0):
      df = yahoo_df.reset_index()
      curr_date = df['Date'].max() - datetime.timedelta(days=delta)
      end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)
      
      df_days = df[df['Date'] >= end_date]
      df_days = df_days[df_days['Date'] <= curr_date]
      return float(df_days['Close'].mean())

  @staticmethod
  def moving_average_volume(yahoo_df, days, delta=0):
      df = yahoo_df.reset_index()
      curr_date = df['Date'].max() - datetime.timedelta(days=delta)
      end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)
      
      df_days = df[df['Date'] >= end_date]
      df_days = df_days[df_days['Date'] <= curr_date]
      return float(df_days['Volume'].mean())

  @staticmethod
  def week52_low_high(yahoo_df):
      df = yahoo_df.reset_index()
      curr_date = df['Date'].max()
      end_date = curr_date - datetime.timedelta(days=365)
      
      df_days = df[df['Date'] >= end_date]
      return float(df_days['Close'].max()), float(df_days['Close'].min())

  @staticmethod
  def SMA200_slope_positive_rule(yahoo_df, ticker, days=21):
    for day in range(days):
      if moving_average(yahoo_df, days=200, delta=day) >= moving_average(yahoo_df, days=200, delta=day+1):
        continue
      else:
        return False
    return True

  @staticmethod
  def check_double_bottom_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_doublebottom'], table='Performance', order='price')
    except:
      stocks = []

    df['Double Bottom Chart'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Double Bottom Chart'] = True
    return df

  @staticmethod
  def check_inverse_head_and_shoulder_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_headandshouldersinv'], table='Performance', order='price')
    except:
      stocks = []

    df['Inverse Head and Shoulder Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Inverse Head and Shoulder Pattern'] = True
    return df

  @staticmethod
  def check_multiple_bottom_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_multiplebottom'], table='Performance', order='price')
    except:
      stocks = []

    df['Multiple Bottom Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Multiple Bottom Pattern'] = True
    return df

  @staticmethod
  def check_channel_up_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_channelup'], table='Performance', order='price')
    except:
      stocks = []

    df['Channel Up Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Channel Up Pattern'] = True
    return df

  @staticmethod
  def check_channel_up_strong_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_channelup2'], table='Performance', order='price')
    except:
      stocks = []

    df['Channel Up Strong Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Channel Up Strong Pattern'] = True
    return df

  @staticmethod
  def check_wedge_down_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_wedgedown'], table='Performance', order='price')
    except:
      stocks = []

    df['Wedge Down Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Wedge Down Pattern'] = True
    return df

  @staticmethod
  def check_wedge_down_strong_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_wedgedown2'], table='Performance', order='price')
    except:
      stocks = []

    df['Wedge Down Strong Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Wedge Down Strong Pattern'] = True
    return df

  @staticmethod
  def screen_stock(stock):
    if stock["Ticker"] == "":
      return

    finviz_stats = finviz.get_stock(stock['Ticker'])
    prev_close = float(finviz_stats['Prev Close'].replace("$",""))

    # Price greater than $10 rule
    if prev_close < 10:
      return

    screened_stocks[stock['Ticker']] = {}
    
    try:
        yahoo_df = pdr.get_data_yahoo(stock['Ticker'], interval = "d")
    except:
      return

    SMA200_value = moving_average(yahoo_df, days=200)
    SMA150_value = moving_average(yahoo_df, days=150)
    SMA50_value = moving_average(yahoo_df, days=50)
    SMA50_volume_value = moving_average_volume(yahoo_df, days=50)

    # Liquidity Rule
    if SMA50_value*SMA50_volume_value <= 20e6:
      return

    SMA200_percent = float(finviz_stats['SMA200'].replace("%",""))/100
    SMA50_percent = float(finviz_stats['SMA50'].replace("%",""))/100
    volume = float(finviz_stats['Volume'].replace(",",""))

    try:
      EPS_QoQ_percent = float(finviz_stats['EPS Q/Q'].replace("%",""))/100
    except:
      EPS_QoQ_percent = 0

    try:
      Sales_QoQ_percent = float(finviz_stats['Sales Q/Q'].replace("%",""))/100
    except:
      Sales_QoQ_percent = 0

    try:
      inst_own = float(finviz_stats['Inst Own'].replace("%",""))/100
    except:
      inst_own = 0
    
    shares_outstanding = finviz_stats['Shs Outstand']
    if 'M' in shares_outstanding:
      shares_outstanding = float(shares_outstanding.replace("M", ""))*1e6
    elif 'B' in shares_outstanding:
      shares_outstanding = float(shares_outstanding.replace("B", ""))*1e9
    elif 'T' in shares_outstanding:
      shares_outstanding = float(shares_outstanding.replace("T", ""))*1e12
    else:
      shares_outstanding = 0

    week52_high, week52_low = week52_low_high(yahoo_df)
    
    screened_stocks[stock['Ticker']]['SMA200_value'] = SMA200_value
    screened_stocks[stock['Ticker']]['SMA150_value'] = SMA150_value
    screened_stocks[stock['Ticker']]['SMA50_value'] = SMA50_value
    screened_stocks[stock['Ticker']]['SMA200_percent'] = SMA200_percent
    screened_stocks[stock['Ticker']]['SMA50_percent'] = SMA50_percent
    screened_stocks[stock['Ticker']]['EPS_QoQ_percent'] = EPS_QoQ_percent
    screened_stocks[stock['Ticker']]['Sales_QoQ_percent'] = Sales_QoQ_percent
    screened_stocks[stock['Ticker']]['prev_close'] = prev_close
    screened_stocks[stock['Ticker']]['week52_high'] = week52_high
    screened_stocks[stock['Ticker']]['week52_low'] = week52_low
    screened_stocks[stock['Ticker']]['Inst. Ownership'] = inst_own
    screened_stocks[stock['Ticker']]['Shares Outstanding'] = shares_outstanding
    screened_stocks[stock['Ticker']]['volume'] = volume

    # volume*price > $15mm rule
    if volume*prev_close > 15000000:
      vol_price_rule = True
    else:
      vol_price_rule = False
    screened_stocks[stock['Ticker']]['vol_price_rule'] = vol_price_rule

    # EPS QoQ Yearly > 18% rule
    if EPS_QoQ_percent >= .18:
      eps_QoQ_yearly_rule = True
    else:
      eps_QoQ_yearly_rule = False
    screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule'] = eps_QoQ_yearly_rule

    # Sales QoQ Yearly > 25% rule
    if Sales_QoQ_percent >= .25:
      sales_QoQ_yearly_rule = True
    else:
      sales_QoQ_yearly_rule = False
    screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule'] = sales_QoQ_yearly_rule

    # Shares Outstanding <= 25 mil
    if shares_outstanding <= 25e6:
      shares_outstanding_rule = True
    else:
      shares_outstanding_rule = False
    screened_stocks[stock['Ticker']]['shares_outstanding_rule'] = shares_outstanding_rule

    # Institutional Ownership < 35%
    if 0.05 <= inst_own <= .35:
      inst_ownership_rule = True
    else:
      inst_ownership_rule = False
    screened_stocks[stock['Ticker']]['inst_ownership_rule'] = inst_ownership_rule

    # Positive 200d MA positive
    SMA200_slope_rule = SMA200_slope_positive_rule(yahoo_df, ticker=stock['Ticker'], days=21)
    screened_stocks[stock['Ticker']]['SMA200_slope_rule'] = SMA200_slope_rule
        
    # 150d MA greater than 200d MA
    if SMA150_value > SMA200_value:
        SMA150_greater_SMA200_rule = True
    else:
        SMA150_greater_SMA200_rule = False
    screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule'] = SMA150_greater_SMA200_rule
        
    # 50d MA greater than 150d MA
    if SMA50_value > SMA150_value:
        SMA50_greater_SMA150_rule = True
    else:
        SMA50_greater_SMA150_rule = False
    screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule'] = SMA50_greater_SMA150_rule
        
    # Close above 50d MA
    if prev_close > SMA50_value:
        close_greater_SMA50_rule = True
    else:
        close_greater_SMA50_rule = False
    screened_stocks[stock['Ticker']]['close_greater_SMA50_rule'] = close_greater_SMA50_rule
        
    # 52 week high low span rule
    if 0.75*week52_high > 1.25*week52_low:
        week52_span_rule = True
    else:
        week52_span_rule = False
    screened_stocks[stock['Ticker']]['week52_span_rule'] = week52_span_rule
    
    # Close above 52 week high - 25%
    if prev_close > 0.75*week52_high:
        close_above_52weekhigh_rule = True
    else:
        close_above_52weekhigh_rule = False
    screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule'] = close_above_52weekhigh_rule
    return screened_stocks

  @staticmethod
  def cleanup_screen(df_out):
    primary_rules = ['eps_QoQ_yearly_rule', 'sales_QoQ_yearly_rule', 'SMA200_slope_rule', 
                 'SMA150_greater_SMA200_rule', 'SMA50_greater_SMA150_rule', 'close_greater_SMA50_rule', 
                 'week52_span_rule', 'close_above_52weekhigh_rule']

    secondary_rules = ['vol_price_rule', 'inst_ownership_rule', 'shares_outstanding_rule']
    df_out['Primary Passed Tests'] = (df_out[list(primary_rules)]).sum(1)
    df_out['Secondary Passed Tests'] = (df_out[list(secondary_rules)]).sum(1)

    cols = df_out.columns.tolist()

    for rule in primary_rules:
      if rule in cols:
        idx = cols.index(rule)
        cols[idx] = rule + " (1st)"

    for rule in secondary_rules:
      if rule in cols:
        idx = cols.index(rule)
        cols[idx] = rule + " (2nd)"

    df_out.columns = cols
    return df_out

  @staticmethod
  def main_screen(stock_list):
    screened_stocks = {}
    results = process_map(StockScreener.screen_stock, stock_list, max_workers=16)
    screened_stocks = {}
    for d in results:
      if d is not None:
        screened_stocks.update(d)
      
    output_list = []
    for stock in screened_stocks.keys():
        cols = ["Ticker"] + list(screened_stocks[stock].keys())
        temp_list = []
        temp_list.append(stock)
        for rule in screened_stocks[stock].keys():
            temp_list.append(screened_stocks[stock][rule])
        output_list.append(temp_list)
            
    df_out = pd.DataFrame(output_list,columns=cols)
    return df_out
    
  @staticmethod
  def chart_pattern_screen(df_out):
    df_passed = df_out[df_out["Primary Passed Tests"] >= 8]
    df_passed = check_double_bottom_chart_pattern(df_passed)
    df_passed = check_inverse_head_and_shoulder_chart_pattern(df_passed)
    df_passed = check_multiple_bottom_chart_pattern(df_passed)
    df_passed = check_channel_up_chart_pattern(df_passed)
    df_passed = check_channel_up_strong_chart_pattern(df_passed)
    df_passed = check_wedge_down_chart_pattern(df_passed)
    df_passed = check_wedge_down_strong_chart_pattern(df_passed)
    return df_passed

  def screen(self):
    print("Starting Screener")
    stock_list = StockScreener.initial_screen()
    print("Initial Screen Done")
    df_out = StockScreener.main_screen(stock_list)
    print("Main Screen Done")
    df_out = StockScreener.cleanup_screen(df_out)
    print("Cleanup Screen Done")
    df_final = StockScreener.chart_pattern_screen(df_out)
    return df_final

screener = StockScreener()
df_final = screener.screen()
df_final.to_csv("screener_results.py")

  
