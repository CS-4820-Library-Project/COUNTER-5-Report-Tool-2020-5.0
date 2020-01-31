There are 2 levels of reports, Master Reports (e.g. PR, DR) which show all possible columns and Standard Views (e.g. PR_P1, DR_D1, DR_D2) which only show some of the columns from the master reports.

## Report Fetching
All reports are fetched via the COUNTER_SUSHI API, data is returned as JSON. The JSON models and all other details can be found at: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

### Authentication
SUSHI requests can use these parameters for authentication:
- customer_id (required)
- requestor_id (optional)
- api_key (optional)
There are also other optional parametrs like "platform"

### URL Building
Request supported reports: [base_url]/reports?[authentication],[parameters]

Request report: [base_url]/reports/[report_type]?[authentication],[parameters],[begin_date],[end_date]

## TSV Report Formatting
All information about report formatting can be found at: https://www.projectcounter.org/code-of-practice-five-sections/3-0-technical-specifications/#formats

All reports should be formatted like in this image: https://www.projectcounter.org/wp-content/uploads/2017/07/image3.png

### Report Header
All reports should have a header that takes the first 12 rows of the report. The header should be formatted like in this image: https://www.projectcounter.org/wp-content/uploads/2018/09/FIG-3D.png

A blank row should then be added to separate the report header from the column headings and body of the report. 

### Report Column Headings and Body
The column headings for each report type are as follows:

PR
["Platform", "Data_Type", "Access_Method"]

PR_P1
["Platform"]

DR
["Database", "Publisher", "Publisher_ID", "Platform", "Propriety_ID", "Data_Type", "Access_Method"]

DR_D1 and DR_D2
["Database", "Publisher", "Publisher_ID", "Platform", "Propriety_ID"]

TR
["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "ISBN", "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "Data_Type", "Section_Type", "YOP", "Access_Type", "Access_Method"]

TR_B1 and TR_B2
["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "ISBN", "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "YOP"]

TR_B3
["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "ISBN", "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "YOP", "Access_Type"]

TR_J1 and TR_J2
["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI"]

TR_J3
["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "Access_Type"]

TR_J4
["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "YOP"]

IR
["Item", "Publisher", "Publisher_ID", "Platform", "Authors", "Publication_Date", "Article_version", "DOI", "Propriety_ID", "ISBN", "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "Parent_Title", "Parent_Authors", "Parent_Publication_Date", "Parent_Article_Version", "Parent_Data_Type", "Parent_DOI", "Parent_Proprietary_ID", "Parent_ISBN", "Parent_Print_ISSN", "Parent_Online_ISSN", "Parent_URI", "Data_Type", "YOP", "Access_Type", "Access_Method"]

IR_A1
["Item", "Publisher", "Publisher_ID", "Platform", "Authors", "Publication_Date", "Article_version", "DOI", "Propriety_ID", "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "Parent_Title", "Parent_Authors", "Parent_Article_Version", "Parent_DOI", "Parent_Proprietary_ID", "Parent_Print_ISSN", "Parent_Online_ISSN", "Parent_URI", "Access_Type"]

IR_M1
["Item", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "URI"]


All report types end with these headings:
[
   "Metric_Type",
   "Reporting_Period_Total",
   "January",
   "February",
   "March",
   "April",
   "May",
   "June",
   "July",
   "August",
   "September",
   "October",
   "November",
   "December"
]

The report body is then populated with the data received
