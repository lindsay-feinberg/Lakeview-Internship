# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 09:17:42 2023

@author: lfeinberg
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook

def check_sign_change(df):
    list = []
    for column in df.columns:
        previous_value = None
        sign_change_count = False
        for value in df[column]:
            if previous_value is not None:
                if (previous_value < 0 and value > 0) or (previous_value > 0 and value < 0):
                    sign_change_count = True
            previous_value = value

        if sign_change_count:
            list.append(column)
    return list



def ticker_delta_exposure (file):
    df = pd.read_excel(io =file, sheet_name = 1, skiprows = 4)
    df['ticker'] = df['Ticker'].str.split(expand = True)[0]
    #datacleaning and separating options and equities
    option_df = df[df.Multiplier == 100].reset_index()
    equity_df = df[df.Multiplier == 1].reset_index()
    #only keeping delta exposure and names 
    option_deltas_df = option_df[['ticker', 'Delta Exposure']]
    equity_deltas_df = equity_df[['ticker', 'Delta Exposure']]

    #creating dictionary
    delta_dictionary = {}

    #combining like names for options
    for index in option_deltas_df.index:
        if option_deltas_df.at[index, 'ticker'] in delta_dictionary.keys():
            delta_dictionary[option_deltas_df.at[index, 'ticker']] = delta_dictionary[option_deltas_df.at[index, 'ticker']] + option_deltas_df.at[index, 'Delta Exposure']
        else:
            delta_dictionary[option_deltas_df.at[index, 'ticker']] = option_deltas_df.at[index, 'Delta Exposure']

    #combining like names for equities(adding to options)
    for index in equity_deltas_df.index:
        if equity_deltas_df.at[index, 'ticker'] in delta_dictionary.keys():
            delta_dictionary[equity_deltas_df.at[index, 'ticker']] = delta_dictionary[equity_deltas_df.at[index, 'ticker']] + equity_deltas_df.at[index, 'Delta Exposure']
        else:
            delta_dictionary[equity_deltas_df.at[index, 'ticker']] = equity_deltas_df.at[index, 'Delta Exposure']

    return_df = (pd.DataFrame.from_dict(delta_dictionary, orient = 'index')
                 .rename(columns = {0 : 'delta_exposure'}))
    return_df = return_df.sort_index()
    return return_df

#reading in 8.1.18 file
beginning_august_2018 = ticker_delta_exposure(r'L:/Lakeview Investment Group/Lindsay/vix tracker paste values 8.1.18.xlsx')    
beginning_august_2018['date_column'] = '8.1.18'
concat_df = beginning_august_2018

file_list = ([r'L:/Lakeview Investment Group/Lindsay/vix tracker paste values 8.20.18.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker paste values 8.31.18.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker paste values 9.17.18.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker paste values 9.28.18.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker paste values 10.16.18.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 10.31.18 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 11.20.18 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 11.30.18 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 12.17.18 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 12.31.18 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/1.14.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/1.31.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/2.11.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/2.28.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/3.18.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/3.29.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/4.15.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/4.30.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/5.20.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/5.31.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/6.17.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/6.28.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/7.15.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/7.31.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/8.19.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/8.30.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/9.16.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/9.30.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/10.14.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/10.31.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/11.18.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/11.29.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/12.16.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/12.31.19 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 1.21.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 1.31.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 2.18.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 2.28.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 3.16.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 3.31.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 4.13.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 4.30.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 5.18.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 5.29.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 6.15.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 7.1.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 7.20.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 7.31.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 8.17.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 8.31.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 9.14.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 9.30.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 10.19.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 10.30.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 11.16.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 11.30.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 12.14.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 12.31.20 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 1.19.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 1.29.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 2.16.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 2.26.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 3.15.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 3.31.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 4.19.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 4.30.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 5.17.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 5.28.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 6.14.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 6.30.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 7.19.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 7.30.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 8.16.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 8.31.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 9.13.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 9.30.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 10.18.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 10.29.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 11.15.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 11.30.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 12.20.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 12.31.21 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 1.18.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 1.31.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 2.14.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 2.28.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 3.14.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 3.31.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 4.18.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 4.29.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 5.16.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 5.31.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 6.13.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 6.30.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 7.18.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 7.29.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 8.15.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 8.31.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 9.19.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 9.30.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 10.17.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 10.31.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 11.14.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 11.30.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 12.19.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 12.30.22 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 1.17.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 1.31.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 2.13.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 2.28.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 3.20.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 3.31.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 4.17.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 4.28.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 5.15.23 paste values.xlsx',
              r'L:/Lakeview Investment Group/Lindsay/vix tracker 5.31.23 paste values.xlsx'
              ])
date_list = (['8.20.18', '8.31.18', '9.17.18', '9.28.18', '10.16.18', '10.31.18',
              '11.19.18', '11.30.18', '12.17.18', '12.31.18', '1.14.19', '1.31.19', 
              '2.11.19', '2.28.19', '3.18.19', '3.29.19', '4.15.19', '4.30.19',
              '5.20.19', '5.31.19', '6.17.19', '6.28.19', '7.15.19', '7.31.19',
              '8.19.19', '8.30.19', '9.16.19', '9.30.19', '10.14.19', '10.31.19',
              '11.18.19', '11.29.19', '12.16.19', '12.31.19', '1.21.20', '1.31.20',
              '2.18.20', '2.28.20', '3.16.20', '3.31.20', '4.13.20', '4.30.20', 
              '5.18.20', '5.29.20', '6.15.20', '7.1.20', '7.20.20', '7.31.20',
              '8.17.20', '8.31.20', '9.14.20', '9.30.20', '10.19.20', '10.30.20', 
              '11.16.20', '11.30.20', '12.14.20', '12.31.20', '1.19.21', '1.29.21',
              '2.16.21', '2.26.21', '3.15.21', '3.31.21', '4.19.21', '4.30.21', 
              '5.17.21', '5.28.21', '6.14.21', '6.30.21', '7.19.21', '7.30.21',
              '8.16.21', '8.31.21', '9.13.21', '9.30.21', '10.18.21', '10.29.21',
              '11.15.21', '11.30.21', '12.20.21', '12.31.21', '1.18.22', '1.31.22',
              '2.14.22', '2.28.22', '3.14.22', '3.31.22', '4.18.22', '4.29.22',
              '5.16.22', '5.31.22', '6.13.22', '6.30.22', '7.18.22', '7.29.22',
              '8.15.22', '8.31.22', '9.19.22', '9.30.22', '10.17.22', '10.31.22',
              '11.14.22', '11.30.22', '12.19.22', '12.30.22', '1.17.23', '1.31.23',
              '2.13.23', '2.28.23', '3.20.23', '3.31.23', '4.17.23', '4.28.23', 
              '5.15.23', '5.31.23'
              ])
print(len(file_list))
print(len(date_list))
for (file, date) in zip(file_list, date_list):
    individual_df = ticker_delta_exposure(file)
    individual_df['date_column'] = date
    concat_df = pd.concat([concat_df, individual_df])

concat_df['date_column'] = pd.to_datetime(concat_df.date_column, format = 'mixed')
concat_df['index_column'] = concat_df.index
concat_df = concat_df.sort_values(by = 'date_column')
print(concat_df.index_column)

pivot_df = concat_df.pivot(index = 'date_column', columns = 'index_column', values = 'delta_exposure')
change = check_sign_change(pivot_df)

# Get the unique years from the DateTimeIndex
# Get the unique years from the DateTimeIndex
'''years = pivot_df.index.year.unique()

# Create an Excel workbook
workbook = Workbook()

# Iterate over each year
for year in years:
    # Filter the DataFrame for the current year
    filtered_df = pivot_df[pivot_df.index.year == year]
    
    # Create a new sheet with the year as the sheet name
    sheet = workbook.create_sheet(title=str(year))
    
    filtered_df.index = filtered_df.index.strftime('%Y-%m-%d')
    # Write the column names to the sheet
    sheet.append([filtered_df.index.name] + filtered_df.columns.tolist())
    
    # Write the index and data rows to the sheet
    for index, row in filtered_df.iterrows():
        sheet.append([index] + row.tolist())

# Remove the default sheet created by openpyxl
workbook.remove(workbook['Sheet'])

# Save the Excel file
workbook.save('L:/Lakeview Investment Group/Lindsay/firm_exposure.xlsx')'''
'''years = pivot_df.index.year.unique()

# Create a Pandas Excel writer object
writer = pd.ExcelWriter('L:/Lakeview Investment Group/Lindsay/firm_exposure.xlsx')

# Iterate over each year
for year in years:
    # Filter the DataFrame for the current year
    filtered_df = pivot_df[pivot_df.index.year == year]
    
    # Write the filtered data to a new sheet with the year as the sheet name
    filtered_df.to_excel(writer, sheet_name=str(year))

'''