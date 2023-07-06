# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 08:58:17 2023

@author: lfeinberg
"""

#importing, will take out stuff at end when not needed
import pandas as pd
import numpy as np
import math
import calendar
from openpyxl import Workbook
import datetime
from datetime import datetime
from pandas.tseries.offsets import BMonthEnd

#returns a list of the last business day each month
def last_business_days(start_date, end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    #pandas BusinessMonth
    dates = pd.date_range(start=start_date, end=end_date, freq='BM')
    last_business_days = dates + BMonthEnd()

    return last_business_days.tolist()

#filtering df to make it divided by type of trade
def filtering_df(df, type_one, type_two):
    return df[(df.type == type_one) | (df.type == type_two)]

def true_price (daily_trades, index, current_pnl, equity_quantity, current_weighted_ave):
    if daily_trades.at[index, 'type'] == 'ASSIGN':
        new_pnl_ae = current_pnl + equity_quantity*(daily_trades.at[index, 'price'] - current_weighted_ave)
    else:
        new_pnl_ae = current_pnl + equity_quantity*(daily_trades.at[index, 'price'] + current_weighted_ave)
    return new_pnl_ae
#making it more readable, and differentiate the files
trade_file = r'L:/Lakeview Investment Group/Lindsay/abn_trades_lindsay.xlsx'
#trade_file = r'L:/Lakeview Investment Group/Lindsay/debugging_pnl.xlsx'
#bloomberg_file = r'L:/Lakeview Investment Group/Lindsay/bloomberg_data_onesheet.xlsx'
bloomberg_file = r'L:/Lakeview Investment Group/Lindsay/bloomberg_data_copy.xlsx'
label_type_file = r'L:/Lakeview Investment Group/Lindsay/long_short_mixed_fixed.xlsx'
#long_short_mixed_file = r'L:/Lakeview Investment Group/Lindsay/firm_exposure_together.xlsx'

#reading in files
trade_df = pd.read_excel(trade_file)
#trade_df = pd.read_excel(r'L:/Lakeview Investment Group/Lindsay/debugging_pnl.xlsx')
bloomberg_df = pd.read_excel(bloomberg_file)

final_showing_df = pd.DataFrame({'long':[], 'short':[], 'short LETF':[], 'long LETF':[], 'VIX':[]})

label_type_df = pd.read_excel(label_type_file)

#fixing index
label_type_df.index = label_type_df.date_column
label_type_df = label_type_df.drop(labels = 'date_column', axis =1)

#long_short_mixed_df = pd.read_excel(long_short_mixed_file)

'''#accessing only date part of long/short/mixed_df
long_short_mixed_dates_df = long_short_mixed_df.head(118)

#accessing only type
label_df = long_short_mixed_df.tail(1)

for column in label_df.columns:
    index = 124
    if label_df.at[index, column] == 'short':
        long_short_mixed_dates_df[column] = 'short'
    elif label_df.at[index, column] == 'long':
        long_short_mixed_dates_df[column] = 'long'
    elif ((label_df.at[index, column] == 'long LETF') | (label_df.at[index, column] == 'long LTF')):
        long_short_mixed_dates_df[column] = 'long LETF'
    elif ((label_df.at[index, column] == 'short LETF') | (label_df.at[index, column] == 'short LTF')):
        long_short_mixed_dates_df[column] = 'short LETF'
    elif label_df.at[index, column] == 'VIX':
        long_short_mixed_dates_df[column] = 'VIX'

long_short_mixed_dates_df.index = long_short_mixed_dates_df.date_column
long_short_mixed_dates_df = long_short_mixed_dates_df.drop(labels = 'date_column', axis =1)

'''
#setting index to date for bloomberg so it is accessible
bloomberg_df = bloomberg_df.set_index(bloomberg_df.DATES)

#filtering the trade_df by the type
stock_option_df = filtering_df(trade_df, 'OPTION', 'STOCK')
assign_exer_df = filtering_df(trade_df, 'ASSIGN', 'EXER')

#creating pnl dictionary
pnl_dict = {}

#creating an unique list of trade dates
unique_trade_dates = pd.unique(trade_df.date)

#adding the last business day of each month if that particular month did not
#have a trade that day
extra_dates = [datetime(2019, 10, 31), datetime(2019, 11, 29), 
                                datetime(2019, 12, 31), datetime(2020, 1, 31),
                                datetime(2020, 4, 30), datetime(2020, 5, 29), 
                                datetime(2020, 7,31), datetime(2020, 10, 30), 
                                datetime(2020, 1, 17), datetime(2020, 3, 20),
                                datetime(2020, 6, 19),
                                datetime(2020, 7, 17), datetime(2022, 9, 2),
                                datetime(2022, 9, 9), datetime(2022, 9, 16),
                                datetime(2022, 10, 21), datetime(2022, 11, 18),
                                datetime(2022, 12, 16), datetime(2023, 1, 20),
                                datetime(2023, 2, 17), datetime(2023, 3, 17),
                                datetime(2023, 6, 16), datetime(2023, 9, 15),
                                datetime(2024, 1, 19)]
#debugging
#extra_dates.
#extra_dates.append(datetime(2020, 11, 30))
#combining and sorting full list of unique dates
extra_dates = pd.Series(extra_dates)
unique_trade_dates = pd.Series(unique_trade_dates)
unique_trade_dates = pd.concat([extra_dates, unique_trade_dates])
unique_trade_dates = unique_trade_dates.sort_values().reset_index(drop=True)


#set beginning and end of time period
s_date = datetime(2019, 9, 1)
e_date = datetime(2022, 8, 31)

#getting the list of last business day per month and add in 5/28 (before MDW)
d_list = last_business_days(s_date, e_date)
d_list.append(datetime(2021, 5, 28))

#set up monthly dictionary
monthly_dict = {}
test_dict = {}
exp_dict = {}
#unique_trade_dates = unique_trade_dates[2:6]
lis = []
#month_pnl
monthly_pnl_list = []
#loop through each trade date
for date in unique_trade_dates:  
    #get a dataframe with only trades of that day
    day_trades = stock_option_df[stock_option_df.date == date]
    expiring_df = stock_option_df[stock_option_df.expiration == date]
    
    #loop through all trades of that day
    for index in day_trades.index:
        tick = day_trades.at[index, 'ticker']
        real_quantity = day_trades.at[index, 'quantity']
        
        #get correct value for quantity
        if day_trades.at[index, 'type'] == 'OPTION':
            quantity = 100 * real_quantity
        else:
            quantity = real_quantity
        
        #checking if ticker is in dictionary
        if tick in pnl_dict.keys():
            #getting current values 
            current_weighted_ave = pnl_dict[tick][0]
            current_position = pnl_dict[tick][1]
            current_pnl = pnl_dict[tick][2]
            current_type = pnl_dict[tick][3]
            
            #getting new position after trade
            new_position = current_position + real_quantity
            
            #fixing stock split
            if (date == datetime(2020, 4, 23)) & (tick == 'TECS Equity'):
                pnl_dict[tick] = [current_weighted_ave*10, current_position/10, current_pnl, current_type]
                continue
            elif (date == datetime(2020, 8, 18)) & (tick == 'SQQQ Equity'):
                pnl_dict[tick] = [current_weighted_ave*5, current_position/5, current_pnl, current_type]
                continue
            elif (date == datetime(2021, 1, 11)) & (tick == 'SPXS Equity'):
                pnl_dict[tick] = [current_weighted_ave*10, current_position/10, current_pnl, current_type]
                continue
            elif (date == datetime(2021, 1, 21)) & (tick == 'TQQQ Equity'):
                pnl_dict[tick] = [current_weighted_ave/2, current_position*2, current_pnl, current_type]
                continue
            elif (date == datetime(2021, 3, 2)) & (tick == 'TZA Equity'):
                pnl_dict[tick] = [current_weighted_ave*8, current_position/8, current_pnl, current_type]
                continue
            elif (date == datetime(2022, 1, 13)) & (tick == 'TQQQ Equity'):
                pnl_dict[tick] = [current_weighted_ave/2, current_position*2, current_pnl, current_type]
                continue
            elif (date == datetime(2022, 1, 13)) & (tick == 'SQQQ Equity'):
                pnl_dict[tick] = [current_weighted_ave*5, current_position/5, current_pnl, current_type]
                continue
            
            
            #checking if opening or closing position
            if (((current_position >= 0) and (day_trades.at[index, 'quantity'] > 0)) or 
                ((current_position <= 0) and (day_trades.at[index, 'quantity'] < 0))):
                
                #get new weighted ave
                new_weighted_ave = ((current_weighted_ave*current_position + real_quantity*day_trades.at[index, 'price']) 
                                / new_position)
                pnl_dict[tick] = [new_weighted_ave, new_position, current_pnl, day_trades.at[index, 'type']]
              
               
            else:
                #get new pnl
                new_pnl = (-day_trades.at[index, 'price'] + current_weighted_ave)*(quantity) + current_pnl
                pnl_dict[tick] = [current_weighted_ave, new_position, new_pnl, day_trades.at[index, 'type']]
                
    
        else:
            #adding new ticker into dictionary
            pnl_dict[tick] = [day_trades.at[index, 'price'], real_quantity, 0, day_trades.at[index, 'type']]
    
    #get a dataframe with only trades of that day
    daily_trades = assign_exer_df[assign_exer_df.date == date]
    
    #for debugging (understanding what i am adding each date)
    lis.append(day_trades)
    lis.append(daily_trades)
    
    #loop through all trades of that day
    for index in daily_trades.index:
        #ticker and quantities assign and exer
        tick_assign_exer = daily_trades.at[index, 'ticker']
        space_index = (tick_assign_exer.index(' '))
        equity_name = tick_assign_exer[0: space_index] + ' Equity'
        equity_quantity = daily_trades.at[index, 'quantity']
        option_quantity = equity_quantity/100
        
        if equity_name == 'VIAC Equity':
            equity_name = 'PARA Equity'
        elif equity_name == 'FB Equity':
            equity_name = 'META Equity'
        elif equity_name == 'SQQQ1 Equity':
            equity_name = 'SQQQ Equity'
        
        #checking if ticker is in dictionary
        if tick_assign_exer in pnl_dict.keys():
            #getting current values 
            current_weighted_ave = pnl_dict[tick_assign_exer][0]
            current_position = pnl_dict[tick_assign_exer][1]
            current_pnl = pnl_dict[tick_assign_exer][2]
            current_type = pnl_dict[tick_assign_exer][3]
    
            #getting new position
            if daily_trades.at[index, 'type'] == 'EXER':
                new_pos = -abs(option_quantity) + current_position
            else:
                new_pos = abs(option_quantity) + current_position
            
            pnl_dict[tick_assign_exer] = [current_weighted_ave, new_pos, current_pnl, current_type]
        else:
            pnl_dict[tick_assign_exer] = [0, option_quantity, 0, daily_trades.at[index, 'type']]
        
        #equity
        if equity_name in pnl_dict.keys():
            #getting current values 
            current_weighted_ave = pnl_dict[equity_name][0]
            current_position = pnl_dict[equity_name][1]
            current_pnl = pnl_dict[equity_name][2]
            current_type = pnl_dict[equity_name][3]
            
            #getting new position
            new_pos = equity_quantity+current_position
            
            #checking if opening or closing position
            if (((pnl_dict[equity_name][1] >= 0) and (daily_trades.at[index, 'quantity'] > 0)) or 
                ((pnl_dict[equity_name][1] <= 0) and (daily_trades.at[index, 'quantity'] < 0))):                
                #get new weighted ave
                if daily_trades.at[index, 'type'] == 'EXER':
                    new_weighted_ave = ((current_weighted_ave*current_position + 
                                         ((daily_trades.at[index, 'price'] + pnl_dict[tick_assign_exer][0])*equity_quantity)) 
                                         / new_pos)
                else:
                    new_weighted_ave = ((current_weighted_ave*current_position + 
                                         ((daily_trades.at[index, 'price'] - pnl_dict[tick_assign_exer][0])*equity_quantity)) 
                                         / new_pos)
                #filling dictionary
                pnl_dict[equity_name] = [new_weighted_ave, new_pos, current_pnl, daily_trades.at[index, 'type']]
            else:
                #get new pnl
                if daily_trades.at[index, 'type'] == 'EXER':
                    new_pnl = (-daily_trades.at[index, 'price'] - pnl_dict[tick_assign_exer][0] + current_weighted_ave)*(equity_quantity) + current_pnl
                else:
                    new_pnl = (-daily_trades.at[index, 'price'] + pnl_dict[tick_assign_exer][0] + current_weighted_ave)*(equity_quantity) + current_pnl
                pnl_dict[equity_name] = [current_weighted_ave, new_pos, new_pnl, daily_trades.at[index, 'type']]
            
        else:
            if daily_trades.at[index, 'type'] == 'EXER':
                pnl_dict[equity_name] = [(daily_trades.at[index, 'price'] + pnl_dict[tick_assign_exer][0]), equity_quantity, 0, daily_trades.at[index, 'type']]
            else:
                pnl_dict[equity_name] = [(daily_trades.at[index, 'price'] - pnl_dict[tick_assign_exer][0]), equity_quantity, 0, daily_trades.at[index, 'type']]
    #checking if holding when it expires
    for index in expiring_df.index: 
        tick = expiring_df.at[index, 'ticker']
        if (pnl_dict[tick][1] != 0):
            current_weighted_ave = pnl_dict[tick][0]
            current_position = pnl_dict[tick][1]
            current_pnl = pnl_dict[tick][2]
            current_type = pnl_dict[tick][3]
            pnl_dict[tick] = [current_weighted_ave, 0, current_pnl + current_weighted_ave*current_position*100, current_type]       
            
    #checking if end of month
    if date in d_list:
        #copying dictionary so values are not changed
        pnl_copy = pnl_dict.copy()
        
        #setting up monthly_pnl
        month_pnl = 0
        
        #looping through each ticker
        for ticker in pnl_copy.keys():
            if str(ticker) != 'nan':
                #getting current values
               current_weighted_ave = pnl_copy[ticker][0]
               current_position = pnl_copy[ticker][1]
               current_pnl = pnl_copy[ticker][2]
               current_type = pnl_copy[ticker][3]
               
               #getting ticker for label
               space_ind = (ticker.index(' '))
               label_name = ticker[0: space_ind]
               
               #getting new price at the end of the month
               new_price = bloomberg_df.at[date, ticker]
               
               #getting label data
               if date == datetime(2020, 6, 30):
                   label_date = datetime(2020,7,1)
               else:
                   label_date = date
               if label_name in label_type_df.columns:
                   label = label_type_df.at[label_date, label_name]
               else:
                   label = 'no data'
                   
               #monthly filling pnl
               if str(new_price) == 'nan':
                   if current_pnl == 0:
                       label = 'no position'
                   pnl_copy[ticker] = [0, current_position, (current_pnl), current_type, label]
                   month_pnl += current_pnl
               else:   
                   if (current_type == 'OPTION'):
                       quantity = 100 * current_position  
                   else:
                       quantity = current_position
                   new_pnl = current_pnl + (new_price - current_weighted_ave)*quantity
                   month_pnl += new_pnl
                   if new_pnl == 0:
                       label = 'no position'
                   pnl_copy[ticker] = [current_weighted_ave, current_position, new_pnl, current_type, label]
        #assigning values to monthly dictionary
        monthly_dict[date] = (pnl_copy)
        
        #assigning new values to price and pnl
        for ticker in pnl_copy.keys():
            if str(ticker) != 'nan':
               current_position = pnl_copy[ticker][1]
               current_type = pnl_copy[ticker][3]
               if str(bloomberg_df.at[date, ticker]) == 'nan':
                   #print(ticker, date)
                   pnl_dict[ticker] = [0, current_position, 0, current_type]
               else:   
                   if current_position == 0:
                       pnl_dict[ticker] = [0, 0, 0, current_type]
                   else:
                       pnl_dict[ticker] = [bloomberg_df.at[date, ticker], current_position, 0, current_type]
        test_dict[date] = pnl_dict.copy()

# Convert the dictionary of dictionaries into a DataFrame
df = pd.DataFrame.from_dict(monthly_dict, orient='index')  
for date in df.index:
    month_pnl = 0
    for ticker in df.columns:
        if isinstance(df.at[date, ticker], list) :
            if not pd.isna(df.at[date,ticker][2]):
                month_pnl += df.at[date,ticker][2]
    monthly_pnl_list.append(month_pnl)

df['month_pnl'] = pd.Series(monthly_pnl_list, index = df.index)

final_df = df.transpose()

#final_df.to_excel(excel_writer = r"L:/Lakeview Investment Group/Lindsay/pnl_older_version_test_fixed.xlsx")

day_list = []
for day in monthly_dict:
    day_list.append(day)
day_list = pd.Series(day_list)
final_showing_df = final_showing_df.reindex(day_list)

#doing for long_short columns
for column in final_df.columns:
    long_pnl = 0
    short_pnl = 0
    long_letf_pnl = 0
    short_letf_pnl = 0
    vix_pnl = 0
    for ticker in final_df.index:
        value = final_df.at[ticker, column]
        if type(value) != float:
            if str(value[2]) != 'nan':
                if value[4] == 'long':
                    long_pnl += float(value[2])
                elif value[4] == 'short':
                    short_pnl += float(value[2])
                elif value[4] == 'long LETF':
                    long_letf_pnl += float(value[2])
                elif value[4] == 'short LETF':
                    short_letf_pnl += float(value[2])
                elif value[4] == 'VIX':
                    vix_pnl += float(value[2])
                    
    final_showing_df.at[column, 'long'] = long_pnl
    final_showing_df.at[column, 'short'] = short_pnl     
    final_showing_df.at[column, 'long LETF'] = long_letf_pnl
    final_showing_df.at[column, 'short LETF'] = short_letf_pnl   
    final_showing_df.at[column, 'VIX'] = vix_pnl    

final_showing_df['total_pnl'] = final_showing_df.long + final_showing_df.short + final_showing_df['long LETF'] + final_showing_df['short LETF'] + final_showing_df.VIX
    
for column in df.columns:
    for row in df.index:
        if isinstance(df.at[row, column], list):
            #print(type(df.at[row, column]))
            df.at[row, column] = df.at[row, column][2]
    
df.to_excel(r'L:/Lakeview Investment Group/Lindsay/month_pnl_by_ticker_5.xlsx')    
final_showing_df.to_excel(r'L:/Lakeview Investment Group/Lindsay/fully_fixed_bloomberg15.xlsx')


