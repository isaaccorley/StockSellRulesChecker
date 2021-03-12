import datetime
import pandas as pd
import stockquotes
import argparse
import os

class SellRuleChecker:
      
    @staticmethod
    def golden_sell_rule(buy_price,curr_price, tolerance=-0.08):
        percent_gain = (curr_price-buy_price)/buy_price
        print("Current Percent Gain/Loss: {:.2f}%".format(percent_gain*100))
        if percent_gain > tolerance:
            print("Do Not Sell Based on Golden Rule Check")
            return False
        else:
            print("Sell Based on Golden Rule Check")
            return True
        
    @staticmethod
    def standard_profit_goal_sell_rule(buy_price,curr_price, investment_date, date_tolerance_weeks=8, pct_tolerance=0.20):
        weeks_invested = (datetime.datetime.now() - investment_date).total_seconds()/(60*60*24*7)
        if weeks_invested <= date_tolerance_weeks:
            print("Investment is too young, do not sell based on Standard Profit Goal Sell Rule.")
            return False

        percent_gain = (curr_price-buy_price)/buy_price
        print("Current Percent Gain/Loss: {:.2f}%".format(percent_gain*100))
        if percent_gain > pct_tolerance:
            print("Sell Based on Golden Rule Check")
            return True
        else:
            print("Do Not Sell Based on Golden Rule Check")
            return False
        
    @staticmethod
    def decline_from_peak_sell_rule(buy_price, curr_price, profit_pct_lower=0.035, profit_pct_upper=0.11, trail_stop_pct=0.1):
        percent_gain = (curr_price-buy_price)/buy_price
        if percent_gain >= profit_pct_lower and percent_gain <= profit_pct_upper:
            print("Place a {:.2f}% trailing stop based on the Decline from Peak Sell Rule".format(trail_stop_pct*100))
            return True
        else:
            print("Do Not Place a trailing stop based on the Decline from Peak Sell Rule")
            return False
                    
    @staticmethod
    def certainteed_exception_rule(buy_price,curr_price, investment_date, date_tolerance_weeks=3, pct_tolerance=0.20):
        percent_gain = (curr_price-buy_price)/buy_price
        weeks_invested = (datetime.datetime.now() - investment_date).total_seconds()/(60*60*24*7)
        if weeks_invested <= date_tolerance_weeks and percent_gain>=pct_tolerance:
            print("Hold for a full 8 weeks.")
            return True
        else:
            print("You do not need to hold for a full 8 weeks")
            return False
        
    @staticmethod
    def check_sell_rules(input_csv_path, output_csv_path):
        df = pd.read_csv(input_csv_path)
        df["Sell Golden Rule"] = False
        df["Sell Standard Profit Goal"] = False
        df["Place Trailing Stop for Decline from Peak Sell Rule"] = False
        df["Hold for 8 Weeks for Certainteed Exception Rule"] = False

        for i, stock in df.iterrows():
            symbol = stock["Symbol"]
            print("---------------------------------")
            print(symbol)
            investment_date = datetime.datetime.strptime(stock['Buy Date'],'%m/%d/%Y')
            avg_share_price = float(stock['Buy Price'].replace("$", ""))
            curr_price = stockquotes.Stock(symbol).current_price
            df.loc[df.Symbol == symbol, 'Sell Golden Rule'] = SellRuleChecker.golden_sell_rule(avg_share_price, curr_price=curr_price)
            df.loc[df.Symbol == symbol, 'Sell Standard Profit Goal'] = SellRuleChecker.standard_profit_goal_sell_rule(avg_share_price, curr_price=curr_price, investment_date=investment_date)
            df.loc[df.Symbol == symbol, 'Place Trailing Stop for Decline from Peak Sell Rule'] = SellRuleChecker.decline_from_peak_sell_rule(avg_share_price, curr_price=curr_price)
            df.loc[df.Symbol == symbol, 'Hold for 8 Weeks for Certainteed Exception Rule'] = SellRuleChecker.certainteed_exception_rule(avg_share_price, curr_price=curr_price, investment_date=investment_date)
            print("---------------------------------")
            df.to_csv(output_csv_path)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv_path", help="Path to input portfolio CSV file", type=str, default = "input_portfolio.csv")
    parser.add_argument("--output_csv_path", help="Path to output portfolio CSV file", type=str, default="output_portfolio.csv")
    args = parser.parse_args()
    sell_rule_checker = SellRuleChecker()
    sell_rule_checker.check_sell_rules(os.path.join(args.input_csv_path), os.path.join(args.output_csv_path))
    
        