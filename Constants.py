from enum import Enum

# Variable Constants for MainDriver.py

HELP_SITE = "https://github.com/CS-4820-Library-Project/COUNTER-5-Report-Tool/wiki"

# region Variable Constants for ManageDB

# region field and table definitions
# region dictionary keys
NAME_KEY = 'name'
TYPE_KEY = 'type'
OPTIONS_KEY = 'options'
REPORTS_KEY = 'reports'
CALCULATION_KEY = 'calculation'
SOURCE_KEY = 'source'

FIELD_KEY = 'field'
COMPARISON_KEY = 'comparison'
VALUE_KEY = 'value'
# endregion

# region header definition
HEADER_ENTRIES = ('report_name', 'report_id', 'release', 'institution_name', 'institution_id', 'metric_types',
                  'report_filters', 'report_attributes', 'exceptions', 'reporting_period', 'created', 'created_by')
HEADER_ROWS = len(HEADER_ENTRIES)
BLANK_ROWS = 1
# endregion

# region database report definitions
DATABASE_REPORTS = ('DR', 'DR_D1', 'DR_D2')
DATABASE_REPORTS_METRIC = ('Searches_Automated',
                           'Searches_Federated',
                           'Searches_Regular',
                           'Total_Item_Investigations',
                           'Total_Item_Requests',
                           'Unique_Item_Investigations',
                           'Unique_Item_Requests',
                           'Unique_Title_Investigations',
                           'Unique_Title_Requests',
                           'Limit_Exceeded',
                           'No_License')
DATABASE_REPORTS_ATTRIBUTES = ("Data_Type",
                               "Access_Method")
DATABASE_REPORT_FIELDS = ({NAME_KEY: 'database',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('DR', 'DR_D1', 'DR_D2')},
                          {NAME_KEY: 'publisher',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('DR', 'DR_D1', 'DR_D2')},
                          {NAME_KEY: 'publisher_id',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('DR', 'DR_D1', 'DR_D2')},
                          {NAME_KEY: 'platform',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('DR', 'DR_D1', 'DR_D2')},
                          {NAME_KEY: 'proprietary_id',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('DR', 'DR_D1', 'DR_D2')},
                          {NAME_KEY: 'data_type',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('DR',)},
                          {NAME_KEY: 'access_method',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('DR',)})
# endregion

# region item report definitions
ITEM_REPORTS = ('IR', 'IR_A1', 'IR_M1')
ITEM_REPORTS_METRIC = ('Total_Item_Investigations',
                       'Total_Item_Requests',
                       'Unique_Item_Investigations',
                       'Unique_Item_Requests',
                       'Limit_Exceeded',
                       'No_License')
ITEM_REPORTS_ATTRIBUTES = ("Data_Type",
                           "Access_Type",
                           "Access_Method",
                           "YOP",
                           "Authors",
                           "Publication_Date",
                           "Article_Version")
ITEM_REPORT_FIELDS = ({NAME_KEY: 'item',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1', 'IR_M1')},
                      {NAME_KEY: 'publisher',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1', 'IR_M1')},
                      {NAME_KEY: 'publisher_id',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1', 'IR_M1')},
                      {NAME_KEY: 'platform',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1', 'IR_M1')},
                      {NAME_KEY: 'authors',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'publication_date',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'doi',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1', 'IR_M1')},
                      {NAME_KEY: 'proprietary_id',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1', 'IR_M1')},
                      {NAME_KEY: 'isbn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'print_issn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'online_issn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'uri',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1', 'IR_M1')},
                      {NAME_KEY: 'parent_title',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'parent_authors',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'parent_publication_date',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'parent_article_version',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'parent_data_type',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'parent_doi',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'parent_proprietary_id',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'parent_isbn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'parent_print_issn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'parent_online_issn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'parent_uri',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'component_title',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_authors',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_publication_date',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_data_type',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_doi',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_proprietary_id',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_isbn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_print_issn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_online_issn',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'component_uri',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'data_type',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'yop',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)},
                      {NAME_KEY: 'access_type',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR', 'IR_A1')},
                      {NAME_KEY: 'access_method',
                       TYPE_KEY: 'TEXT',
                       OPTIONS_KEY: ('NOT NULL',),
                       REPORTS_KEY: ('IR',)})
# endregion

# region platform report definitions
PLATFORM_REPORTS = ('PR', 'PR_P1')
PLATFORM_REPORTS_METRIC = ('Searches_Platform',
                           'Total_Item_Investigations',
                           'Total_Item_Requests',
                           'Unique_Item_Investigations',
                           'Unique_Item_Requests',
                           'Unique_Title_Investigations',
                           'Unique_Title_Requests')
PLATFORM_REPORTS_ATTRIBUTES = ("Data_Type",
                               "Access_Method")
PLATFORM_REPORT_FIELDS = ({NAME_KEY: 'platform',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('PR', 'PR_P1')},
                          {NAME_KEY: 'data_type',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('PR',)},
                          {NAME_KEY: 'access_type',
                           TYPE_KEY: 'TEXT',
                           OPTIONS_KEY: ('NOT NULL',),
                           REPORTS_KEY: ('PR',)})
# endregion

# region title report definitions
TITLE_REPORTS = ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')
TITLE_REPORTS_METRIC = ('Total_Item_Investigations',
                        'Total_Item_Requests',
                        'Unique_Item_Investigations',
                        'Unique_Item_Requests',
                        'Unique_Title_Investigations',
                        'Unique_Title_Requests',
                        'Limit_Exceeded',
                        'No_License')
TITLE_REPORTS_ATTRIBUTES = ("Data_Type",
                            "Section_Type",
                            "Access_Type",
                            "Access_Method",
                            "YOP")
TITLE_REPORT_FIELDS = ({NAME_KEY: 'title',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'publisher',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'publisher_id',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'platform',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'doi',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'proprietary_id',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'isbn',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3')},
                       {NAME_KEY: 'print_issn',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'online_issn',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'uri',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {NAME_KEY: 'data_type',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR',)},
                       {NAME_KEY: 'section_type',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR',)},
                       {NAME_KEY: 'yop',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J4')},
                       {NAME_KEY: 'access_type',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR', 'TR_B3', 'TR_J3')},
                       {NAME_KEY: 'access_method',
                        TYPE_KEY: 'TEXT',
                        OPTIONS_KEY: ('NOT NULL',),
                        REPORTS_KEY: ('TR',)})
# endregion

# region fields that all reports have
ALL_REPORT_FIELDS = ({NAME_KEY: 'metric_type',
                      TYPE_KEY: 'TEXT',
                      OPTIONS_KEY: ('NOT NULL', 'CHECK(metric_type <> \"\")')},
                     {NAME_KEY: 'vendor',
                      TYPE_KEY: 'TEXT',
                      OPTIONS_KEY: ('NOT NULL', 'CHECK(vendor <> \"\")')},
                     {NAME_KEY: 'year',
                      TYPE_KEY: 'INTEGER',
                      OPTIONS_KEY: ('NOT NULL', 'CHECK(LENGTH(year) = 4)')},
                     {NAME_KEY: 'month',
                      TYPE_KEY: 'INTEGER',
                      OPTIONS_KEY: ('NOT NULL', 'CHECK(month BETWEEN 1 AND 12)')},
                     {NAME_KEY: 'metric',
                      TYPE_KEY: 'INTEGER',
                      OPTIONS_KEY: ('NOT NULL', 'CHECK(metric > 0)')},
                     {NAME_KEY: 'updated_on',
                      TYPE_KEY: 'TEXT',
                      OPTIONS_KEY: ('NOT NULL',)},
                     {NAME_KEY: 'file',
                      TYPE_KEY: 'TEXT',
                      OPTIONS_KEY: ('NOT NULL',)})
# endregion

# region cost table fields
COST_FIELDS = ({NAME_KEY: 'cost_in_original_currency',
                TYPE_KEY: 'REAL',
                OPTIONS_KEY: ('NOT NULL', 'CHECK(cost_in_original_currency >= 0)')},
               {NAME_KEY: 'original_currency',
                TYPE_KEY: 'TEXT',
                OPTIONS_KEY: ('NOT NULL', 'CHECK(original_currency <> \"\")')},
               {NAME_KEY: 'cost_in_local_currency',
                TYPE_KEY: 'REAL',
                OPTIONS_KEY: ('NOT NULL', 'CHECK(cost_in_local_currency >= 0)')},
               {NAME_KEY: 'cost_in_local_currency_with_tax',
                TYPE_KEY: 'REAL',
                OPTIONS_KEY: ('NOT NULL', 'CHECK(cost_in_local_currency_with_tax >= 0)')})
# endregion
# endregion

ALL_REPORTS = DATABASE_REPORTS + ITEM_REPORTS + PLATFORM_REPORTS + TITLE_REPORTS
REPORT_TYPE_SWITCHER = {'DR': {REPORTS_KEY: DATABASE_REPORTS, 'report_fields': DATABASE_REPORT_FIELDS},
                        'IR': {REPORTS_KEY: ITEM_REPORTS, 'report_fields': ITEM_REPORT_FIELDS},
                        'PR': {REPORTS_KEY: PLATFORM_REPORTS, 'report_fields': PLATFORM_REPORT_FIELDS},
                        'TR': {REPORTS_KEY: TITLE_REPORTS, 'report_fields': TITLE_REPORT_FIELDS}}
NAME_FIELD_SWITCHER = {'DR': 'database', 'IR': 'item', 'PR': 'platform', 'TR': 'title'}

MONTHS = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june',
          7: 'july', 8: 'august', 9: 'september', 10: 'october', 11: 'november', 12: 'december'}
MONTH_CALCULATION = 'COALESCE(SUM(CASE month' + ' WHEN {} THEN ' + 'metric' + ' END), 0)'

YEAR_TOTAL = 'reporting_period_total'
YEAR_TOTAL_CALCULATION = 'SUM(' + 'metric' + ')'

RANKING = 'ranking'
RANKING_CALCULATION = 'RANK() OVER(ORDER BY ' + 'SUM(' + 'metric' + ')' + ' DESC)'

VIEW_SUFFIX = '_view'
VISUAL_VIEW_SUFFIX = '_visual_view'
COST_TABLE_SUFFIX = '_costs'

FIELDS_NOT_IN_VIEWS = ('month', 'metric', 'updated_on')
FIELDS_NOT_IN_KEYS = ('metric', 'updated_on')
FIELDS_NOT_IN_SEARCH_DROPDOWN = ('year',)
FIELDS_IN_CHARTS = ('month', 'year', 'metric',)
FIELDS_NOT_IN_TOP_NUMBER_CHARTS = FIELDS_IN_CHARTS + ('year',)

COSTS_KEY_FIELDS = ('vendor', 'month', 'year')
CHART_KEY_FIELDS = ('vendor', 'metric_type')

DATABASE_FOLDER = r'./all_data/search/'
DATABASE_LOCATION = DATABASE_FOLDER + r'search.db'
# All yearly reports tsv and json are saved here in original condition as backup
PROTECTED_DATABASE_FILE_DIR = "./all_data/.DO_NOT_MODIFY/"
FILE_SUBDIRECTORY_ORDER = ('year', 'vendor')
COSTS_SAVE_FOLDER = PROTECTED_DATABASE_FILE_DIR + 'costs/'

DELIMITERS = {'.tsv': '\t', '.csv': ','}

COMPARISON_OPERATORS = ('LIKE', 'NOT LIKE', '=', '<=', '<', '>=', '>', '<>')
NON_COMPARISONS = ('IS NULL', 'IS NOT NULL')

CURRENCY_LIST = ('USD', 'EUR', 'JPY', 'GBP', 'CAD', 'AUD')
CURRENCY_SIGNS = ('$', '€', '¥', '£', '$', '$')

# endregion

# region Variable Constants for FileDialog Filters
JSON_FILTER = ('JSON files (*.dat)',)
TSV_FILTER = ('TSV files (*.tsv)',)
CSV_FILTER = ('CSV files (*.csv)',)
TSV_AND_CSV_FILTER = ('Report files (*.csv *.tsv)',)
EXCEL_FILTER = ('Excel files (*.xlsx)',)
# endregion


# region Variable Constants for FetchData
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December")

MASTER_REPORTS = ("DR", "IR", "PR", "TR")


class MajorReportType(Enum):
    PLATFORM = "PR"
    DATABASE = "DR"
    TITLE = "TR"
    ITEM = "IR"


class SpecialOptionType(Enum):
    TO = 0  # Tabular Only, not included in request url, only used in creating tabular report
    AO = 1  # Attribute Only, only in attributes_to_include, does not have it's own parameters in request url
    AP = 2  # Attribute Parameter, in attributes_to_include and has it's own parameters in request url
    ADP = 3  # Attribute Date Parameter, in attributes_to_include and has it's own date parameters in request url
    POS = 4  # Parameter Only String, NOT in attributes_to_include and has it's own parameters in request url
    POB = 5  # Parameter Only Bool, NOT in attributes_to_include and has it's own parameters in request url


SPECIAL_REPORT_OPTIONS = {
    MajorReportType.PLATFORM: [(SpecialOptionType.AP, "Data_Type", ["Article",
                                                                    "Book",
                                                                    "Book_Segment",
                                                                    "Database",
                                                                    "Dataset",
                                                                    "Journal",
                                                                    "Multimedia",
                                                                    "Newspaper_or_Newsletter",
                                                                    "Other",
                                                                    "Platform",
                                                                    "Report",
                                                                    "Repository_Item",
                                                                    "Thesis_or_Dissertation"]),
                               (SpecialOptionType.AP, "Access_Method", ["Regular",
                                                                        "TDM"]),
                               (SpecialOptionType.POS, "Metric_Type", ["Searches_Platform",
                                                                       "Total_Item_Investigations",
                                                                       "Total_Item_Requests",
                                                                       "Unique_Item_Investigations",
                                                                       "Unique_Item_Requests",
                                                                       "Unique_Title_Investigations",
                                                                       "Unique_Title_Requests"]),
                               (SpecialOptionType.TO, "Exclude_Monthly_Details")],
    MajorReportType.DATABASE: [(SpecialOptionType.AP, "Data_Type", ["Book",
                                                                    "Database",
                                                                    "Journal",
                                                                    "Multimedia",
                                                                    "Newspaper_or_Newsletter",
                                                                    "Other",
                                                                    "Report",
                                                                    "Repository_Item",
                                                                    "Thesis_or_Dissertation"]),
                               (SpecialOptionType.AP, "Access_Method", ["Regular",
                                                                        "TDM"]),
                               (SpecialOptionType.POS, "Metric_Type", ["Searches_Automated",
                                                                       "Searches_Federated",
                                                                       "Searches_Regular",
                                                                       "Total_Item_Investigations",
                                                                       "Total_Item_Requests",
                                                                       "Unique_Item_Investigations",
                                                                       "Unique_Item_Requests",
                                                                       "Unique_Title_Investigations",
                                                                       "Unique_Title_Requests",
                                                                       "Limit_Exceeded",
                                                                       "No_License"]),
                               (SpecialOptionType.TO, "Exclude_Monthly_Details")],
    MajorReportType.TITLE: [(SpecialOptionType.AP, "Data_Type", ["Book",
                                                                 "Journal",
                                                                 "Newspaper_or_Newsletter",
                                                                 "Other",
                                                                 "Report",
                                                                 "Thesis_or_Dissertation"]),
                            (SpecialOptionType.AP, "Section_Type", ["Article",
                                                                    "Book",
                                                                    "Chapter",
                                                                    "Other",
                                                                    "Section"]),
                            (SpecialOptionType.AP, "Access_Type", ["Controlled",
                                                                   "OA_Gold"]),
                            (SpecialOptionType.AP, "Access_Method", ["Regular",
                                                                     "TDM"]),
                            (SpecialOptionType.POS, "Metric_Type", ["Total_Item_Investigations",
                                                                    "Total_Item_Requests",
                                                                    "Unique_Item_Investigations",
                                                                    "Unique_Item_Requests",
                                                                    "Unique_Title_Investigations",
                                                                    "Unique_Title_Requests",
                                                                    "Limit_Exceeded",
                                                                    "No_License"]),
                            (SpecialOptionType.ADP, "YOP"),
                            (SpecialOptionType.TO, "Exclude_Monthly_Details")],
    MajorReportType.ITEM: [(SpecialOptionType.AP, "Data_Type", ["Article",
                                                                "Book",
                                                                "Book_Segment",
                                                                "Dataset",
                                                                "Journal",
                                                                "Multimedia",
                                                                "Newspaper_or_Newsletter",
                                                                "Other",
                                                                "Report",
                                                                "Repository_Item",
                                                                "Thesis_or_Dissertation"]),
                           (SpecialOptionType.AP, "Access_Type", ["Controlled",
                                                                  "OA_Gold",
                                                                  "Other_Free_To_Read"]),
                           (SpecialOptionType.AP, "Access_Method", ["Regular",
                                                                    "TDM"]),
                           (SpecialOptionType.POS, "Metric_Type", ["Total_Item_Investigations",
                                                                   "Total_Item_Requests",
                                                                   "Unique_Item_Investigations",
                                                                   "Unique_Item_Requests",
                                                                   "Limit_Exceeded",
                                                                   "No_License"]),
                           (SpecialOptionType.ADP, "YOP"),
                           (SpecialOptionType.AO, "Authors"),
                           (SpecialOptionType.AO, "Publication_Date"),
                           (SpecialOptionType.AO, "Article_Version"),
                           (SpecialOptionType.POB, "Include_Component_Details"),
                           (SpecialOptionType.POB, "Include_Parent_Details"),
                           (SpecialOptionType.TO, "Exclude_Monthly_Details")]
}

DEFAULT_SPECIAL_OPTION_VALUE = "all"

# If these codes are received with a Report_Header, files will be created and saved
ACCEPTABLE_CODES = [0,
                    3030,
                    3031,
                    3032,
                    3040,
                    3050,
                    3060,
                    3062] + list(range(0, 1000))

# If these codes are received the retry checkbox will be checked, user can retry later
RETRY_LATER_CODES = [1010,
                     1011]
RETRY_WAIT_TIME = 5  # Seconds


class CompletionStatus(Enum):
    SUCCESSFUL = "Successful!"
    WARNING = "Warning!"
    FAILED = "Failed!"
    CANCELLED = "Cancelled!"

# endregion


# region Variable Constants for Settings
SETTINGS_FILE_DIR = "./all_data/settings/"
SETTINGS_FILE_NAME = "settings.dat"

# Default Settings
SHOW_DEBUG_MESSAGES = False
YEARLY_DIR = "./all_data/yearly_files/"
OTHER_DIR = "./all_data/other_files/"
REQUEST_INTERVAL = 3  # Seconds
REQUEST_TIMEOUT = 120  # Seconds
CONCURRENT_VENDORS = 2
CONCURRENT_REPORTS = 2
USER_AGENT = "Mozilla/5.0 Firefox/73.0 Chrome/80.0.3987.132 Safari/605.1.15"
DEFAULT_CURRENCY = 'USD'
# endregion


# region Variable Constants for ManageVendors
VENDORS_FILE_DIR = "./all_data/vendor_manager/"
VENDORS_FILE_NAME = "vendors.dat"
VENDORS_FILE_PATH = VENDORS_FILE_DIR + VENDORS_FILE_NAME

EXPORT_VENDORS_FILE_NAME = "exported_vendor_data.tsv"
# endregion


# region Variable Constants for ImportFile
COUNTER_4_REPORT_EQUIVALENTS = {
    "BR1": "TR, TR_B1",
    "BR1, BR2": "TR, TR_B1",
    "BR1, BR2, BR3, JR1, JR2": "TR, TR_B1, TR_B2, TR_J1, TR_J2",
    "BR2": "TR, TR_B1",
    "BR3": "TR, TR_B2",
    "DB1": "DR, DR_D1",
    "DB1, DB2": "DR, DR_D1, DR_D2",
    "DB2": "DR, DR_D2",
    "JR1": "TR, TR_J1",
    "JR1, JR2": "TR, TR_J1, TR_J2",
    "JR2": "TR, TR_J2",
    "PR1": "PR, PR_P1"
}

COUNTER_5_REPORT_EQUIVALENTS = {
    "TR_B1": "BR1, BR2",
    "TR_B2": "BR3",
    "TR_J1": "JR1",
    "TR_J2": "JR2",
    "TR": "BR1, BR2, BR3, JR1, JR2",
    "DR_D1": "DB1",
    "DR_D2": "DB2",
    "DR": "DB1, DB2",
    "JR1": "TR_J1",
    "JR2": "TR_J2",
    "PR_P1": "PR1",
    "PR": "PR1"
}
# endregion


# region Variable Constants for Visual
CHART_COLOR_SET = "Set1"
# endregion
