import pandas as pd
import os, argparse, sys
import numpy as np
from zipfile import ZipFile

def unzip_and_analyze(filename):
    basepath = os.getcwd()
    temp_path = os.path.join(basepath, 'temp')
    temp_out_path = os.path.join(basepath, 'temp_out')
    incenive_scheme_path = os.path.join(basepath, 'incentive_scheme')
    shovel_codes_file = os.path.join(incenive_scheme_path, 'shovels.csv')
    dumper_codes_file = os.path.join(incenive_scheme_path, 'dumpers.csv')
    combination_codes_file = os.path.join(incenive_scheme_path, 'shovel-dumper-combination.csv')
    code_trip_rate_file = os.path.join(incenive_scheme_path, 'code_trip_rate.csv')

    if(filename):
        with ZipFile(filename, 'r') as zip_reference:
            zip_reference.extractall(temp_path)
    else:
        return

    #get excel file list
    files = os.listdir(temp_path)
    excel_files = [os.path.join(temp_path, x) for x in files if x.endswith('.xlsx')]
    
    # combine files and output to temp_out_path dir
    combined_df = pd.concat([pd.read_excel(x) for x in excel_files], ignore_index=True)
    combined_df.to_excel(os.path.join(temp_out_path, 'total_production.xlsx'), index=False)
    combined_df.to_csv(os.path.join(temp_out_path, 'total_production.csv'), index=False, sep=',')

    #Prepare dataframe for incentive
    inc = pd.pivot_table(combined_df, values=['Dumper_Number_of_Trips'], index=['Production_Dates', 'shift', 'Operator.1' , 'Shovel_number', 'Dumper_Number'], aggfunc=np.sum).fillna(0)
    inc.index.names = ['Production_Date', 'Shift', 'Operator_No', 'Shovel_Number', 'Dumper_Number']
    inc.columns = ['Dumper_Trips']

    #read incentive scheme
    shovel_codes = pd.read_csv(shovel_codes_file)
    dumper_codes = pd.read_csv(dumper_codes_file)
    combination_codes = pd.read_csv(combination_codes_file)
    code_trip_rates = pd.read_csv(code_trip_rate_file)

    # print(dumper_codes.loc[dumper_codes['DUMPER'] == 'CN-03', 'CODE'].iloc[0])
    #further modify incentive dataframe
    def add_shovel_dumper_code(row):
        shovel_code = shovel_codes.loc[shovel_codes['SHOVEL'] == row.name[3], 'CODE']
        dumper_code = dumper_codes.loc[dumper_codes['DUMPER'] == row.name[4], 'CODE']
        s=''
        d=''
        if (len(shovel_code) > 0):
            s = shovel_code.iloc[0]
        if (len(dumper_code) > 0):
            d = dumper_code.iloc[0]
        return s+d+'L10'

    def add_code_n_trip(row):
        code_n_trip = str(row['Combination_Code']) + str(row['Dumper_Trips']).zfill(2)
        return code_n_trip

    def add_combination_code(row):
        code = combination_codes.loc[combination_codes['COMBINATION'] == row['Shovel_Dumper_Lead'], 'CODE']
        c = ''
        if (len(code) > 0):
            c = code.iloc[0]
        return c

    def add_shovel_dumper_code(row):
        shovel_code = shovel_codes.loc[shovel_codes['SHOVEL'] == row.name[3], 'CODE']
        dumper_code = dumper_codes.loc[dumper_codes['DUMPER'] == row.name[4], 'CODE']
        s=''
        d=''
        if (len(shovel_code) > 0):
            s = shovel_code.iloc[0]
        if (len(dumper_code) > 0):
            d = dumper_code.iloc[0]
        return s+d+'L10'

    def add_incentive_earning(row):
        incenive_earning = code_trip_rates.loc[code_trip_rates['CODE_TRIP'] == int(row['Code_N_Trip']), 'EARNING']
        i = ''
        if (len(incenive_earning) > 0):
            i = incenive_earning.iloc[0]
        return i

    inc['Shovel_Dumper_Lead'] = inc.apply(lambda row: add_shovel_dumper_code(row), axis=1)
    inc['Combination_Code'] = inc.apply(lambda row: add_combination_code(row), axis=1)
    inc['Code_N_Trip'] = inc.apply(lambda row: add_code_n_trip(row), axis=1)
    inc['Incentive_Earning'] = inc.apply(lambda row: add_incentive_earning(row), axis=1)

    inc.to_excel(os.path.join(temp_out_path, 'inc2.xlsx'))

    #Traverse Row wise
    # for row in inc.itertuples():
    #     print(row)

if __name__ == '__main__':
    argvparser = argparse.ArgumentParser()
    argvparser.add_argument('-i', '--input', help='Zip file name')
    args = argvparser.parse_args()
    unzip_and_analyze(args.input)
    
