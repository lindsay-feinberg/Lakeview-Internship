import csv
import math
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import pytz
import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import seaborn as sns
from scipy import stats
from scipy.stats import beta

def change_to_chicago_tz(quote_datetime: pd.Series):
    return (
        quote_datetime.dt.tz_localize("US/Eastern")
        .dt.tz_convert("US/Central")
        .dt.tz_localize(None)
    )


def read_in_files(file):
    read_file = pd.read_csv(file, parse_dates = ['quote_datetime'])
    read_file['close'] = read_file['close'].replace(0, np.nan)
    return read_file


def filtering_daily(df):
    return df.groupby('trade_date')[['trade_date', 'close']].last().reset_index(drop = True)


def log_return(df):
    return np.log(df.close) - np.log(df.close.shift(1))


def plotting_scatterplots(df):
    plotting_data = pd.DataFrame(
        {"log_return_spx": df.log_return_spx, "log_return_vix": df.log_return_vix}
    )
    p = plotting_data.log_return_spx
    q = plotting_data.log_return_vix
    model = sm.OLS(q, p).fit()
    predictions = model.predict(p)
    
    print_model = model.summary()
    print(print_model)
    
    # sns.regplot('ave_spx', 'ave_vix', data= plotting_data)
    plt.show()
    
    print(p.describe())
    print(q.describe())
    """ plot_tf = (
        (
            plotting_data.log_return_spx
            >= np.mean(plotting_data.log_return_spx) + 0.5 * np.std(plotting_data.log_return_spx)
        )
        | (
            plotting_data.log_return_spx
            <= np.mean(plotting_data.log_return_spx) - 0.5 * np.std(plotting_data.log_return_spx)
        )
    ) & (
        (
            plotting_data.log_return_vix
            >= np.mean(plotting_data.log_return_vix) + 0.5 * np.std(plotting_data.log_return_vix)
        )
        | (
            plotting_data.log_return_vix
            <= np.mean(plotting_data.log_return_vix) - 0.5 * np.std(plotting_data.log_return_vix)
        )
    )
    plotting_data["z_scores_spx"] = stats.zscore(plotting_data.log_return_spx, axis=None)
    plotting_data["z_scores_vix"] = stats.zscore(plotting_data.log_return_vix, axis=None)
    not_outlier = (abs(plotting_data["z_scores_spx"]) < 3) & (
        abs(plotting_data["z_scores_vix"]) < 3
    )
    plotting_data["plott"] = plot_tf & not_outlier
    
    
    filtered_plot = plotting_data[(plotting_data.plott)]
    r = np.array(filtered_plot.log_return_spx)
    e = np.array(filtered_plot.log_return_vix)
    """
    r = np.array(plotting_data.log_return_spx)
    e = np.array(plotting_data.log_return_vix)
    plt.plot(r, e, "o")
    mf, bf = np.polyfit(r, e, 1)
    plt.plot(r, mf * r + bf)
    print(mf)
    
    model_t = sm.OLS(e, r).fit()
    predictions_t = model_t.predict(r)
    print_model_t = model_t.summary()
    print(print_model_t)



def beta_per_year(df):
    var = df.groupby(df.trade_date.dt.year).apply(
        lambda x: x.log_return_spx.cov(x.log_return_spx)
    )
    cov = df.groupby(df.trade_date.dt.year).apply(
        lambda x: x.log_return_spx.cov(x.log_return_vix)
    )
    beta_series_in_function = cov / var
    beta_series_in_function.index = pd.to_datetime(beta_series_in_function.index, format = '%Y')
    return beta_series_in_function


def main():
    # reading in files
    spx_reader = read_in_files("L:\Lakeview Investment Group\Lindsay\spx_index.csv")
    vix_reader = read_in_files("L:\Lakeview Investment Group\Lindsay\VIX_Futures_Minutely.csv")
    
    #print(vix_rdr.iloc[1])
    
    # changing vix_reader trade_date and expiration columns to datetime format
    vix_reader["trade_date"] = pd.to_datetime(vix_reader.trade_date, format="mixed")
    vix_reader["expiration"] = pd.to_datetime(vix_reader.expiration, format="mixed")
    
    # changing to CST timezone
    spx_reader["quote_datetime"] = change_to_chicago_tz(spx_reader.quote_datetime)
    
    # comparing expiration date to trade date
    unique_expiration = sorted(vix_reader.expiration.unique())
    vix_reader["month"] = (
        np.searchsorted(unique_expiration, vix_reader.expiration, side="left") -
        np.searchsorted(unique_expiration, vix_reader.trade_date, side="left")
    )
    
    # filtering to only front month
    vix_reader = vix_reader[(vix_reader.month) == 0]
    
    # performing log return calculations (do not need right now because minutely log returns)
    """ vix_temp = vix_reader.groupby(vix_reader.quote_datetime.dt.date)["close"].apply(
        lambda x: np.log(x) - np.log(x.shift(1))
    )
    spx_temp = spx_reader.groupby(spx_reader.quote_datetime.dt.date)["close"].apply(
        lambda x: np.log(x) - np.log(x.shift(1))
    )
    
    reader["Log_return"] = spx_temp.reset_index(drop=True)
    vix_reader["Log_return"] = vix_temp.values
    
    logset_spx = reader["Log_return"]
    logset_vix = vix_reader["Log_return"]
    """
    # print(vix_reader.loc[vix_reader['Log_return'].idxmax(), 'quote_datetime'])
    
    # making trade_dates column for spx
    spx_reader['trade_date'] = spx_reader.quote_datetime.dt.date
    vix_reader['trade_date'] = vix_reader.quote_datetime.dt.date
    
    # filtering spx and vix for only trade_date and close
    spxdf = filtering_daily(spx_reader)
    vixdf = filtering_daily(vix_reader)
    
    # calculating daily log returns and dropping na values
    spxdf["log_return_spx"] = log_return(spxdf)
    spxdf.dropna(inplace=True)
    vixdf["log_return_vix"] = log_return(vixdf)
    
    vixdf.dropna(inplace=True)
    
    #merging data
    ave_merged_data = pd.merge(
        spxdf, vixdf, left_on="trade_date", right_on="trade_date", how="inner"
    )
    
    
    # printing first ten to check if correct
    #for row in range(10):
        #print(reader.iloc[row])
    """
    bin_width_spx = np.std(logset_spx)
    logmean_spx = np.mean(logset_spx)
    bin_edges_spx = np.linspace(
        logmean_spx - bin_width_spx * 5, logmean_spx + bin_width_spx * 5, num=250
    )
    hist, edges = np.histogram(logset_spx, bins=bin_edges_spx)
    
    # Plot the histogram
    plt.hist(logset_spx, bins=bin_edges_spx, edgecolor="black")
    
    # Add labels and title
    plt.show()
    
    print(logset_spx.describe())
    
    # vix
    bin_width_vix = np.std(logset_vix)
    logmean_vix = np.mean(logset_vix)
    bin_edges_vix = np.linspace(
        logmean_vix - bin_width_vix * 5, logmean_vix + bin_width_vix * 5, num=250
    )
    hist, edges = np.histogram(logset_vix, bins=bin_edges_vix)
    
    # Plot the histogram
    plt.hist(logset_vix, bins=bin_edges_vix, edgecolor="black")
    
    # Add labels and title
    plt.show()
    
    print(logset_vix.describe())
    """
    
    # linear regression (playing around with it)
    x = np.array(ave_merged_data.log_return_spx).reshape(-1, 1)
    y = np.array(ave_merged_data.log_return_vix)
    
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x, y)
    print(r_sq)
    
    #solving for variance and covariance to solve for beta and intercept
    ave_merged_data["variance"] = ((ave_merged_data.log_return_spx 
                                   - np.mean((ave_merged_data.log_return_spx)))**2 )
    merged_data_variance = np.sum(ave_merged_data.variance)
    ave_merged_data["covariance"] = (
        ave_merged_data.log_return_spx - np.mean((ave_merged_data.log_return_spx))
    ) * (ave_merged_data.log_return_vix - np.mean((ave_merged_data.log_return_vix)))
    merged_data_covariance = np.sum(ave_merged_data.covariance)
    
    #solving for beta and intercept
    beta = merged_data_covariance / merged_data_variance
    intercept = (
        np.mean((ave_merged_data.log_return_vix)) - np.mean((ave_merged_data.log_return_spx)) * beta
    )
    
    #solving for r^2
    ave_merged_data["residual"] = (
        (ave_merged_data.log_return_vix) - (intercept + (ave_merged_data.log_return_spx) * beta)) **2 
    ave_merged_data["sum_squares"] = (
        ave_merged_data.log_return_vix - np.mean((ave_merged_data.log_return_vix))
    ) **2 
    ssr = np.sum(ave_merged_data.residual)
    sst = np.sum(ave_merged_data.sum_squares)
    r_sq = 1 - ssr / sst
    
    #showing scatterplot
    plt.scatter(ave_merged_data.log_return_spx, ave_merged_data.log_return_vix)
    plt.show()
    
    #plotting with regression line
    z = np.array(ave_merged_data.log_return_spx)
    plt.plot(z, y, "o")
    m, b = np.polyfit(z, y, 1)
    
    # add linear regression line to scatterplot
    plt.plot(z, m * z + b)
    
    print(beta) 
   
    #plotting data
   
    plotting_scatterplots(ave_merged_data)
    
    #converting trade_date to datetime
    ave_merged_data["trade_date"] = pd.to_datetime(ave_merged_data.trade_date)
    # testing hypotheses, not rolling
    beta_series = beta_per_year(ave_merged_data)
    
    # testing hypothesis, rolling
    temp_df = pd.DataFrame(
        {"log_return_spx": ave_merged_data.log_return_spx, "log_return_vix": ave_merged_data.log_return_vix}
    )
    varspx_rolling = temp_df.rolling(252).var()["log_return_spx"]
    covx_rolling_df = temp_df.rolling(252).cov()["log_return_vix"]
    covx_rolling_df.index = covx_rolling_df.index.get_level_values(1)
    covx_rolling_df = covx_rolling_df[covx_rolling_df.index == "log_return_spx"].reset_index(
        level=0, drop=True
    )
    
    
    beta_series_rolling = covx_rolling_df / varspx_rolling
    graphing_df = pd.DataFrame({"beta_rolling": beta_series_rolling})
    graphing_df.index = ave_merged_data["trade_date"]
    graphing_df.index.name = "Date"
    graphing_df = graphing_df.dropna()
    
    #starting up and down spx hypothesis
    negative_spx_df = ave_merged_data[ave_merged_data.log_return_spx <= 0]
    plotting_scatterplots(negative_spx_df)
    print("donefirst")
    positive_spx_df = ave_merged_data[ave_merged_data.log_return_spx > 0]
    plotting_scatterplots(positive_spx_df)
    
    #getting beta series for negative spx
    beta_series_negative_spx = beta_per_year(negative_spx_df)
    #getting beta series for positive spx
    beta_series_positive_spx = beta_per_year(positive_spx_df)
    

if __name__ == "__main__":
    main()
# beta_series_rolling = beta_series_rolling.dropna()

# plotting_data['plot'] = (plotting_data['ave_spx'] >= np.mean(plotting_data['ave_spx']) + np.std(plotting_data['ave_spx']))
# -*- coding: utf-8

"""
Spyder Editor
plotting_data['plot'] = ((plotting_data['ave_spx'] >= np.mean(plotting_data['ave_spx']) + np.std(plotting_data['ave_spx'])) or (plotting_data['ave_spx'] <= np.mean(plotting_data['ave_spx']) - np.std(plotting_data['ave_spx']))) and ((plotting_data['ave_vix'] >= np.mean(plotting_data['ave_vix']) + np.std(plotting_data['ave_vix'])) or (plotting_data['ave_vix'] <= np.mean(plotting_data['ave_vix']) - np.std(plotting_data['ave_vix'])))

This is a temporary script file.
"""
