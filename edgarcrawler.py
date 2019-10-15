# REFERENCE LINKS
# Source of data: Financial Statements Data (SEC) - https://www.sec.gov/dera/data/financial-statement-data-sets.html
# Accessing EDGAR Data (SEC) - https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm
# Text file documentation of data here (SEC) - https://www.sec.gov/files/aqfs.pdf

# Imports
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime 

# TODO Support quarterly filings
# TODO Support amended statements

# Retrieves the appropriate filing page

class EdgarCrawler:
    def get_filings(self, ticker, start_date, end_date):
        # Finds the CIK of the company, CIK is required for more specific page requests
        cik_search = requests.get('https://www.sec.gov/cgi-bin/browse-edgar?CIK=' + ticker + '&owner=exclude&action=getcompany')
        cik_search_content = cik_search.content
        cik_soup = BeautifulSoup(cik_search_content, 'html.parser')
        CIK_text = ''
        CIK_list = []
        CIK = ''
        for link in cik_soup.find_all(attrs={'class':'companyName'}):
            CIK_text = link.text
            CIK_list = CIK_text.split()
            CIK = CIK_list[3]
        # Gets the annual filings dataframe
        df_a_filings_page = pd.read_html('https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + CIK + '&type=10-K&dateb=&owner=exclude&count=100')

        # Gets the annual filing dates
        df_a_filings = df_a_filings_page[2]
        df_a_filing_dates = pd.DataFrame(df_a_filings['Filing Date']) # list of filing dates

        # Gets the annual filing accession numbers
        df_a_search = df_a_filings_page[2]
        df_descriptions = pd.DataFrame(df_a_search['Description'])

        # Parse the accession numbers from the filing page
        lst_accession = []
        for row in df_descriptions['Description']:
            split = row.split(' ')
            accession_regex = re.findall(r'\d{10}-\d{2}-\d{6}', row)
            lst_accession.append(accession_regex)
        # Converts a list of lists to a list of strings
        lst_accession = list(map(''.join, lst_accession))
        # Merges the dates and accession numbers into one dataframe
        df_a_filing_dates['Accession_No'] = lst_accession

        # Selects the dates of interest
        mask = (df_a_filing_dates['Filing Date'] > start_date) & (df_a_filing_dates['Filing Date'] <= end_date)
        df_between_dates = df_a_filing_dates.loc[mask]
        lst_filing_dates = [] 
        for row in df_between_dates['Filing Date']:
            new_val = datetime.strptime(row, '%Y-%m-%d')
            lst_filing_dates.append(new_val)
        df_between_dates['Dates'] = lst_filing_dates
        return df_between_dates



    def get_fundamentals(self, ticker, start_date, end_date, dataset):
        # Retrieves the filing dates and accession numbers
        filing_info = self.get_filings(ticker, start_date, end_date)

        # Creates a list of lists: each row is a list, each item on each row is a list
        dataset_fundamentals = dataset
        lst_dataset = []
        for row in dataset_fundamentals:
            split_row = row.split()
            lst_dataset.append(split_row)
        # Finds every row where the accession number matches the desired accession numbers
        # Returns each row as a list of lists - allowing the individual line items to be used
        match_dataset = []
        for acc_no in filing_info['Accession_No']:
            for row in lst_dataset:
                for item in row:
                    if item == acc_no:
                        match_dataset.append(row)
        # When the accession number and tag (line item name) match, only return the first case
        # all subsequent cases are for previous periods, which are listed on the filing for disclosure reasons
        unique_dataset = []
        length = len(match_dataset) -1
        ctr = 0
        while ctr < length:
            if match_dataset[ctr][0] == match_dataset[ctr+1][0] and match_dataset[ctr][1] != match_dataset[ctr+1][1]:
                if match_dataset[ctr+1] not in unique_dataset:
                    unique_dataset.append(match_dataset[ctr])
            ctr += 1
        
        # Adds the filing date to each line item, using the accession number
        filing_dates = [] 
        accession_numbers = []

        for date in filing_info['Dates']:
            filing_dates.append(date)
        
        for acc_no in filing_info['Accession_No']:
            accession_numbers.append(acc_no)
        
        for acc_no in accession_numbers:
            cur_idx = accession_numbers.index(acc_no)
            for row in unique_dataset:
                if row[0] == acc_no:
                    row.insert(0, filing_dates[cur_idx])

        # Returns list containing only the required columns
        dates = []
        accession_numbers = []
        items = []
        values = []
        quarters = []

        for row in unique_dataset:
            if len(row) == 8:
                dates.append(row[0])
                accession_numbers.append(row[1])
                items.append(row[2])
                values.append(row[-1])
                quarters.append(row[4])
            elif len(row) == 9:
                dates.append(row[0])
                accession_numbers.append(row[1])
                items.append(row[2])
                values.append(row[-1])
                quarters.append(row[5])
            else:
                dates.append(row[0])
                accession_numbers.append(row[1])
                items.append(row[2])
                values.append(row[-1])
                quarters.append(row[4])
        list_of_tuples = list(zip(dates, accession_numbers, items, values, quarters))
        df_reduced = pd.DataFrame(list_of_tuples, columns=['Date','Acc_no','Item','Value','Quarter'])
        
        return df_reduced

    # Creates list containing all text files.
    def get_files(self, ticker, start, end, filenames):
        all_files = []
        df_list = []
        for file in filenames:
            #dataset_fundamentals = open(r'C:/Users/User/Documents/Development/python/Edgar Crawler/datasets/'+ file + '.txt','r')
            dataset_fundamentals = open(r'./datasets/'+ file + '.txt','r')
            all_files.append(dataset_fundamentals)
        for txt in all_files:
            df = self.get_fundamentals(ticker, start, end, txt)
            df_list.append(df)
        master_df = pd.concat(df_list)
        master_df.to_csv('AAPL', sep='\t', encoding='utf-8', index=False)
        return master_df

files = [
        '2009q1', 
        '2009q2',
        '2009q3',
        '2009q4',
        '2010q1',
        '2010q2',
        '2010q3',
        '2010q4',
        '2011q1',
        '2011q2',
        '2011q3',
        '2011q4',
        '2012q1',
        '2012q2',
        '2012q3',
        '2012q4',
        '2013q1',
        '2013q2',
        '2013q3',
        '2013q4',
        '2014q1',
        '2014q2',
        '2014q3',
        '2014q4',
        '2015q1',
        '2015q2',
        '2015q3',
        '2015q4',
        '2016q1',
        '2016q2',
        '2016q3',
        '2016q4',
        '2017q1',
        '2017q2',
        '2017q3',
        '2017q4',
        '2018q1',
        '2018q2',
        '2018q3',
        '2018q4',
        '2019q1',
        '2019q2',
        '2019q3'
    ]

AAPL = EdgarCrawler()
AAPL.get_files('AAPL','2010-01-01','2019-01-01', files)
