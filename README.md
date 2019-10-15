# edgar-crawler
Retrieves US public company financials by parsing quarterly XBRL dumps. Scrapes EDGAR for CIK and accession numbers.

## Required Data
To use this module you'll need the [~8GB XBRL dumps](https://www.sec.gov/dera/data/financial-statement-data-sets.html).
On that page, you will need to download each zip folder, and extract the 'num.txt' file. 
Give the num.txt file the same name as the parent folder (e.g. 2019q1, 2019q2).
Put each renamed num.txt file into a folder called 'datasets.' The datasets folder should be in the same directory as the edgar-crawler file.

The SEC updates the XBRL dump every quarter, so you must download a new one each quarter.

## Annual Filings
Call the `get_files` method on an instance of the EdgarCrawler class. Get files has four parameters: ticker, start date, end date, and files.
Ticker is a string of the desired ticker. Start and end dates are given as strings in the YYYY-MM-DD format. Files is a list of file names, which are predefined using the naming convention used by the SEC. 

## Quarterly Filings
Not currently supported. Working on it. 





