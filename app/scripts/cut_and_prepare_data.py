import pandas as pd
import math
from scripts.data_utils import create_regex, create_all_regexs

## THIS FILE IS USED JUST BEFORE DATA IS FED TO THE MODEL.
## This file cuts the data to right length computed in periods. Eg. 10 periods to have 2 years of data.

## Some features are computed here to not have skewed data. Eg. if student has been absent for 2 consecutive periods. That cannot be computed before cutting.
## ONLY MODEL SPESIFIC MODIFICATIONS SHOULD BE DONE AFTRE RUNNNING THIS FILE.


def cut_data(prediction_epoch, years, include_enrolls, file_prefix = None):
    # Convert years to periods
    periods_dict ={
        1:   5,
        1.5: 7,
        2:   10,
        2.5: 12,
        3:   15,
        3.5: 17
    }
    periods = periods_dict[prediction_epoch]


    file_name = 'combined_'
    if (include_enrolls):
        file_name += 'enrolls_'

    # years list to file_name
    file_name += str(years[0]) + '-' + str(years[-1]) + '.csv'

    return cut_after_periods(periods, include_enrolls, file_name, file_prefix)

def cut_after_periods(periods, include_enrolls, file_name, file_prefix):
    file_path = 'data_processed/'
    if (file_prefix is not None):
        file_path += file_prefix

    file_path = file_path + file_name
    
    # Compute amount of semesters included.
    years = (periods / 5)
    semester_count = math.ceil(years * 2)

    df_students = pd.read_csv(file_path, delimiter=',')

    # drop columns where is lk_ilmo in their name and semester ordinal is bigger or same than semester_count. Semesters starts from 0.
    regex_lk_ilmo = create_regex('lk_ilmo', semester_count)
    df_students = df_students.drop(columns=df_students.filter(regex=regex_lk_ilmo).columns)

    # Drop columns where number in the name the number after _ symbols is greater or same than number of periods
    periods = periods + 1 # Real periods starts from 1. Period 0 is data from earlier studies if added to study plan.
    regex_ka_op_kesk = create_all_regexs(periods)
    df_students = df_students.drop(columns=df_students.filter(regex=regex_ka_op_kesk).columns)

    # Has student been absent for 2 or 3 consecutive periods without adecuate reason?
    df_students['2_perak_per'] = 0
    df_students['3_perak_per'] = 0
    df_students['hyl_yht'] = 0
    if (include_enrolls):
        df_students['kesk_yht'] = 0
    for index, row in df_students.iterrows():
        # Loop through periods
        for period in range(1, periods):
            if (period < (periods - 1)):
                # Compute absences
                if row['op_' + str(period)] == 0 and row['op_' + str(period + 1)] == 0:
                    df_students.at[index, '2_perak_per'] = 1
            if (period < (periods - 2)):
                # Compute absences
                if row['op_' + str(period)] == 0 and row['op_' + str(period + 1)] == 0 and row['op_' + str(period + 2)] == 0:
                    df_students.at[index, '3_perak_per'] = 1
            # Compute failed courses
            if row['fail_' + str(period)] > 0:
                df_students.at[index, 'hyl_yht'] += row['fail_' + str(period)]
            if (include_enrolls):
                # Compute dropped courses
                if row['kesk_' + str(period)] > 0:
                    df_students.at[index, 'kesk_yht'] += row['kesk_' + str(period)]

    # Drop all columns that have 'fail_' in their name
    df_students.drop(df_students.filter(regex='fail_').columns, axis=1, inplace=True)
    
    output_path = 'data_processed/data_ready_for_model/'

    if (file_prefix is not None):
        output_path += file_prefix

    # save to csv
    df_students.to_csv(output_path + str(periods -1) + 'prds_' + file_name, index=False)

    return df_students
