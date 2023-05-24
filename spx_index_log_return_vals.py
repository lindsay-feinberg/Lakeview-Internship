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

def change_to_chicago_tz(quote_datetime: pd.Series):
    return (quote_datetime.dt.tz_localize('US/Eastern')
                              .dt.tz_convert('US/Central')
                              .dt.tz_localize(None))





#reading in file
reader = pd.read_csv('L:\Lakeview Investment Group\Lindsay\spx_index.csv')
vix_rdr = pd.read_csv('L:\Lakeview Investment Group\Lindsay\VIX_Futures_Minutely.csv')
print(vix_rdr.iloc[1])

reader['close'].replace(0, np.nan, inplace=True)
vix_rdr['close'].replace(0, np.nan, inplace=True)


#converting quote_datetime from string to dataetime format
reader['quote_datetime'] = pd.to_datetime(reader['quote_datetime'])  
vix_rdr['quote_datetime'] = pd.to_datetime(vix_rdr['quote_datetime'])
vix_rdr['trade_date'] = pd.to_datetime(vix_rdr['trade_date'], format = 'mixed') 
vix_rdr['expiration'] = pd.to_datetime(vix_rdr['expiration'], format = 'mixed')


#changing to CST timezone
reader['quote_datetime'] = change_to_chicago_tz(reader.quote_datetime)
spx_temp = reader.groupby(reader.quote_datetime.dt.date)['close'].apply(lambda x: np.log(x) - np.log(x.shift(1)))
ordered_by_exp = vix_rdr.groupby('expiration').apply(lambda x: x.sort_values('quote_datetime')).reset_index(drop=True)

#comparing front month
un_exp = ordered_by_exp['expiration'].unique().tolist()
vix_rdr['front_month'] = vix_rdr['expiration'] == np.array(un_exp)[np.searchsorted(un_exp, vix_rdr['trade_date'], side = 'left')]

filtered_vix = vix_rdr[(vix_rdr.front_month)]
vix_temp = filtered_vix.groupby(filtered_vix.quote_datetime.dt.date)['close'].apply(lambda x: np.log(x) - np.log(x.shift(1)))
     
reader['Log_return'] = spx_temp.reset_index(drop=True)
filtered_vix['Log_return'] = vix_temp.values

logset_spx = reader['Log_return']   
logset_vix = filtered_vix['Log_return']

#print(filtered_vix.loc[filtered_vix['Log_return'].idxmax(), 'quote_datetime'])

spxdf = pd.DataFrame({'datespx': reader.groupby(reader.quote_datetime.dt.date)['quote_datetime'].last().reset_index(drop=True), 'closespx': reader.groupby(reader.quote_datetime.dt.date)['close'].last().reset_index(drop=True)})
spxdf['ave_spx'] = np.log(spxdf.closespx) - np.log(spxdf.closespx.shift(1))
spxdf['datespx'] = spxdf['datespx'].dt.normalize()
spxdf.dropna(inplace=True)

vixdf = pd.DataFrame({'datevix': filtered_vix.groupby(filtered_vix.trade_date.dt.date)['trade_date'].last().reset_index(drop=True), 'closevix': filtered_vix.groupby(filtered_vix.trade_date.dt.date)['close'].last().reset_index(drop=True)})
vixdf['ave_vix'] = np.log(vixdf.closevix) - np.log(vixdf.closevix.shift(1))
vixdf.dropna(inplace=True)

ave_merged_data = pd.merge(spxdf, vixdf, left_on= 'datespx', right_on = 'datevix', how = 'inner')



#printing first ten to check if correct
for row in range(10):
    print(reader.iloc[row])

bin_width_spx = np.std(logset_spx)
logmean_spx = np.mean(logset_spx)
bin_edges_spx = np.linspace(logmean_spx - bin_width_spx*5, logmean_spx + bin_width_spx*5, num=250)
hist, edges = np.histogram(logset_spx, bins=bin_edges_spx)

# Plot the histogram
plt.hist(logset_spx, bins=bin_edges_spx, edgecolor='black')

# Add labels and title
plt.show()

print(logset_spx.describe())

#vix
bin_width_vix = np.std(logset_vix)
logmean_vix = np.mean(logset_vix)
bin_edges_vix = np.linspace(logmean_vix - bin_width_vix*5, logmean_vix + bin_width_vix*5, num=250)
hist, edges = np.histogram(logset_vix, bins=bin_edges_vix)

# Plot the histogram
plt.hist(logset_vix, bins=bin_edges_vix, edgecolor='black')

# Add labels and title
plt.show()

print(logset_vix.describe())

#determining beta
x = np.array(ave_merged_data['ave_spx']).reshape(-1,1)
y = np.array(ave_merged_data['ave_vix'])

model = LinearRegression().fit(x, y)
r_sq = model.score(x, y)
print(r_sq)

ave_merged_data['variance'] = ((ave_merged_data['ave_spx'] - np.mean((ave_merged_data['ave_spx'])))*(ave_merged_data['ave_spx'] - np.mean((ave_merged_data['ave_spx']))))
md_var = np.sum(ave_merged_data['variance'])
ave_merged_data['covariance'] = ((ave_merged_data['ave_spx'] - np.mean((ave_merged_data['ave_spx'])))*(ave_merged_data['ave_vix'] - np.mean((ave_merged_data['ave_vix']))))
md_covar = np.sum(ave_merged_data['covariance'])
beta = md_covar/ md_var
a_eq = np.mean((ave_merged_data['ave_vix'])) - np.mean((ave_merged_data['ave_spx']))*beta
ave_merged_data['residual'] = ((ave_merged_data['ave_vix']) - (a_eq + (ave_merged_data['ave_spx'])*beta))* ((ave_merged_data['ave_vix']) - (a_eq + (ave_merged_data['ave_spx'])*beta))
ave_merged_data['sum_squares'] = (ave_merged_data['ave_vix'] - np.mean((ave_merged_data['ave_vix'])))*(ave_merged_data['ave_vix'] - np.mean((ave_merged_data['ave_vix'])))
ssr = np.sum(ave_merged_data['residual'])
sst = np.sum(ave_merged_data['sum_squares'])
r_sq = 1 - ssr/sst

plt.scatter(ave_merged_data['ave_spx'], ave_merged_data['ave_vix'])
plt.show()

z = np.array(ave_merged_data['ave_spx'])
plt.plot(z, y, 'o')
m, b = np.polyfit(z, y, 1)

#add linear regression line to scatterplot 
plt.plot(x, m*z+b)

print(beta)

plotting_data = pd.DataFrame({'ave_spx': ave_merged_data['ave_spx'], 'ave_vix': ave_merged_data['ave_vix']})
p = plotting_data['ave_spx']
q = plotting_data['ave_vix']
model = sm.OLS(q, p).fit()
predictions = model.predict(p) 

print_model = model.summary()
print(print_model)

sns.regplot('ave_spx', 'ave_vix', data= plotting_data)
plt.show()

print(p.describe())
print(q.describe())
plot_tf = (((plotting_data['ave_spx'] >= np.mean(plotting_data['ave_spx']) + .5*np.std(plotting_data['ave_spx'])) | (plotting_data['ave_spx'] <= np.mean(plotting_data['ave_spx']) - .5*np.std(plotting_data['ave_spx']))) & ((plotting_data['ave_vix'] >= np.mean(plotting_data['ave_vix']) + .5*np.std(plotting_data['ave_vix'])) | (plotting_data['ave_vix'] <= np.mean(plotting_data['ave_vix']) - .5*np.std(plotting_data['ave_vix'])))) 
plotting_data['z_scores_spx'] = stats.zscore(plotting_data['ave_spx'], axis = None)
plotting_data['z_scores_vix'] = stats.zscore(plotting_data['ave_vix'], axis = None)
not_outlier = (abs(plotting_data['z_scores_spx']) < 3) & (abs(plotting_data['z_scores_vix']) < 3)
plotting_data['plott'] = plot_tf & not_outlier


filtered_plot = plotting_data[(plotting_data.plott)]
r = np.array(filtered_plot['ave_spx'])
e = np.array(filtered_plot['ave_vix'])
plt.plot(r,e,'o')
mf, bf = np.polyfit(r, e, 1)
plt.plot(r, mf*r+bf)
print(mf)

model_t = sm.OLS(e, r).fit()
predictions_t = model_t.predict(r)
print_model_t = model_t.summary()
print(print_model_t)

#plotting_data['plot'] = (plotting_data['ave_spx'] >= np.mean(plotting_data['ave_spx']) + np.std(plotting_data['ave_spx']))
# -*- coding: utf-8 

"""
Spyder Editor
plotting_data['plot'] = ((plotting_data['ave_spx'] >= np.mean(plotting_data['ave_spx']) + np.std(plotting_data['ave_spx'])) or (plotting_data['ave_spx'] <= np.mean(plotting_data['ave_spx']) - np.std(plotting_data['ave_spx']))) and ((plotting_data['ave_vix'] >= np.mean(plotting_data['ave_vix']) + np.std(plotting_data['ave_vix'])) or (plotting_data['ave_vix'] <= np.mean(plotting_data['ave_vix']) - np.std(plotting_data['ave_vix'])))

This is a temporary script file.
"""

