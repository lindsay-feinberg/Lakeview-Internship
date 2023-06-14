# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 09:24:22 2023

@author: lfeinberg
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook

def read_in_files(beginning_month, end_month):
    beginning_df = pd.read_csv(beginning_month)
    end_df = pd.read_csv(end_month)
    pnl_dictionary = {}
    for (ticker, pnl) in zip(end_df.ticker, end_df.pnl):
        pnl_dictionary[ticker] = pnl
    for (ticker, pnl) in zip(beginning_df.ticker, beginning_df.pnl):
        if ticker in pnl_dictionary.keys():
            pnl_dictionary[ticker] = pnl_dictionary[ticker] - pnl
        else:
            pnl_dictionary[ticker] = pnl
           
    return_df = (pd.DataFrame.from_dict(pnl_dictionary, orient = 'index')
                 .rename(columns = {0 : 'pnl'}))
    return_df['date'] = beginning_month[-12:-6]
    return return_df

file_list = ([r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20220802.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20220830.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20220902.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20220930.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20221003.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20221031.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20221101.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20221130.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20221201.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20221230.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230103.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230130.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230201.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230228.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230301.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230331.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230403.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230428.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230501.csv",
r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/pnl_20230531.csv"])

concat_df = pd.DataFrame()
iterator = iter(file_list)
for file in iterator:
    individual_df = read_in_files(file, next(iterator))
    concat_df = pd.concat([concat_df, individual_df])

concat_df['date'] = pd.to_datetime(concat_df.date, format ='%Y%m')
concat_df['ticker'] = concat_df.index
pivot_df = concat_df.pivot(index = 'date', columns = 'ticker', values = 'pnl')
pivot_df.index = pivot_df.index.strftime('%Y-%m')

pivot_df.to_excel(excel_writer = r"L:/Lakeview Investment Group/Lindsay/pnl_ytd/together_total_pnl.xlsx")