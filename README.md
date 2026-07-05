# ESG Momentum and the Business Cycle: Evidence from European Equity Markets

## Abstract
> This thesis examines whether ESG momentum, which is measured as the 12-month Re
finitiv ESG score change of a firm, is positively associated with stock returns among
stocks in the STOXX Europe 600 index between June 2016 and September 2025. To
do so, it uses pooled OLS, random effects, fixed effects, and two-step difference gener
alized method of moments estimation. It further investigates whether long–short ESG
momentum portfolio payoffs are related to the business cycle and whether the com
mon macroeconomic variables dividend yield, short-term yield, term spread, and default
spread are associated with ESG momentum payoffs. The results suggest that ESG score
levels are generally negatively related to stock returns and ESG momentum is positively
associated with returns, although the significance of the evidence is subject to model
specifications. This result is consistent with the interpretation that ESG levels and ESG
momentum capture different economic mechanisms. High ESG score levels may proxy
for lower risk, while ESG momentum may capture repricing during the period in which
new information about ESG activities is incorporated into stock prices. The business
cycle analysis further suggests that ESG momentum payoffs are unlikely to be purely
firm-specific. ESG momentum portfolios with high ESG score changes exhibit higher
returns predicted by macro variables, and payoffs become small or negative after re
moving the macro-predicted component, especially in value-weighted ESG momentum
portfolios. Lagged macroeconomic variables appear to account for a meaningful share
of payoffs, as direct payoff regressions suggest that ESG momentum returns are partly
explained by dividend yield, short-term yield, term spread, and default spread. How
ever, the evidence remains sensitive to model specifications and weighting schemes.

## Author

Maurice Schmetzer  
M.Sc. Data Science in Business & Economics, University of Tübingen  
LinkedIn: [linkedin.com/in/maurice-schmetzer](https://www.linkedin.com/in/maurice-schmetzer) <br>
GitHub: [github.com/mauriceschmetzer](https://github.com/mauriceschmetzer)

## Repository Overview
This repository contains the Python code used to perform the analysis of the master thesis. It uses docker container, Python files and Juypter Notebooks.  

### Repository Structure

- `requirements.txt`: Python packages used across the notebooks and Refinitiv download scripts.
- `src/refinitiv_data_download/`: Python scripts and helper functions for Refinitiv data download.
- `src/data_analysis/`: Jupyter notebooks used for analysis. The notebooks are labeled `1` to `8` and are intended to be read and run in sequence.
- `src/data/input_data/`: Raw data files (Refinitiv & Other Data).
- `src/data/processed_data/`: Processed output data.
- `src/data/graphs/`: Generated figures.

### What each File Does

- The Python scripts are used to download refinitiv data
- Jupyter Notebook 1 cleans and transforms the raw data
- Jupyter Notebook 2 calculates the parameters used for the analysis
- Jupyter Notebook 3 converts the data to long format
- Jupyter Notebook 4 performs descriptive statistics
- Jupyter Notebook 5 executes POLS, RE, and FE analysis
- Jupyter Notebook 6 executes GMM analysis
- Jupyter Notebook 7 executes business-cycle analysis
- Jupyter Notebook 8 adds further visuals

### Output Files

The prefix (e.g. 01) indicates which jupyter notebook generated the file. 

- `data/processed_data/01_prepared_raw_data.xlsx`
- `data/processed_data/02_parameters.xlsx`
- `data/processed_data/03_pols_fe_re_gmm_data.csv`
- `data/processed_data/03_pols_fe_re_gmm_winsorized_data.csv`
- `data/processed_data/03_bc_data.csv`
- `data/processed_data/05_panel_model_results.xlsx`
- `data/processed_data/06_gmm_results.xlsx`
- `data/processed_data/07_portfolios.csv`
- `data/processed_data/07_portfolio_constituents.csv`
- `data/processed_data/07_portfolio_returns.csv`
- `data/processed_data/07_esg_momentum_payoff.csv`
- `data/processed_data/07_esg_momentum_payoff_with_macro_variables.csv`


### Running the code

Either run the repository within a docker container or install the required packages directly with:

```bash
pip install -r requirements.txt
```

- The main dependencies are `pandas`, `numpy`, `statsmodels`, `linearmodels`, `pydynpd`, `openpyxl`, `great-tables`, and `refinitiv.data`.
- The two Refinitiv download scripts currently contain a hard-coded Windows `local_path` and will need to be adapted before rerunning them on another machine.
- The notebooks assume relative paths such as `data/input_data/` and `data/processed_data/` and change directories with `os.chdir("..")`, so they are intended to be run from within the `src/data_analysis/` folder context.

### Data

This repository does not contain any proprietary market data from Refinitiv/Eikon or any other third-party data provider.
