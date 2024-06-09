from radprompter import Prompt, RadPrompter, vLLMClient, OllamaClient, OpenAIClient
import os
import pandas as pd
import numpy as np 
import pandas as pd

if __name__ == '__main__':
    
    prompt = Prompt("SIIM.toml")
    # to use vllm, make sure you have port accessible:
    # ssh -N -L localhost:10000:localhost:8000 bje01@roqril006a&
    client = OpenAIClient(
        model="meta-llama/Meta-Llama-3-70B-Instruct",
        base_url="http://localhost:10000/v1",
        temperature=0.0,
        seed=42,
        api_key="EMPTY"
    )
    # delete any prior output
    if os.path.exists('output-vllm70B.csv'):
        os.remove("output-vllm70B.csv")
    
    
    engine = RadPrompter(
        client=client,
        prompt=prompt, 
        output_file="output-vllm70B.csv",
    )
    
    #---
    
    # now read in the reports from SIIMCombinedReports.xlsx into a pandas dataframe
    
    # Load the Excel file into a DataFrame
    reports_df = pd.read_excel('~/Desktop/SIIMCombinedReports.xlsx')
    # strip spaces out of the FIndings column
    reports_df['Findings'] = reports_df['Findings'].str.replace(' ', '')
    
    reports_df['Report'] = reports_df['Report'].str.replace('\n', '')
    reports_df['Report'] = reports_df['Report'].str.replace('_0x000D_', '')
    reports_df['Report'] = reports_df['Report'].str.replace('    ', '')
    reports_df['Report'] = reports_df['Report'].str.replace('  ', '')
    
    reports_df = reports_df.replace({np.nan: 'No', 'None': 'No'})
    
    reports_df
    
    #---
    
    # Splitting the reports_df into separate dataframes based on the 'ExamClass' column
    
    # Creating a dictionary to hold the dataframes for each category
    categories = reports_df['ExamClass'].unique()
    print (categories)
    dfs = {category: reports_df[reports_df['ExamClass'] == category] for category in categories}
    
    # Now dfs dictionary contains separate dataframes for each category in 'ExamClass'
    # For example, to access the dataframe for 'Cervical Spine Fracture', you can use dfs['Cervical Spine Fracture']
    dfs['Cervical Spine Fracture']
    
    #---
    
    # Summing up the number of rows with 'None' and not 'None' in the 'Findings' column for each category
    
    # Initialize a dictionary to store the results
    category_summary = {}
    
    # Iterate over each category dataframe
    for category, df in dfs.items():
        unique_values = df['Findings'].unique()  # Get unique values in 'Findings' column
        unique_counts = df['Findings'].value_counts()  # Count the number of each unique value
        total_count = len(df)  # Total number of rows
        category_summary[category] = {
            'Unique_Values': unique_values,
            'Unique_Counts': unique_counts,
            'Total': total_count
        }
    # Print the results for each column
    for category, counts in category_summary.items():
        print(f"Category: {category}")
        for value, count in counts['Unique_Counts'].items():
            print(f"{value}: {count} {count*100//counts['Total']}%")
        print(f"Total: {counts['Total']}")
        print()
    
    #---
    
    # Extract all reports from the 'Report' column and clean them by removing extra whitespace and blank lines
    reports = [{'report': report.strip(), 'filename': category} for report, category in zip(reports_df['Report'], reports_df['ExamClass']) if report.strip()]
    
    #---
    
    
    print ('Doing inference...')
    #out=engine(reports)
    
    #---
    
    
    output_df = pd.read_csv("output.csv", index_col='index')
    # rename the colume in output_df from 'filename' to 'ExamClass'
    out_df = output_df.rename(columns={'filename': 'ExamClass'}) 
    
    # Delete the column with reports
    out_df.drop(columns=['report'], inplace=True, axis=1)
    # Merge the 'Findings' column from reports_df into output_df
    out_df = out_df.join(reports_df['Findings'])
    
    #---
    
    if os.path.exists('~/Desktop/SIIM_Results_vllm70B.csv'):
        os.remove("~/Desktop/SIIM_Results_vllm70B.csv")
    # Write the combined dataframe to a CSV fil
    out_df.to_csv('~/Desktop/SIIM_Results_vllm70B.csv')
    
    print('View SIIM_Results_vllm to confirm no reports or other PHI. Please send this file back to BJE@mayo.edu')
 


##########################################################################
# This file was converted using nb2py: https://github.com/BardiaKh/nb2py #
##########################################################################
