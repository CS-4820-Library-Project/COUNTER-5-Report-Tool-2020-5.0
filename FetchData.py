"""This module handles all operations involving fetching reports.

The process of fetching reports is made up of these steps:

1. Each vendor is queried for its supported reports using the SUSHI API
2. The vendor is then queried for each supported report, also using the SUSHI API
3. The raw JSON response is converted to JsonModel objects that make it easier to work with the JSON data.
4. The model objects are then used to create create row objects that will be in the final TSV file.
5. The row objects are then sorted by their primary columns, for example, item reports are sorted by the item column.
6. The sorted rows are then used to create and save a final TSV report file that adheres to the COUNTER 5 standards.
7. After all reports are processed, the database is updated with the new data

.. NOTE::
    All fetch operations are multi-threaded. Each vendor has it's own thread, each report for that vendor
    also has it's own thread. The maximum concurrent vendors and reports (per vendor) can be changed in the settings tab
    on the GUI
"""

from os import path, makedirs
import csv
import json
import requests
import platform
import copy
import ctypes

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QDate, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QPushButton, QDialog, QWidget, QProgressBar, QLabel, QVBoxLayout, QDialogButtonBox, \
    QCheckBox, QDateEdit, QFrame, QHBoxLayout, QSizePolicy, QLineEdit, QListView, QRadioButton, QButtonGroup

import GeneralUtils
from ui import FetchReportsTab, FetchSpecialReportsTab, FetchProgressDialog, ReportResultWidget, VendorResultsWidget
from GeneralUtils import JsonModel
from ManageVendors import Vendor
from Settings import SettingsModel
from ManageDB import UpdateDatabaseWorker
from Constants import *


# region Models
class SupportedReportModel(JsonModel):
    """Models a SUSHI Supported Report"""
    def __init__(self, report_id: str):
        self.report_id = report_id

    @classmethod
    def from_json(cls, json_dict: dict):
        report_id = str(json_dict["Report_ID"]).upper() if "Report_ID" in json_dict else ""

        return cls(report_id)


class PeriodModel(JsonModel):
    """Models a SUSHI Period"""
    def __init__(self, begin_date: str, end_date: str):
        self.begin_date = begin_date
        self.end_date = end_date

    @classmethod
    def from_json(cls, json_dict: dict):
        begin_date = json_dict["Begin_Date"] if "Begin_Date" in json_dict else ""
        end_date = json_dict["End_Date"] if "End_Date" in json_dict else ""

        return cls(begin_date, end_date)


class InstanceModel(JsonModel):
    """Models a SUSHI Instance"""
    def __init__(self, metric_type: str, count: int):
        self.metric_type = metric_type
        self.count = count

    @classmethod
    def from_json(cls, json_dict: dict):
        metric_type = json_dict["Metric_Type"] if "Metric_Type" in json_dict else ""
        count = int(json_dict["Count"]) if "Count" in json_dict else 0

        return cls(metric_type, count)


class PerformanceModel(JsonModel):
    """Models a SUSHI Performance"""
    def __init__(self, period: PeriodModel, instances: list):
        self.period = period
        self.instances = instances

    @classmethod
    def from_json(cls, json_dict: dict):
        period = PeriodModel.from_json(json_dict["Period"]) if "Period" in json_dict else None

        instances = get_models("Instance", InstanceModel, json_dict)

        return cls(period, instances)


class TypeValueModel(JsonModel):
    """Models SUSHI models that are made up of Type and value"""
    def __init__(self, item_type: str, value: str):
        self.item_type = item_type
        self.value = value

    @classmethod
    def from_json(cls, json_dict: dict):
        item_type = str(json_dict["Type"]) if "Type" in json_dict else ""
        value = str(json_dict["Value"]) if "Value" in json_dict else ""

        return cls(item_type, value)


class NameValueModel(JsonModel):
    """Models SUSHI models that are made up of Name and value"""
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    @classmethod
    def from_json(cls, json_dict: dict):
        name = str(json_dict["Name"]) if "Name" in json_dict else ""
        value = str(json_dict["Value"]) if "Value" in json_dict else ""

        return cls(name, value)


class ExceptionModel(JsonModel):
    """Models a SUSHI Exception"""
    def __init__(self, code: int, message: str, severity: str, data: str):
        self.code = code
        self.message = message
        self.severity = severity
        self.data = data

    @classmethod
    def from_json(cls, json_dict: dict):
        code = int(json_dict["Code"]) if "Code" in json_dict else 0
        message = json_dict["Message"] if "Message" in json_dict else ""
        severity = json_dict["Severity"] if "Severity" in json_dict else ""
        data = json_dict["Data"] if "Data" in json_dict else ""

        return cls(code, message, severity, data)


class ReportHeaderModel(JsonModel):
    """Models a SUSHI Report Header"""
    def __init__(self, report_name: str, report_id: str, release: str, institution_name: str, institution_ids: list,
                 report_filters: list, report_attributes: list, exceptions: list, created: str, created_by: str):
        self.report_name = report_name
        self.report_id = report_id
        self.release = release
        self.institution_name = institution_name
        self.institution_ids = institution_ids
        self.report_filters = report_filters
        self.report_attributes = report_attributes
        self.exceptions = exceptions
        self.created = created
        self.created_by = created_by

        # Not part of JSON
        self.major_report_type = None

    @classmethod
    def from_json(cls, json_dict: dict):
        report_name = json_dict["Report_Name"] if "Report_Name" in json_dict else ""
        report_id = str(json_dict["Report_ID"]).upper() if "Report_ID" in json_dict else ""
        release = json_dict["Release"] if "Release" in json_dict else ""
        institution_name = json_dict["Institution_Name"] if "Institution_Name" in json_dict else ""
        created = json_dict["Created"] if "Created" in json_dict else ""
        created_by = json_dict["Created_By"] if "Created_By" in json_dict else ""

        institution_ids = get_models("Institution_ID", TypeValueModel, json_dict)
        report_filters = get_models("Report_Filters", NameValueModel, json_dict)
        report_attributes = get_models("Report_Attributes", NameValueModel, json_dict)
        exceptions = get_models("Exceptions", ExceptionModel, json_dict)

        return cls(report_name, report_id, release, institution_name, institution_ids, report_filters,
                   report_attributes, exceptions, created, created_by)


class ReportModel(JsonModel):
    """Models a SUSHI Report"""
    def __init__(self, report_header: ReportHeaderModel, report_items: list):
        self.report_header = report_header
        self.report_items = report_items

        # Not part of JSON
        self.exceptions = []

    @classmethod
    def from_json(cls, json_dict: dict):
        exceptions = ReportModel.process_exceptions(json_dict)

        report_header = ReportHeaderModel.from_json(json_dict["Report_Header"])
        report_type = report_header.report_id
        major_report_type = GeneralUtils.get_major_report_type(report_type)
        report_header.major_report_type = major_report_type

        report_items = []
        if "Report_Items" in json_dict:
            report_item_dicts = json_dict["Report_Items"]
            if len(report_item_dicts) > 0:
                if major_report_type == MajorReportType.PLATFORM:
                    for report_item_dict in report_item_dicts:
                        report_items.append(PlatformReportItemModel.from_json(report_item_dict))

                elif major_report_type == MajorReportType.DATABASE:
                    for report_item_dict in report_item_dicts:
                        report_items.append(DatabaseReportItemModel.from_json(report_item_dict))

                elif major_report_type == MajorReportType.TITLE:
                    for report_item_dict in report_item_dicts:
                        report_items.append(TitleReportItemModel.from_json(report_item_dict))

                elif major_report_type == MajorReportType.ITEM:
                    for report_item_dict in report_item_dicts:
                        report_items.append(ItemReportItemModel.from_json(report_item_dict))

        report_model = cls(report_header, report_items)
        report_model.exceptions = exceptions
        return report_model

    @classmethod
    def process_exceptions(cls, json_dict: dict) -> list:
        """Gets all exception models in a JSON dict, returns them as a list

        :param json_dict: A JSON dict
        :raises ReportHeaderMissingException: When the report header is missing
        :raises RetryLaterException: When a retry later exception model is received
        :raises UnacceptableCodeException: When the report cannot be processed based on the exception code
        """
        exceptions = []

        if "Exception" in json_dict:
            exceptions.append(ExceptionModel.from_json(json_dict["Exception"]))

        code = int(json_dict["Code"]) if "Code" in json_dict else ""
        message = json_dict["Message"] if "Message" in json_dict else ""
        data = json_dict["Data"] if "Data" in json_dict else ""
        severity = json_dict["Severity"] if "Severity" in json_dict else ""
        if code:
            exceptions.append(ExceptionModel(code, message, severity, data))

        if "Report_Header" in json_dict:
            report_header = ReportHeaderModel.from_json(json_dict["Report_Header"])
            if len(report_header.exceptions) > 0:
                for exception in report_header.exceptions:
                    exceptions.append(exception)
        else:
            raise ReportHeaderMissingException(exceptions)

        for exception in exceptions:
            if exception.code in RETRY_LATER_CODES:
                raise RetryLaterException(exceptions)
            elif exception.code not in ACCEPTABLE_CODES:
                raise UnacceptableCodeException(exceptions)

        return exceptions


class PlatformReportItemModel(JsonModel):
    """Models a SUSHI Platform Report Item"""
    def __init__(self, platform: str, data_type: str, access_method: str, performances: list):
        self.platform = platform
        self.data_type = data_type
        self.access_method = access_method
        self.performances = performances

    @classmethod
    def from_json(cls, json_dict: dict):
        platform = json_dict["Platform"] if "Platform" in json_dict else ""
        data_type = json_dict["Data_Type"] if "Data_Type" in json_dict else ""
        access_method = json_dict["Access_Method"] if "Access_Method" in json_dict else ""

        performances = get_models("Performance", PerformanceModel, json_dict)

        return cls(platform, data_type, access_method, performances)


class DatabaseReportItemModel(JsonModel):
    """Models a SUSHI Database Report Item"""
    def __init__(self, database: str, publisher: str, item_ids: list, publisher_ids: list, platform: str,
                 data_type: str, access_method: str,
                 performances: list):
        self.database = database
        self.publisher = publisher
        self.item_ids = item_ids
        self.publisher_ids = publisher_ids
        self.platform = platform
        self.data_type = data_type
        self.access_method = access_method
        self.performances = performances

    @classmethod
    def from_json(cls, json_dict: dict):
        database = json_dict["Database"] if "Database" in json_dict else ""
        publisher = json_dict["Publisher"] if "Publisher" in json_dict else ""
        platform = json_dict["Platform"] if "Platform" in json_dict else ""
        data_type = json_dict["Data_Type"] if "Data_Type" in json_dict else ""
        access_method = json_dict["Access_Method"] if "Access_Method" in json_dict else ""

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        publisher_ids = get_models("Publisher_ID", TypeValueModel, json_dict)
        performances = get_models("Performance", PerformanceModel, json_dict)

        return cls(database, publisher, item_ids, publisher_ids, platform, data_type, access_method, performances)


class TitleReportItemModel(JsonModel):
    """Models a SUSHI Title Report Item"""
    def __init__(self, title: str, item_ids: list, platform: str, publisher: str, publisher_ids: list, data_type: str,
                 section_type: str, yop: str, access_type: str, access_method: str, performances: list):
        self.title = title
        self.item_ids = item_ids
        self.platform = platform
        self.publisher = publisher
        self.publisher_ids = publisher_ids
        self.data_type = data_type
        self.section_type = section_type
        self.yop = yop  # Year of publication
        self.access_type = access_type
        self.access_method = access_method
        self.performances = performances

    @classmethod
    def from_json(cls, json_dict: dict):
        title = json_dict["Title"] if "Title" in json_dict else ""
        platform = json_dict["Platform"] if "Platform" in json_dict else ""
        publisher = json_dict["Publisher"] if "Publisher" in json_dict else ""
        data_type = json_dict["Data_Type"] if "Data_Type" in json_dict else ""
        section_type = json_dict["Section_Type"] if "Section_Type" in json_dict else ""
        yop = json_dict["YOP"] if "YOP" in json_dict else ""
        access_type = json_dict["Access_Type"] if "Access_Type" in json_dict else ""
        access_method = json_dict["Access_Method"] if "Access_Method" in json_dict else ""

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        publisher_ids = get_models("Publisher_ID", TypeValueModel, json_dict)
        performances = get_models("Performance", PerformanceModel, json_dict)

        return cls(title, item_ids, platform, publisher, publisher_ids, data_type, section_type, yop, access_type,
                   access_method, performances)


class ItemContributorModel(JsonModel):
    """Models a SUSHI Item Contributor"""
    def __init__(self, item_type: str, name: str, identifier: str):
        self.item_type = item_type
        self.name = name
        self.identifier = identifier

    @classmethod
    def from_json(cls, json_dict: dict):
        item_type = json_dict["Type"] if "Type" in json_dict else ""
        name = json_dict["Name"] if "Name" in json_dict else ""
        identifier = json_dict["Identifier"] if "Identifier" in json_dict else ""

        return cls(item_type, name, identifier)


class ItemParentModel(JsonModel):
    """Models a SUSHI Item Parent"""
    def __init__(self, item_name: str, item_ids: list, item_contributors: list, item_dates: list, item_attributes: list,
                 data_type: str):
        self.item_name = item_name
        self.item_ids = item_ids
        self.item_contributors = item_contributors
        self.item_dates = item_dates
        self.item_attributes = item_attributes
        self.data_type = data_type

    @classmethod
    def from_json(cls, json_dict: dict):
        item_name = json_dict["Item_Name"] if "Item_Name" in json_dict else ""
        data_type = json_dict["Data_Type"] if "Data_Type" in json_dict else ""

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        item_contributors = get_models("Item_Contributors", ItemContributorModel, json_dict)
        item_dates = get_models("Item_Dates", TypeValueModel, json_dict)
        item_attributes = get_models("Item_Attributes", TypeValueModel, json_dict)

        return cls(item_name, item_ids, item_contributors, item_dates, item_attributes, data_type)


class ItemComponentModel(JsonModel):
    """Models a SUSHI Item Component"""
    def __init__(self, item_name: str, item_ids: list, item_contributors: list, item_dates: list, item_attributes: list,
                 data_type: str, performances: list):
        self.item_name = item_name
        self.item_ids = item_ids
        self.item_contributors = item_contributors
        self.item_dates = item_dates
        self.item_attributes = item_attributes
        self.data_type = data_type
        self.performances = performances

    @classmethod
    def from_json(cls, json_dict: dict):
        item_name = json_dict["Item_Name"] if "Item_Name" in json_dict else ""
        data_type = json_dict["Data_Type"] if "Data_Type" in json_dict else ""

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        item_contributors = get_models("Item_Contributors", ItemContributorModel, json_dict)
        item_dates = get_models("Item_Dates", TypeValueModel, json_dict)
        item_attributes = get_models("Item_Attributes", TypeValueModel, json_dict)
        performances = get_models("Performance", PerformanceModel, json_dict)

        return cls(item_name, item_ids, item_contributors, item_dates, item_attributes, data_type, performances)


class ItemReportItemModel(JsonModel):
    """Models a SUSHI Item Report model"""
    def __init__(self, item: str, item_ids: list, item_contributors: list, item_dates: list, item_attributes: list,
                 platform: str, publisher: str, publisher_ids: list, item_parent: ItemParentModel,
                 item_components: list, data_type: str, yop: str, access_type: str,
                 access_method: str, performances: list):
        self.item = item
        self.item_ids = item_ids
        self.item_contributors = item_contributors
        self.item_dates = item_dates
        self.item_attributes = item_attributes
        self.platform = platform
        self.publisher = publisher
        self.publisher_ids = publisher_ids
        self.item_parent = item_parent
        self.item_components = item_components
        self.data_type = data_type
        self.yop = yop  # Year of publication
        self.access_type = access_type
        self.access_method = access_method
        self.performances = performances

    @classmethod
    def from_json(cls, json_dict: dict):
        item = json_dict["Item"] if "Item" in json_dict else ""
        platform = json_dict["Platform"] if "Platform" in json_dict else ""
        publisher = json_dict["Publisher"] if "Publisher" in json_dict else ""
        data_type = json_dict["Data_Type"] if "Data_Type" in json_dict else ""
        yop = json_dict["YOP"] if "YOP" in json_dict else ""
        access_type = json_dict["Access_Type"] if "Access_Type" in json_dict else ""
        access_method = json_dict["Access_Method"] if "Access_Method" in json_dict else ""

        item_parent = ItemParentModel.from_json(json_dict["Item_Parent"]) if "Item_Parent" in json_dict else None

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        item_contributors = get_models("Item_Contributors", ItemContributorModel, json_dict)
        item_dates = get_models("Item_Dates", TypeValueModel, json_dict)
        item_attributes = get_models("Item_Attributes", TypeValueModel, json_dict)
        publisher_ids = get_models("Publisher_ID", TypeValueModel, json_dict)
        item_components = get_models("Item_Component", ItemComponentModel, json_dict)
        performances = get_models("Performance", PerformanceModel, json_dict)

        return cls(item, item_ids, item_contributors, item_dates, item_attributes, platform, publisher, publisher_ids,
                   item_parent, item_components, data_type, yop, access_type, access_method, performances)


# endregion


# region Custom Exceptions
class RetryLaterException(Exception):
    """An exception raised when a retry later exception code is received in an exception model"""
    def __init__(self, exceptions: list):
        self.exceptions = exceptions


class ReportHeaderMissingException(Exception):
    """An exception raised when a report header is missing from a report"""
    def __init__(self, exceptions: list):
        self.exceptions = exceptions


class UnacceptableCodeException(Exception):
    """An exception raised when a report cannot be processed based on an exception code"""
    def __init__(self, exceptions: list):
        self.exceptions = exceptions
# endregion


def exception_models_to_message(exceptions: list) -> str:
    """Formats a list of exception models into a single string """
    message = ""
    for exception in exceptions:
        if message: message += "\n\n"
        message += f"Code: {exception.code}" \
                   f"\nMessage: {exception.message}" \
                   f"\nSeverity: {exception.severity}" \
                   f"\nData: {exception.data}"

    return message


def get_models(model_key: str, model_type, json_dict: dict) -> list:
    """This converts json lists into a list of the specified SUSHI model type

    :param model_key: The target key to get the list of JSONObjects
    :param model_type: The target model type, e.g PerformanceModel
    :param json_dict: The JSON dict to get the list from
    """
    # Some vendors sometimes return a single dict even when the standard specifies a list,
    # we need to check for that
    models = []
    if model_key in json_dict and json_dict[model_key] is not None:
        if type(json_dict[model_key]) is list:
            model_dicts = json_dict[model_key]
            for model_dict in model_dicts:
                models.append(model_type.from_json(model_dict))

        elif type(json_dict[model_key]) is dict:
            models.append(model_type.from_json(json_dict[model_key]))

    return models


def get_month_years(begin_date: QDate, end_date: QDate) -> list:
    """Returns a list of month-year (MMM-yyyy) strings within a date range"""
    month_years = []
    if begin_date.year() == end_date.year():
        num_months = (end_date.month() - begin_date.month()) + 1
    else:
        num_months = (12 - begin_date.month() + end_date.month()) + 1
        num_years = end_date.year() - begin_date.year()
        num_months += (num_years - 1) * 12

    for i in range(num_months):
        month_years.append(begin_date.addMonths(i).toString("MMM-yyyy"))

    return month_years


class SpecialReportOptions:
    """This holds all the parameters that are used to process a special report

    The options are stored as tuples, (option has non-default value, option type, option name, list of option values)
    """
    def __init__(self):
        # PR, DR, TR, IR
        self.data_type = False, SpecialOptionType.AP, "Data_Type", [DEFAULT_SPECIAL_OPTION_VALUE]
        self.access_method = False, SpecialOptionType.AP, "Access_Method", [DEFAULT_SPECIAL_OPTION_VALUE]
        self.metric_type = False, SpecialOptionType.POS, "Metric_Type", [DEFAULT_SPECIAL_OPTION_VALUE]
        self.exclude_monthly_details = False, SpecialOptionType.TO, None, None
        # TR, IR
        current_date = QDate.currentDate()
        self.yop = False, SpecialOptionType.ADP, "YOP", [DEFAULT_SPECIAL_OPTION_VALUE]
        self.access_type = False, SpecialOptionType.AP, "Access_Type", [DEFAULT_SPECIAL_OPTION_VALUE]
        # TR
        self.section_type = False, SpecialOptionType.AP, "Section_Type", [DEFAULT_SPECIAL_OPTION_VALUE]
        # IR
        self.authors = False, SpecialOptionType.AO, "Authors", [DEFAULT_SPECIAL_OPTION_VALUE]
        self.publication_date = False, SpecialOptionType.AO, "Publication_Date", [DEFAULT_SPECIAL_OPTION_VALUE]
        self.article_version = False, SpecialOptionType.AO, "Article_Version", [DEFAULT_SPECIAL_OPTION_VALUE]
        self.include_component_details = False, SpecialOptionType.POB, None, None
        self.include_parent_details = False, SpecialOptionType.POB, None, None


class ReportRow:
    """This models a row in the generated report, it contains every possible column

    :param begin_date: The begin date of the request, used to populate the month columns in the report
    :param end_date: The end date of the request, used to populate the month columns in the report
    """
    def __init__(self, begin_date: QDate, end_date: QDate):
        self.database = ""
        self.title = ""
        self.item = ""
        self.publisher = ""
        self.publisher_id = ""
        self.platform = ""
        self.authors = ""
        self.publication_date = ""
        self.article_version = ""
        self.doi = ""
        self.proprietary_id = ""
        self.online_issn = ""
        self.print_issn = ""
        self.linking_issn = ""
        self.isbn = ""
        self.uri = ""
        self.parent_title = ""
        self.parent_authors = ""
        self.parent_publication_date = ""
        self.parent_article_version = ""
        self.parent_data_type = ""
        self.parent_doi = ""
        self.parent_proprietary_id = ""
        self.parent_online_issn = ""
        self.parent_print_issn = ""
        self.parent_linking_issn = ""
        self.parent_isbn = ""
        self.parent_uri = ""
        self.component_title = ""
        self.component_authors = ""
        self.component_publication_date = ""
        self.component_data_type = ""
        self.component_doi = ""
        self.component_proprietary_id = ""
        self.component_online_issn = ""
        self.component_print_issn = ""
        self.component_linking_issn = ""
        self.component_isbn = ""
        self.component_uri = ""
        self.data_type = ""
        self.section_type = ""
        self.yop = ""
        self.access_type = ""
        self.access_method = ""
        self.metric_type = ""
        self.total_count = 0

        self.month_counts = {}

        # This only works with 12 months
        # for i in range(12):
        #     curr_date: QDate
        #     if QDate(begin_date.year(), i + 1, 1) < begin_date:
        #         curr_date = QDate(end_date.year(), i + 1, 1)
        #     else:
        #         curr_date = QDate(begin_date.year(), i + 1, 1)
        #
        #     self.month_counts[curr_date.toString("MMM-yyyy")] = 0
        #
        # self.total_count = 0

        # This works with more than 12 months
        for month_year_str in get_month_years(begin_date, end_date):
            self.month_counts[month_year_str] = 0


class RequestData:
    """This holds the data about a report request

    :param vendor: The vendor being processed
    :param target_report_types: The report types to attempt to fetch
    :param begin_date: The begin date to specify in the request
    :param end_date: The end date to specify in the request
    :param save_location: Where the generated report should be saved
    :param settings: The system's settings object
    :param special_options: Special options if fetching a special report
    """
    def __init__(self, vendor: Vendor, target_report_types: list, begin_date: QDate, end_date: QDate,
                 save_location: str, settings: SettingsModel, special_options: SpecialReportOptions = None):
        self.vendor = vendor
        self.target_report_types = target_report_types
        self.begin_date = begin_date
        self.end_date = end_date
        self.save_location = save_location
        self.settings = settings
        self.special_options = special_options


class ProcessResult:
    """This holds the results of an fetch process

    :param vendor: The target vendor
    :param report_type: The target report type
    """
    def __init__(self, vendor: Vendor, report_type: str = None):
        self.vendor = vendor
        self.report_type = report_type
        self.completion_status = CompletionStatus.SUCCESSFUL
        self.message = ""
        self.retry = False
        self.file_name = ""
        self.file_dir = ""
        self.file_path = ""
        self.protected_file_path = ""
        self.year = ""


class FetchReportsAbstract:
    def __init__(self, vendors: list, settings: SettingsModel, widget: QWidget):
        """This contains common functionality shared between classes that fetch reports

        :param vendors: The list of vendors in the system
        :param settings: The system's user settings
        :param widget: The widget of the tab that this class controls
        """

        # region General
        self.widget = widget
        self.vendors = []
        self.update_vendors(vendors)
        self.selected_data = []  # List of ReportData Objects
        self.retry_data = []  # List of (Vendor, list[report_types])>
        self.vendor_workers = {}  # <k = worker_id, v = (VendorWorker, Thread)>
        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0
        self.begin_date = QDate()
        self.end_date = QDate()
        self.selected_options = None
        self.save_dir = ""
        self.is_cancelling = False
        self.is_yearly_fetch = False
        self.settings = settings
        self.database_report_data = []
        # endregion

        # region Fetch Progress Dialog
        self.fetch_progress_dialog: QDialog = None
        self.progress_bar: QProgressBar = None
        self.status_label: QLabel = None
        self.scroll_contents: QWidget = None
        self.scroll_layout: QVBoxLayout = None
        self.ok_button: QPushButton = None
        self.retry_button: QPushButton = None
        self.cancel_button: QPushButton = None

        self.vendor_result_widgets = {}  # <k = vendor name, v = (VendorResultsWidget, VendorResultsUI)>
        # endregion

        # region Update Database Dialog
        self.is_updating_database = False
        self.add_to_database = True
        self.database_thread = None
        self.database_worker = None

        # endregion

    def on_vendors_changed(self, vendors: list):
        """Handles the signal emitted when the system's vendor list is updated

        :param vendors: An updated list of the system's vendors
        """
        self.update_vendors(vendors)
        self.update_vendors_ui()

    def update_vendors(self, vendors: list):
        """ Updates the local copy of vendors that support report fetching (SUSHI)

        :param vendors: A list of vendors
        """
        self.vendors = []
        for vendor in vendors:
            if vendor.is_non_sushi: continue
            self.vendors.append(vendor)

    def update_vendors_ui(self):
        """Updates the UI to show vendors that support report fetching (SUSHI)"""
        raise NotImplementedError()

    def fetch_vendor_data(self, request_data: RequestData):
        """Initiates the process to fetch reports from a vendor

        This creates a new thread to work on this vendor

        :param request_data: The request data for this vendor request
        """
        worker_id = request_data.vendor.name
        if worker_id in self.vendor_workers: return  # Avoid processing a vendor twice

        vendor_worker = VendorWorker(worker_id, request_data)
        vendor_worker.worker_finished_signal.connect(self.on_vendor_worker_finished)
        vendor_thread = QThread()
        self.vendor_workers[worker_id] = vendor_worker, vendor_thread
        vendor_worker.moveToThread(vendor_thread)
        vendor_thread.started.connect(vendor_worker.work)
        vendor_thread.finished.connect(vendor_thread.deleteLater)

        vendor_thread.start()

        if self.settings.show_debug_messages: print(f"{worker_id}: Added a process, total processes: {self.total_processes}")
        self.update_results_ui(request_data.vendor)

    def update_results_ui(self, vendor: Vendor, vendor_result: ProcessResult = None, report_results: list = None):
        """Updates the fetch progress dialog to show results

        :param vendor: The vendor being updated
        :param vendor_result: The result of the vendor
        :param report_results: The results of the vendor's reports
        """
        self.progress_bar.setValue(int((self.completed_processes / self.total_processes) * 100))
        if not self.is_cancelling and self.completed_processes != self.total_processes:
            self.status_label.setText(f"Vendor progress: {self.completed_processes}/{self.total_processes}")

        if vendor.name in self.vendor_result_widgets:
            vendor_results_widget, vendor_results_ui = self.vendor_result_widgets[vendor.name]
            vertical_layout = vendor_results_ui.results_frame.layout()
            status_label = vendor_results_ui.status_label
        else:
            vendor_results_widget = QWidget(self.scroll_contents)
            vendor_results_ui = VendorResultsWidget.Ui_VendorResultsWidget()
            vendor_results_ui.setupUi(vendor_results_widget)
            vendor_results_ui.vendor_label.setText(vendor.name)
            vertical_layout = vendor_results_ui.results_frame.layout()

            status_label = vendor_results_ui.status_label
            frame = vendor_results_ui.results_frame
            expand_button = vendor_results_ui.expand_button
            collapse_button = vendor_results_ui.collapse_button

            status_label.setText("Working...")
            frame.hide()
            expand_button.clicked.connect(lambda: frame.show())
            collapse_button.clicked.connect(lambda: frame.hide())

            self.vendor_result_widgets[vendor.name] = vendor_results_widget, vendor_results_ui
            self.scroll_layout.addWidget(vendor_results_widget)

        if vendor_result is None: return

        status_label.setText("Done")
        result_widget = self.get_result_widget(vendor, vendor_results_widget, vendor_result)
        vertical_layout.addWidget(result_widget)

        for report_result in report_results:
            result_widget = self.get_result_widget(vendor, vendor_results_widget, report_result)
            vertical_layout.addWidget(result_widget)

    def get_result_widget(self, vendor: Vendor, vendor_widget: QWidget, process_result: ProcessResult) -> QWidget:
        """This creates a result widget for either a vendor or a vendor's report

        :param vendor: The target vendor
        :param vendor_widget: The vendor's widget in the fetch progress dialog
        :param process_result: The result to show
        """
        completion_status = process_result.completion_status
        report_result_widget = QWidget(vendor_widget)
        report_result_ui = ReportResultWidget.Ui_ReportResultWidget()
        report_result_ui.setupUi(report_result_widget)

        if process_result.message:
            report_result_ui.message_label.setText(process_result.message)
        else:
            report_result_ui.message_label.hide()

        if process_result.report_type is not None:  # If this is a report result, not vendor
            report_result_ui.report_type_label.setText(process_result.report_type)
            if completion_status == CompletionStatus.SUCCESSFUL or completion_status == CompletionStatus.WARNING:
                report_result_ui.file_frame.show()

                report_result_ui.folder_button.clicked.connect(
                    lambda: GeneralUtils.open_file_or_dir(process_result.file_dir))

                report_result_ui.file_label.setText(f"Saved as: {process_result.file_name}")
                report_result_ui.file_label.mousePressEvent = \
                    lambda event: GeneralUtils.open_file_or_dir(process_result.file_path)
            else:
                report_result_ui.file_frame.hide()
        else:
            report_result_ui.report_type_label.setText("Target Reports")
            report_result_ui.file_frame.hide()
            report_result_ui.retry_frame.hide()

        report_result_ui.success_label.setText(process_result.completion_status.value)
        if completion_status == CompletionStatus.FAILED:
            report_result_ui.retry_check_box.stateChanged.connect(
                lambda checked_state: self.on_report_to_retry_toggled(checked_state, vendor, process_result.report_type))
        else:
            report_result_ui.retry_frame.hide()

        return report_result_widget

    def on_vendor_worker_finished(self, worker_id: str):
        """Handles the signal emmited when a vendor worker has finished

        :param worker_id: The worker ID of the vendor
        """
        self.completed_processes += 1

        thread: QThread
        worker: VendorWorker
        worker, thread = self.vendor_workers[worker_id]
        self.update_results_ui(worker.vendor, worker.process_result, worker.report_process_results)

        if self.is_yearly_fetch:
            process_result: ProcessResult
            for process_result in worker.report_process_results:
                if process_result.completion_status != CompletionStatus.SUCCESSFUL:
                    continue

                self.database_report_data.append({'file': process_result.protected_file_path,
                                                  'vendor': process_result.vendor.name,
                                                  'year': process_result.year})

        worker.deleteLater()
        thread.quit()
        thread.wait()
        self.vendor_workers.pop(worker_id, None)

        if self.started_processes < self.total_processes and not self.is_cancelling:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1

        elif len(self.vendor_workers) == 0: self.finish_fetching_reports()

    def start_progress_dialog(self, window_title: str):
        """Sets up and shows the fetch progress dialog

        :param window_title: The title of the fetch progress dialog
        """
        self.vendor_result_widgets = {}

        if self.fetch_progress_dialog: self.fetch_progress_dialog.close()
        self.fetch_progress_dialog = QDialog(self.widget, flags=Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        fetch_progress_ui = FetchProgressDialog.Ui_FetchProgressDialog()
        fetch_progress_ui.setupUi(self.fetch_progress_dialog)
        self.fetch_progress_dialog.setWindowTitle(window_title)

        self.progress_bar = fetch_progress_ui.progress_bar
        self.status_label = fetch_progress_ui.status_label
        self.scroll_contents = fetch_progress_ui.scroll_area_widget_contents
        self.scroll_layout = fetch_progress_ui.scroll_area_vertical_layout

        self.ok_button = fetch_progress_ui.buttonBox.button(QDialogButtonBox.Ok)
        self.retry_button = fetch_progress_ui.buttonBox.button(QDialogButtonBox.Retry)
        self.cancel_button = fetch_progress_ui.buttonBox.button(QDialogButtonBox.Cancel)

        self.ok_button.setEnabled(False)
        self.retry_button.setEnabled(False)
        self.retry_button.setText("Retry Selected")
        self.ok_button.clicked.connect(lambda: self.fetch_progress_dialog.close())
        self.retry_button.clicked.connect(lambda: self.retry_selected_reports(window_title))
        self.cancel_button.clicked.connect(self.cancel_workers)

        self.status_label.setText("Starting...")
        self.fetch_progress_dialog.show()

    def on_report_to_retry_toggled(self, checked_state: int, vendor: Vendor, report_type):
        """Handles the signal emmited when a report result's retry checkbox is toggled

        The report is added the the list of reports to be retried when the 'retry selected reports' button is clicked

        :param checked_state: The new checked state
        :param vendor: The vendor that this report belongs to
        :param report_type: The report type of the report
        """
        if checked_state == Qt.Checked:
            found = False
            for i in range(len(self.retry_data)):
                v, report_types = self.retry_data[i]
                if v == vendor:
                    report_types.append(report_type)
                    found = True

            if not found:
                self.retry_data.append((vendor, [report_type]))

        elif checked_state == Qt.Unchecked:
            for i in range(len(self.retry_data)):
                v, report_types = self.retry_data[i]
                if v == vendor:
                    report_types.remove(report_type)
                    if len(report_types) == 0: self.retry_data.pop(i)

    def retry_selected_reports(self, progress_window_title: str):
        """Retries the selected reports to retry

        :param progress_window_title: The title of the fetch progress dialog
        """
        if len(self.retry_data) == 0:
            GeneralUtils.show_message("No report selected")
            return

        self.selected_data = []
        for vendor, report_types in self.retry_data:
            request_data = RequestData(vendor, report_types, self.begin_date, self.end_date, self.save_dir,
                                       self.settings, self.selected_options)
            self.selected_data.append(request_data)

        self.start_progress_dialog(progress_window_title)
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        concurrent_vendors = self.settings.concurrent_vendors
        while self.started_processes < len(self.selected_data) and self.started_processes < concurrent_vendors:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1

    def finish_fetching_reports(self):
        """Finishes up the fetch process"""
        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0
        self.is_cancelling = False
        self.cancel_button.setEnabled(False)

        # Start updating database...
        if self.is_yearly_fetch and len(self.database_report_data) > 0:
            if not self.start_updating_database(): self.finish_updating_database()
        else:
            self.finish_updating_database()

    def finish_updating_database(self):
        """Finishes up the database update process"""
        self.is_updating_database = False
        self.database_report_data = []

        self.ok_button.setEnabled(True)
        self.retry_button.setEnabled(True)
        self.status_label.setText("Done!")
        if self.settings.show_debug_messages: print("Fin!")

    def cancel_workers(self):
        """Sends a cancel signal to all vendor workers, updates the UI accordingly"""
        self.is_cancelling = True
        self.total_processes = self.started_processes
        self.status_label.setText(f"Cancelling... (Waiting for started requests to finish)")
        for worker, thread in self.vendor_workers.values():
            worker.set_cancelling()

    def is_yearly_range(self, begin_date: QDate, end_date: QDate) -> bool:
        """Checks if a date range will retrieve all available reports for one year

        :param begin_date: The begin date
        :param end_date: The end date
        """
        current_date = QDate.currentDate()

        if begin_date.year() != end_date.year() or begin_date.year() > current_date.year():
            return False

        if begin_date.year() == current_date.year():
            if begin_date.month() == 1 and end_date.month() == max(current_date.month() - 1, 1):
                return True
        else:
            if begin_date.month() == 1 and end_date.month() == 12:
                return True

        return False

    def start_updating_database(self) -> bool:
        """Starts a thread to update the database. Returns True if successfully started"""
        if self.is_updating_database:
            if self.settings.show_debug_messages: print("Database is already updating")
            return False

        self.is_updating_database = True
        self.status_label.setText("Updating database...")

        self.database_thread = QThread()
        self.database_worker = UpdateDatabaseWorker(self.database_report_data, False)
        self.database_worker.moveToThread(self.database_thread)

        def on_progress_changed(progress: int):
            self.progress_bar.setValue(int((progress / len(self.database_report_data)) * 100))

        def on_worker_finished(code):
            self.database_thread.quit()
            self.database_thread.wait()
            self.finish_updating_database()

        self.database_worker.progress_changed_signal.connect(on_progress_changed)
        self.database_worker.worker_finished_signal.connect(on_worker_finished)

        self.database_thread.started.connect(self.database_worker.work)
        self.database_thread.start()

        return True


class FetchReportsController(FetchReportsAbstract):
    """Controls the Fetch Reports tab

    This class fetches master and standard reports with default parameters. The generated TSV files only include
    the mandatory columns for each report type

    :param vendors: The list of vendors in the system
    :param settings: The system's user settings
    :param widget: The fetch reports widget
    :param fetch_reports_ui: The UI for the fetch reports widget
    """
    def __init__(self, vendors: list, settings: SettingsModel, widget: QWidget,
                 fetch_reports_ui: FetchReportsTab.Ui_fetch_reports_tab):
        super().__init__(vendors, settings, widget)

        # region General
        current_date = QDate.currentDate()
        begin_date = QDate(current_date.year(), 1, 1)
        end_date = QDate(current_date.year(), max(current_date.month() - 1, 1), 1)
        self.fetch_all_begin_date = QDate(begin_date)
        self.adv_begin_date = QDate(begin_date)
        self.fetch_all_end_date = QDate(end_date)
        self.adv_end_date = QDate(end_date)
        self.is_last_fetch_advanced = False
        # endregion

        # region Start Fetch Buttons
        self.fetch_all_btn = fetch_reports_ui.fetch_all_data_button
        self.fetch_all_btn.clicked.connect(self.fetch_all_basic_data)

        self.fetch_adv_btn = fetch_reports_ui.fetch_advanced_button
        self.fetch_adv_btn.clicked.connect(self.fetch_advanced_data)
        # endregion

        # region Vendors
        self.vendor_list_view = fetch_reports_ui.vendors_list_view_fetch
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        self.update_vendors_ui()

        self.select_vendors_btn = fetch_reports_ui.select_vendors_button_fetch
        self.select_vendors_btn.clicked.connect(self.select_all_vendors)
        self.deselect_vendors_btn = fetch_reports_ui.deselect_vendors_button_fetch
        self.deselect_vendors_btn.clicked.connect(self.deselect_all_vendors)
        # endregion

        # region Report Types
        self.report_type_list_view = fetch_reports_ui.report_types_list_view
        self.report_type_list_model = QStandardItemModel(self.report_type_list_view)
        self.report_type_list_view.setModel(self.report_type_list_model)
        for report_type in ALL_REPORTS:
            item = QStandardItem(report_type)
            item.setCheckable(True)
            item.setEditable(False)
            self.report_type_list_model.appendRow(item)

        self.select_report_types_btn = fetch_reports_ui.select_report_types_button_fetch
        self.select_report_types_btn.clicked.connect(self.select_all_report_types)
        self.deselect_report_types_btn = fetch_reports_ui.deselect_report_types_button_fetch
        self.deselect_report_types_btn.clicked.connect(self.deselect_all_report_types)

        self.report_types_help_btn = fetch_reports_ui.report_types_help_button
        self.report_types_help_btn.clicked.connect(
            lambda: GeneralUtils.show_message("Only reports supported by each respective vendor will be retrieved, "
                                              "and unsupported reports will be listed in \"Expand\" results"))
        # endregion

        # region Custom Directory
        self.custom_dir_frame = fetch_reports_ui.custom_dir_frame
        self.custom_dir_frame.hide()
        self.custom_dir_message_frame = fetch_reports_ui.frame
        self.custom_dir_message_frame.hide()
        self.custom_dir_message_frame2 = fetch_reports_ui.frame_2
        self.custom_dir_message_frame2.hide()
        self.custom_dir_frame_message1 = fetch_reports_ui.label_38
        self.custom_dir_frame_message2 = fetch_reports_ui.label
        self.custom_dir_edit = fetch_reports_ui.custom_dir_edit
        self.custom_dir_edit.setText(self.settings.other_directory)
        self.custom_dir_button = fetch_reports_ui.custom_dir_button
        self.custom_dir_button.clicked.connect(self.on_custom_dir_clicked)
        self.date_range_help_btn = fetch_reports_ui.date_range_help_button
        self.date_range_help_btn.clicked.connect(
            lambda: GeneralUtils.show_message("Reports run for date ranges that represent a normal Jan-Dec calendar" 
                                              " year, or Jan-last month for calendar years in progress, will be added" 
                                              " to (or updated in) the search database. All other date ranges will be " 
                                              "saved in the specified folder but not added to the search database."))
        self.date_range_help_btn2 = fetch_reports_ui.date_range_help_button2
        self.date_range_help_btn2.clicked.connect(
            lambda: GeneralUtils.show_message("Reports run for date ranges that represent a normal Jan-Dec calendar"
                                              " year, or Jan-last month for calendar years in progress, will be added"
                                              " to (or updated in) the search database. All other date ranges will be "
                                              "saved in the specified folder but not added to the search database."))
        self.date_range_help_btn3 = fetch_reports_ui.date_range_help_button3
        self.date_range_help_btn3.clicked.connect(
            lambda: GeneralUtils.show_message("See Other Reports Directory setting in Settings for default"))

        # endregion

        # region Date Edits
        self.all_date_edit = fetch_reports_ui.All_reports_edit_fetch
        self.all_date_edit.setDate(self.fetch_all_begin_date)
        self.all_date_edit.dateChanged.connect(self.on_fetch_all_date_changed)

        self.begin_date_edit_year = fetch_reports_ui.begin_date_edit_fetch_year
        self.begin_date_edit_year.setDate(self.adv_begin_date)
        self.begin_date_edit_year.dateChanged.connect(lambda date: self.on_date_year_changed(date, "adv_begin"))

        self.end_date_edit_year = fetch_reports_ui.end_date_edit_fetch_year
        self.end_date_edit_year.setDate(self.adv_end_date)
        self.end_date_edit_year.dateChanged.connect(lambda date: self.on_date_year_changed(date, "adv_end"))

        self.begin_month_combo_box = fetch_reports_ui.begin_month_combo_box
        for month in MONTH_NAMES:
            self.begin_month_combo_box.addItem(month)
        self.begin_month_combo_box.currentIndexChanged.connect(
            lambda index: self.on_date_month_changed(index + 1, "adv_begin"))
        self.begin_month_combo_box.setCurrentIndex(self.adv_begin_date.month() - 1)

        self.end_month_combo_box = fetch_reports_ui.end_month_combo_box
        for month in MONTH_NAMES:
            self.end_month_combo_box.addItem(month)
        self.end_month_combo_box.currentIndexChanged.connect(
            lambda index: self.on_date_month_changed(index + 1, "adv_end"))
        self.end_month_combo_box.setCurrentIndex(self.adv_end_date.month() - 1)

        # endregion

    def update_vendors_ui(self):
        """Updates the UI to show vendors that support report fetching (SUSHI)"""
        self.vendor_list_model.clear()
        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setCheckable(True)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

    def on_fetch_all_date_changed(self, date: QDate):
        """Handles the signal emitted when the 'fetch all' date is changed

        :param date: The new date
        """
        current_date = QDate.currentDate()
        if date.year() == current_date.year():
            self.fetch_all_begin_date = QDate(current_date.year(), 1, 1)
            self.fetch_all_end_date = QDate(current_date.year(), max(current_date.month() - 1, 1), 1)
        elif date.year() < current_date.year():
            self.fetch_all_begin_date = QDate(date.year(), 1, 1)
            self.fetch_all_end_date = QDate(date.year(), 12, 1)
        else:
            self.all_date_edit.setDate(current_date)

    def on_date_year_changed(self, date: QDate, date_type: str):
        """Handles the signal emitted when a date's year is changed

        :param date: The new date
        :param date_type: The date to be updated
        """
        if date_type == "adv_begin":
            self.adv_begin_date = QDate(date.year(), self.adv_begin_date.month(), self.adv_begin_date.day())

        elif date_type == "adv_end":
            self.adv_end_date = QDate(date.year(), self.adv_end_date.month(), self.adv_end_date.day())

        if self.is_yearly_range(self.adv_begin_date, self.adv_end_date):
            self.custom_dir_frame.hide()
            self.custom_dir_message_frame.hide()
            self.custom_dir_message_frame2.hide()
        else:
            self.custom_dir_frame.show()
            if self.custom_dir_frame_message_show(self.adv_begin_date, self.adv_end_date):
                self.custom_dir_message_frame2.show()
                self.custom_dir_message_frame.hide()
            else:
                self.custom_dir_message_frame.show()
                self.custom_dir_message_frame2.hide()

    def on_date_month_changed(self, month: int, date_type: str):
        """Handles the signal emitted when a date's month is changed

        :param month: The new month
        :param date_type: The date to be updated
        """
        if date_type == "adv_begin":
            self.adv_begin_date = QDate(self.adv_begin_date.year(), month, self.adv_begin_date.day())

        elif date_type == "adv_end":
            self.adv_end_date = QDate(self.adv_end_date.year(), month, self.adv_end_date.day())

        if self.is_yearly_range(self.adv_begin_date, self.adv_end_date):
            self.custom_dir_frame.hide()
            self.custom_dir_message_frame.hide()
            self.custom_dir_message_frame2.hide()
        else:
            self.custom_dir_frame.show()
            if self.custom_dir_frame_message_show(self.adv_begin_date, self.adv_end_date):
                self.custom_dir_message_frame2.show()
                self.custom_dir_message_frame.hide()
            else:
                self.custom_dir_message_frame.show()
                self.custom_dir_message_frame2.hide()

    def custom_dir_frame_message_show(self, begin_date: QDate, end_date: QDate) -> bool:
        """Checks which message will show on the custom dir frame

        :param begin_date: The begin date
        :param end_date: The end date
        """
        current_date = QDate.currentDate()

        if begin_date.year() == end_date.year() == current_date.year():
            if begin_date.month() == 1 and end_date.month() == 12:
                return True

        return False

    def on_custom_dir_clicked(self):
        """Handles the signal emitted when the choose custom directory button is clicked"""
        dir_path = GeneralUtils.choose_directory()
        if dir_path: self.custom_dir_edit.setText(dir_path)

    def select_all_vendors(self):
        """Checks all vendors in the vendors list view"""
        for i in range(self.vendor_list_model.rowCount()):
            self.vendor_list_model.item(i).setCheckState(Qt.Checked)

    def deselect_all_vendors(self):
        """Un-checks all vendors in the vendors list view"""
        for i in range(self.vendor_list_model.rowCount()):
            self.vendor_list_model.item(i).setCheckState(Qt.Unchecked)

    def select_all_report_types(self):
        """Checks all report types in the report types list view"""
        for i in range(self.report_type_list_model.rowCount()):
            self.report_type_list_model.item(i).setCheckState(Qt.Checked)

    def deselect_all_report_types(self):
        """Un-checks all report types in the report types list view"""
        for i in range(self.report_type_list_model.rowCount()):
            self.report_type_list_model.item(i).setCheckState(Qt.Unchecked)

    def fetch_all_basic_data(self):
        """Fetches all reports for the selected year"""
        if self.total_processes > 0:
            GeneralUtils.show_message(f"Waiting for pending processes to complete...")
            if self.settings.show_debug_messages: print(f"Waiting for pending processes to complete...")
            return

        if len(self.vendors) == 0:
            GeneralUtils.show_message("Vendor list is empty")
            return

        self.begin_date = self.fetch_all_begin_date
        self.end_date = self.fetch_all_end_date
        if self.begin_date > self.end_date:
            GeneralUtils.show_message("\'Begin Date\' is earlier than \'End Date\'")
            return

        self.is_yearly_fetch = True
        self.save_dir = self.settings.yearly_directory
        self.selected_data = []
        for i in range(len(self.vendors)):
            if self.vendors[i].is_non_sushi: continue

            request_data = RequestData(self.vendors[i], ALL_REPORTS, self.begin_date, self.end_date,
                                       self.save_dir, self.settings)
            self.selected_data.append(request_data)

        self.is_last_fetch_advanced = False
        self.start_progress_dialog("Fetch Reports Progress")
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        concurrent_vendors = self.settings.concurrent_vendors
        while self.started_processes < len(self.selected_data) and self.started_processes < concurrent_vendors:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1

    def fetch_advanced_data(self):
        """Fetches reports based on the selected options in the advanced view of the UI"""
        if self.total_processes > 0:
            GeneralUtils.show_message(f"Waiting for pending processes to complete...")
            if self.settings.show_debug_messages: print(f"Waiting for pending processes to complete...")
            return

        if len(self.vendors) == 0:
            GeneralUtils.show_message("Vendor list is empty")
            return

        self.begin_date = self.adv_begin_date
        self.end_date = self.adv_end_date
        if self.begin_date > self.end_date:
            GeneralUtils.show_message("\'Begin Date\' is earlier than \'End Date\'")
            return

        self.selected_data = []
        selected_report_types = []
        for i in range(len(ALL_REPORTS)):
            if self.report_type_list_model.item(i).checkState() == Qt.Checked:
                selected_report_types.append(ALL_REPORTS[i])
        if len(selected_report_types) == 0:
            GeneralUtils.show_message("No report type selected")
            return

        self.is_yearly_fetch = self.is_yearly_range(self.adv_begin_date, self.adv_end_date)
        custom_dir = self.custom_dir_edit.text()
        if not custom_dir: custom_dir = self.settings.other_directory
        self.save_dir = custom_dir if not self.is_yearly_fetch else self.settings.yearly_directory
        for i in range(self.vendor_list_model.rowCount()):
            if self.vendor_list_model.item(i).checkState() == Qt.Checked:
                request_data = RequestData(self.vendors[i], selected_report_types, self.begin_date, self.end_date,
                                           self.save_dir, self.settings)
                self.selected_data.append(request_data)
        if len(self.selected_data) == 0:
            GeneralUtils.show_message("No vendor selected")
            return

        self.start_progress_dialog("Fetch Reports Progress")
        self.is_last_fetch_advanced = False
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        concurrent_vendors = self.settings.concurrent_vendors
        while self.started_processes < len(self.selected_data) and self.started_processes < concurrent_vendors:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1


class FetchSpecialReportsController(FetchReportsAbstract):
    def __init__(self, vendors: list, settings: SettingsModel, widget: QWidget,
                 fetch_special_reports_ui: FetchSpecialReportsTab.Ui_fetch_special_reports_tab):
        super().__init__(vendors, settings, widget)

        # region General
        self.selected_report_type = None
        self.selected_options = SpecialReportOptions()
        current_date = QDate.currentDate()
        self.begin_date = QDate(current_date.year(), 1, 1)
        self.end_date = QDate(current_date.year(), max(current_date.month() - 1, 1), 1)
        # endregion

        # region Start Fetch Button
        self.fetch_special_btn = fetch_special_reports_ui.fetch_special_data_button
        self.fetch_special_btn.clicked.connect(self.fetch_special_data)
        # endregion

        # region Vendors
        self.vendor_list_view = fetch_special_reports_ui.vendors_list_view_special
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        self.update_vendors_ui()

        self.select_vendors_btn = fetch_special_reports_ui.select_vendors_button_special
        self.select_vendors_btn.clicked.connect(self.select_all_vendors)
        self.deselect_vendors_btn = fetch_special_reports_ui.deselect_vendors_button_special
        self.deselect_vendors_btn.clicked.connect(self.deselect_all_vendors)
        # endregion

        # region Options
        self.options_frame = fetch_special_reports_ui.options_frame
        self.options_layout = self.options_frame.layout()
        help_message = "The 'show' checkboxes will break down your data by displaying extra columns with the " \
                       "selected attributes (usually results in more lines per item)\n" \
                       "Filters will limit your data to just the selected options (implies also showing that " \
                       "attribute).\n" \
                       "You can show the attribute breakdown without selecting filtering to specific values."
        fetch_special_reports_ui.options_help_button.clicked.connect(
            lambda: GeneralUtils.show_message(help_message)
        )
        # endregion

        # region Report Types
        self.pr_radio_button = fetch_special_reports_ui.pr_radio_button
        self.dr_radio_button = fetch_special_reports_ui.dr_radio_button
        self.tr_radio_button = fetch_special_reports_ui.tr_radio_button
        self.ir_radio_button = fetch_special_reports_ui.ir_radio_button

        self.pr_radio_button.clicked.connect(lambda checked: self.on_report_type_selected(MajorReportType.PLATFORM))
        self.dr_radio_button.clicked.connect(lambda checked: self.on_report_type_selected(MajorReportType.DATABASE))
        self.tr_radio_button.clicked.connect(lambda checked: self.on_report_type_selected(MajorReportType.TITLE))
        self.ir_radio_button.clicked.connect(lambda checked: self.on_report_type_selected(MajorReportType.ITEM))

        self.pr_radio_button.setChecked(True)
        self.on_report_type_selected(MajorReportType.PLATFORM)

        # endregion

        # region Date Edits
        self.date_range_help_btn = fetch_special_reports_ui.date_range_help_button
        self.date_range_help_btn.clicked.connect(
            lambda: GeneralUtils.show_message("Many vendors do not support a date range longer than 12 consecutive months."))

        self.begin_date_edit_year = fetch_special_reports_ui.begin_date_edit_special_year
        self.begin_date_edit_year.setDate(self.begin_date)
        self.begin_date_edit_year.dateChanged.connect(lambda date: self.on_date_year_changed(date, "begin_date"))

        self.end_date_edit_year = fetch_special_reports_ui.end_date_edit_special_year
        self.end_date_edit_year.setDate(self.end_date)
        self.end_date_edit_year.dateChanged.connect(lambda date: self.on_date_year_changed(date, "end_date"))

        self.begin_month_combo_box = fetch_special_reports_ui.begin_month_combo_box
        for month in MONTH_NAMES:
            self.begin_month_combo_box.addItem(month)
        self.begin_month_combo_box.currentIndexChanged.connect(
            lambda index: self.on_date_month_changed(index + 1, "begin_date"))
        self.begin_month_combo_box.setCurrentIndex(self.begin_date.month() - 1)

        self.end_month_combo_box = fetch_special_reports_ui.end_month_combo_box
        for month in MONTH_NAMES:
            self.end_month_combo_box.addItem(month)
        self.end_month_combo_box.currentIndexChanged.connect(
            lambda index: self.on_date_month_changed(index + 1, "end_date"))
        self.end_month_combo_box.setCurrentIndex(self.end_date.month() - 1)

        # endregion

        # region Custom Directory
        self.custom_dir_frame = fetch_special_reports_ui.custom_dir_frame
        self.custom_dir_edit = fetch_special_reports_ui.custom_dir_edit
        self.custom_dir_edit.setText(self.settings.other_directory)
        self.custom_dir_button = fetch_special_reports_ui.custom_dir_button
        self.custom_dir_button.clicked.connect(self.on_custom_dir_clicked)
        self.custom_dir_help_btn = fetch_special_reports_ui.custom_dir_help_button
        self.custom_dir_help_btn.clicked.connect(
            lambda: GeneralUtils.show_message("See Other Reports Directory setting in Settings for default."))
        # endregion

    def update_vendors_ui(self):
        """Updates the UI to show vendors that support report fetching (SUSHI)"""
        self.vendor_list_model.clear()
        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setCheckable(True)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

    def on_date_year_changed(self, date: QDate, date_type: str):
        """Handles the signal emitted when a date's year is changed

        :param date: The new date
        :param date_type: The date to be updated
        """
        if date_type == "begin_date":
            self.begin_date = QDate(date.year(),self.begin_date.month(),self.begin_date.day())
        elif date_type == "end_date":
            self.end_date = QDate(date.year(),self.end_date.month(),self.end_date.day())

    def on_date_month_changed(self, month: int, date_type: str):
        """Handles the signal emitted when a date's month is changed

        :param month: The new month
        :param date_type: The date to be updated
        """
        if date_type == "begin_date":
            self.begin_date = QDate(self.begin_date.year(), month, self.begin_date.day())
        elif date_type == "end_date":
            self.end_date = QDate(self.end_date.year(), month, self.end_date.day())

    def on_report_type_selected(self, major_report_type: MajorReportType):
        """Handles the signal emitted when a report type is selected

        :param major_report_type: The major report type (Only master reports are supported)
        """
        if major_report_type == self.selected_report_type: return

        self.selected_report_type = major_report_type
        self.selected_options = SpecialReportOptions()

        # Remove existing options from ui
        for i in reversed(range(self.options_layout.count())):
            widget = self.options_layout.itemAt(i).widget()
            # remove it from the layout list
            self.options_layout.removeWidget(widget)
            # remove it from the gui
            widget.deleteLater()

        # Add new options
        self.options_layout.addWidget(QLabel("Show", self.options_frame), 0, 0)
        self.options_layout.addWidget(QLabel("Filters", self.options_frame), 0, 1)

        special_options = SPECIAL_REPORT_OPTIONS[major_report_type]
        for i in range(len(special_options)):
            option_name = special_options[i][1]
            checkbox = QCheckBox(option_name, self.options_frame)
            checkbox.toggled.connect(
                lambda is_checked, option=option_name: self.on_special_option_toggled(option, is_checked))
            self.options_layout.addWidget(checkbox, i + 1, 0)

            option_type: SpecialOptionType = special_options[i][0]
            if option_type == SpecialOptionType.AP or option_type == SpecialOptionType.POS\
                    or option_type == SpecialOptionType.ADP:
                line_edit = QLineEdit(DEFAULT_SPECIAL_OPTION_VALUE, self.options_frame)
                line_edit.setReadOnly(True)
                button = QPushButton("Choose", self.options_frame)
                if option_type == SpecialOptionType.ADP:
                    button.clicked.connect(
                        lambda c, so=special_options[i], edit=line_edit:
                        self.on_special_date_parameter_option_button_clicked(so, edit))
                else:
                    button.clicked.connect(
                        lambda c, so=special_options[i], edit=line_edit:
                        self.on_special_parameter_option_button_clicked(so, edit))

                self.options_layout.addWidget(line_edit, i + 1, 1)
                self.options_layout.addWidget(button, i + 1, 2)

    def on_special_option_toggled(self, option: str, is_checked: bool):
        """Handles the signal emitted when a special option is checked or un-checked

        :param option: The special option
        :param is_checked: Checked or un-checked
        """
        option = option.lower()
        __, option_type, option_name, curr_options = self.selected_options.__getattribute__(option)
        self.selected_options.__setattr__(option, (is_checked, option_type, option_name, curr_options))

    def on_special_parameter_option_button_clicked(self, special_option, line_edit):
        """Handles the signal emitted when a special option with parameters clicked

        :param special_option: The special option
        :param line_edit: The line edit to show the selected parameters for this option
        """
        option_type, option_name, option_list = special_option
        is_selected, option_type, option_name, curr_options = self.selected_options.__getattribute__(option_name.lower())

        dialog = QDialog(self.options_frame, flags=Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        dialog.setWindowTitle(option_name + " options")
        layout = QVBoxLayout(dialog)

        list_view = QListView(dialog)
        list_view.setAlternatingRowColors(True)
        model = QStandardItemModel(list_view)

        for option in option_list:
            item = QStandardItem(option)
            item.setCheckable(True)
            item.setEditable(False)
            if option in curr_options:
                item.setCheckState(Qt.Checked)
            model.appendRow(item)

        list_view.setModel(model)

        layout.addWidget(list_view)

        def on_ok_button_clicked():
            checked_list = []
            for i in range(model.rowCount()):
                if model.item(i).checkState() == Qt.Checked:
                    checked_list.append(model.item(i).text())

            if len(checked_list) == 0:
                checked_list = [DEFAULT_SPECIAL_OPTION_VALUE]

            line_edit.setText("|".join(checked_list))
            self.selected_options.__setattr__(option_name.lower(), (is_selected, option_type, option_name, checked_list))
            dialog.close()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        button_box.accepted.connect(on_ok_button_clicked)
        button_box.rejected.connect(lambda: dialog.close())
        button_box.setCenterButtons(True)
        layout.addWidget(button_box)

        dialog.exec_()

    def on_special_date_parameter_option_button_clicked(self, special_option, line_edit):
        """Handles the signal emitted when a date special option is clicked

        :param special_option: The special option
        :param line_edit: The line edit to show the selected date parameters for this option
        """
        option_type, option_name = special_option
        is_selected, option_type, option_name, selected_options = self.selected_options.__getattribute__(option_name.lower())

        dialog = QDialog(self.options_frame, flags=Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        dialog.setWindowTitle(option_name + " options")
        layout = QVBoxLayout(dialog)

        radio_button_group = QButtonGroup(dialog)

        default_frame = QFrame(dialog)
        default_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        default_layout = QHBoxLayout(default_frame)
        default_layout.setContentsMargins(0, 0, 0, 0)

        default_radio_btn = QRadioButton(default_frame)
        default_radio_btn.setChecked(True)
        radio_button_group.addButton(default_radio_btn)
        default_label = QLabel(DEFAULT_SPECIAL_OPTION_VALUE, dialog)

        default_layout.addWidget(default_radio_btn)
        default_layout.addWidget(default_label)

        single_date_frame = QFrame(dialog)
        single_date_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        single_date_layout = QHBoxLayout(single_date_frame)
        single_date_layout.setContentsMargins(0, 0, 0, 0)

        single_date_radio_btn = QRadioButton(single_date_frame)
        radio_button_group.addButton(single_date_radio_btn)
        single_date_edit = QDateEdit(QDate.currentDate(), single_date_frame)
        single_date_edit.setDisplayFormat("yyyy")

        single_date_layout.addWidget(single_date_radio_btn)
        single_date_layout.addWidget(single_date_edit)

        range_date_frame = QFrame(dialog)
        range_date_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        range_date_layout = QHBoxLayout(range_date_frame)
        range_date_layout.setContentsMargins(0, 0, 0, 0)

        range_date_radio_btn = QRadioButton(range_date_frame)
        radio_button_group.addButton(range_date_radio_btn)
        begin_date_edit = QDateEdit(QDate.currentDate(), range_date_frame)
        end_date_edit = QDateEdit(QDate.currentDate(), range_date_frame)
        begin_date_edit.setDisplayFormat("yyyy")
        end_date_edit.setDisplayFormat("yyyy")
        to_label = QLabel(" to ", range_date_frame)
        to_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        range_date_layout.addWidget(range_date_radio_btn)
        range_date_layout.addWidget(begin_date_edit)
        range_date_layout.addWidget(to_label)
        range_date_layout.addWidget(end_date_edit)

        def on_ok_button_clicked():
            new_selection = [DEFAULT_SPECIAL_OPTION_VALUE]
            checked_button = radio_button_group.checkedButton()
            if checked_button == single_date_radio_btn:
                new_selection = [single_date_edit.date().toString("yyyy")]
            elif checked_button == range_date_radio_btn:
                new_selection = [begin_date_edit.date().toString("yyyy") + "-" + end_date_edit.date().toString("yyyy")]

            line_edit.setText(new_selection[0])
            self.selected_options.__setattr__(option_name.lower(), (is_selected, option_type, option_name, new_selection))
            dialog.close()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        button_box.accepted.connect(on_ok_button_clicked)
        button_box.rejected.connect(lambda: dialog.close())
        button_box.setCenterButtons(True)

        layout.addWidget(default_frame)
        layout.addWidget(single_date_frame)
        layout.addWidget(range_date_frame)
        layout.addWidget(button_box)

        dialog.exec_()

    def on_custom_dir_clicked(self):
        """Handles the signal emitted when the choose custom directory button is clicked"""
        dir_path = GeneralUtils.choose_directory()
        if dir_path: self.custom_dir_edit.setText(dir_path)

    def select_all_vendors(self):
        """Checks all vendors in the vendors list view"""
        for i in range(self.vendor_list_model.rowCount()):
            self.vendor_list_model.item(i).setCheckState(Qt.Checked)

    def deselect_all_vendors(self):
        """Un-checks all vendors in the vendors list view"""
        for i in range(self.vendor_list_model.rowCount()):
            self.vendor_list_model.item(i).setCheckState(Qt.Unchecked)

    def fetch_special_data(self):
        """Fetches reports based on the selected options in the UI"""
        if self.total_processes > 0:
            GeneralUtils.show_message(f"Waiting for pending processes to complete...")
            if self.settings.show_debug_messages: print(f"Waiting for pending processes to complete...")
            return

        if len(self.vendors) == 0:
            GeneralUtils.show_message("Vendor list is empty")
            return

        if self.begin_date > self.end_date:
            GeneralUtils.show_message("\'Begin Date\' is earlier than \'End Date\'")
            return

        self.selected_data = []
        selected_report_types = [self.selected_report_type.value]

        self.is_yearly_fetch = False
        custom_dir = self.custom_dir_edit.text()
        self.save_dir = custom_dir if custom_dir else self.settings.other_directory
        for i in range(self.vendor_list_model.rowCount()):
            if self.vendor_list_model.item(i).checkState() == Qt.Checked:
                request_data = RequestData(self.vendors[i], selected_report_types, self.begin_date, self.end_date,
                                           self.save_dir, self.settings, self.selected_options)
                self.selected_data.append(request_data)
        if len(self.selected_data) == 0:
            GeneralUtils.show_message("No vendor selected")
            return

        self.start_progress_dialog("Fetch Special Reports Progress")
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        concurrent_vendors = self.settings.concurrent_vendors
        while self.started_processes < len(self.selected_data) and self.started_processes < concurrent_vendors:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1


class VendorWorker(QObject):
    """This does all the work for a vendor when fetching reports

    :param worker_id: The ID to identify this worker (vendor_name)
    :param request_data: The request data for this request
    """
    worker_finished_signal = pyqtSignal(str)

    def __init__(self, worker_id: str, request_data: RequestData):
        super().__init__()
        self.worker_id = worker_id
        self.request_data = request_data
        self.vendor = request_data.vendor
        self.target_report_types = request_data.target_report_types
        self.show_debug = request_data.settings.show_debug_messages
        self.concurrent_reports = request_data.settings.concurrent_reports
        self.request_interval = request_data.settings.request_interval
        self.request_timeout = request_data.settings.request_timeout
        self.user_agent = request_data.settings.user_agent
        self.reports_to_process = []
        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0

        self.process_result = ProcessResult(self.vendor)
        self.report_process_results = []
        self.report_workers = {}  # <k = worker_id, v = (ReportWorker, Thread)>
        self.is_cancelling = False

    def work(self):
        """Processes the vendor's requests

        Requests the vendor's supported reports before requesting only the supported reports
        """
        if self.show_debug: print(f"{self.vendor.name}: Fetching supported reports")
        request_query = {}
        if self.vendor.customer_id.strip(): request_query["customer_id"] = self.vendor.customer_id
        if self.vendor.requestor_id.strip(): request_query["requestor_id"] = self.vendor.requestor_id
        if self.vendor.api_key.strip(): request_query["api_key"] = self.vendor.api_key
        if self.vendor.platform.strip(): request_query["platform"] = self.vendor.platform

        request_url = self.vendor.base_url

        try:
            # Some vendors only work if they think a web browser is making the request...
            response = requests.get(request_url, request_query, headers={'User-Agent': self.user_agent},
                                    timeout=self.request_timeout)
            if self.show_debug: print(response.url)
            if response.status_code == 200:
                self.process_response(response)
            else:
                self.process_result.completion_status = CompletionStatus.FAILED
                self.process_result.message = f"Unexpected HTTP status code received: {response.status_code}"
        except requests.exceptions.Timeout as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"Request timed out after {self.request_timeout} second(s)"
            if self.show_debug: print(f"{self.vendor.name}: Request timed out")
        except requests.exceptions.RequestException as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"Request Exception: {e}"
            if self.show_debug: print(f"{self.vendor.name}: Request Exception: {e}")

        if len(self.report_workers) == 0: self.notify_worker_finished()

    def process_response(self, response: requests.Response):
        """Processes the response from a REST request

        Requests the target reports that are supported by the vendor
        """
        if self.is_cancelling:
            self.process_result.message = "Target reports not processed"
            self.process_result.completion_status = CompletionStatus.CANCELLED
            return

        try:
            json_response = response.json()
            exceptions = self.check_for_exception(json_response)
            if len(exceptions) > 0:
                self.process_result.message = exception_models_to_message(exceptions)
                self.process_result.completion_status = CompletionStatus.FAILED
                return

            json_dicts = []
            if type(json_response) is dict:  # This should never be a dict by the standard, but some vendors......
                json_dicts = json_response["Report_Items"] if "Report_Items" in json_response else []  # Report_Items???
                # Some other vendor might implement it in a different way..........................
            elif type(json_response) is list:
                json_dicts = json_response

            if len(json_dicts) == 0:
                raise Exception("JSON is empty")

            supported_report_types = []
            self.reports_to_process = []
            for json_dict in json_dicts:
                supported_report = SupportedReportModel.from_json(json_dict)
                supported_report_types.append(supported_report.report_id)

                if supported_report.report_id in self.target_report_types:
                    self.reports_to_process.append(supported_report.report_id)

            unsupported_report_types = list(set(self.target_report_types) - set(supported_report_types))

            self.process_result.message = "Supported by vendor: "
            self.process_result.message += ", ".join(self.reports_to_process)
            self.process_result.message += "\nUnsupported: "
            self.process_result.message += ", ".join(unsupported_report_types)

            if len(self.reports_to_process) == 0: return

            self.total_processes = len(self.reports_to_process)
            self.started_processes = 0
            while self.started_processes < self.total_processes and self.started_processes < self.concurrent_reports:
                QThread.currentThread().sleep(self.request_interval)  # Avoid spamming vendor's server
                if self.is_cancelling:
                    self.process_result.completion_status = CompletionStatus.CANCELLED
                    return

                self.fetch_report(self.reports_to_process[self.started_processes])
                self.started_processes += 1

        except json.JSONDecodeError as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"JSON Exception: {e}"
            if self.show_debug: print(f"{self.vendor.name}: JSON Exception: {e.msg}")
        except Exception as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = str(e)
            if self.show_debug: print(f"{self.vendor.name}: Exception: {e}")

    def fetch_report(self, report_type: str):
        """Initiates the process to fetch a report

        :param report_type: The target report type
        """
        worker_id = report_type
        if worker_id in self.report_workers: return  # Avoid fetching a report twice, app will crash!!

        report_worker = ReportWorker(worker_id, report_type, self.request_data)
        report_worker.worker_finished_signal.connect(self.on_report_worker_finished)
        report_thread = QThread()
        self.report_workers[worker_id] = report_worker, report_thread
        report_worker.moveToThread(report_thread)
        report_thread.started.connect(report_worker.work)
        report_thread.finished.connect(report_thread.deleteLater)

        report_thread.start()

    def check_for_exception(self, json_response) -> list:
        """Checks a JSON response for exception models

        :param json_response: The JSON response to be processed
        """
        exceptions = []

        if type(json_response) is dict:
            if "Exception" in json_response:
                exceptions.append(ExceptionModel.from_json(json_response["Exception"]))
                # raise Exception(f"Code: {exception.code}, Message: {exception.message}")

            code = int(json_response["Code"]) if "Code" in json_response else ""
            message = json_response["Message"] if "Message" in json_response else ""
            data = json_response["Data"] if "Data" in json_response else ""
            severity = json_response["Severity"] if "Severity" in json_response else ""
            if code:
                exceptions.append(ExceptionModel(code, message, severity, data))

        elif type(json_response) is list:
            for json_dict in json_response:
                exception = ExceptionModel.from_json(json_dict)
                if exception.code:
                    exceptions.append(exception)

        return exceptions

    def notify_worker_finished(self):
        """Notifies any listeners that this worker has finished"""
        self.worker_finished_signal.emit(self.vendor.name)

    def on_report_worker_finished(self, worker_id: str):
        """Handles the signal emmited when a report worker has finished

        :param worker_id: The report worker's worker id
        """
        self.completed_processes += 1

        thread: QThread
        worker: ReportWorker
        worker, thread = self.report_workers[worker_id]

        self.report_process_results.append(worker.process_result)
        worker.deleteLater()
        thread.quit()
        thread.wait()
        self.report_workers.pop(worker_id, None)

        if self.started_processes < self.total_processes and not self.is_cancelling:
            QThread.currentThread().sleep(self.request_interval)  # Avoid spamming vendor's server
            self.fetch_report(self.reports_to_process[self.started_processes])
            self.started_processes += 1

        if len(self.report_workers) == 0: self.notify_worker_finished()

    def set_cancelling(self):
        """Sets the worker to a cancelling state"""
        self.is_cancelling = True


class ReportWorker(QObject):
    """This does all the work for a report

    :param worker_id: The ID to identify this worker (vendor_name-report_type)
    :param report_type: The report type to be processed
    :param request_data: The request data for this request
    """
    worker_finished_signal = pyqtSignal(str)

    def __init__(self, worker_id: str, report_type: str, request_data: RequestData):
        super().__init__()
        self.worker_id = worker_id
        self.report_type = report_type
        self.vendor = request_data.vendor
        self.begin_date = request_data.begin_date
        self.end_date = request_data.end_date
        self.show_debug = request_data.settings.show_debug_messages
        self.request_timeout = request_data.settings.request_timeout
        self.user_agent = request_data.settings.user_agent
        self.save_dir = request_data.save_location
        self.special_options = request_data.special_options

        self.is_yearly = self.save_dir == request_data.settings.yearly_directory
        self.is_special = self.special_options is not None
        self.is_master = self.report_type in MASTER_REPORTS

        self.process_result = ProcessResult(self.vendor, self.report_type)
        self.retried_request = False

    def work(self):
        """Processes the report request"""
        if self.show_debug: print(f"{self.vendor.name}-{self.report_type}: Fetching Report")

        self.make_request()

        if self.show_debug: print(f"{self.vendor.name}-{self.report_type}: Done")
        self.notify_worker_finished()

    def make_request(self):
        """Sends the request fetch a report"""
        request_query = {}
        if self.vendor.customer_id.strip(): request_query["customer_id"] = self.vendor.customer_id
        if self.vendor.requestor_id.strip(): request_query["requestor_id"] = self.vendor.requestor_id
        if self.vendor.api_key.strip(): request_query["api_key"] = self.vendor.api_key
        if self.vendor.platform.strip(): request_query["platform"] = self.vendor.platform
        request_query["begin_date"] = self.begin_date.toString("yyyy-MM")
        request_query["end_date"] = self.end_date.toString("yyyy-MM")

        attributes_to_show = ""
        if self.is_special:
            attr_count = 0
            special_options_dict = self.special_options.__dict__
            for option in special_options_dict:
                value = special_options_dict[option]
                is_selected, option_type, option_name, option_parameters = value

                if is_selected:
                    if option_type == SpecialOptionType.AP or option_type == SpecialOptionType.ADP\
                            or option_type == SpecialOptionType.POS:
                        if option_parameters[0] != DEFAULT_SPECIAL_OPTION_VALUE:
                            request_query[option] = "|".join(option_parameters)

                    elif option_type == SpecialOptionType.POB:
                        request_query[option] = "True"

                    if option_type == SpecialOptionType.AP or option_type == SpecialOptionType.ADP\
                            or option_type == SpecialOptionType.AO:
                        if attr_count == 0:
                            attributes_to_show += option_name
                            attr_count += 1
                        elif attr_count > 0:
                            attributes_to_show += f"|{option_name}"
                            attr_count += 1
        elif self.is_yearly and self.is_master:
            major_report_type = GeneralUtils.get_major_report_type(self.report_type)
            if major_report_type == MajorReportType.PLATFORM:
                attributes_to_show = "|".join(PLATFORM_REPORTS_ATTRIBUTES)
            elif major_report_type == MajorReportType.DATABASE:
                attributes_to_show = "|".join(DATABASE_REPORTS_ATTRIBUTES)
            elif major_report_type == MajorReportType.TITLE:
                attributes_to_show = "|".join(TITLE_REPORTS_ATTRIBUTES)
            elif major_report_type == MajorReportType.ITEM:
                attributes_to_show = "|".join(ITEM_REPORTS_ATTRIBUTES)
                request_query["include_parent_details"] = True
                request_query["include_component_details"] = True

        if attributes_to_show: request_query["attributes_to_show"] = attributes_to_show

        request_url = f"{self.vendor.base_url}/{self.report_type.lower()}"

        try:
            # Some vendors only work if they think a web browser is making the request...
            response = requests.get(request_url, request_query, headers={'User-Agent': self.user_agent},
                                    timeout=self.request_timeout)
            if self.show_debug: print(response.url)
            if response.status_code == 200:
                self.process_response(response)
            else:
                self.process_result.completion_status = CompletionStatus.FAILED
                self.process_result.message = f"Unexpected HTTP status code received: {response.status_code}"
        except requests.exceptions.Timeout as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"Request timed out after {self.request_timeout} second(s)"
            if self.show_debug: print(f"{self.vendor.name}: Request timed out")
        except requests.exceptions.RequestException as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"Request Exception: {e}"
            if self.show_debug: print(
                f"{self.vendor.name}-{self.report_type}: Request Exception: {e}")

    def process_response(self, response: requests.Response):
        """Processes the response from a request

        Converts the receoved JSON to a SUSHI Report Model

        :param response: The received response
        """
        try:
            json_string = response.text
            if self.is_yearly: self.save_json_file(json_string)

            json_dict = json.loads(json_string)
            report_model = ReportModel.from_json(json_dict)
            self.process_report_model(report_model)
            if len(report_model.report_items) > 0 or len(report_model.exceptions) > 0:
                self.process_result.message = exception_models_to_message(report_model.exceptions)
            else:
                self.process_result.message = "Report items not received. No exception received."
        except json.JSONDecodeError as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            if e.msg == "Expecting value":
                self.process_result.message = f"Vendor did not return any data"
            else:
                self.process_result.message = f"JSON Exception: {e.msg}"
            if self.show_debug: print(
                f"{self.vendor.name}-{self.report_type}: JSON Exception: {e.msg}")
        except RetryLaterException as e:
            if not self.retried_request:
                if self.show_debug:
                    print(f"{self.vendor.name}-{self.report_type}: Retry Later Exception: {e}")
                    print(f"{self.vendor.name}-{self.report_type}: Retrying in {RETRY_WAIT_TIME} seconds...")
                QThread.currentThread().sleep(RETRY_WAIT_TIME)  # Wait some time before retrying request
                self.retried_request = True
                self.make_request()
            else:
                self.process_result.message = "Retry later exception received"
                message = exception_models_to_message(e.exceptions)
                if message: self.process_result.message += "\n\n" + message
                self.process_result.completion_status = CompletionStatus.FAILED
                self.process_result.retry = True
                if self.show_debug: print(
                    f"{self.vendor.name}-{self.report_type}: Retry Later Exception: {e}")
        except ReportHeaderMissingException as e:
            self.process_result.message = "Report_Header not received, no file was created"
            message = exception_models_to_message(e.exceptions)
            if message: self.process_result.message += "\n\n" + message
            self.process_result.completion_status = CompletionStatus.FAILED
            if self.show_debug: print(
                f"{self.vendor.name}-{self.report_type}: Report Header Missing Exception: {e}")
        except UnacceptableCodeException as e:
            self.process_result.message = "Unsupported exception code received"
            message = exception_models_to_message(e.exceptions)
            if message: self.process_result.message += "\n\n" + message
            self.process_result.completion_status = CompletionStatus.FAILED
            if self.show_debug: print(
                f"{self.vendor.name}-{self.report_type}: Unsupported Code Exception: {e}")
        except Exception as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = str(e)
            if self.show_debug: print(f"{self.vendor.name}-{self.report_type}: Exception: {e}")

    def process_report_model(self, report_model: ReportModel):
        """Processes the report model into a TSV report

        :param report_model: The report model
        """
        report_type = report_model.report_header.report_id
        major_report_type = report_model.report_header.major_report_type
        report_items = report_model.report_items
        report_rows = []
        file_dir = f"{self.save_dir}{self.begin_date.toString('yyyy')}/{self.vendor.name}/"
        file_name = f"{self.begin_date.toString('yyyy')}_{self.vendor.name}_{report_type}.tsv"
        file_path = f"{file_dir}{file_name}"

        if self.show_debug: print(f"{self.vendor.name}-{self.report_type}: Processing report")

        for report_item in report_items:
            metric_row_dict = {}  # <k = metric_type, v = ReportRow> Some metric_types have a list of components
            # Some Item report metric_types have a list of components
            components = []  # list({component_values_as_dict})

            performance: PerformanceModel
            for performance in report_item.performances:
                begin_month = QDate.fromString(performance.period.begin_date, "yyyy-MM-dd").toString("MMM-yyyy")

                instance: InstanceModel
                for instance in performance.instances:
                    metric_type = instance.metric_type
                    if metric_type not in metric_row_dict:
                        metric_row = ReportRow(self.begin_date, self.end_date)
                        metric_row.metric_type = metric_type

                        metric_row_dict[metric_type] = metric_row
                    else:
                        metric_row = metric_row_dict[metric_type]

                    if major_report_type == MajorReportType.PLATFORM:
                        report_item: PlatformReportItemModel
                        if report_item.platform: metric_row.platform = report_item.platform
                        if report_item.data_type: metric_row.data_type = report_item.data_type
                        if report_item.access_method: metric_row.access_method = report_item.access_method

                    elif major_report_type == MajorReportType.DATABASE:
                        report_item: DatabaseReportItemModel
                        if report_item.database: metric_row.database = report_item.database
                        if report_item.publisher: metric_row.publisher = report_item.publisher
                        if report_item.platform: metric_row.platform = report_item.platform
                        if report_item.data_type: metric_row.data_type = report_item.data_type
                        if report_item.access_method: metric_row.access_method = report_item.access_method

                        pub_id_str = ""
                        for pub_id in report_item.publisher_ids:
                            pub_id_str += f"{pub_id.item_type}:{pub_id.value}; "
                        if pub_id_str: metric_row.publisher_id = pub_id_str

                        for item_id in report_item.item_ids:
                            if item_id.item_type == "Proprietary" or item_id.item_type == "Proprietary_ID":
                                metric_row.proprietary_id = item_id.value

                    elif major_report_type == MajorReportType.TITLE:
                        report_item: TitleReportItemModel
                        if report_item.title: metric_row.title = report_item.title
                        if report_item.publisher: metric_row.publisher = report_item.publisher
                        if report_item.platform: metric_row.platform = report_item.platform
                        if report_item.data_type: metric_row.data_type = report_item.data_type
                        if report_item.section_type: metric_row.section_type = report_item.section_type
                        if report_item.yop: metric_row.yop = report_item.yop
                        if report_item.access_type: metric_row.access_type = report_item.access_type
                        if report_item.access_method: metric_row.access_method = report_item.access_method

                        pub_id_str = ""
                        for pub_id in report_item.publisher_ids:
                            pub_id_str += f"{pub_id.item_type}:{pub_id.value}; "
                        if pub_id_str: metric_row.publisher_id = pub_id_str

                        item_id: TypeValueModel
                        for item_id in report_item.item_ids:
                            item_type = item_id.item_type

                            if item_type == "DOI":
                                metric_row.doi = item_id.value
                            elif item_type == "Proprietary" or item_type == "Proprietary_ID":
                                metric_row.proprietary_id = item_id.value
                            elif item_type == "ISBN":
                                metric_row.isbn = item_id.value
                            elif item_type == "Print_ISSN":
                                metric_row.print_issn = item_id.value
                            elif item_type == "Online_ISSN":
                                metric_row.online_issn = item_id.value
                            elif item_type == "Linking_ISSN":
                                metric_row.linking_issn = item_id.value
                            elif item_type == "URI":
                                metric_row.uri = item_id.value

                    elif major_report_type == MajorReportType.ITEM:
                        report_item: ItemReportItemModel
                        if report_item.item: metric_row.item = report_item.item
                        if report_item.publisher: metric_row.publisher = report_item.publisher
                        if report_item.platform: metric_row.platform = report_item.platform
                        if report_item.data_type: metric_row.data_type = report_item.data_type
                        if report_item.yop: metric_row.yop = report_item.yop
                        if report_item.access_type: metric_row.access_type = report_item.access_type
                        if report_item.access_method: metric_row.access_method = report_item.access_method

                        # Publisher ID
                        pub_id_str = ""
                        for pub_id in report_item.publisher_ids:
                            pub_id_str += f"{pub_id.item_type}:{pub_id.value}; "
                        if pub_id_str: metric_row.publisher_id = pub_id_str

                        # Authors
                        authors_str = ""
                        item_contributor: ItemContributorModel
                        for item_contributor in report_item.item_contributors:
                            if item_contributor.item_type == "Author":
                                authors_str += f"{item_contributor.name}"
                                if item_contributor.identifier:
                                    authors_str += f" ({item_contributor.identifier})"
                                authors_str += "; "
                        if authors_str: metric_row.authors = authors_str.rstrip("; ")

                        # Publication date
                        item_date: TypeValueModel
                        for item_date in report_item.item_dates:
                            if item_date.item_type == "Publication_Date":
                                metric_row.publication_date = item_date.value

                        # Article version
                        item_attribute: TypeValueModel
                        for item_attribute in report_item.item_attributes:
                            if item_attribute.item_type == "Article_Version":
                                metric_row.article_version = item_attribute.value

                        # Base IDs
                        item_id: TypeValueModel
                        for item_id in report_item.item_ids:
                            item_type = item_id.item_type

                            if item_type == "DOI":
                                metric_row.doi = item_id.value
                            elif item_type == "Proprietary" or item_type == "Proprietary_ID":
                                metric_row.proprietary_id = item_id.value
                            elif item_type == "ISBN":
                                metric_row.isbn = item_id.value
                            elif item_type == "Print_ISSN":
                                metric_row.print_issn = item_id.value
                            elif item_type == "Online_ISSN":
                                metric_row.online_issn = item_id.value
                            elif item_type == "Linking_ISSN":
                                metric_row.linking_issn = item_id.value
                            elif item_type == "URI":
                                metric_row.uri = item_id.value

                        # Parent
                        if report_item.item_parent is not None:
                            item_parent: ItemParentModel
                            item_parent = report_item.item_parent
                            if item_parent.item_name: metric_row.parent_title = item_parent.item_name
                            if item_parent.data_type: metric_row.parent_data_type = item_parent.data_type

                            # Authors
                            authors_str = ""
                            item_contributor: ItemContributorModel
                            for item_contributor in report_item.item_contributors:
                                if item_contributor.item_type == "Author":
                                    authors_str += f"{item_contributor.name}"
                                    if item_contributor.identifier:
                                        authors_str += f" ({item_contributor.identifier})"
                                    authors_str += "; "
                            authors_str.rstrip("; ")
                            if authors_str: metric_row.authors = authors_str

                            # Publication date
                            item_date: TypeValueModel
                            for item_date in item_parent.item_dates:
                                if item_date.item_type == "Publication_Date" or item_date.item_type == "Pub_Date":
                                    metric_row.parent_publication_date = item_date.value

                            # Article version
                            item_attribute: TypeValueModel
                            for item_attribute in item_parent.item_attributes:
                                if item_attribute.item_type == "Article_Version":
                                    metric_row.parent_article_version = item_attribute.value

                            # Parent IDs
                            item_id: TypeValueModel
                            for item_id in item_parent.item_ids:
                                item_type = item_id.item_type

                                if item_type == "DOI":
                                    metric_row.parent_doi = item_id.value
                                elif item_type == "Proprietary" or item_type == "Proprietary_ID":
                                    metric_row.parent_proprietary_id = item_id.value
                                elif item_type == "ISBN":
                                    metric_row.parent_isbn = item_id.value
                                elif item_type == "Print_ISSN":
                                    metric_row.parent_print_issn = item_id.value
                                elif item_type == "Online_ISSN":
                                    metric_row.parent_online_issn = item_id.value
                                elif item_type == "URI":
                                    metric_row.parent_uri = item_id.value

                    else:
                        if self.show_debug: print(
                            f"{self.vendor.name}-{self.report_type}: Unexpected report type")

                    month_counts = metric_row.month_counts
                    month_counts[begin_month] += instance.count

                    metric_row.total_count += instance.count

            if major_report_type == MajorReportType.ITEM:
                # Item Components
                item_component: ItemComponentModel
                for item_component in report_item.item_components:
                    component_dict = {
                        "component_title": "",
                        "component_authors": "",
                        "component_publication_date": "",
                        "component_data_type": "",
                        "component_doi": "",
                        "component_proprietary_id": "",
                        "component_isbn": "",
                        "component_print_issn": "",
                        "component_online_issn": "",
                        "component_uri": ""
                    }

                    if item_component.item_name: component_dict["component_title"] = item_component.item_name
                    if item_component.data_type: component_dict["component_data_type"] = item_component.data_type

                    # Authors
                    authors_str = ""
                    item_contributor: ItemContributorModel
                    for item_contributor in item_component.item_contributors:
                        if item_contributor.item_type == "Author":
                            authors_str += f"{item_contributor.name}"
                            if item_contributor.identifier:
                                authors_str += f" ({item_contributor.identifier})"
                            authors_str += "; "
                    authors_str.rstrip("; ")
                    if authors_str: component_dict["component_authors"] = authors_str

                    # Publication date
                    item_date: TypeValueModel
                    for item_date in item_component.item_dates:
                        if item_date.item_type == "Publication_Date" or item_date.item_type == "Pub_Date":
                            component_dict["component_publication_date"] = item_date.value

                    # Component IDs
                    item_id: TypeValueModel
                    for item_id in item_component.item_ids:
                        item_type = item_id.item_type

                        if item_type == "DOI":
                            component_dict["component_doi"] = item_id.value
                        elif item_type == "Proprietary" or item_type == "Proprietary_ID":
                            component_dict["component_proprietary_id"] = item_id.value
                        elif item_type == "ISBN":
                            component_dict["component_isbn"] = item_id.value
                        elif item_type == "Print_ISSN":
                            component_dict["component_print_issn"] = item_id.value
                        elif item_type == "Online_ISSN":
                            component_dict["component_online_issn"] = item_id.value
                        elif item_type == "URI":
                            component_dict["component_uri"] = item_id.value

                    components.append(component_dict)

            for metric_type in metric_row_dict:
                metric_row = metric_row_dict[metric_type]

                if major_report_type == MajorReportType.ITEM:
                    if len(components) > 0 and \
                            (metric_type == "Total_Item_Investigations" or metric_type == "Total_Item_Requests"):
                        for component in components:
                            row = copy.copy(metric_row)
                            row.component_title = component["component_title"]
                            row.component_authors = component["component_authors"]
                            row.component_publication_date = component["component_publication_date"]
                            row.component_data_type = component["component_data_type"]
                            row.component_doi = component["component_doi"]
                            row.component_proprietary_id = component["component_proprietary_id"]
                            row.component_isbn = component["component_isbn"]
                            row.component_print_issn = component["component_print_issn"]
                            row.component_online_issn = component["component_online_issn"]
                            row.component_uri = component["component_uri"]
                            report_rows.append(row)
                    else:
                        report_rows.append(metric_row)
                else:
                    report_rows.append(metric_row)

        report_rows = self.sort_rows(report_rows, major_report_type)
        self.save_tsv_files(report_model.report_header, report_rows)

    def sort_rows(self, report_rows: list, major_report_type: MajorReportType) -> list:
        """Sorts the rows of the report

        :param report_rows: The report's rows
        :param major_report_type: The major report type of this report type
        """
        if major_report_type == MajorReportType.PLATFORM:
            return sorted(report_rows, key=lambda row: row.platform.lower())
        elif major_report_type == MajorReportType.DATABASE:
            return sorted(report_rows, key=lambda row: row.database.lower())
        elif major_report_type == MajorReportType.TITLE:
            return sorted(report_rows, key=lambda row: (row.title.lower(), row.yop))
        elif major_report_type == MajorReportType.ITEM:
            return sorted(report_rows, key=lambda row: row.item.lower())

    def save_tsv_files(self, report_header, report_rows: list):
        """Saves the TSV file in the target directories

        :param report_header: The SUSHI report header model
        :param report_rows: The report's rows
        """
        report_type = report_header.report_id
        major_report_type = report_header.major_report_type

        if self.is_yearly:
            file_dir = GeneralUtils.get_yearly_file_dir(self.save_dir, self.vendor.name, self.begin_date)
            file_name = GeneralUtils.get_yearly_file_name(self.vendor.name, self.report_type, self.begin_date)
        elif self.is_special:
            file_dir = GeneralUtils.get_special_file_dir(self.save_dir, self.vendor.name)
            file_name = GeneralUtils.get_special_file_name(self.vendor.name, self.report_type, self.begin_date,
                                                           self.end_date)
        else:
            file_dir = GeneralUtils.get_other_file_dir(self.save_dir, self.vendor.name)
            file_name = GeneralUtils.get_other_file_name(self.vendor.name, self.report_type, self.begin_date,
                                                         self.end_date)

        # Save user tsv file
        if not path.isdir(file_dir):
            makedirs(file_dir)

        file_path = f"{file_dir}{file_name}"
        file = open(file_path, 'w', encoding="utf-8", newline='')
        if self.is_yearly and self.is_master:
            self.add_report_header_to_file(report_header, file, False)
        else:
            self.add_report_header_to_file(report_header, file, True)

        if not self.add_report_rows_to_file(report_type, report_rows, file, False):
            self.process_result.completion_status = CompletionStatus.WARNING

        file.close()
        self.process_result.file_name = file_name
        self.process_result.file_dir = file_dir
        self.process_result.file_path = file_path
        self.process_result.year = self.begin_date.toString('yyyy')

        # Save protected tsv file
        if self.is_yearly:
            protected_file_dir = GeneralUtils.get_yearly_file_dir(PROTECTED_DATABASE_FILE_DIR, self.vendor.name,
                                                                  self.begin_date)
            if not path.isdir(protected_file_dir):
                makedirs(protected_file_dir)
                if platform.system() == "Windows":
                    ctypes.windll.kernel32.SetFileAttributesW(PROTECTED_DATABASE_FILE_DIR, 2)  # Hide folder

            protected_file_path = f"{protected_file_dir}{file_name}"
            protected_file = open(protected_file_path, 'w', encoding="utf-8", newline='')
            self.add_report_header_to_file(report_header, protected_file, True)
            self.add_report_rows_to_file(report_type, report_rows, protected_file, True)

            protected_file.close()
            self.process_result.protected_file_path = protected_file_path

    def add_report_header_to_file(self, report_header: ReportHeaderModel, file, include_attributes: bool):
        """Adds the report header to a TSV file

        :param report_header: The report header model
        :param file: The TSV file to write to
        :param include_attributes: Include the Report_Attributes value
        """
        tsv_writer = csv.writer(file, delimiter='\t')
        tsv_writer.writerow(["Report_Name", report_header.report_name])
        tsv_writer.writerow(["Report_ID", report_header.report_id])
        tsv_writer.writerow(["Release", report_header.release])
        tsv_writer.writerow(["Institution_Name", report_header.institution_name])

        institution_ids_str = ""
        for institution_id in report_header.institution_ids:
            institution_ids_str += f"{institution_id.value}; "
        tsv_writer.writerow(["Institution_ID", institution_ids_str.rstrip("; ")])

        metric_types_str = ""
        reporting_period_str = ""
        report_filters_str = ""
        for report_filter in report_header.report_filters:
            if report_filter.name == "Metric_Type":
                metric_types_str += f"{report_filter.value}; "
            elif report_filter.name == "Begin_Date" or report_filter.name == "End_Date":
                reporting_period_str += f"{report_filter.name}={report_filter.value}; "
            else:
                report_filters_str += f"{report_filter.name}={report_filter.value}; "
        tsv_writer.writerow(["Metric_Types", metric_types_str.replace("|", "; ").rstrip("; ")])
        tsv_writer.writerow(["Report_Filters", report_filters_str.rstrip("; ")])

        report_attributes_str = ""
        if include_attributes:
            for report_attribute in report_header.report_attributes:
                report_attributes_str += f"{report_attribute.name}={report_attribute.value}; "
        tsv_writer.writerow(["Report_Attributes", report_attributes_str.rstrip("; ")])

        exceptions_str = ""
        for exception in report_header.exceptions:
            exceptions_str += f"{exception.code}: {exception.message} ({exception.data}); "
        tsv_writer.writerow(["Exceptions", exceptions_str.rstrip("; ")])

        tsv_writer.writerow(["Reporting_Period", reporting_period_str.rstrip("; ")])
        tsv_writer.writerow(["Created", report_header.created])
        tsv_writer.writerow(["Created_By", report_header.created_by])
        tsv_writer.writerow([])

    def add_report_rows_to_file(self, report_type: str, report_rows: list, file, include_all_attributes: bool) -> bool:
        """Adds the report's rows to a TSV file

        :param report_type: The report type
        :param report_rows: The report's rows
        :param file: The TSV file to write to
        :param include_all_attributes: Option to include all possible attributes for this report type to the report
        """
        column_names = []
        row_dicts = []

        if report_type == "PR":
            column_names += ["Platform"]
            if self.is_special:
                special_options_dict = self.special_options.__dict__
                if special_options_dict["data_type"][0]: column_names.append("Data_Type")
                if special_options_dict["access_method"][0]: column_names.append("Access_Method")
            elif include_all_attributes:
                column_names.append("Data_Type")
                column_names.append("Access_Method")

            row: ReportRow
            for row in report_rows:
                row_dict = {"Platform": row.platform}
                if self.is_special:
                    special_options_dict = self.special_options.__dict__
                    if special_options_dict["data_type"][0]: row_dict["Data_Type"] = row.data_type
                    if special_options_dict["access_method"][0]: row_dict["Access_Method"] = row.access_method

                    if not special_options_dict["exclude_monthly_details"][0]:
                        row_dict.update(row.month_counts)
                else:
                    if include_all_attributes:
                        row_dict["Data_Type"] = row.data_type
                        row_dict["Access_Method"] = row.access_method
                    row_dict.update(row.month_counts)

                row_dict.update({"Metric_Type": row.metric_type,
                                 "Reporting_Period_Total": row.total_count})
                row_dicts.append(row_dict)

        elif report_type == "PR_P1":
            column_names += ["Platform"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Platform": row.platform,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "DR":
            column_names += ["Database", "Publisher", "Publisher_ID", "Platform", "Proprietary_ID"]
            if self.is_special:
                special_options_dict = self.special_options.__dict__
                if special_options_dict["data_type"][0]: column_names.append("Data_Type")
                if special_options_dict["access_method"][0]: column_names.append("Access_Method")
            elif include_all_attributes:
                column_names.append("Data_Type")
                column_names.append("Access_Method")

            row: ReportRow
            for row in report_rows:
                row_dict = {"Database": row.database,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "Proprietary_ID": row.proprietary_id}

                if self.is_special:
                    special_options_dict = self.special_options.__dict__
                    if special_options_dict["data_type"][0]: row_dict["Data_Type"] = row.data_type
                    if special_options_dict["access_method"][0]: row_dict["Access_Method"] = row.access_method

                    if not special_options_dict["exclude_monthly_details"][0]:
                        row_dict.update(row.month_counts)
                else:
                    if include_all_attributes:
                        row_dict["Data_Type"] = row.data_type
                        row_dict["Access_Method"] = row.access_method
                    row_dict.update(row.month_counts)

                row_dict.update({"Metric_Type": row.metric_type,
                                 "Reporting_Period_Total": row.total_count})
                row_dicts.append(row_dict)

        elif report_type == "DR_D1" or report_type == "DR_D2":
            column_names += ["Database", "Publisher", "Publisher_ID", "Platform", "Proprietary_ID"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Database": row.database,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "Proprietary_ID": row.proprietary_id,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Proprietary_ID", "ISBN",
                             "Print_ISSN", "Online_ISSN", "URI"]
            if self.is_special:
                special_options_dict = self.special_options.__dict__
                if special_options_dict["data_type"][0]: column_names.append("Data_Type")
                if special_options_dict["section_type"][0]: column_names.append("Section_Type")
                if special_options_dict["yop"][0]: column_names.append("YOP")
                if special_options_dict["access_type"][0]: column_names.append("Access_Type")
                if special_options_dict["access_method"][0]: column_names.append("Access_Method")
            elif include_all_attributes:
                column_names.append("Data_Type")
                column_names.append("Section_Type")
                column_names.append("YOP")
                column_names.append("Access_Type")
                column_names.append("Access_Method")

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "ISBN": row.isbn,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "URI": row.uri}

                if self.is_special:
                    special_options_dict = self.special_options.__dict__
                    if special_options_dict["data_type"][0]: row_dict["Data_Type"] = row.data_type
                    if special_options_dict["section_type"][0]: row_dict["Section_Type"] = row.section_type
                    if special_options_dict["yop"][0]: row_dict["YOP"] = row.yop
                    if special_options_dict["access_type"][0]: row_dict["Access_Type"] = row.access_type
                    if special_options_dict["access_method"][0]: row_dict["Access_Method"] = row.access_method

                    if not special_options_dict["exclude_monthly_details"][0]:
                        row_dict.update(row.month_counts)
                else:
                    if include_all_attributes:
                        row_dict["Data_Type"] = row.data_type
                        row_dict["Section_Type"] = row.section_type
                        row_dict["YOP"] = row.yop
                        row_dict["Access_Type"] = row.access_type
                        row_dict["Access_Method"] = row.access_method
                    row_dict.update(row.month_counts)

                row_dict.update({"Metric_Type": row.metric_type,
                                 "Reporting_Period_Total": row.total_count})
                row_dicts.append(row_dict)

        elif report_type == "TR_B1" or report_type == "TR_B2":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Proprietary_ID", "ISBN",
                             "Print_ISSN", "Online_ISSN", "URI", "YOP"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "ISBN": row.isbn,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "URI": row.uri,
                            "YOP": row.yop,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_B3":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Proprietary_ID", "ISBN",
                             "Print_ISSN", "Online_ISSN", "URI", "YOP", "Access_Type"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "ISBN": row.isbn,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "URI": row.uri,
                            "YOP": row.yop,
                            "Access_Type": row.access_type,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_J1" or report_type == "TR_J2":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Proprietary_ID", "Print_ISSN",
                             "Online_ISSN", "URI"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "URI": row.uri,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_J3":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Proprietary_ID", "Print_ISSN",
                             "Online_ISSN", "URI", "Access_Type"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "URI": row.uri,
                            "Access_Type": row.access_type,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_J4":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Proprietary_ID", "Print_ISSN",
                             "Online_ISSN", "URI", "YOP"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "URI": row.uri,
                            "YOP": row.yop,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "IR":
            column_names += ["Item", "Publisher", "Publisher_ID", "Platform"]
            if self.is_special:
                special_options_dict = self.special_options.__dict__
                if special_options_dict["authors"][0]: column_names.append("Authors")
                if special_options_dict["publication_date"][0]: column_names.append("Publication_Date")
                if special_options_dict["article_version"][0]: column_names.append("Article_version")
            elif include_all_attributes:
                column_names.append("Authors")
                column_names.append("Publication_Date")
                column_names.append("Article_version")
            column_names += ["DOI", "Proprietary_ID", "ISBN", "Print_ISSN", "Online_ISSN", "URI"]
            if self.is_special:
                special_options_dict = self.special_options.__dict__
                if special_options_dict["include_parent_details"][0]:
                    column_names += ["Parent_Title", "Parent_Authors", "Parent_Publication_Date",
                                     "Parent_Article_Version", "Parent_Data_Type", "Parent_DOI",
                                     "Parent_Proprietary_ID", "Parent_ISBN", "Parent_Print_ISSN", "Parent_Online_ISSN",
                                     "Parent_URI"]
                if special_options_dict["include_component_details"][0]:
                    column_names += ["Component_Title", "Component_Authors", "Component_Publication_Date",
                                     "Component_Data_Type", "Component_DOI", "Component_Proprietary_ID",
                                     "Component_ISBN", "Component_Print_ISSN", "Component_Online_ISSN", "Component_URI"]
                if special_options_dict["data_type"][0]: column_names.append("Data_Type")
                if special_options_dict["yop"][0]: column_names.append("YOP")
                if special_options_dict["access_type"][0]: column_names.append("Access_Type")
                if special_options_dict["access_method"][0]: column_names.append("Access_Method")
            elif include_all_attributes:
                column_names += ["Parent_Title", "Parent_Authors", "Parent_Publication_Date", "Parent_Article_Version",
                                 "Parent_Data_Type", "Parent_DOI", "Parent_Proprietary_ID", "Parent_ISBN",
                                 "Parent_Print_ISSN", "Parent_Online_ISSN", "Parent_URI"]
                column_names += ["Component_Title", "Component_Authors", "Component_Publication_Date",
                                 "Component_Data_Type", "Component_DOI", "Component_Proprietary_ID", "Component_ISBN",
                                 "Component_Print_ISSN", "Component_Online_ISSN", "Component_URI"]
                column_names.append("Data_Type")
                column_names.append("YOP")
                column_names.append("Access_Type")
                column_names.append("Access_Method")

            row: ReportRow
            for row in report_rows:
                row_dict = {"Item": row.item,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "ISBN": row.isbn,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "URI": row.uri}

                if self.is_special:
                    special_options_dict = self.special_options.__dict__
                    if special_options_dict["authors"][0]: row_dict["Authors"] = row.authors
                    if special_options_dict["publication_date"][0]: row_dict["Publication_Date"] = row.publication_date
                    if special_options_dict["article_version"][0]: row_dict["Article_version"] = row.article_version
                    if special_options_dict["include_parent_details"][0]:
                        row_dict.update({"Parent_Title": row.parent_title,
                                         "Parent_Authors": row.parent_authors,
                                         "Parent_Publication_Date": row.parent_publication_date,
                                         "Parent_Article_Version": row.parent_article_version,
                                         "Parent_Data_Type": row.parent_data_type,
                                         "Parent_DOI": row.parent_doi,
                                         "Parent_Proprietary_ID": row.parent_proprietary_id,
                                         "Parent_ISBN": row.parent_isbn,
                                         "Parent_Print_ISSN": row.parent_print_issn,
                                         "Parent_Online_ISSN": row.parent_online_issn,
                                         "Parent_URI": row.parent_uri})
                    if special_options_dict["include_component_details"][0]:
                        row_dict.update({"Component_Title": row.component_title,
                                         "Component_Authors": row.component_authors,
                                         "Component_Publication_Date": row.component_publication_date,
                                         "Component_Data_Type": row.component_data_type,
                                         "Component_DOI": row.component_doi,
                                         "Component_Proprietary_ID": row.component_proprietary_id,
                                         "Component_ISBN": row.component_isbn,
                                         "Component_Print_ISSN": row.component_print_issn,
                                         "Component_Online_ISSN": row.component_online_issn,
                                         "Component_URI": row.component_uri})
                    if special_options_dict["data_type"][0]: row_dict["Data_Type"] = row.data_type
                    if special_options_dict["yop"][0]: row_dict["YOP"] = row.yop
                    if special_options_dict["access_type"][0]: row_dict["Access_Type"] = row.access_type
                    if special_options_dict["access_method"][0]: row_dict["Access_Method"] = row.access_method

                    if not special_options_dict["exclude_monthly_details"][0]:
                        row_dict.update(row.month_counts)
                else:
                    if include_all_attributes:
                        row_dict["Authors"] = row.authors
                        row_dict["Publication_Date"] = row.publication_date
                        row_dict["Article_version"] = row.article_version
                        row_dict.update({"Parent_Title": row.parent_title,
                                         "Parent_Authors": row.parent_authors,
                                         "Parent_Publication_Date": row.parent_publication_date,
                                         "Parent_Article_Version": row.parent_article_version,
                                         "Parent_Data_Type": row.parent_data_type,
                                         "Parent_DOI": row.parent_doi,
                                         "Parent_Proprietary_ID": row.parent_proprietary_id,
                                         "Parent_ISBN": row.parent_isbn,
                                         "Parent_Print_ISSN": row.parent_print_issn,
                                         "Parent_Online_ISSN": row.parent_online_issn,
                                         "Parent_URI": row.parent_uri})
                        row_dict.update({"Component_Title": row.component_title,
                                         "Component_Authors": row.component_authors,
                                         "Component_Publication_Date": row.component_publication_date,
                                         "Component_Data_Type": row.component_data_type,
                                         "Component_DOI": row.component_doi,
                                         "Component_Proprietary_ID": row.component_proprietary_id,
                                         "Component_ISBN": row.component_isbn,
                                         "Component_Print_ISSN": row.component_print_issn,
                                         "Component_Online_ISSN": row.component_online_issn,
                                         "Component_URI": row.component_uri})
                        row_dict["Data_Type"] = row.data_type
                        row_dict["YOP"] = row.yop
                        row_dict["Access_Type"] = row.access_type
                        row_dict["Access_Method"] = row.access_method
                    row_dict.update(row.month_counts)

                row_dict.update({"Metric_Type": row.metric_type,
                                 "Reporting_Period_Total": row.total_count})
                row_dicts.append(row_dict)

        elif report_type == "IR_A1":
            column_names += ["Item", "Publisher", "Publisher_ID", "Platform", "Authors", "Publication_Date",
                             "Article_version", "DOI", "Proprietary_ID", "Print_ISSN", "Online_ISSN", "URI",
                             "Parent_Title", "Parent_Authors", "Parent_Article_Version", "Parent_DOI",
                             "Parent_Proprietary_ID", "Parent_Print_ISSN", "Parent_Online_ISSN", "Parent_URI",
                             "Access_Type"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Item": row.item,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "Authors": row.authors,
                            "Publication_Date": row.publication_date,
                            "Article_version": row.article_version,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "URI": row.uri,
                            "Parent_Title": row.parent_title,
                            "Parent_Authors": row.parent_authors,
                            "Parent_Article_Version": row.parent_article_version,
                            "Parent_DOI": row.parent_doi,
                            "Parent_Proprietary_ID": row.parent_proprietary_id,
                            "Parent_Print_ISSN": row.parent_print_issn,
                            "Parent_Online_ISSN": row.parent_online_issn,
                            "Parent_URI": row.parent_uri,
                            "Access_Type": row.access_type,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "IR_M1":
            column_names += ["Item", "Publisher", "Publisher_ID", "Platform", "DOI", "Proprietary_ID", "URI"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Item": row.item,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Proprietary_ID": row.proprietary_id,
                            "URI": row.uri,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        column_names += ["Metric_Type", "Reporting_Period_Total"]

        if self.is_special:
            special_options_dict = self.special_options.__dict__
            if not special_options_dict["exclude_monthly_details"][0]:
                column_names += get_month_years(self.begin_date, self.end_date)
        else:
            column_names += get_month_years(self.begin_date, self.end_date)

        tsv_dict_writer = csv.DictWriter(file, column_names, delimiter='\t')
        tsv_dict_writer.writeheader()

        if len(row_dicts) == 0:
            return False

        tsv_dict_writer.writerows(row_dicts)
        return True

    def save_json_file(self, json_string: str):
        """Saves a raw JSON file of the report

        :param json_string: The JSON string
        """
        file_dir = f"{PROTECTED_DATABASE_FILE_DIR}_json/{self.begin_date.toString('yyyy')}/{self.vendor.name}/"
        file_name = f"{self.begin_date.toString('yyyy')}_{self.vendor.name}_{self.report_type}.json"
        file_path = f"{file_dir}{file_name}"

        if not path.isdir(file_dir):
            makedirs(file_dir)

        json_file = open(file_path, 'w', encoding="utf-8")
        json_file.write(json_string)
        json_file.close()

    def notify_worker_finished(self):
        """Notifies any listeners that this worker has finished"""
        self.worker_finished_signal.emit(self.worker_id)

# El Psy Kongroo
