# Stock Sell Rules Checker
### Summary

This is an automated tool to check some sell rules for a stock portfolio.

### Installation
```
$ pip install -r requirements.txt
```

### How to Run on Entire Portfolio
1. You must have a CSV file with the following case sensitive columns (Symbol,Buy Price,Buy Date). You can see [input_portfolio.csv](input_portfolio.csv) for an example.
2. Run the command below.
```
$ python CheckSellRules.py --input_csv_path PATH_TO_INPUT_CSV_PORTFOLIO --output_csv_path PATH_TO_SAVE_OUTPUT_CSV_PORTFOLIO
```

### Use Google Colab to Run on a Single Stock
1. Navigate to the [Google Colab Notebook](CheckStockSellRules.ipynb) then click on the "Open in Colab" button towards the top.

