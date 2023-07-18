# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 14:27:41 2023

@author: lfeinberg
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook

df = pd.read_excel(r'L:/Lakeview Investment Group/Lindsay/august 2022 checking.xlsx')
checking_dict = {}
df = df.fillna(0)
for ind in df.index:
    ticker = df.at[ind, 'ticker']
    space_index = (ticker.index(' '))
    equity_name = ticker[0: space_index]
    if equity_name in checking_dict.keys():
        if not df.at[ind, 'pnl'] == 0:
            checking_dict[equity_name] = checking_dict[equity_name] + df.at[ind, 'pnl']
        
    else:
        if not df.at[ind, 'pnl'] == 0:
            checking_dict[equity_name] = df.at[ind, 'pnl']

final_df = pd.DataFrame.from_dict(checking_dict, orient='index')         

final_df.to_excel(r'L:/Lakeview Investment Group/Lindsay/august 2021 checking condensed2.xlsx')
