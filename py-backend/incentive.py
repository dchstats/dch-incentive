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
    inc = pd.pivot_table(combined_df, values=['Dumper_Number_of_Trips'], index=['Operator.1', 'Production_Dates', 'shift', 'Shovel_number', 'Dumper_Number'], aggfunc=np.sum).fillna(0)
    inc.index.names = ['Operator_No', 'Production_Date', 'Shift', 'Shovel_Number', 'Dumper_Number']
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

    def add_combination_code(row):
        code = combination_codes.loc[combination_codes['COMBINATION'] == row['Shovel_Dumper_Lead'], 'CODE']
        c = ''
        if (len(code) > 0):
            c = code.iloc[0]
        return c
                
    def add_incentive(row):
        trips = code_trip_rates.loc[code_trip_rates['CODE'] == row['Eq_Comb_Code'], 'TRIP']
        rates = code_trip_rates.loc[code_trip_rates['CODE'] == row['Eq_Comb_Code'], 'RATE']
        earning = code_trip_rates.loc[code_trip_rates['CODE'] == row['Eq_Comb_Code'], 'EARNING']
        trips = trips.tolist()
        rates = rates.tolist()
        earning = earning.tolist()
        eq_trip = np.rint(row['Equivalent_Trips'])
        incentive = 0
        if eq_trip and len(trips)>0:
            trip_difference_array = eq_trip - trips
            nearest_trip_index = len(list(filter(lambda x:x>-1,trip_difference_array)))-1
            if(nearest_trip_index > -1):
                incentive = earning[nearest_trip_index] + rates[nearest_trip_index]*trip_difference_array[nearest_trip_index]
        return np.rint(incentive)
        
    def add_equivalent_trips(row):
        operator_no_index = row.name[0:3]
        same_operator_combs = inc.loc[operator_no_index]
        all_weights = []
        equivalent_case_standard_trip = 0
        equivalent_case_comb_code = 0
        max_trips = 0
        for i in same_operator_combs.index:
            dumper_trips = same_operator_combs['Dumper_Trips'][i]
            # print(dumper_trips)
            standard_trip = same_operator_combs['Standard_Trips'][i]
            comb_code = same_operator_combs['Comb_Code'][i]
            if dumper_trips and standard_trip and comb_code:
                weight = int(dumper_trips) / int(standard_trip)
                all_weights.append(weight)
                if int(dumper_trips) > max_trips:
                    max_trips = dumper_trips
                    equivalent_case_standard_trip = standard_trip
                    equivalent_case_comb_code = comb_code
        equivalent_trips = all_weights * equivalent_case_standard_trip
        eq = np.rint(np.sum(equivalent_trips))
        return pd.Series([eq,equivalent_case_comb_code], index=['Equivalent_Trips', 'Eq_Comb_Code'])
    
    def add_standard_trips(row):
        code = combination_codes.loc[combination_codes['COMBINATION'] == row['Shovel_Dumper_Lead'], 'STD TRIP']
        c = ''
        if (len(code) > 0):
            c = code.iloc[0]
        return c

    inc['Shovel_Dumper_Lead'] = inc.apply(lambda row: add_shovel_dumper_code(row), axis=1)
    inc['Comb_Code'] = inc.apply(lambda row: add_combination_code(row), axis=1)
    inc['Standard_Trips'] = inc.apply(lambda row: add_standard_trips(row), axis=1)
    inc[['Equivalent_Trips', 'Eq_Comb_Code']] = inc.apply(lambda row: add_equivalent_trips(row), axis=1)
    inc['Incentive'] = inc.apply(lambda row: add_incentive(row), axis=1)
    
    inc.to_excel(os.path.join(temp_out_path, 'inc2.xlsx'))

if __name__ == '__main__':
    argvparser = argparse.ArgumentParser()
    argvparser.add_argument('-i', '--input', help='Zip file name')
    args = argvparser.parse_args()
    unzip_and_analyze(args.input)
