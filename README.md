# Stock Sell Rules Checker
### Summary

This is an automated tool to check some sell rules for a stock portfolio.

### Installation
```
$ pip install -r requirements.txt
```

### How to Run
1. You must have a CSV file with the following case sensitive columns (Symbol,Buy Price,Buy Date). You can see [input_portfolio.csv](input_portfolio.csv) for an example.
2. Run the command below.
```
$ python CheckSellRules.py --input_csv_path PATH_TO_INPUT_CSV_PORTFOLIO --output_csv_path PATH_TO_SAVE_OUTPUT_CSV_PORTFOLIO
```

