## PARSE STUDENTS AND COURSES INTO A DATAFRAME FOR TRAINING THE MODEL.
## THIS IS THE FIRST FILE TO RUN WHEN DATA IS RECEIVED FROM THE UNIVERSITY.
import pandas as pd
import numpy as np
import scripts.data_utils as data_utils
# Read data in
# Suppose data_in/ folder has the following files:
# YEAR_students.csv, where YEAR is the year of the student getting the study right
# YEAR_credits.csv
# YEAR_enrollments.csv

## SETTINGS

# Eg. years = [2017, 2018, 2019, 2020, 2021, 2022]
# include_enrolls - Include enrollments to the data

semester_max = 17 # approx 8 years of studies
def parse_students(years, include_enrolls, file_prefix = None):
    path = 'data_in/'
    if (file_prefix is not None):
        path = path + file_prefix
    for year in years:
        students_file = path + str(year) + '_students.csv'
        courses_file  = path + str(year) + '_credits.csv'
        enroll_file   = path + str(year) + '_enrollments.csv'

        # Students data
        df_students = pd.read_csv(students_file, delimiter=';', header=None, names=['opisknro', 'opinto-oik_alku', 'opinto-oik_loppu', 'aloituspvm', 'valmistunut', 'lukukausi-ilmot', 'syntynyt', 'sukupuoli'])

        # Courses data
        df_courses = pd.read_csv(courses_file, delimiter=';', header=None, names=['opisknro', 'arvosana', 'opintopisteet', 'suoritus_pvm', 'kurssikoodi'])

        # Enrollments data
        df_enroll = pd.read_csv(enroll_file, delimiter=';', header=None, names=['opisknro', 'suoritus_lukukausi', 'suoritus_pvm', 'lukukausi2', 'kurssikoodi'])


        # HANDLE STUDENT ID AND DATES

        df_students['aloituspvm'] = pd.to_datetime(df_students['aloituspvm'])
        # If aloituspvmis missing, it is 1970. Change it to correspond opinto-oik_alku
        df_students['opinto-oik_alku'] = pd.to_datetime(df_students['opinto-oik_alku'])
        # Some rows do not have aloituspvm, it is set to 1970 if missing. Use opinto-oik_alku instead.
        df_students.loc[df_students['aloituspvm'] < df_students['opinto-oik_alku'], 'aloituspvm'] = df_students['opinto-oik_alku']
        df_students['suoritus_vuosi'] = pd.to_numeric(df_students['aloituspvm'].dt.year) # aloitus_vuosi in reality, use this name for the function to work
        df_students['suoritus_kk'] = pd.to_numeric(df_students['aloituspvm'].dt.month) # aloitus_kk in reality, use this name for the function to work
        df_students['aloitus_periodi'] = df_students['suoritus_kk'].apply(data_utils.convert_to_fake_period)
        df_students['aloitus_vuosi'] = df_students['suoritus_vuosi']
        # Convert birth year to age
        df_students['ika'] = df_students['aloitus_vuosi'] - df_students['syntynyt']
        # Drop syntynyt
        df_students = df_students.drop(columns=['syntynyt'])
        # Drop temp columns
        df_students = df_students.drop(columns=['suoritus_vuosi', 'suoritus_kk'])
        # Convert all date values to include only the year in numeric format
        df_students['opinto-oik_alku'] = df_students['opinto-oik_alku'].dt.year
        df_students['opinto-oik_loppu_datetime'] = pd.to_datetime(df_students['opinto-oik_loppu'])
        df_students['opinto-oik_loppu'] = pd.to_numeric(df_students['opinto-oik_loppu'].str.slice(0, 4))

        # convert graduation value (bool) into 0 or 1
        df_students['valmistunut'] = df_students['valmistunut'].astype(int)

        # Save graduation period (ordinal)
        df_students['valmistumisperiodi'] = df_students.apply(data_utils.define_ordinal_period_of_graduation, axis=1)

        # HANDLE SEMESTER ENROLLMENTS

        # Semester enrollments are in format: 137:1,138:1,139:1,140:1,141:1,142:1,143:1.. etc. random amount, max 17 though.
        # This study is for candidate students, so ignore study right after graduating to candidate.
        df_students['lukukausi-ilmot'] = df_students.apply(data_utils.ingore_semesters_after_graduating, axis=1)
        # Parse semesters into separate columns
        # Each row has students all semester enrollments starting from the first semester.
        df_students_semesters = df_students['lukukausi-ilmot'].str.split(',', expand=True)
        # Remove the number before the colon. Example: 137:1 -> 1
        df_students_semesters = df_students_semesters.replace(to_replace=r'^\d+:', value='', regex=True)
        # Fill NaN values with -1
        df_students_semesters = df_students_semesters.fillna(-1)
        # Convert to numeric
        df_students_semesters = df_students_semesters.apply(pd.to_numeric)
        # Rename each column to have a prefix 'lk_ilmo_'
        df_students_semesters = df_students_semesters.add_prefix('lk_ilmo_')
        # compute max semester amount in this data
        semester_local_max = len(df_students_semesters.columns)
        # Add columns to have max amount of 'lk_ilmo_*ordinal*' columns. Students started at 2017 may have max amount of semesters.
        # Pad those files that does not have so much semesters.
        for i in range(semester_local_max, semester_max + 1):
            df_students_semesters['lk_ilmo_' + str(i)] = -2 # This indicates semester is in future

        # Drop lukukausi-ilmot 
        # df_students = df_students.drop(columns=['lukukausi-ilmot'])
        # Merge semesters to the students data frame. This df will have the student info and average grades + gredits per period.
        df_students_periodial = pd.concat([df_students, df_students_semesters], axis=1)

        # Convert whole data frame to use int16 to save memory
        # Int16 maximum value is 32767, which should be enough for all the values in the data frame
        # df_students = df_students.astype('int16')
        # df_students.head(10)

        # HANDLE COURSE COMPLETION DATES

        df_courses = df_courses.merge(df_students_periodial[['opisknro', 'aloitus_vuosi', 'aloitus_periodi',  'opinto-oik_loppu_datetime', 'valmistumisperiodi']], on='opisknro')
        # Convert to year-period
        df_courses['suoritus_pvm'] = pd.to_datetime(df_courses['suoritus_pvm'])
        df_courses['suoritus_vuosi'] = df_courses['suoritus_pvm'].dt.year
        df_courses['suoritus_kk'] = df_courses['suoritus_pvm'].dt.month
        df_courses['suoritus_periodi'] = df_courses.apply(data_utils.convert_to_year_fake_period, axis=1)
        df_courses['suoritus_lukukausi'] = df_courses['suoritus_pvm'].apply(data_utils.convert_date_to_semester)
        df_courses['periodi'] = df_courses['suoritus_kk'].apply(data_utils.convert_to_fake_period)
        df_courses['period_ordinal'] = df_courses.apply(data_utils.define_period_ordinal, axis=1)


        # Group table by kurssikoodi to get course info for enrollments
        df_course_infos = df_courses.groupby('kurssikoodi').agg({'opintopisteet': 'median', 'arvosana': 'first'}).reset_index()

        df_course_infos['arvosana'] = -1

        # REMOVE ROWS THAT ARE AFTER GRADUATION
        df_courses = df_courses[df_courses['suoritus_pvm'] <= df_courses['opinto-oik_loppu_datetime']]

        if (include_enrolls):
            # CREATE COURSES FROM ENROLLMENTS IF COURSE IS NOT PASSED

            # If df_enroll has same opisknro than in df_courses but a kurssikoodi which does not exist in df_courses, then add that row of df_enroll to df_courses
            def create_course_from_enrollment(row):
                if row['kurssikoodi'] not in df_courses.loc[df_courses['opisknro'] == row['opisknro'], ['kurssikoodi']].values:
                    return True
                else:
                    return False

            # Remove rows where kussikoodi is NaN
            df_enroll = df_enroll.dropna(subset=['kurssikoodi'])
            df_enroll = df_enroll.merge(df_students_periodial[['opisknro', 'aloitus_vuosi', 'aloitus_periodi',  'opinto-oik_loppu_datetime', 'valmistumisperiodi']], on='opisknro')
            df_enroll['suoritus_pvm'] = pd.to_datetime(df_enroll['suoritus_pvm'])
            df_enroll['suoritus_vuosi'] = df_enroll['suoritus_pvm'].dt.year
            df_enroll['suoritus_kk'] = df_enroll['suoritus_pvm'].dt.month
            df_enroll['suoritus_periodi'] = df_enroll.apply(data_utils.convert_to_year_fake_period, axis=1)
            df_enroll['periodi'] = df_enroll['suoritus_kk'].apply(data_utils.convert_to_fake_period)
            df_enroll['period_ordinal'] = df_enroll.apply(data_utils.define_period_ordinal, axis=1)

            # Remove rows after graduation
            df_enroll = df_enroll[df_enroll['suoritus_pvm'] <= df_enroll['opinto-oik_loppu_datetime']]
            # Drop all columns except 'opisknro', 'period_ordinal', 'kurssikoodi'
            df_enroll = df_enroll.drop(columns=['suoritus_lukukausi','periodi', 'lukukausi2', 'suoritus_pvm', 'suoritus_periodi', 'opinto-oik_loppu_datetime', 'suoritus_vuosi', 'suoritus_kk', 'aloitus_vuosi', 'aloitus_periodi', 'valmistumisperiodi'])
            df_enroll = df_enroll.merge(df_course_infos, on='kurssikoodi')
            courses_to_add = df_enroll[df_enroll.apply(create_course_from_enrollment, axis=1)]
            df_courses_simple = df_courses[['opisknro', 'kurssikoodi', 'arvosana', 'opintopisteet', 'period_ordinal']]

            # Merge df_enroll to df_courses but do not accept duplicates for opisknro + kurssikoodi combination
            df_courses_with_enrollments = pd.concat([df_courses_simple, df_enroll]).drop_duplicates(subset=['opisknro','kurssikoodi'], keep='first')

            # Convert arvosana and opintopisteet to numeric. Grades may include for example 'ECLA', 'L', 'CL', '0', '1', 'Hyv,' etc.
            grade_conversions = pd.read_csv('utils/grade_conversions.csv', delimiter=',')
            conversion_dict = grade_conversions.set_index('arvosana').T.to_dict('records')[0]
            df_courses_with_enrollments['arvosana'] = df_courses_with_enrollments['arvosana'].apply(lambda x: data_utils.convert_grade_str_to_number(x, conversion_dict))

            df_courses_with_enrollments['arvosana'] = pd.to_numeric(df_courses_with_enrollments['arvosana'], errors='coerce')
            df_courses_with_enrollments['opintopisteet'] = pd.to_numeric(df_courses_with_enrollments['opintopisteet'], errors='coerce')
            # If arvosana is -1 or np.nan, then set keskeytetty to 1, otherwise 0
            df_courses_with_enrollments['keskeytetty'] = df_courses_with_enrollments['arvosana'].apply(lambda x: 0 if x >= 0 else 1)

            # convert 'arvosana back to np.nan if it is -1 ( to avoid problems when computing mean and sum )
            df_courses_with_enrollments['arvosana'] = df_courses_with_enrollments['arvosana'].apply(lambda x: np.nan if x <= 0 else x)

            df_courses = pd.concat([df_courses, df_courses_with_enrollments]).drop_duplicates(subset=['opisknro','kurssikoodi'], keep='first')
            # Fill 'keskeytetty' with 0 if it is np.nan since df_courses may not have that column set
            df_courses['keskeytetty'] = df_courses['keskeytetty'].fillna(0)

        # REMOVE ROWS OF 0 CREDITS ( this makes average grade calculation more accurate. Also 0 credit courses are usually completed at same time with course with credits (like bachelor thesis) )
        df_courses = df_courses[df_courses['opintopisteet'] > 0]

        # Drop the now unnecessary date columns
        df_courses = df_courses.drop(columns=['suoritus_pvm', 'suoritus_vuosi', 'suoritus_kk', 'opinto-oik_loppu_datetime'])

        # HANDLE COURSE GRADES AND CREDITS

        # Convert arvosana and opintopisteet to numeric. Grades may include for example 'ECLA', 'L', 'CL', '0', '1', 'Hyv,' etc.
        grade_conversions = pd.read_csv('utils/grade_conversions.csv', delimiter=',')
        conversion_dict = grade_conversions.set_index('arvosana').T.to_dict('records')[0]
        df_courses['arvosana'] = df_courses['arvosana'].apply(lambda x: data_utils.convert_grade_str_to_number(x, conversion_dict))

        df_courses['arvosana'] = pd.to_numeric(df_courses['arvosana'], errors='coerce')

        df_courses['opintopisteet'] = pd.to_numeric(df_courses['opintopisteet'], errors='coerce')
        if (include_enrolls):
            # Keskeytetty only exists if enrollments are involved.
            df_courses['keskeytetty'] = pd.to_numeric(df_courses['keskeytetty'], errors='coerce')
        else:
            # Convert grades -1 to 0 if enrollments are not involved. There may be some -1 grades, since some courses do not give zero for student that drops the course and informs lecturer about dropping.
            df_courses['arvosana'] = df_courses['arvosana'].apply(lambda x: 0 if x <= 0 else x)

        # Duplicate arvosana column
        df_courses['arvosana_dup'] = df_courses['arvosana']

        # Set flag for failed courses
        df_courses['failed'] = df_courses['arvosana'].apply(lambda x: 1 if x == 0 else 0)

        # If arvosana is -1, set it to np.nan to not to be included in sum and mean calculations
        df_courses['arvosana'] = df_courses['arvosana'].apply(lambda x: np.nan if x < 0 else x)
        df_courses['arvosana_dup'] = df_courses['arvosana_dup'].apply(lambda x: np.nan if x < 0 else x)

        if (not include_enrolls):
            df_courses_with_enrollments = df_courses
        
        # GROUP COURSES COMPLETED IN SAME PERIOD (period ordinal)), COMPUTE AVG GRADE AND SUM CREDITS (opintoipisteet) PER STUDENT
        # group by student id and period
        if (include_enrolls):
            df_courses_grouped = df_courses.groupby(['opisknro', 'period_ordinal']).agg({'arvosana': 'mean', 'arvosana_dup': 'median', 'opintopisteet': 'sum', 'keskeytetty': 'sum', 'failed': 'sum'}).reset_index()
        else:
            df_courses_grouped = df_courses.groupby(['opisknro', 'period_ordinal']).agg({'arvosana': 'mean', 'arvosana_dup': 'median', 'opintopisteet': 'sum', 'failed': 'sum'}).reset_index()

        # Rename arvosana to period_ka and opintopisteet to period_pisteet
        df_courses_grouped = df_courses_grouped.rename(columns={'arvosana': 'period_ka', 'arvosana_dup': 'period_medi', 'opintopisteet': 'period_pisteet'})


        # Create 36 columns for each period to store the average grade and sum of credits.
        for i in range(0, 37):
            df_students_periodial['ka_' + str(i)] = np.nan
            df_students_periodial['op_' + str(i)] = 0.0
            df_students_periodial['fail_' + str(i)] = 0.0
            if (include_enrolls):
                df_students_periodial['kesk_' + str(i)] = 0.0

        # Fill columns 
        for index, row in df_courses_grouped.iterrows():
            df_students_periodial.loc[df_students_periodial['opisknro'] == row['opisknro'], 'ka_' + str(row['period_ordinal'])] = row['period_ka']
            df_students_periodial.loc[df_students_periodial['opisknro'] == row['opisknro'], 'op_' + str(row['period_ordinal'])] = row['period_pisteet']
            df_students_periodial.loc[df_students_periodial['opisknro'] == row['opisknro'], 'fail_' + str(row['period_ordinal'])] = row['failed']
            if (include_enrolls):
                df_students_periodial.loc[df_students_periodial['opisknro'] == row['opisknro'], 'kesk_' + str(row['period_ordinal'])] = row['keskeytetty']

        # Fill periods after graduation with NaN
        for i in range(0, 37):
            df_students_periodial.loc[df_students_periodial['valmistumisperiodi'] <= i, 'ka_' + str(i)] = np.nan
            df_students_periodial.loc[df_students_periodial['valmistumisperiodi'] <= i, 'op_' + str(i)] = np.nan
            df_students_periodial.loc[df_students_periodial['valmistumisperiodi'] <= i, 'fail_' + str(i)] = np.nan
            if (include_enrolls):
                df_students_periodial.loc[df_students_periodial['valmistumisperiodi'] <= i, 'kesk_' + str(i)] = np.nan

        # Fill period gredits with NaN where student is not enrolled for semester (adecuate reason) and has no credits
        df_students_periodial = df_students_periodial.apply(data_utils.credits_to_nan_if_adequate_absent, axis=1)


        # HAS STUDENT BEEN ABSENT FOR 6 CONSECUTIVE PERIODS WITHOUT ADECUATE REASON? This is the definition of 'dropout' in this study.
        df_students_periodial['6_consecutive_zeros'] = 0
        for index, row in df_students_periodial.iterrows():
            # Loop through periods 1-30, because we check 6 periods at once
            for period in range(1, 31):
                if row['op_' + str(period)] == 0 and row['op_' + str(period + 1)] == 0 and row['op_' + str(period + 2)] == 0 and row['op_' + str(period + 3)] == 0 and row['op_' + str(period + 4)] == 0 and row['op_' + str(period + 5)] == 0:
                    df_students_periodial.at[index, '6_consecutive_zeros'] = 1
                    break
        
        # ATTACH "6_CONSECUTIVE_ZEROS" ALSO TO ENROLLMENTS DATA BY STUDENT IDENTIFIER
        if (include_enrolls):
            df_courses_with_enrollments = pd.merge(df_courses_with_enrollments, df_students_periodial[['6_consecutive_zeros', 'opisknro']], on='opisknro', how='left')

        # Remove columns opisknro,opinto-oik_alku,opinto-oik_loppu,aloituspvm,valmistunut,lukukausi-ilmot,syntynyt,sukupuoli,aloitus_periodi,aloitus_vuosi,opinto-oik_loppu_datetime,valmistumisperiodi,
        df_students_periodial = df_students_periodial.drop(columns=['opisknro', 'opinto-oik_alku', 'opinto-oik_loppu', 'aloituspvm', 'valmistunut', 'lukukausi-ilmot', 'aloitus_periodi', 'aloitus_vuosi', 'opinto-oik_loppu_datetime', 'valmistumisperiodi'])
        # Rename "6_consecutive_zeros" to "dropout"
        df_students_periodial = df_students_periodial.rename(columns={'6_consecutive_zeros': 'dropout'})

        #save df to csv file
        output_path = 'data_processed/'
        if (file_prefix is not None):
            output_path += file_prefix
        processed_file_name = output_path + str(year) + '_processed.csv'
        df_students_periodial.to_csv(processed_file_name, index=False)
