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
from datetime import datetime

trade_file = r'L:/Lakeview Investment Group/Lindsay/abn_trades_lindsay.xlsx'
bloomberg_file = r'L:/Lakeview Investment Group/Lindsay/bloomberg_data_onesheet.xlsx'

trade_df = pd.read_excel(trade_file)
bloomberg_df = pd.read_excel(bloomberg_file)
bloomberg_df = bloomberg_df.set_index(bloomberg_df.DATES)
stock_option_df = trade_df[(trade_df.type == 'STOCK') | (trade_df.type == 'OPTION')]
assign_exer_df = trade_df[(trade_df.type == 'ASSIGN') | (trade_df.type == 'EXER')]


#start and end dates
start_year = 2019
start_month = 9  # September
end_year = 2022
end_month = 8    # August
pnl_dict = {}
#loop over months
for year in range(start_year, end_year + 1):
    # Set the range of months based on the current year
    if year == start_year:
        start_month_iter = start_month
    else:
        start_month_iter = 1

    if year == end_year:
        end_month_iter = end_month + 1
    else:
        end_month_iter = 13

    # Iterate over the months
    for month in range(start_month_iter, end_month_iter):
        
        # Get the last day of the current month
        _, last_day_num = calendar.monthrange(year, month)
        last_day = datetime(year, month, last_day_num)
        first_day = datetime(year, month, 1)
        business_days = pd.date_range(start=first_day, end=last_day, freq='B')
        for day in business_days:
            day_trades = stock_option_df[stock_option_df.date == day]
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
                        new_pnl = (day_trades.at[index, 'price'] - current_weighted_ave)*(abs(quantity))
                        pnl_dict[tick] = [current_weighted_ave, new_position, new_pnl]
                else:
                    pnl_dict[tick] = [day_trades.at[index, 'price'], quantity, 0]
            if day == business_days[len(business_days)-1]:
                if day == datetime(2021, 5, 31):
                    day = datetime(2021, 5, 28)
                for ticker in pnl_dict.keys():
                    if str(ticker) != 'nan':
                       current_weighted_ave = pnl_dict[ticker][0]
                       current_position = pnl_dict[ticker][1]
                       current_pnl = pnl_dict[ticker][2]
                       new_price = bloomberg_df.at[day, ticker]
                       if str(new_price) == 'nan':
                           pnl_dict[ticker] = [current_weighted_ave, current_position, (current_pnl)]
                       else:   
                           new_pnl = current_pnl + bloomberg_df.at[day, ticker] - current_weighted_ave
                           pnl_dict[ticker] = [new_price, current_position, new_pnl]
                      
            