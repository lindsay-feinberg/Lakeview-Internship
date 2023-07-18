import pandas as pd
import numpy as np
from openpyxl import Workbook


def read_in_files(file):
    pnl_dictionary = {}
    file_reader = pd.read_csv(file)
    for (string_input, pnl) in zip (file_reader.Symbol, file_reader['Mark-to-Market P/L Total']):
        # Convert each string to a series of characters
        string_series = pd.Series(list(string_input))
        
        # Find the index of the first occurrence of a number
        first_number_index = string_series.loc[string_series.str.isnumeric()].index.min()
        if pd.isna(first_number_index):
            if string_input in pnl_dictionary.keys():
                pnl_dictionary[string_input] = pnl_dictionary[string_input] + pnl
            else:
                pnl_dictionary[string_input] = pnl

        elif (len(string_input) < 6):
            if string_input in pnl_dictionary.keys():
                pnl_dictionary[string_input] = pnl_dictionary[string_input] + pnl
            else:
                pnl_dictionary[string_input] = pnl
        else:
            # Extract the substring before the first number
            substring = string_input[:first_number_index]
            if substring in pnl_dictionary.keys():
                pnl_dictionary[substring] = pnl_dictionary[substring] + pnl
            else:
                pnl_dictionary[substring] = pnl
    
    return_df = (pd.DataFrame.from_dict(pnl_dictionary, orient = 'index')
                 .rename(columns = {0 : 'adjusted_pnl'}))
    return_df['date'] =  file[-19:-13]    
    return return_df


file_list = ([r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201808_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201809_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201810_v1_ibpnl.csv', 
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201811_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201812_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201901_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201902_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201903_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201904_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201905_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201906_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201907_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201908_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201909_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201910_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201911_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/201912_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202001_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202002_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202003_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202004_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202005_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202006_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202007_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202008_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202009_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202010_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202011_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202012_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202101_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202102_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202103_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202104_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202105_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202106_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202107_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202108_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202109_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202110_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202111_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202112_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202201_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202202_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202203_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202204_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202205_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202206_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202207_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202208_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202209_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202210_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202211_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202212_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202301_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202302_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202303_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202304_v1_ibpnl.csv',
              r'L:/Lakeview Investment Group/Lindsay/ib_pnl/202305_v1_ibpnl.csv'])

concat_df = pd.DataFrame()
label_type_file = r'L:/Lakeview Investment Group/Lindsay/long_short_mixed_fixed.xlsx'
label_type_df = pd.read_excel(label_type_file)
label_type_df.index = label_type_df.date_column
label_type_df = label_type_df.drop(labels = 'date_column', axis =1)

label_type_df.index = label_type_df.index.strftime('%Y-%m-%d')
for file in file_list:
    individual_df = read_in_files(file)
    concat_df = pd.concat([concat_df, individual_df])
    
concat_df['date'] = pd.to_datetime(concat_df.date, format = '%Y%m')
concat_df['index_column'] = concat_df.index
pivot_df = concat_df.pivot(index = 'date', columns = 'index_column', values = 'adjusted_pnl')
pivot_df.index = pivot_df.index.strftime('%Y-%m')
#pivot_df.to_excel(excel_writer = r'L:/Lakeview Investment Group/Lindsay/ib_pnl_firm_good2.xlsx')

date_list = ['2018-08-31', '2018-09-28', '2018-10-31', '2018-11-30', '2018-12-31',
             '2019-01-31', '2019-02-28', '2019-03-29', '2019-04-30', '2019-05-31',
             '2019-06-28', '2019-07-31','2019-08-30', '2019-09-30', '2019-10-31', 
             '2019-11-29', '2019-12-31','2020-01-31', '2020-02-28', '2020-03-31',
             '2020-04-30', '2020-05-29','2020-06-15', '2020-07-31','2020-08-31', 
             '2020-09-30', '2020-10-30','2020-11-30', '2020-12-31','2021-01-29', 
             '2021-02-26', '2021-03-31','2021-04-30', '2021-05-28','2021-06-30',
             '2021-07-30','2021-08-31','2021-09-30', '2021-10-29','2021-11-30', 
             '2021-12-31','2022-01-31','2022-02-28', '2022-03-31','2022-04-29', 
             '2022-05-31','2022-06-30', '2022-07-29','2022-08-31']

transposed_df = pivot_df.T
copy_df = transposed_df.copy()
for row in transposed_df.index:
    label_name = row
    for date in date_list:
        label_date = date
        if label_name in label_type_df.columns:
            label = label_type_df.at[label_date, label_name]
        else:
            label = 'no data'
        copy_df.at[row, date] = label 
copy_df.to_excel(excel_writer = r'L:/Lakeview Investment Group/Lindsay/labeled_pnl_older_ib2.xlsx')
