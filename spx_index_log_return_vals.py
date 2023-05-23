import csv
import math
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import pytz
import numpy as np
from sklearn.linear_model import LinearRegression

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


spxdf = pd.DataFrame({'datespx': reader['quote_datetime'], 'ave_spx': reader['Log_return']})

vixdf = pd.DataFrame({'datevix': filtered_vix['quote_datetime'], 'ave_vix': filtered_vix['Log_return']})

merged_data = pd.merge(spxdf, vixdf, left_on= 'datespx', right_on = 'datevix', how = 'inner')



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

merged_data['date'] = merged_data['datespx'].dt.date
ave_merged_data = merged_data.groupby('date').apply(lambda x: x[x['datespx'] == x['datespx'].max()])
ave_merged_data.reset_index(drop=True, inplace=True)
ave_merged_data.dropna(inplace=True)


"""
steps = 27
ave_spx = []
ave_vix = []
for i in range(0, len(merged_data), steps):
    ave_spx.append(merged_data.loc[i, 'Log_return_x'])
    
for i in range(0, len(merged_data), steps):
    ave_vix.append(merged_data.loc[i,'Log_return_y'])

ave_spx_ser = pd.Series(ave_spx)
ave_spx_ser.name = 'ave_spx'
ave_vix_ser = pd.Series(ave_vix)
ave_vix_ser.name = 'ave_vix'

ave_merged_data = pd.merge(ave_spx_ser, ave_vix_ser, right_index = True, left_index = True)
"""
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
print(beta)

# -*- coding: utf-8 

"""
Spyder Editor

This is a temporary script file.
"""

