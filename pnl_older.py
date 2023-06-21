# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 08:58:17 2023

@author: lfeinberg
"""
import pandas as pd
import numpy as np
import math
import calendar
from openpyxl import Workbook
import datetime
from datetime import datetime
from pandas.tseries.offsets import BMonthEnd

def last_business_days(start_date, end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    dates = pd.date_range(start=start_date, end=end_date, freq='BM')
    last_business_days = dates + BMonthEnd()

    return last_business_days.tolist()


trade_file = r'L:/Lakeview Investment Group/Lindsay/abn_trades_lindsay.xlsx'
bloomberg_file = r'L:/Lakeview Investment Group/Lindsay/bloomberg_data_onesheet.xlsx'

trade_df = pd.read_excel(trade_file)
bloomberg_df = pd.read_excel(bloomberg_file)
bloomberg_df = bloomberg_df.set_index(bloomberg_df.DATES)
stock_option_df = trade_df[(trade_df.type == 'STOCK') | (trade_df.type == 'OPTION')]
assign_exer_df = trade_df[(trade_df.type == 'ASSIGN') | (trade_df.type == 'EXER')]

pnl_dict = {}
unique_trade_dates = pd.unique(stock_option_df.date)
extra_dates = [datetime(2019, 10, 31), datetime(2019, 11, 29), 
                                datetime(2019, 12, 31), datetime(2020, 1, 31),
                                datetime(2020, 4, 30), datetime(2020, 5, 29), 
                                datetime(2020, 7,31), datetime(2020, 10, 30)]
extra_dates = pd.Series(extra_dates)
unique_trade_dates = pd.Series(unique_trade_dates)
unique_trade_dates = pd.concat([extra_dates, unique_trade_dates])
unique_trade_dates = unique_trade_dates.sort_values()

s_date = datetime(2019, 9, 1)
e_date = datetime(2022, 8, 31)

d_list = last_business_days(s_date, e_date)
d_list.append(datetime(2021, 5, 28))
monthly_dict = {}

for date in unique_trade_dates:
    day_trades = stock_option_df[stock_option_df.date == date]
    for index in day_trades.index:
        tick = day_trades.at[index, 'ticker']
        if day_trades.at[index, 'type'] == 'OPTION':
            quantity = 100* day_trades.at[index, 'quantity']
        else:
            quantity = day_trades.at[index, 'quantity']
        if tick in pnl_dict.keys():
            current_weighted_ave = pnl_dict[tick][0]
            current_position = pnl_dict[tick][1]
            current_pnl = pnl_dict[tick][2]
            new_position = current_position + quantity
            
            if (((pnl_dict[tick][1] >= 0) and (day_trades.at[index, 'quantity'] > 0)) or 
                ((pnl_dict[tick][1] <= 0) and (day_trades.at[index, 'quantity'] < 0))):
                new_weighted_ave = ((current_weighted_ave*current_position + quantity*day_trades.at[index, 'price']) 
                                    / new_position)
                
                pnl_dict[tick] = [new_weighted_ave, new_position, current_pnl]
                
            else:
                new_pnl = (-day_trades.at[index, 'price'] + current_weighted_ave)*(quantity)
                pnl_dict[tick] = [current_weighted_ave, new_position, new_pnl]
        else:
            pnl_dict[tick] = [day_trades.at[index, 'price'], quantity, 0]
  
    if date in d_list:
        pnl_copy = pnl_dict.copy()
        for ticker in pnl_dict.keys():
            if str(ticker) != 'nan':
               current_weighted_ave = pnl_copy[ticker][0]
               current_position = pnl_copy[ticker][1]
               current_pnl = pnl_copy[ticker][2]
               new_price = bloomberg_df.at[date, ticker]
               if str(new_price) == 'nan':
                   pnl_copy[ticker] = [current_weighted_ave, current_position, (current_pnl)]
               else:   
                   new_pnl = current_pnl + bloomberg_df.at[date, ticker] - current_weighted_ave
                   pnl_copy[ticker] = [current_weighted_ave, current_position, new_pnl]
        monthly_dict[date] = pnl_copy
        

        for ticker in pnl_dict.keys():
            if str(ticker) != 'nan':
               current_position = pnl_copy[ticker][1]
               new_price = bloomberg_df.at[date, ticker]
               if str(new_price) == 'nan':
                   pnl_dict[ticker] = [current_weighted_ave, current_position, 0]
               else:   
                   pnl_dict[ticker] = [new_price, current_position, 0]
         
   
