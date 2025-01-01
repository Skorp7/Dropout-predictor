import numpy as np
import pandas as pd

# In reality period 1 months are 9-10, period 2 months are 11-12, period 3 months are 1-2, period 4 months are 3-4, summer period months are 5-8
# Here we define perdiods as 1-5 starting from the beginning of the year.
# Function to convert year and month columns to year-period
def convert_to_year_fake_period(row):
    if row['suoritus_kk'] in [1, 2]:
        return str(row['suoritus_vuosi']) + '-1'
    elif row['suoritus_kk'] in [3, 4]:
        return str(row['suoritus_vuosi']) + '-2'
    elif row['suoritus_kk'] in [5, 6, 7]:
        return str(row['suoritus_vuosi']) + '-3'
    elif row['suoritus_kk'] in [8, 9, 10]:
        return str(row['suoritus_vuosi']) + '-4'
    elif row['suoritus_kk'] in [11, 12]:
        return str(row['suoritus_vuosi']) + '-5'
    
def convert_to_fake_period(month):
    if month in [1, 2]:
        return 1
    elif month in [3, 4]:
        return 2
    elif month in [5, 6, 7]:
        return 3
    elif month in [8, 9, 10]:
        return 4
    elif month in [11, 12]:
        return 5

# Function to define period ordinal based on the start year and period number
# Example: Student started in 2017 period 3 and completed course in 2018 period 1, then the completion period is 4th in this student's history.
def define_period_ordinal(row):
    # Multiply the difference between the course year and the start year by 5 (number of periods in a year)
    # Substract the start period number from total periods (5) and add the current period number
    # print the calculation with - anmd * and + signs to see the calculation
    start_year_missed_periods = 5 - row['aloitus_periodi']
    if (row['suoritus_vuosi'] == row['aloitus_vuosi']):
        period = row['periodi'] - start_year_missed_periods
    else:
        full_years = (row['suoritus_vuosi'] - row['aloitus_vuosi'])

        period = full_years * 5 - start_year_missed_periods + row['periodi']

    if period < 1:
        # Grade is from the previous studies
        period = 0
    
    return period

def define_ordinal_period_of_graduation(row):
    start_year_missed_periods = 5 - row['aloitus_periodi']
    end_period = convert_to_fake_period(row['opinto-oik_loppu_datetime'].month)
    if row['opinto-oik_loppu_datetime'].year == row['aloitus_vuosi']:
        return end_period - start_year_missed_periods
    else:
        full_years = (row['opinto-oik_loppu_datetime'].year - row['aloitus_vuosi'])

        period = full_years * 5 - start_year_missed_periods + end_period

    return period

def get_semester_of_ordinal_period(period_ordinal, starting_date):
    # semester 135: autumn 2017, 136: spring 2018
    first_semester = convert_date_to_semester(starting_date)
    first_semester_is_autumn = first_semester % 2 == 1
    first_period = convert_to_fake_period(starting_date.month)
    missed_periods_of_first_semester = 0
    if (first_semester_is_autumn and first_period == 5):
        missed_periods_of_first_semester = 1
    if (not first_semester_is_autumn and first_period in [2, 3]):
        missed_periods_of_first_semester = abs(1 - first_period)
    period_ordinal = period_ordinal + missed_periods_of_first_semester
    # each year has 2 semesters and 5 periods
    # period_ordinal = 1 or 2 then it is the first semester of the year
    # period_ordinal = 3, 4 or 5 then it is the second semester of the year
    full_years = period_ordinal // 5
    remaining_periods = period_ordinal % 5
    if (remaining_periods == 0):
        semester_number = first_semester + (full_years * 2) - 1
    elif (first_semester_is_autumn):
        # Then remaining periods 1-2 are autumn semester and 3-5 are spring semester
        if remaining_periods in [1, 2]:
            semester_number = first_semester + (full_years * 2)
        else:
            semester_number = first_semester + (full_years * 2) + 1
    else:
        # Then remaining periods 1-3 are spring semester and 4-5 are autumn semester
        if remaining_periods in [1, 2, 3]:
            semester_number = first_semester + (full_years * 2)
        else:
            semester_number = first_semester + (full_years * 2) + 1

    # compute semester ordinal
    ordinal = semester_number - first_semester + 1

    # convert to ints
    semester_number = int(semester_number)
    ordinal = int(ordinal)

    return (semester_number, ordinal)

def convert_date_to_semester(date):
    # semester 135: autumn 2017, 136: spring 2018
    full_semesters_from_autumn_to_autumn = 135 + ((date.year - 2017) * 2)
    if date.month in [1, 2, 3, 4, 5, 6, 7]:
        # spring semester, substract 1 from the result
        return full_semesters_from_autumn_to_autumn - 1
    else:
        return full_semesters_from_autumn_to_autumn

def ingore_semesters_after_graduating(row):
    if row['valmistunut'] == 1:
        semester_enrollments = row['lukukausi-ilmot']
        # semester 135: autumn 2017, 136: spring 2018
        # Convert opinto-oik_loppu_datetime to semestser
        last_semester = convert_date_to_semester(row['opinto-oik_loppu_datetime'])
        # Remove semesters after the last semester
        semester_enrollments = semester_enrollments.split(',')
        # Seek what is the array index where string includes the last semester
        last_semester_index = next((i for i, lk_ilmo in enumerate(semester_enrollments) if str(last_semester) in lk_ilmo), None)
        # Remove semesters after the last semester in array
        if last_semester_index is not None:
            semester_enrollments = semester_enrollments[:last_semester_index + 1]
        # Convert back to string
        semester_enrollments = ','.join(semester_enrollments)
        return semester_enrollments
    else:
        return row['lukukausi-ilmot']

def convert_grade_str_to_number(grade_str, conversion_dict):
    try:
        grade = conversion_dict[grade_str]
    except KeyError:
        grade = -1

    return grade

def credits_to_nan_if_adequate_absent(row):
    for i in range(1, 37):
        if (row['op_' + str(i)] == 0.0):
            semester, semester_ordinal = get_semester_of_ordinal_period(i, row['aloituspvm'])
            # Is student is absent with adequate reason
            # -2 lukukausi on tulevaisuudessa (tämä koskee esim. vuonna 2022 aloittaneita, joilla on vain vähän lukukausia)
            # -1 ei opiskeluoikeutta
            # 0: luvanvarainen poissaolo (armeija, siviilipalvelus, äityysloma)
            # 1: ilmoittautunut läsnäolevaksi
            # 2: ilmoittautunut poissaolevaksi
            # 3: ilmoittautuminen laiminlylöty
            if row['lk_ilmo_' + str(semester_ordinal)] in [-2, -1, 0, 2]:
                row['op_' + str(i)] = np.nan
    return row

def create_regex(prefix, number):
    tens = prefix + '_1[0-9]|'
    two_tens = prefix + '_2[0-9]|'
    three_tens = prefix + '_3[0-9]'
    if number < 9:

        return prefix + '_[' + str(number) + '-9]|' + tens + two_tens + three_tens
    if number == 9:

        return prefix + '_9|' + tens + two_tens + three_tens
    if number >= 10 and number < 19:
        number = str(number)

        return prefix + '_1[' + number[1] + '-9]|' + two_tens + three_tens
    if number == 19:

        return prefix + '_19|' + two_tens + three_tens
    if number >= 20 and number < 29:
        number = str(number)

        return prefix + '_2[' + number[1] + '-9]|' + three_tens
    if number == 29:

        return prefix + '_29|' + three_tens
    if number >= 30 and number < 39:
        number = str(number)

        return prefix + '_3[' + number[1] + '-9]|'
    
def create_all_regexs(number):
    concatenated = ''
    for prefix in ['ka', 'op', 'kesk', 'fail']:
        if concatenated == '':
            concatenated = create_regex(prefix, number)
        else:
            concatenated = concatenated + '|' + create_regex(prefix, number)

    return concatenated
