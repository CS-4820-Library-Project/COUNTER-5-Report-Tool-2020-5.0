from enum import Enum

# region Variable Constants for ManageDB

# region field and table definitions
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
DATABASE_REPORT_FIELDS = ({'name': 'database',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'publisher',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'publisher_id',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'platform',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'proprietary_id',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'data_type',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR',)},
                          {'name': 'access_method',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR',)})
# endregion

# region item report definitions
ITEM_REPORTS = ('IR', 'IR_A1', 'IR_M1')
ITEM_REPORTS_METRIC = ('Total_Item_Investigations',
                       'Total_Item_Requests',
                       'Unique_Item_Investigations',
                       'Unique_Item_Requests',
                       'Limit_Exceeded',
                       'No_License')
ITEM_REPORT_FIELDS = ({'name': 'item',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'publisher',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'publisher_id',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'platform',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'authors',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'publication_date',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'doi',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'proprietary_id',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'isbn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'print_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'online_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'uri',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'parent_title',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_authors',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_publication_date',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'parent_article_version',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_data_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'parent_doi',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_proprietary_id',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_isbn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'parent_print_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_online_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_uri',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'component_title',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_authors',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_publication_date',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_data_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_doi',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_proprietary_id',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_isbn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_print_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_online_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_uri',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'data_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'yop',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'access_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'access_method',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)})
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
PLATFORM_REPORT_FIELDS = ({'name': 'platform',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('PR', 'PR_P1')},
                          {'name': 'data_type',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('PR',)},
                          {'name': 'access_type',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('PR',)})
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
TITLE_REPORT_FIELDS = ({'name': 'title',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'publisher',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'publisher_id',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'platform',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'doi',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'proprietary_id',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'isbn',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3')},
                       {'name': 'print_issn',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'online_issn',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'uri',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'data_type',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR',)},
                       {'name': 'section_type',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR',)},
                       {'name': 'yop',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J4')},
                       {'name': 'access_type',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B3', 'TR_J3')},
                       {'name': 'access_method',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR',)})
# endregion

# region fields that all reports have
ALL_REPORT_FIELDS = ({'name': 'metric_type',
                      'type': 'TEXT',
                      'options': ('NOT NULL', 'CHECK(metric_type <> \"\")')},
                     {'name': 'vendor',
                      'type': 'TEXT',
                      'options': ('NOT NULL', 'CHECK(vendor <> \"\")')},
                     {'name': 'year',
                      'type': 'INTEGER',
                      'options': ('NOT NULL', 'CHECK(LENGTH(year) = 4)')},
                     {'name': 'month',
                      'type': 'INTEGER',
                      'options': ('NOT NULL', 'CHECK(month BETWEEN 1 AND 12)')},
                     {'name': 'metric',
                      'type': 'INTEGER',
                      'options': ('NOT NULL', 'CHECK(metric > 0)')},
                     {'name': 'updated_on',
                      'type': 'TEXT',
                      'options': ('NOT NULL',)},
                     {'name': 'file',
                      'type': 'TEXT',
                      'options': ('NOT NULL',)})
# endregion

# region cost table fields
COST_FIELDS = ({'name': 'cost_in_original_currency',
                'type': 'REAL',
                'options': ('NOT NULL', 'CHECK(cost_in_original_currency >= 0)')},
               {'name': 'original_currency',
                'type': 'TEXT',
                'options': ('NOT NULL', 'CHECK(original_currency <> \"\")')},
               {'name': 'cost_in_local_currency',
                'type': 'REAL',
                'options': ('NOT NULL', 'CHECK(cost_in_local_currency >= 0)')},
               {'name': 'cost_in_local_currency_with_tax',
                'type': 'REAL',
                'options': ('NOT NULL', 'CHECK(cost_in_local_currency_with_tax >= 0)')})
# endregion
# endregion

ALL_REPORTS = DATABASE_REPORTS + ITEM_REPORTS + PLATFORM_REPORTS + TITLE_REPORTS
REPORT_TYPE_SWITCHER = {'DR': {'reports': DATABASE_REPORTS, 'report_fields': DATABASE_REPORT_FIELDS},
                        'IR': {'reports': ITEM_REPORTS, 'report_fields': ITEM_REPORT_FIELDS},
                        'PR': {'reports': PLATFORM_REPORTS, 'report_fields': PLATFORM_REPORT_FIELDS},
                        'TR': {'reports': TITLE_REPORTS, 'report_fields': TITLE_REPORT_FIELDS}}
NAME_FIELD_SWITCHER = {'DR': 'database', 'IR': 'item', 'PR': 'platform', 'TR': 'title'}

MONTHS = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june',
          7: 'july', 8: 'august', 9: 'september', 10: 'october', 11: 'november', 12: 'december'}

YEAR_TOTAL = 'reporting_period_total'

RANKING = 'ranking'

VIEW_SUFFIX = '_view'
COST_TABLE_SUFFIX = '_costs'

FIELDS_NOT_IN_VIEWS = ('month', 'metric', 'updated_on')
FIELDS_NOT_IN_KEYS = ('metric', 'updated_on')
FIELDS_NOT_IN_SEARCH_DROPDOWN = ('year',)
FIELDS_NOT_IN_TOP_NUMBER_CHARTS = ('file', 'updated_on')
COST_FIELDS_IN_CHARTS = ('cost_in_local_currency_with_tax',)

COSTS_KEY_FIELDS = ('vendor', 'year')

DATABASE_FOLDER = r'./all_data/search/'
DATABASE_LOCATION = DATABASE_FOLDER + r'search.db'
# All yearly reports tsv and json are saved here in original condition as backup
PROTECTED_DATABASE_FILE_DIR = "./all_data/.DO_NOT_MODIFY/"
FILE_SUBDIRECTORY_ORDER = ('year', 'vendor')
COSTS_SAVE_FOLDER = r'./all_data/costs/'

DELIMITERS = {'.tsv': '\t', '.csv': ','}

COMPARISON_OPERATORS = ('=', '<=', '<', '>=', '>', '<>', 'LIKE', 'NOT LIKE')
NON_COMPARISONS = ('IS NULL', 'IS NOT NULL')

CURRENCY_LIST = ('USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CAD', 'AUD')

# endregion

# region Variable Constants for FileDialog Filters
JSON_FILTER = ('JSON files (*.dat)',)
TSV_FILTER = ('TSV files (*.tsv)',)
CSV_FILTER = ('CSV files (*.csv)',)
EXCEL_FILTER = ('Excel files (*.xlsx)',)
# endregion

# region Variable Constants for FetchData
SHOW_DEBUG_MESSAGES = False


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
ACCEPTABLE_CODES = [3030,
                    3031,
                    3032,
                    3040,
                    3050,
                    3060,
                    3062] + list(range(1, 1000))

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
