import pandas as pd
import numpy as np 

if __name__ == '__main__':
    # now read in the reports from SIIMCombinedReports.xlsx into a pandas dataframe
    # these are results using ollama and llama3:8B
    
    # Load the Excel file into a DataFrame
    results_df = pd.read_csv('SIIM_Results.csv')
    
    # convert all 'Absent' to 'No'
    #results_df.replace('Absent', 'No', inplace=True)
    #results_df.replace('Present', 'Yes', inplace=True)
    results_df
    analysis_file = open("Analysis.txt", "w")
    
    #---
    
    # extract results_df into 5 sepeate dataframes based on ExamClass column, 
    PE_df = results_df[results_df['ExamClass'] == 'Pulmonary Embolism']
    Pneumonia_df = results_df[results_df['ExamClass'] == 'Pneumonia']
    LiverMets_df = results_df[results_df['ExamClass'] == 'Liver metastases']
    Glioma_df = results_df[results_df['ExamClass'] == 'Glioma progression']
    ICH_df = results_df[results_df['ExamClass'] == 'Intracranial hemorrhage']
    CSFX_df = results_df[results_df['ExamClass'] == 'Cervical Spine Fracture']
    #PE_df.describe()
    #Pneumonia_df.describe()
    #LiverMets_df.describe()
    #Glioma_df.describe()
    #ICH_df.describe()
    #CSFX_df.describe()
    
    #---
    
    # Mapping of categories to their respective response columns in output_df
    binary_category_response_values = ['Pneumonia_response', 'LiverMets_response', 'Pulmonary Embolism_response']
    #     'Cervical Spine Fracture' : 'CSFx_response',
    #    'Glioma progression': 'Glioma_response',
    #     'Intracranial hemorrhage': ''
    #categories = results_df['ExamClass'].unique()
    #print (categories)
    
    # Create a new column 'Correct' in output_df
    results_df['Correct'] = 0
    pn_correct = pe_correct = lm_correct = 0
    pn_incorrect = pe_incorrect = lm_incorrect = 0
    # first process the 3 report types that are binary
    for i, examClass in enumerate(['Pneumonia', 'Liver metastases', 'Pulmonary Embolism']):
    # Iterate over each row in reports_df
        for index, row in results_df.iterrows():
            # Check if the 'ExamClass' is one of the keys in binary_category_response_map
            #print (index, row)
            if row['ExamClass'] == examClass:
                #print (index, binary_category_response_keys[key_index])
                # Get the response column for this 'ExamClass'
                response_column = binary_category_response_values[i]
                #print (response_column)
                # get the value in the cell for the 'reponse_column'
                response = row[response_column]
    #            output_row = output_df.loc[index]
                # If the output row is not empty, compare the 'Findings' value with the value in the response column
     #           if not output_row.empty:
                findings = row['Findings']
    #                response = output_row[response_column].values[0]
                    
                    # Set 'Correct' to 1 if the findings match the response, otherwise set to 0
                #print(row)
                # print (f'Row: {index}: {response} - {findings} ')
    
                if findings == response:
                    #print (f'Correct: {index} is {examClass}: {response} - {findings} ')
                    results_df.iloc[index, results_df.columns.get_loc('Correct')] = 1
                    if i == 0:
                        pn_correct += 1
                    elif i == 1:
                        lm_correct += 1
                    else:
                        pe_correct += 1
                else:
                    #print (f'Incorrect: {index} is {examClass}: {response} - {findings} ')
                    if i == 0:
                        pn_incorrect += 1
                    elif i == 1:
                        lm_incorrect += 1
                    else:
                        pe_incorrect += 1
        
    
    print(f"Pneumonia Correct Counts: {pn_correct} VERSUS  Incorrect Counts: {pn_incorrect} = {pn_correct*100//(pn_correct + pn_incorrect)}% right")
    print(f"PE Correct Counts: {pe_correct} VERSUS  Incorrect Counts: {pe_incorrect} = {pe_correct*100//(pe_correct + pe_incorrect)}% right")
    print(f"Liver Mets Correct Counts: {lm_correct} VERSUS  Incorrect Counts: {lm_incorrect} = {lm_correct*100//(lm_correct + lm_incorrect)}% right")
    
    # write the same reults out to analysis_file
    analysis_file.write(f"Pneumonia Correct Counts: {pn_correct} VERSUS  Incorrect Counts: {pn_incorrect} = {pn_correct*100//(pn_correct + pn_incorrect)}% right\n")
    analysis_file.write(f"PE Correct Counts: {pe_correct} VERSUS  Incorrect Counts: {pe_incorrect} = {pe_correct*100//(pe_correct + pe_incorrect)}% right\n")
    analysis_file.write(f"Liver Mets Correct Counts: {lm_correct} VERSUS  Incorrect Counts: {lm_incorrect} = {lm_correct*100//(lm_correct + lm_incorrect)}% right\n")
    
    # Count the number of correct and incorrect by each 'ExamClass'
    ''' 
    correct_counts = results_df.groupby('ExamClass')['Correct'].sum()
    incorrect_counts = results_df.groupby('ExamClass')['Correct'].count() - correct_counts
    
    print(f"Correct Counts (so far--only binary categories done): {correct}")
    print(correct_counts)
    print(f"\n\nIncorrect Counts: {incorrect}")
    print(incorrect_counts)
    '''
    
    
    #---
    
    # now work on Spine fractures. Challenging since there can be more than 1
    correct = 0
    incorrect = 0
    
    for index, row in CSFX_df.iterrows():
        # Check if the 'ExamClass' is one of the keys in binary_category_response_map
        #print (index, row)
    #    if row['ExamClass'] == 'Cervical Spine Fracture':
        # Get the response column for this 'ExamClass'
        result = 'No'
        for i in range (1,8):
            cat_name = f'C{i}FX_response'
            response = row[cat_name]
            if response == 'Yes': # if fracture
                if result == 'No': # replace if none seen to this point
                    result = f'C{i}FX'
                else: # or concatenate
                    result += f',C{i}FX'
        #print (result)            
    #            output_row = output_df.loc[index]
        # If the output row is not empty, compare the 'Findings' value with the value in the response column
    #           if not output_row.empty:
        findings = row['Findings']
        findings = findings.replace(" ","")
        if len(findings) != len(result):
            Correct = 0  # not correct if number of fractures doesn't match 
            incorrect += 1
            #print (f'row {index}: {findings} vs (predicted): {result} -- INCORRECT')
        else:
            Correct = 1
            correct += 1
            #print (f'row {index}: {findings} vs (predicted): {result} -- CORRECT')
        CSFX_df.loc[index, 'Correct'] = Correct
    
    
    #    CSFX_df.iloc[index, CSFX_df.columns.get_loc('Correct')] = Correct
    
    print(f"CSpine FX Correct Counts: {correct} VERSUS  Incorrect Counts: {incorrect} = {correct*100//(correct + incorrect)}% right")
    analysis_file.write(f"CSpine FX Correct Counts: {correct} VERSUS  Incorrect Counts: {incorrect} = {correct*100//(correct + incorrect)}% right\n")
    
    
    #---
    
    GBM_Response_Types = ['IMPROVED', 'PROGRESSION', 'STABLE', 'PSEUDOPROGRESSION']
    # now work on Spine fractures. Challenging since there can be more than 1
    correct = 0
    incorrect = 0
    
    for index, row in Glioma_df.iterrows():
        # Check if the 'ExamClass' is one of the keys in binary_category_response_map
        #print (index, row)
    #    if row['ExamClass'] == 'Cervical Spine Fracture':
        # Get the response column for this 'ExamClass'
        prediction = row['GliomaStatus_response'].lower()
        truth = row['Findings'].lower()
        if prediction == 'no':
            prediction = 'stable'
        if prediction in truth:
            Correct = 1
            correct += 1
            #print (f'row {index}: {truth} vs {prediction}: -- CORRECT')
        else:
            Correct = 0  # not correct if number of fractures doesn't match 
            incorrect += 1
            #print (f'row {index}: {truth} vs {prediction}:-- INCORRECT')
        Glioma_df.loc[index, 'Correct'] = Correct
    
    print(f"GLIOMA--Correct Counts: {correct} VERSUS  Incorrect Counts: {incorrect} = {correct*100//(correct + incorrect)}% right")
    analysis_file.write(f"GLIOMA--Correct Counts: {correct} VERSUS  Incorrect Counts: {incorrect} = {correct*100//(correct + incorrect)}% right\n")
    
    #---
    
    '''
    ICH_Types = ['SAH', 'SDH', 'EDH', 'IPH', 'IVH']
    # now work on Spine fractures. Challenging since there can be more than 1
    correct = 0
    incorrect = 0
    
    for index, row in ICH_df.iterrows():
        # Check if the 'ExamClass' is one of the keys in binary_category_response_map
        #print (index, row)
    #    if row['ExamClass'] == 'Cervical Spine Fracture':
        # Get the response column for this 'ExamClass'
        result = 'No'
        for i, ich_type in enumerate(ICH_Types):
            cat_name = f'C{i}FX_response'
            response = row[cat_name]
            if response == 'Yes': # if fracture
                if result == 'No': # replace if none seen to this point
                    result = f'C{i}FX'
                else: # or concatenate
                    result += f',C{i}FX'
        #print (result)            
    #            output_row = output_df.loc[index]
        # If the output row is not empty, compare the 'Findings' value with the value in the response column
    #           if not output_row.empty:
        findings = row['Findings']
        findings = findings.replace(" ","")
        if len(findings) != len(result):
            Correct = 0  # not correct if number of fractures doesn't match 
            incorrect += 1
            #print (f'row {index}: {findings} vs (predicted): {result} -- INCORRECT')
        else:
            Correct = 1
            correct += 1
            #print (f'row {index}: {findings} vs (predicted): {result} -- CORRECT')
        ICH_df.at[index, 'Correct'] = Correct
    
    
    #    CSFX_df.iloc[index, CSFX_df.columns.get_loc('Correct')] = Correct
    
    
    # Count the number of correct and incorrect by each 'ExamClass'
    correct_counts = ICH_df['Correct'].sum()
    incorrect_counts = ICH_df['Correct'].count() - correct_counts
    
    print(f"Correct Counts: {correct} VERSUS  Incorrect Counts: {incorrect} = {correct*100//(correct + incorrect)}% right")
    
    '''
    
    #---
    
    analysis_file.close()


##########################################################################
# This file was converted using nb2py: https://github.com/BardiaKh/nb2py #
##########################################################################
