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

#making it more readable, and differentiate the files
trade_file = r'L:/Lakeview Investment Group/Lindsay/abn_trades_lindsay.xlsx'
bloomberg_file = r'L:/Lakeview Investment Group/Lindsay/bloomberg_data_onesheet.xlsx'

#reading in files
trade_df = pd.read_excel(trade_file)
bloomberg_df = pd.read_excel(bloomberg_file)

#setting index to date for bloomberg so it is accessible
bloomberg_df = bloomberg_df.set_index(bloomberg_df.DATES)

#filtering the trade_df by the type
stock_option_df = filtering_df(trade_df, 'OPTION', 'STOCK')
assign_exer_df = filtering_df(trade_df, 'ASSIGN', 'EXER')

#creating pnl dictionary
pnl_dict = {}

#creating an unique list of trade dates
unique_trade_dates = pd.unique(stock_option_df.date)

#adding the last business day of each month if that particular month did not
#have a trade that day
extra_dates = [datetime(2019, 10, 31), datetime(2019, 11, 29), 
                                datetime(2019, 12, 31), datetime(2020, 1, 31),
                                datetime(2020, 4, 30), datetime(2020, 5, 29), 
                                datetime(2020, 7,31), datetime(2020, 10, 30)]

#combining and sorting full list of unique dates
extra_dates = pd.Series(extra_dates)
unique_trade_dates = pd.Series(unique_trade_dates)
unique_trade_dates = pd.concat([extra_dates, unique_trade_dates])
unique_trade_dates = unique_trade_dates.sort_values()

#set beginning and end of time period
s_date = datetime(2019, 9, 1)
e_date = datetime(2022, 8, 31)

#getting the list of last business day per month and add in 5/28 (before MDW)
d_list = last_business_days(s_date, e_date)
d_list.append(datetime(2021, 5, 28))

#set up monthly dictionary
monthly_dict = {}

#loop through each trade date
for date in unique_trade_dates:  
    #get a dataframe with only trades of that day
    day_trades = stock_option_df[stock_option_df.date == date]
    
    #loop through all trades of that day
    for index in day_trades.index:
        tick = day_trades.at[index, 'ticker']
        real_quantity = day_trades.at[index, 'quantity']
        #get correct value for quantity
        if day_trades.at[index, 'type'] == 'OPTION':
            quantity = 100 * day_trades.at[index, 'quantity']
        else:
            quantity = day_trades.at[index, 'quantity']
        
        #checking if ticker is in dictionary
        if tick in pnl_dict.keys():
            
            #getting current values 
            current_weighted_ave = pnl_dict[tick][0]
            current_position = pnl_dict[tick][1]
            current_pnl = pnl_dict[tick][2]
            
            #getting new position after trade
            new_position = current_position + real_quantity
            
            #checking if opening or closing position
            if (((pnl_dict[tick][1] >= 0) and (day_trades.at[index, 'quantity'] > 0)) or 
                ((pnl_dict[tick][1] <= 0) and (day_trades.at[index, 'quantity'] < 0))):
                
                #get new weighted ave
                new_weighted_ave = ((current_weighted_ave*current_position + real_quantity*day_trades.at[index, 'price']) 
                                / new_position)
                pnl_dict[tick] = [new_weighted_ave, new_position, current_pnl]
            
            else:
                #get new pnl
                new_pnl = (-day_trades.at[index, 'price'] + current_weighted_ave)*(quantity)
                pnl_dict[tick] = [current_weighted_ave, new_position, new_pnl]
        else:
            #adding new ticker into dictionary
            pnl_dict[tick] = [day_trades.at[index, 'price'], real_quantity, 0]
    #get a dataframe with only trades of that day
    daily_trades = assign_exer_df[assign_exer_df.date == date]
    
    #loop through all trades of that day
    for index in daily_trades.index:
        #ticker and quantities assign and exer
        tick_assign_exer = daily_trades.at[index, 'ticker']
        space_index = (tick_assign_exer.index(' '))
        equity_name = tick_assign_exer[0: space_index] + ' Equity'
        equity_quantity = daily_trades.at[index, 'quantity']
        option_quantity = equity_quantity/100
        
        #checking if ticker is in dictionary
        if tick_assign_exer in pnl_dict.keys():
            
            #getting current values 
            current_weighted_ave = pnl_dict[tick_assign_exer][0]
            current_position = pnl_dict[tick_assign_exer][1]
            current_pnl = pnl_dict[tick_assign_exer][2]
            
            #getting new position
            new_pos = option_quantity + current_position
            
            #new pnl
            new_pnl_ae = current_pnl + option_quantity*daily_trades.at[index, 'price']
            pnl_dict[tick_assign_exer] = [current_weighted_ave, new_pos, new_pnl_ae]
        else:
            pnl_dict[tick_assign_exer] = [0, option_quantity, option_quantity*daily_trades.at[index, 'price']]
        
        #equity
        if equity_name in pnl_dict.keys():
            #getting current values 
            current_weighted_ave = pnl_dict[tick_assign_exer][0]
            current_position = pnl_dict[tick_assign_exer][1]
            current_pnl = pnl_dict[tick_assign_exer][2]
            
            #getting new position
            new_pos = equity_quantity + current_position
            
            #new pnl
            new_pnl_ae = current_pnl + equity_quantity*daily_trades.at[index, 'price']
            pnl_dict[equity_name] = [current_weighted_ave, new_pos, new_pnl_ae]
        else:
            pnl_dict[equity_name] = [0, equity_quantity, equity_quantity*daily_trades.at[index, 'price']]
    #checking if end of month
    if date in d_list:
        print(date)
        #copying dictionary so values are not changed
        pnl_copy = pnl_dict.copy()
        
        #looping through each ticker
        for ticker in pnl_copy.keys():
            if str(ticker) != 'nan':
                #getting current values
               current_weighted_ave = pnl_copy[ticker][0]
               current_position = pnl_copy[ticker][1]
               current_pnl = pnl_copy[ticker][2]
               
               #getting new price at the end of the month
               new_price = bloomberg_df.at[date, ticker]
               if str(new_price) == 'nan':
                   pnl_copy[ticker] = [current_weighted_ave, current_position, (current_pnl)]
               else:   
                   new_pnl = current_pnl + bloomberg_df.at[date, ticker] - current_weighted_ave
                   pnl_copy[ticker] = [current_weighted_ave, current_position, new_pnl]
        
        #assigning values to monthly dictionary
        monthly_dict[date] = pnl_copy
        
        #assigning new values to price and pnl
        for ticker in pnl_dict.keys():
            if str(ticker) != 'nan':
               current_position = pnl_copy[ticker][1]
               new_price = bloomberg_df.at[date, ticker]
               if str(new_price) == 'nan':
                   pnl_dict[ticker] = [current_weighted_ave, current_position, 0]
               else:   
                   pnl_dict[ticker] = [new_price, current_position, 0]

    
    

