# Downside-Risk
Analyzing a downside risk based trading strategy 

## Strategy description

For any asset X, using data from the past year, estimate its CAPM market beta and downside CAPM market beta which conditions on days where the market returns is lower than usual. Define the trading signal as (downside beta - beta). Update signals each month and form portfolios by ranking assets based on such signal. 

## Asset class

Stocks, Corporate bonds, ETFs

## Data

Daily stock returns of all common stocks on NYSE, NASDAQ and AMEX (2001 - 2023)

Monthly US corporate bond returns (2007 - 2023)

Daily ETF returns (2007 - 2023)

## Results

The long-only equity strategy appears to outperform the market when using a long sample period. However, the strategy has a high correlation to the market and the outperformance disappears when restricted to a more recent sample period. Long-short strategies tend to achieve much lower Sharpe ratios. No significant alpha is found when the strategy is regressed on the Fama-French 5 factors + Momentum. Generally, the strategy has a high turnover.

For details, please refer to `Results`.


## References

Downside Risk, Andrew Ang, Joseph Chen and Yuhang Xing, 2006

Conditional risk premia in currency markets and other asset classes, Martin Lettau, Matteo Maggiori and Michael Weber, 2013
