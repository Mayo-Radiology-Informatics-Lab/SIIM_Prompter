from radprompter import Prompt, RadPrompter, vLLMClient, OllamaClient, OpenAIClient
import os
import pandas as pd
import pandas as pd
import numpy as np 
import pandas as pd

if __name__ == '__main__':
    import argparse

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Run LLM model inference")
    parser.add_argument('--model', type=str, default='llama3', help='Model name to use')
    parser.add_argument('--server_port', type=int, default=1234, help='Server port number')
    parser.add_argument('--interval', type=int, default=10, help='Interval for processing and negative value skips inference altogether')
    parser.add_argument('--subset', type=str, default='', help='process a subset of rows. specify as <first>:<last> where those values are integers')

    # Parse arguments
    args = parser.parse_args()

    MODEL = args.model
    SERVER_PORT = args.server_port
    INTERVAL = args.interval
    SUBSET_STR = args.subset
    if SUBSET_STR != '':
        START_LINE, END_LINE = map(int, SUBSET_STR.split(':'))
    else:
        START_LINE = 0
        END_LINE = -1
    
    prompt = Prompt("SIIM.toml")
#    MODEL = 'mixtral:8x22b'
    INPUT_FILE = '~/Desktop/SIIMCombinedReports.xlsx'
    OUTPUT_FILE = '~/Desktop/SIIM_Results-' + MODEL + '.csv'
    TEMP_OUT = '~/Desktop/output-' + MODEL + '.csv'
    
    
    if SERVER_PORT == 10000:
        # use this command to port-forward from a server (roqril0006a) running vllm which will then appear on localhost port 10000:
        # ssh -N -L localhost:10000:localhost:8000 bje01@roqril006a&
        client = vLLMClient(
            model=MODEL,
            base_url="http://localhost:10000/v1",
            temperature=0.0,
            seed=42
        )
    elif SERVER_PORT == 11434:
        client = OllamaClient(
            model=MODEL,
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            temperature=0.0,
            seed=42,
        )
    elif SERVER_PORT == 1234:
        client = OpenAIClient(
            model=MODEL,
            base_url="http://localhost:1234/v1",
            temperature=0.0,
            api_key="lm-studio",
            seed=42,
        )
    elif SERVER_PORT == 0:
        client = OpenAIClient(
        model="GPT-4o",
        api_key="",
        temperature=0.0,
        seed=42
    )
    else:
        print (f"Error--unknown server port {SERVER_PORT}")
        exit(-1)
    print (f"Using port {SERVER_PORT} with model {MODEL}. output will be {OUTPUT_FILE}")
    
    
    # delete any prior output
    
    if os.path.exists(TEMP_OUT):
        os.remove(TEMP_OUT)
    
    
    engine = RadPrompter(
        client=client,
        prompt=prompt, 
        hide_blocks=True,
        output_file=TEMP_OUT,
    )
    
    #---
    
    # now read in the reports from SIIMCombinedReports.xlsx into a pandas dataframe
    
    # Load the Excel file into a DataFrame
    reports_df = pd.read_excel(INPUT_FILE)
    
    if END_LINE != -1: # they specified a subset
        reports_df = reports_df.iloc[START_LINE:END_LINE]
    if INTERVAL > 1: #specified a skip
        reports_df = reports_df.iloc[::INTERVAL]
        
        
        
    # strip spaces out of the FIndings column
    reports_df['Findings'] = reports_df['Findings'].str.replace(' ', '')
    # Remove any instance of '_x000D_' in the entire dataframe
    reports_df = reports_df.replace('_x000D_', '', regex=True)
    # Remove all newline characters and replace multiple spaces with a single space in the 'Report' column
    reports_df['Report'] = reports_df['Report'].str.replace('\n', ' ')
    reports_df['Report'] = reports_df['Report'].str.replace(r'\s+', ' ', regex=True)
    
    
    
    reports_df = reports_df.replace({np.nan: 'No', 'None': 'No', 'Absent':'No', 'Present':'Yes'})
    
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
    
    if INTERVAL > -1:
        print ('Doing inference...')
        out=engine(reports)
    else:
        print ("Skipped doing inference")    
    #---
    
    
    output_df = pd.read_csv(TEMP_OUT, index_col='index')
    # rename the colume in output_df from 'filename' to 'ExamClass'
    out_df = output_df.rename(columns={'filename': 'ExamClass'}) 
    
    # Delete the column with reports
    out_df.drop(columns=['report'], inplace=True, axis=1)
    # Merge the 'Findings' column from reports_df into output_df
    out_df = out_df.join(reports_df['Findings'])
    
    out_df
    
    #---
    
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    # sometimes the LLM gives a long answer, so remove all that
    # Remove all lines after the first line of a cell (including the '\n') throughout the dataframe
    out_df = out_df.applymap(lambda x: x.split('\n')[0] if isinstance(x, str) else x)
    
    
    # Write the combined dataframe to a CSV fil
    out_df.replace('Absent', 'No', inplace=True)
    out_df.replace('Present', 'Yes', inplace=True)
    out_df.to_csv(OUTPUT_FILE)
    
    print('The below should show only results, no reports or other PHI. Please send this file back to BJE@mayo.edu')
    
    out_df


##########################################################################
# This file was converted using nb2py: https://github.com/BardiaKh/nb2py #
##########################################################################
