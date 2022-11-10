import pandas as pd
import os, argparse, sys
import numpy as np
from zipfile import ZipFile
from collections import defaultdict

def unzip_and_analyze(filename):
    basepath = os.getcwd()
    temp_path = os.path.join(basepath, 'temp')
    temp_out_path = os.path.join(basepath, 'temp_out')
    incenive_scheme_path = os.path.join(basepath, 'incentive_scheme')
    shovel_codes_file = os.path.join(incenive_scheme_path, 'shovels.csv')
    dumper_codes_file = os.path.join(incenive_scheme_path, 'dumpers.csv')
    combination_codes_file = os.path.join(incenive_scheme_path, 'shovel-dumper-combination.csv')

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

    inc = pd.pivot_table(combined_df, values=['Dumper_Number_of_Trips'], columns=['shift'], index=['Operator.1', 'Shovel_number', 'Dumper_Number'], aggfunc=np.sum).fillna(0)
    inc.to_excel(os.path.join(temp_out_path, 'inc2.xlsx'))

    #read incentive scheme
    shovel_codes = pd.read_csv(shovel_codes_file)

    print(len(shovel_codes.index))


    # Get date shift section
    # excel_references = defaultdict(dict)
    # for file in excel_files:
    #     vars = file.split('.')[0].split('/')[-1].split('_')
    #     date = vars[0]
    #     shift_section = vars[2] + '_' + vars[3]
    #     excel_references[date][shift_section] = pd.read_excel(file)
    # excel_references = dict(excel_references)

    # print('\n---------------------- INDIVIDUAL SHIFT & SECTION ANALYSIS - COAL ----------------------\n')
    # for section,obj in excel_references.items():
    #     for shift,df in obj.items():
    #         print('Coal Production ({} {}): {} Trips {} Tonnes.'
    #               .format(section, shift, df[df['Coal dumped'] >= 0]['Dumper_Number_of_Trips'].sum(), df['Coal dumped'].sum()))
    #
    # print('\n---------------------- INDIVIDUAL SHIFT & SECTION ANALYSIS - OB ----------------------\n')
    # for section,obj in excel_references.items():
    #     for shift,df in obj.items():
    #         print('OB Production ({} {}): {} Trips {} Cum.'
    #               .format(section, shift, df[df['OB Dumped'] >= 0]['Dumper_Number_of_Trips'].sum(), df['OB Dumped'].sum()))
    #
    # #Analyze total production file
    # os.chdir(basepath)
    # the_file = pd.read_excel('total_production.xlsx')
    #
    # print('\n---------------------- ANALYSIS OF {} ----------------------'.format('total_production.xlsx'))
    # print("\nTotal {} rows.\n".format(len(the_file.index)))
    # print('Total Trips: {}.\n'.format(the_file['Dumper_Number_of_Trips'].sum()))
    # print('Total Coal Production: {} Tonnes.\n'.format(the_file['Coal dumped'].sum()))
    # print('Total OB Production: {} Cum.\n'.format(the_file['OB Dumped'].sum()))
    # print('\nData rows per Process-Order \n')
    # print(pd.pivot_table(the_file, values='Coal dumped', columns=['Process_Order'], index='shift', aggfunc=np.count_nonzero))
    # print('\nProcess-Order-wise Total Production --- COAL\n')
    # print(pd.pivot_table(the_file, values='Coal dumped', columns=['Process_Order'], index='shift', aggfunc=np.sum).fillna(0))
    # print('\nOB - Process-Order-wise Total Production --- OB\n')
    # print(pd.pivot_table(the_file, values='OB Dumped', columns=['Process_Order'], index='shift', aggfunc=np.sum).fillna(0))
    #
    # print('\nProcess-Order-wise Overall Totals\n')
    # print(the_file[['Process_Order', 'Coal dumped', 'OB Dumped']].groupby('Process_Order').sum())
    
    #print('\n-----------------------------OTHER TOTALS---------------------------')
    #print('\nSHIFTWISE PRODUCTION TOTALS:\n')
    #print(the_file[['shift', 'Coal dumped', 'OB Dumped']].groupby('shift').sum())
    #print('\nSHIFTWISE TRIP COUNT TOTALS:\n')
    #print(the_file[['shift', 'Dumper_Number_of_Trips']].groupby('shift').sum())
    
    #print('\n---------------------- PIVOT TABLES - COAL ----------------------\n')
    #print('\nSHIFTWISE PRODUCTION TOTALS PER SEAM ------- Coal\n')
    #print(pd.pivot_table(the_file, values='Coal dumped', columns=['SEAM'], index='shift', aggfunc=np.sum).fillna(0))
    #print('\nSHIFTWISE PRODUCTION TOTALS PER SHOVEL------- Coal\n')
    #print(pd.pivot_table(the_file, values='Coal dumped', columns=['Shovel_number'], index='shift', aggfunc=np.sum).fillna(0))
    #print('\nDUMPYARD WISE PRODUCTION TOTALS PER SHOVEL------- Coal\n')
    #print(pd.pivot_table(the_file, values='Coal dumped', columns=['Shovel_number'], index='DUMPYARD CODE', aggfunc=np.sum).fillna(0))

    #print('\n---------------------- PIVOT TABLES - OB ----------------------\n')
    #print('SHIFTWISE PRODUCTION TOTALS PER SEAM ------- OB\n')
    #print(pd.pivot_table(the_file, values='OB Dumped', columns='shift', index='SEAM', aggfunc=np.sum))
    #print('\nSHIFTWISE PRODUCTION TOTALS PER SEAM ------- OB\n')
    #print(pd.pivot_table(the_file, values='OB Dumped', columns=['SEAM'], index='shift', aggfunc=np.sum).fillna(0))
    #print('\n')
    #print(pd.pivot_table(the_file, values='OB Dumped', columns=['Process_Order'], index='shift', aggfunc=np.sum).fillna(0))
    #print('\nSHIFTWISE PRODUCTION TOTALS PER SHOVEL------- OB\n')
    #print(pd.pivot_table(the_file, values='OB Dumped', columns=['Shovel_number'], index='shift', aggfunc=np.sum).fillna(0))
    #print('\nDUMPYARD WISE PRODUCTION TOTALS PER SHOVEL------- OB\n')
    #print(pd.pivot_table(the_file, values='OB Dumped', columns=['Shovel_number'], index='DUMPYARD CODE', aggfunc=np.sum).fillna(0))

if __name__ == '__main__':
    argvparser = argparse.ArgumentParser()
    argvparser.add_argument('-i', '--input', help='Zip file name')
    args = argvparser.parse_args()
    unzip_and_analyze(args.input)
    
