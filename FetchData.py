from enum import Enum
from urllib.parse import urlencode
from os import path, makedirs
import csv
import json
import requests
import sys

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QDate, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QPushButton, QDateEdit, QDialog, QWidget, QProgressBar, QLabel, QVBoxLayout, \
    QDialogButtonBox

from ui import MainWindow, MessageDialog, FetchProgressDialog, ReportResultWidget, VendorResultsWidget
from JsonUtils import JsonModel
from ManageVendors import Vendor
from Search import SearchController

# TODO get Data from exceptions

SHOW_DEBUG_MESSAGES = False
TIME_BETWEEN_VENDOR_REQUESTS = 3  # Seconds
CONCURRENT_VENDOR_PROCESSES = 5
CONCURRENT_REPORT_PROCESSES = 5
EMPTY_CELL = "-"
CSV_DIR = "./all_data/csv_files/"

REPORT_TYPES = ["PR",
                "PR_P1",
                "DR",
                "DR_D1",
                "DR_D2",
                "TR",
                "TR_B1",
                "TR_B2",
                "TR_B3",
                "TR_J1",
                "TR_J2",
                "TR_J3",
                "TR_J4",
                "IR",
                "IR_A1",
                "IR_M1"]


class MajorReportType(Enum):
    PLATFORM = "PLATFORM"
    DATABASE = "DATABASE"
    TITLE = "TITLE"
    ITEM = "ITEM"
    INVALID = "INVALID"


class CompletionStatus(Enum):
    SUCCESSFUL = "Successful!"
    FAILED = "Failed!"
    CANCELLED = "Cancelled!"


def get_major_report_type(report_type: str) -> MajorReportType:
    if report_type == "PR" or report_type == "PR_P1":
        return MajorReportType.PLATFORM

    elif report_type == "DR" or report_type == "DR_D1" or report_type == "DR_D2":
        return MajorReportType.DATABASE

    elif report_type == "TR" or report_type == "TR_B1" or report_type == "TR_B2" \
            or report_type == "TR_B3" or report_type == "TR_J1" or report_type == "TR_J2" \
            or report_type == "TR_J3" or report_type == "TR_J4":
        return MajorReportType.TITLE

    elif report_type == "IR" or report_type == "IR_A1" or report_type == "IR_M1":
        return MajorReportType.ITEM
    else:
        return MajorReportType.INVALID


# region Models

class SupportedReportModel(JsonModel):
    def __init__(self, report_id: str):
        self.report_id = report_id

    @classmethod
    def from_json(cls, json_dict: dict):
        report_id = str(json_dict["Report_ID"]).upper() if "Report_ID" in json_dict else ""

        return cls(report_id)


class PeriodModel(JsonModel):
    def __init__(self, begin_date: str, end_date: str):
        self.begin_date = begin_date
        self.end_date = end_date

    @classmethod
    def from_json(cls, json_dict: dict):
        begin_date = json_dict["Begin_Date"] if "Begin_Date" in json_dict else ""
        end_date = json_dict["End_Date"] if "End_Date" in json_dict else ""

        return cls(begin_date, end_date)


class InstanceModel(JsonModel):
    def __init__(self, metric_type: str, count: int):
        self.metric_type = metric_type
        self.count = count

    @classmethod
    def from_json(cls, json_dict: dict):
        metric_type = json_dict["Metric_Type"] if "Metric_Type" in json_dict else ""
        count = int(json_dict["Count"]) if "Count" in json_dict else 0

        return cls(metric_type, count)


class PerformanceModel(JsonModel):
    def __init__(self, period: PeriodModel, instances: list):
        self.period = period
        self.instances = instances

    @classmethod
    def from_json(cls, json_dict: dict):
        period = PeriodModel.from_json(json_dict["Period"]) if "Period" in json_dict else None

        instances = []
        if "Instance" in json_dict:
            instance_dicts = json_dict["Instance"]
            for instance_dict in instance_dicts:
                instances.append(InstanceModel.from_json(instance_dict))

        return cls(period, instances)


class TypeValueModel(JsonModel):
    def __init__(self, item_type: str, value: str):
        self.item_type = item_type
        self.value = value

    @classmethod
    def from_json(cls, json_dict: dict):
        item_type = str(json_dict["Type"]) if "Type" in json_dict else ""
        value = str(json_dict["Value"]) if "Value" in json_dict else ""

        return cls(item_type, value)


class NameValueModel(JsonModel):
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    @classmethod
    def from_json(cls, json_dict: dict):
        name = str(json_dict["Name"]) if "Name" in json_dict else ""
        value = str(json_dict["Value"]) if "Value" in json_dict else ""

        return cls(name, value)


class ExceptionModel(JsonModel):
    def __init__(self, code: int = None, message: str = None, severity: str = None):
        self.code = code
        self.message = message
        self.severity = severity

    @classmethod
    def from_json(cls, json_dict: dict):
        code = int(json_dict["Code"]) if "Code" in json_dict else None
        message = json_dict["Message"] if "Message" in json_dict else None
        severity = json_dict["Severity"] if "Severity" in json_dict else None

        return cls(code, message, severity)


class ReportHeaderModel(JsonModel):
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

        institution_ids = []
        if "Institution_ID" in json_dict:
            institution_id_dicts = json_dict["Institution_ID"]
            for institution_id_dict in institution_id_dicts:
                institution_ids.append(TypeValueModel.from_json(institution_id_dict))

        report_filters = []
        if "Report_Filters" in json_dict:
            report_filter_dicts = json_dict["Report_Filters"]
            for report_filter_dict in report_filter_dicts:
                report_filters.append(NameValueModel.from_json(report_filter_dict))

        report_attributes = []
        if "Report_Attributes" in json_dict:
            report_attribute_dicts = json_dict["Report_Attributes"]
            for report_attribute_dict in report_attribute_dicts:
                report_attributes.append(NameValueModel.from_json(report_attribute_dict))

        exceptions = []
        if "Exceptions" in json_dict:
            exception_dicts = json_dict["Exceptions"]
            for exception_dict in exception_dicts:
                exceptions.append(ExceptionModel.from_json(exception_dict))

        return cls(report_name, report_id, release, institution_name, institution_ids, report_filters,
                   report_attributes, exceptions, created, created_by)


class ReportModel(JsonModel):
    def __init__(self, report_header: ReportHeaderModel, report_items: list):
        self.report_header = report_header
        self.report_items = report_items

    @classmethod
    def from_json(cls, json_dict: dict):
        exception_messages = ReportModel.check_for_exceptions(json_dict)

        report_header = ReportHeaderModel.from_json(json_dict["Report_Header"])
        report_type = report_header.report_id
        major_report_type = get_major_report_type(report_type)
        if major_report_type == MajorReportType.INVALID:
            if exception_messages == "":
                raise Exception("Invalid report type")
            else:
                raise Exception(exception_messages + "\nInvalid report type")

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

            else:  # Report_Items is empty
                if exception_messages == "":
                    raise Exception("Vendor returned empty Report_Items")
                else:
                    raise Exception(exception_messages + "\nVendor returned empty \"Report_Items\"")

        else:  # Report_Items is missing
            if exception_messages == "":
                raise Exception("Vendor did not return Report_Items")
            else:
                raise Exception(exception_messages + "\nVendor did not return \"Report_Items\"")

        return cls(report_header, report_items)

    @classmethod
    def check_for_exceptions(cls, json_dict: dict) -> str:
        exception_messages = ""
        count = 0
        if "Exception" in json_dict:
            exception = ExceptionModel.from_json(json_dict["Exception"])
            if exception.code == 1011:  # Report Queued for Processing
                raise RetryLaterException(f"Code: {exception.code}, Message: {exception.message}")

            if count == 0:
                exception_messages += f"Code: {exception.code}, Message: {exception.message}"
            else:
                exception_messages += "\n" + f"Code: {exception.code}, Message: {exception.message}"
            count += 1

        code = int(json_dict["Code"]) if "Code" in json_dict else None
        message = json_dict["Message"] if "Message" in json_dict else None
        if code is not None:
            if code == 1011:  # Report Queued for Processing
                raise RetryLaterException(f"Code: {code}, Message: {message}")

            if count == 0:
                exception_messages += f"Code: {code}, Message: {message}"
            else:
                exception_messages += "\n" + f"Code: {code}, Message: {message}"
            count += 1

        if "Report_Header" in json_dict:
            report_header = ReportHeaderModel.from_json(json_dict["Report_Header"])
            if report_header.exceptions is not None:
                if len(report_header.exceptions) > 0:
                    exception: ExceptionModel
                    for exception in report_header.exceptions:
                        if exception.code == 1011:  # Report Queued for Processing
                            raise RetryLaterException(f"Code: {exception.code}, Message: {exception.message}")

                        if count == 0:
                            exception_messages += f"Code: {exception.code}, Message: {exception.message}"
                        else:
                            exception_messages += "\n" + f"Code: {exception.code}, Message: {exception.message}"
                        count += 1
        else:
            if count == 0:
                exception_messages += "Report_Header is missing"
            else:
                exception_messages += "\n" + "Report_Header is missing"
            raise Exception(exception_messages)

        return exception_messages


class PlatformReportItemModel(JsonModel):
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

        performances = []
        if "Performance" in json_dict:
            performance_dicts = json_dict["Performance"]
            for performance_dict in performance_dicts:
                performances.append(PerformanceModel.from_json(performance_dict))

        return cls(platform, data_type, access_method, performances)


class DatabaseReportItemModel(JsonModel):
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

        item_ids = []
        if "Item_ID" in json_dict:
            item_id_dicts = json_dict["Item_ID"]
            for item_id_dict in item_id_dicts:
                item_ids.append(TypeValueModel.from_json(item_id_dict))

        publisher_ids = []
        if "Publisher_ID" in json_dict:
            if type(json_dict["Publisher_ID"]) is dict:  # Some vendors return a dict instead of list
                publisher_ids.append(TypeValueModel.from_json(json_dict["Publisher_ID"]))
            elif type(json_dict["Publisher_ID"]) is list:
                publisher_id_dicts = json_dict["Publisher_ID"]
                for publisher_id_dict in publisher_id_dicts:
                    publisher_ids.append(TypeValueModel.from_json(publisher_id_dict))

        performances = []
        if "Performance" in json_dict:
            performance_dicts = json_dict["Performance"]
            for performance_dict in performance_dicts:
                performances.append(PerformanceModel.from_json(performance_dict))

        return cls(database, publisher, item_ids, publisher_ids, platform, data_type, access_method, performances)


class TitleReportItemModel(JsonModel):
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

        item_ids = []
        if "Item_ID" in json_dict:
            item_id_dicts = json_dict["Item_ID"]
            for item_id_dict in item_id_dicts:
                item_ids.append(TypeValueModel.from_json(item_id_dict))

        publisher_ids = []
        if "Publisher_ID" in json_dict:
            publisher_id_dicts = json_dict["Publisher_ID"]
            for publisher_id_dict in publisher_id_dicts:
                publisher_ids.append(TypeValueModel.from_json(publisher_id_dict))

        performances = []
        if "Performance" in json_dict:
            performance_dicts = json_dict["Performance"]
            for performance_dict in performance_dicts:
                performances.append(PerformanceModel.from_json(performance_dict))

        return cls(title, item_ids, platform, publisher, publisher_ids, data_type, section_type, yop, access_type,
                   access_method, performances)


class ItemContributorModel(JsonModel):
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

        item_ids = []
        if "Item_ID" in json_dict:
            item_id_dicts = json_dict["Item_ID"]
            for item_id_dict in item_id_dicts:
                item_ids.append(TypeValueModel.from_json(item_id_dict))

        item_contributors = []
        if "Item_Contributors" in json_dict:
            item_contributor_dicts = json_dict["Item_Contributors"]
            for item_contributor_dict in item_contributor_dicts:
                item_contributors.append(ItemContributorModel.from_json(item_contributor_dict))

        item_dates = []
        if "Item_Dates" in json_dict:
            item_date_dicts = json_dict["Item_Dates"]
            for item_date_dict in item_date_dicts:
                item_dates.append(TypeValueModel.from_json(item_date_dict))

        item_attributes = []
        if "Item_Attributes" in json_dict:
            item_attribute_dicts = json_dict["Item_Attributes"]
            for item_attribute_dict in item_attribute_dicts:
                item_attributes.append(TypeValueModel.from_json(item_attribute_dict))

        return cls(item_name, item_ids, item_contributors, item_dates, item_attributes, data_type)


class ItemComponentModel(JsonModel):
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

        item_ids = []
        if "Item_ID" in json_dict:
            item_id_dicts = json_dict["Item_ID"]
            for item_id_dict in item_id_dicts:
                item_ids.append(TypeValueModel.from_json(item_id_dict))

        item_contributors = []
        if "Item_Contributors" in json_dict:
            item_contributor_dicts = json_dict["Item_Contributors"]
            for item_contributor_dict in item_contributor_dicts:
                item_contributors.append(ItemContributorModel.from_json(item_contributor_dict))

        item_dates = []
        if "Item_Dates" in json_dict:
            item_date_dicts = json_dict["Item_Dates"]
            for item_date_dict in item_date_dicts:
                item_dates.append(TypeValueModel.from_json(item_date_dict))

        item_attributes = []
        if "Item_Attributes" in json_dict:
            item_attribute_dicts = json_dict["Item_Attributes"]
            for item_attribute_dict in item_attribute_dicts:
                item_attributes.append(TypeValueModel.from_json(item_attribute_dict))

        performances = []
        if "Performance" in json_dict:
            performance_dicts = json_dict["Performance"]
            for performance_dict in performance_dicts:
                performances.append(PerformanceModel.from_json(performance_dict))

        return cls(item_name, item_ids, item_contributors, item_dates, item_attributes, data_type, performances)


class ItemReportItemModel(JsonModel):
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

        item_ids = []
        if "Item_ID" in json_dict:
            item_id_dicts = json_dict["Item_ID"]
            for item_id_dict in item_id_dicts:
                item_ids.append(TypeValueModel.from_json(item_id_dict))

        item_contributors = []
        if "Item_Contributors" in json_dict:
            item_contributor_dicts = json_dict["Item_Contributors"]
            for item_contributor_dict in item_contributor_dicts:
                item_contributors.append(ItemContributorModel.from_json(item_contributor_dict))

        item_dates = []
        if "Item_Dates" in json_dict:
            item_date_dicts = json_dict["Item_Dates"]
            for item_date_dict in item_date_dicts:
                item_dates.append(TypeValueModel.from_json(item_date_dict))

        item_attributes = []
        if "Item_Attributes" in json_dict:
            item_attribute_dicts = json_dict["Item_Attributes"]
            for item_attribute_dict in item_attribute_dicts:
                item_attributes.append(TypeValueModel.from_json(item_attribute_dict))

        publisher_ids = []
        if "Publisher_ID" in json_dict:
            publisher_id_dicts = json_dict["Publisher_ID"]
            for publisher_id_dict in publisher_id_dicts:
                publisher_ids.append(TypeValueModel.from_json(publisher_id_dict))

        item_components = []
        if "Item_Component" in json_dict:
            item_component_dicts = json_dict["Item_Component"]
            for item_component_dict in item_component_dicts:
                item_components.append(ItemComponentModel.from_json(item_component_dict))

        performances = []
        if "Performance" in json_dict:
            performance_dicts = json_dict["Performance"]
            for performance_dict in performance_dicts:
                performances.append(PerformanceModel.from_json(performance_dict))

        return cls(item, item_ids, item_contributors, item_dates, item_attributes, platform, publisher, publisher_ids,
                   item_parent, item_components, data_type, yop, access_type, access_method, performances)


class ReportRow:
    def __init__(self):
        self.database = EMPTY_CELL
        self.title = EMPTY_CELL
        self.item = EMPTY_CELL
        self.publisher = EMPTY_CELL
        self.publisher_id = EMPTY_CELL
        self.platform = EMPTY_CELL
        self.authors = EMPTY_CELL
        self.publication_date = EMPTY_CELL
        self.article_version = EMPTY_CELL
        self.doi = EMPTY_CELL
        self.proprietary_id = EMPTY_CELL
        self.online_issn = EMPTY_CELL
        self.print_issn = EMPTY_CELL
        self.linking_issn = EMPTY_CELL
        self.isbn = EMPTY_CELL
        self.uri = EMPTY_CELL
        self.parent_title = EMPTY_CELL
        self.parent_authors = EMPTY_CELL
        self.parent_publication_date = EMPTY_CELL
        self.parent_article_version = EMPTY_CELL
        self.parent_data_type = EMPTY_CELL
        self.parent_doi = EMPTY_CELL
        self.parent_proprietary_id = EMPTY_CELL
        self.parent_online_issn = EMPTY_CELL
        self.parent_print_issn = EMPTY_CELL
        self.parent_linking_issn = EMPTY_CELL
        self.parent_isbn = EMPTY_CELL
        self.parent_uri = EMPTY_CELL
        self.component_title = EMPTY_CELL
        self.component_authors = EMPTY_CELL
        self.component_publication_date = EMPTY_CELL
        self.component_data_type = EMPTY_CELL
        self.component_doi = EMPTY_CELL
        self.component_proprietary_id = EMPTY_CELL
        self.component_online_issn = EMPTY_CELL
        self.component_print_issn = EMPTY_CELL
        self.component_linking_issn = EMPTY_CELL
        self.component_isbn = EMPTY_CELL
        self.component_uri = EMPTY_CELL
        self.data_type = EMPTY_CELL
        self.section_type = EMPTY_CELL
        self.yop = EMPTY_CELL
        self.access_type = EMPTY_CELL
        self.access_method = EMPTY_CELL
        self.metric_type = EMPTY_CELL

        self.month_counts = {
            'January': 0,
            'February': 0,
            'March': 0,
            'April': 0,
            'May': 0,
            'June': 0,
            'July': 0,
            'August': 0,
            'September': 0,
            'October': 0,
            'November': 0,
            'December': 0
        }

        self.total_count = 0


class ProcessResult:
    def __init__(self, vendor: Vendor, completion_status: CompletionStatus, message: str, report_type: str = None,
                 retry: bool = False):
        self.vendor = vendor
        self.completion_status = completion_status
        self.message = message
        self.report_type = report_type
        self.retry = retry


class RetryLaterException(Exception):
    pass


# endregion

class FetchDataController:
    def __init__(self, vendors: list, search_controller: SearchController, main_window_ui: MainWindow.Ui_mainWindow):

        # region General
        self.search_controller = search_controller
        self.vendors = vendors
        self.selected_data = []  # List of (Vendor, list[report_types])>
        self.retry_data = []  # List of (Vendor, list[report_types])>
        self.vendor_workers = {}  # <k = worker_id, v = (VendorWorker, Thread)>
        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0
        self.begin_date = QDate()
        self.end_date = QDate()
        current_date = QDate.currentDate()
        self.default_begin_date = QDate(current_date.year(), 1, current_date.day())
        self.adv_begin_date = QDate(current_date.year(), 1, current_date.day())
        if current_date.month() != 1:  # If not January
            self.default_end_date = QDate(current_date.year(), current_date.month() - 1, current_date.day())
            self.adv_end_date = QDate(current_date.year(), current_date.month() - 1, current_date.day())
        else:
            self.default_end_date = QDate(current_date)
            self.adv_end_date = QDate(current_date)

        self.is_last_fetch_advanced = False
        self.is_cancelling = False
        # endregion

        # region Start Fetch Buttons
        self.fetch_all_btn = main_window_ui.fetch_all_data_button
        self.fetch_all_btn.clicked.connect(self.fetch_all_data)

        self.fetch_adv_btn = main_window_ui.fetch_advanced_button
        self.fetch_adv_btn.clicked.connect(self.fetch_advanced_data)
        # endregion

        # region Vendors
        self.vendor_list_view = main_window_ui.vendors_list_view_fetch
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        for vendor in vendors:
            item = QStandardItem(vendor.name)
            item.setCheckable(True)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

        self.select_vendors_btn = main_window_ui.select_vendors_button_fetch
        self.select_vendors_btn.clicked.connect(self.select_all_vendors)
        self.deselect_vendors_btn = main_window_ui.deselect_vendors_button_fetch
        self.deselect_vendors_btn.clicked.connect(self.deselect_all_vendors)
        # endregion

        # region Report Types
        self.report_type_list_view = main_window_ui.report_types_list_view
        self.report_type_list_model = QStandardItemModel(self.report_type_list_view)
        self.report_type_list_view.setModel(self.report_type_list_model)
        for report_type in REPORT_TYPES:
            item = QStandardItem(report_type)
            item.setCheckable(True)
            item.setEditable(False)
            self.report_type_list_model.appendRow(item)

        self.select_report_types_btn = main_window_ui.select_report_types_button_fetch
        self.select_report_types_btn.clicked.connect(self.select_all_report_types)
        self.deselect_report_types_btn = main_window_ui.deselect_report_types_button_fetch
        self.deselect_report_types_btn.clicked.connect(self.deselect_all_report_types)
        # endregion

        # region Date Edits
        self.begin_date_edit = main_window_ui.begin_date_edit
        self.begin_date_edit.setDate(self.default_begin_date)
        self.begin_date_edit.dateChanged.connect(lambda date: self.on_date_changed(date, "adv_begin"))
        self.end_date_edit = main_window_ui.end_date_edit
        self.end_date_edit.setDate(self.default_end_date)
        self.end_date_edit.dateChanged.connect(lambda date: self.on_date_changed(date, "adv_end"))
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

    def on_vendors_size_changed(self):
        self.vendor_list_model.removeRows(0, self.vendor_list_model.rowCount())

        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setCheckable(True)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

    def on_date_changed(self, date: QDate, date_type: str):
        if date_type == "adv_begin":
            self.adv_begin_date = date
            if self.adv_begin_date.year() != self.adv_end_date.year():
                self.adv_end_date.setDate(self.adv_begin_date.year(),
                                          self.adv_end_date.month(),
                                          self.adv_end_date.day())
                self.end_date_edit.setDate(self.adv_end_date)
        elif date_type == "adv_end":
            self.adv_end_date = date
            if self.adv_end_date.year() != self.adv_begin_date.year():
                self.adv_begin_date.setDate(self.adv_end_date.year(),
                                            self.adv_begin_date.month(),
                                            self.adv_begin_date.day())
                self.begin_date_edit.setDate(self.adv_begin_date)

    def select_all_vendors(self):
        for i in range(self.vendor_list_model.rowCount()):
            self.vendor_list_model.item(i).setCheckState(Qt.Checked)

    def deselect_all_vendors(self):
        for i in range(self.vendor_list_model.rowCount()):
            self.vendor_list_model.item(i).setCheckState(Qt.Unchecked)

    def select_all_report_types(self):
        for i in range(self.report_type_list_model.rowCount()):
            self.report_type_list_model.item(i).setCheckState(Qt.Checked)

    def deselect_all_report_types(self):
        for i in range(self.report_type_list_model.rowCount()):
            self.report_type_list_model.item(i).setCheckState(Qt.Unchecked)

    def fetch_all_data(self):
        if self.total_processes > 0:
            self.show_message(f"Waiting for pending processes to complete...")
            if SHOW_DEBUG_MESSAGES: print(f"Waiting for pending processes to complete...")
            return

        if len(self.vendors) == 0:
            self.show_message("Vendor list is empty")
            return

        self.selected_data = []
        for i in range(len(self.vendors)):
            self.selected_data.append((self.vendors[i], REPORT_TYPES))

        self.begin_date = self.default_begin_date
        self.end_date = self.default_end_date

        self.is_last_fetch_advanced = False
        self.start_progress_dialog()
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        while self.started_processes < len(self.selected_data) and self.started_processes < CONCURRENT_VENDOR_PROCESSES:
            vendor, report_types = self.selected_data[self.started_processes]
            self.fetch_vendor_data(vendor, report_types)
            self.started_processes += 1

    def fetch_advanced_data(self):
        if self.total_processes > 0:
            self.show_message(f"Waiting for pending processes to complete...")
            if SHOW_DEBUG_MESSAGES: print(f"Waiting for pending processes to complete...")
            return

        if len(self.vendors) == 0:
            self.show_message("Vendor list is empty")
            return

        self.selected_data = []
        selected_report_types = []
        for i in range(len(REPORT_TYPES)):
            if self.report_type_list_model.item(i).checkState() == Qt.Checked:
                selected_report_types.append(REPORT_TYPES[i])
        if len(selected_report_types) == 0:
            self.show_message("No report type selected")
            return

        for i in range(len(self.vendors)):
            if self.vendor_list_model.item(i).checkState() == Qt.Checked:
                self.selected_data.append((self.vendors[i], selected_report_types))
        if len(self.selected_data) == 0:
            self.show_message("No vendor selected")
            return

        self.begin_date = self.adv_begin_date
        self.end_date = self.adv_end_date

        self.start_progress_dialog()
        self.is_last_fetch_advanced = False
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        while self.started_processes < len(self.selected_data) and self.started_processes < CONCURRENT_VENDOR_PROCESSES:
            vendor, report_types = self.selected_data[self.started_processes]
            self.fetch_vendor_data(vendor, report_types)
            self.started_processes += 1

    def fetch_vendor_data(self, vendor: Vendor, report_types: list):
        worker_id = vendor.name
        if worker_id in self.vendor_workers: return  # Avoid processing a vendor twice

        vendor_worker = VendorWorker(worker_id, vendor, self.search_controller, self.begin_date, self.end_date,
                                     report_types)
        vendor_worker.worker_finished_signal.connect(self.on_vendor_worker_finished)
        vendor_thread = QThread()
        self.vendor_workers[worker_id] = vendor_worker, vendor_thread
        vendor_worker.moveToThread(vendor_thread)
        vendor_thread.started.connect(vendor_worker.work)
        vendor_thread.start()

        if SHOW_DEBUG_MESSAGES: print(f"{worker_id}: Added a process, total processes: {self.total_processes}")
        self.update_results_ui(vendor)

    def update_results_ui(self, vendor: Vendor, vendor_result: ProcessResult = None, report_results: list = None):
        self.progress_bar.setValue(int(self.completed_processes / self.total_processes * 100))
        if not self.is_cancelling:
            if self.completed_processes != self.total_processes:
                self.status_label.setText(f"Progress: {self.completed_processes}/{self.total_processes}")
            else:
                self.status_label.setText(f"Finishing...")
        else:
            self.status_label.setText(f"Cancelling...")

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
        report_result_widget = QWidget(vendor_widget)
        report_result_ui = ReportResultWidget.Ui_ReportResultWidget()
        report_result_ui.setupUi(report_result_widget)

        report_result_ui.message_label.setText(process_result.message)
        if process_result.report_type is not None:
            report_result_ui.report_type_label.setText(process_result.report_type)
        else:
            report_result_ui.report_type_label.setText("Target Reports")
            report_result_ui.retry_frame.hide()

        report_result_ui.success_label.setText(process_result.completion_status.value)
        if process_result.completion_status == CompletionStatus.FAILED:
            report_result_ui.retry_check_box.stateChanged.connect(
                lambda checked_state: self.report_to_retry_toggled(checked_state, vendor, process_result.report_type))
        else:
            report_result_ui.retry_frame.hide()

        return report_result_widget

    def on_vendor_worker_finished(self, worker_id: str):
        self.completed_processes += 1

        thread: QThread
        worker: VendorWorker
        worker, thread = self.vendor_workers[worker_id]
        self.update_results_ui(worker.vendor, worker.process_result, worker.report_process_results)

        thread.quit()
        thread.wait()
        self.vendor_workers.pop(worker_id, None)

        if self.started_processes < self.total_processes and not self.is_cancelling:
            vendor, report_types = self.selected_data[self.started_processes]
            self.fetch_vendor_data(vendor, report_types)
            self.started_processes += 1

        elif len(self.vendor_workers) == 0: self.finish()

    def start_progress_dialog(self):
        self.vendor_result_widgets = {}

        self.fetch_progress_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        fetch_progress_ui = FetchProgressDialog.Ui_FetchProgressDialog()
        fetch_progress_ui.setupUi(self.fetch_progress_dialog)

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
        self.retry_button.clicked.connect(self.retry_selected_reports)
        self.cancel_button.clicked.connect(self.cancel_workers)

        self.status_label.setText("Starting...")
        self.fetch_progress_dialog.show()

    def show_message(self, message: str):
        message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        message_dialog_ui = MessageDialog.Ui_message_dialog()
        message_dialog_ui.setupUi(message_dialog)

        message_label = message_dialog_ui.message_label
        message_label.setText(message)

        message_dialog.exec_()

    def report_to_retry_toggled(self, checked_state: int, vendor: Vendor, report_type):
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

    def retry_selected_reports(self):
        if len(self.retry_data) == 0:
            self.show_message("No report selected")
            return

        self.start_progress_dialog()
        self.selected_data = self.retry_data
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        while self.started_processes < len(self.selected_data) and self.started_processes < CONCURRENT_VENDOR_PROCESSES:
            vendor, report_types = self.selected_data[self.started_processes]
            self.fetch_vendor_data(vendor, report_types)
            self.started_processes += 1

    def finish(self):
        self.search_controller.save_all_data()
        self.ok_button.setEnabled(True)
        self.retry_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Done!")

        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0
        self.is_cancelling = False
        if SHOW_DEBUG_MESSAGES: print("Fin!")

    def cancel_workers(self):
        self.is_cancelling = True
        self.total_processes = self.started_processes
        self.status_label.setText(f"Cancelling...")
        for worker, thread in self.vendor_workers.values():
            worker.set_cancelling()


class VendorWorker(QObject):
    worker_finished_signal = pyqtSignal(str)

    def __init__(self, worker_id: str, vendor: Vendor, search_controller: SearchController, begin_date: QDate,
                 end_date: QDate,
                 target_report_types: list = None):
        super().__init__()
        self.worker_id = worker_id
        self.vendor = vendor
        self.search_controller = search_controller
        self.begin_date = begin_date
        self.end_date = end_date
        self.target_report_types = target_report_types
        self.reports_to_process = []
        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0

        self.process_result = ProcessResult(self.vendor, CompletionStatus.SUCCESSFUL, "All Good")
        self.report_process_results = []
        self.report_workers = {}  # <k = worker_id, v = (ReportWorker, Thread)>
        self.is_cancelling = False

    def work(self):
        if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}: Fetching supported reports")
        request_query = {}
        if self.vendor.customer_id.strip(): request_query["customer_id"] = self.vendor.customer_id
        if self.vendor.requestor_id.strip(): request_query["requestor_id"] = self.vendor.requestor_id
        if self.vendor.api_key.strip(): request_query["api_key"] = self.vendor.api_key
        if self.vendor.platform.strip(): request_query["platform"] = self.vendor.platform

        request_url = self.vendor.base_url

        try:
            # Some vendors only work if they think a web browser is making the request...(JSTOR...)
            response = requests.get(request_url, request_query, headers={'User-Agent': 'Mozilla/5.0'})
            if SHOW_DEBUG_MESSAGES: print(response.url)

            if response.status_code == requests.codes.ok:
                self.process_response(response)
            else:
                self.process_result.completion_status = CompletionStatus.FAILED
                self.process_result.message = f"Request failed, status_code: {response.status_code}"
        except requests.exceptions.RequestException as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"Request Exception: {e}"
            if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}: Request Exception: {e}")

        if len(self.report_workers) == 0: self.notify_worker_finished()

    def process_response(self, response: requests.Response):
        if self.is_cancelling:
            self.process_result.message = "Target reports not processed"
            self.process_result.completion_status = CompletionStatus.CANCELLED
            return

        try:
            json_response = response.json()
            self.check_for_exception(json_response)

            json_dicts = []
            if type(json_response) is dict:  # This should never be a dict by the standard, but some vendors......
                json_dicts = json_response["Report_Items"] if "Report_Items" in json_response else []  # Report_Items???
                # Some other vendor might implement it in a different way..........................
            elif type(json_response) is list:
                json_dicts = json_response

            if len(json_dicts) == 0:
                raise Exception("JSON is empty")

            self.reports_to_process = []
            reports_to_process_str = ""
            for json_dict in json_dicts:
                supported_report = SupportedReportModel.from_json(json_dict)

                if supported_report.report_id in self.target_report_types:
                    self.reports_to_process.append(supported_report)
                    reports_to_process_str += f"'{supported_report.report_id}' "

            if len(self.reports_to_process) == 0:
                self.process_result.message = "Target reports not supported"
                return

            self.process_result.message = reports_to_process_str

            self.total_processes = len(self.reports_to_process)
            self.started_processes = 0
            while self.started_processes < self.total_processes and self.started_processes < CONCURRENT_REPORT_PROCESSES:
                QThread.currentThread().sleep(TIME_BETWEEN_VENDOR_REQUESTS)  # Avoid spamming vendor's server
                if self.is_cancelling:
                    self.process_result.completion_status = CompletionStatus.CANCELLED
                    return

                self.fetch_report(self.vendor, self.reports_to_process[self.started_processes])
                self.started_processes += 1

        except json.JSONDecodeError as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"JSON Exception: {e}"
            if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}: JSON Exception: {e.msg}")
        except Exception as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = str(e)
            if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}: Exception: {e}")

    def fetch_report(self, vendor: Vendor, supported_report: SupportedReportModel):
        worker_id = supported_report.report_id
        if worker_id in self.report_workers: return  # Avoid fetching a report twice, app will crash!!

        report_worker = ReportWorker(worker_id, vendor, self.search_controller, supported_report, self.begin_date,
                                     self.end_date)
        report_worker.worker_finished_signal.connect(self.on_report_worker_finished)
        report_thread = QThread()
        self.report_workers[worker_id] = report_worker, report_thread
        report_worker.moveToThread(report_thread)
        report_thread.started.connect(report_worker.work)
        report_thread.start()

    def check_for_exception(self, json_response):
        if type(json_response) is dict:
            if "Exception" in json_response:
                exception = ExceptionModel.from_json(json_response["Exception"])
                raise Exception(f"Code: {exception.code}, Message: {exception.message}")

            code = int(json_response["Code"]) if "Code" in json_response else None
            message = json_response["Message"] if "Message" in json_response else None
            if code is not None: raise Exception(f"Code: {code}, Message: {message}")

    def notify_worker_finished(self):
        self.worker_finished_signal.emit(self.vendor.name)

    def on_report_worker_finished(self, worker_id: str):
        self.completed_processes += 1

        thread: QThread
        worker: ReportWorker
        worker, thread = self.report_workers[worker_id]

        self.report_process_results.append(worker.process_result)
        thread.quit()
        thread.wait()
        self.report_workers.pop(worker_id, None)

        if self.started_processes < self.total_processes and not self.is_cancelling:
            QThread.currentThread().sleep(TIME_BETWEEN_VENDOR_REQUESTS)  # Avoid spamming vendor's server
            self.fetch_report(self.vendor, self.reports_to_process[self.started_processes])
            self.started_processes += 1

        if len(self.report_workers) == 0: self.notify_worker_finished()

    def set_cancelling(self):
        self.is_cancelling = True


class ReportWorker(QObject):
    worker_finished_signal = pyqtSignal(str)

    def __init__(self, worker_id: str, vendor: Vendor,
                 search_controller: SearchController,
                 supported_report: SupportedReportModel, begin_date: QDate, end_date: QDate):
        super().__init__()
        self.worker_id = worker_id
        self.vendor = vendor
        self.search_controller = search_controller
        self.supported_report = supported_report
        self.begin_date = begin_date
        self.end_date = end_date

        self.process_result = ProcessResult(self.vendor, CompletionStatus.SUCCESSFUL, "All Good",
                                            self.supported_report.report_id)

    def work(self):
        if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}-{self.supported_report.report_id}: Fetching Report")
        request_query = {}
        if self.vendor.customer_id.strip(): request_query["customer_id"] = self.vendor.customer_id
        if self.vendor.requestor_id.strip(): request_query["requestor_id"] = self.vendor.requestor_id
        if self.vendor.api_key.strip(): request_query["api_key"] = self.vendor.api_key
        if self.vendor.platform.strip(): request_query["platform"] = self.vendor.platform
        request_query["begin_date"] = self.begin_date.toString("yyyy-MM")
        request_query["end_date"] = self.end_date.toString("yyyy-MM")

        request_url = f"{self.vendor.base_url}/{self.supported_report.report_id.lower()}"

        try:
            # Some vendors only work if they think a web browser is making the request...
            response = requests.get(request_url, request_query, headers={'User-Agent': 'Mozilla/5.0'})
            if SHOW_DEBUG_MESSAGES: print(response.url)
            self.process_response(response)
            if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}-{self.supported_report.report_id}: Done")
        except requests.exceptions.RequestException as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"Request Exception: {e}"
            if SHOW_DEBUG_MESSAGES: print(
                f"{self.vendor.name}-{self.supported_report.report_id}: Request Exception: {e}")

        self.notify_worker_finished()

    def process_response(self, response: requests.Response):
        try:
            json_dict = response.json()
            report_model = ReportModel.from_json(json_dict)
            self.process_report_model(report_model)
        except json.JSONDecodeError as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            if e.msg == "Expecting value":
                self.process_result.message = f"Something went wrong on the vendor's end. No data was returned"
            else:
                self.process_result.message = f"JSON Exception: {e.msg}"
            if SHOW_DEBUG_MESSAGES: print(
                f"{self.vendor.name}-{self.supported_report.report_id}: JSON Exception: {e.msg}")
        except RetryLaterException as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = str(e)
            self.process_result.retry = True
            if SHOW_DEBUG_MESSAGES: print(
                f"{self.vendor.name}-{self.supported_report.report_id}: Retry Later Exception: {e}")
        except Exception as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = str(e)
            if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}-{self.supported_report.report_id}: Exception: {e}")

    def process_report_model(self, report_model: ReportModel):
        report_type = report_model.report_header.report_id
        major_report_type = report_model.report_header.major_report_type
        report_items = report_model.report_items
        report_rows = []
        file_dir = f"{CSV_DIR}/{self.begin_date.toString('yyyy')}/{self.vendor.name}/"
        file_name = f"{self.begin_date.toString('yyyy')}_{self.vendor.name}_{report_type}.csv"
        file_path = f"{file_dir}/{file_name}"

        if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}-{self.supported_report.report_id}: Processing report")

        for report_item in report_items:
            row_dict = {}  # <k = metric_type, v = ReportRow>

            performance: PerformanceModel
            for performance in report_item.performances:
                begin_month = QDate.fromString(performance.period.begin_date, "yyyy-MM-dd").toString("MMMM")

                instance: InstanceModel
                for instance in performance.instances:
                    metric_type = instance.metric_type
                    if metric_type not in row_dict:
                        report_row = ReportRow()
                        report_row.metric_type = metric_type

                        if major_report_type == MajorReportType.PLATFORM:
                            report_item: PlatformReportItemModel
                            if report_item.platform != "": report_row.platform = report_item.platform
                            if report_item.data_type != "": report_row.data_type = report_item.data_type
                            if report_item.access_method != "": report_row.access_method = report_item.access_method

                        elif major_report_type == MajorReportType.DATABASE:
                            report_item: DatabaseReportItemModel
                            if report_item.database != "": report_row.database = report_item.database
                            if report_item.publisher != "": report_row.publisher = report_item.publisher
                            if report_item.platform != "": report_row.platform = report_item.platform
                            if report_item.data_type != "": report_row.data_type = report_item.data_type
                            if report_item.access_method != "": report_row.access_method = report_item.access_method

                            pub_id_str = ""
                            for pub_id in report_item.publisher_ids:
                                pub_id_str += f"{pub_id.item_type}:{pub_id.value}; "

                                if pub_id.item_type == "Proprietary" or pub_id.item_type == "Proprietary_ID":
                                    report_row.proprietary_id = pub_id.value
                            if pub_id_str != "": report_row.publisher_id = pub_id_str

                            for item_id in report_item.item_ids:
                                if item_id.item_type == "Proprietary" or item_id.item_type == "Proprietary_ID":
                                    report_row.proprietary_id = item_id.value

                        elif major_report_type == MajorReportType.TITLE:
                            report_item: TitleReportItemModel
                            if report_item.title != "": report_row.title = report_item.title
                            if report_item.publisher != "": report_row.publisher = report_item.publisher
                            if report_item.platform != "": report_row.platform = report_item.platform
                            if report_item.data_type != "": report_row.data_type = report_item.data_type
                            if report_item.section_type != "": report_row.section_type = report_item.section_type
                            if report_item.yop != "": report_row.yop = report_item.yop
                            if report_item.access_type != "": report_row.access_type = report_item.access_type
                            if report_item.access_method != "": report_row.access_method = report_item.access_method

                            pub_id_str = ""
                            for pub_id in report_item.publisher_ids:
                                pub_id_str += f"{pub_id.item_type}:{pub_id.value}; "

                                if pub_id.item_type == "Proprietary" or pub_id.item_type == "Proprietary_ID":
                                    report_row.proprietary_id = pub_id.value
                            if pub_id_str != "": report_row.publisher_id = pub_id_str

                            item_id: TypeValueModel
                            for item_id in report_item.item_ids:
                                item_type = item_id.item_type

                                if item_type == "DOI":
                                    report_row.doi = item_id.value
                                elif item_type == "Proprietary" or item_type == "Proprietary_ID":
                                    report_row.proprietary_id = item_id.value
                                elif item_type == "ISBN":
                                    report_row.isbn = item_id.value
                                elif item_type == "Print_ISSN":
                                    report_row.print_issn = item_id.value
                                elif item_type == "Online_ISSN":
                                    report_row.online_issn = item_id.value
                                elif item_type == "Linking_ISSN":
                                    report_row.linking_issn = item_id.value
                                elif item_type == "URI":
                                    report_row.uri = item_id.value

                            self.search_controller.index_word(report_row.title,
                                                              file_path,
                                                              self.begin_date.year(),
                                                              self.vendor.name,
                                                              report_row.online_issn,
                                                              report_row.print_issn,
                                                              report_row.linking_issn,
                                                              report_row.isbn)

                        elif major_report_type == MajorReportType.ITEM:
                            report_item: ItemReportItemModel
                            if report_item.item != "": report_row.item = report_item.item
                            if report_item.publisher != "": report_row.publisher = report_item.publisher
                            if report_item.platform != "": report_row.platform = report_item.platform
                            if report_item.data_type != "": report_row.data_type = report_item.data_type
                            if report_item.yop != "": report_row.yop = report_item.yop
                            if report_item.access_type != "": report_row.access_type = report_item.access_type
                            if report_item.access_method != "": report_row.access_method = report_item.access_method

                            # Publisher ID
                            pub_id_str = ""
                            for pub_id in report_item.publisher_ids:
                                pub_id_str += f"{pub_id.item_type}:{pub_id.value}; "

                                if pub_id.item_type == "Proprietary" or pub_id.item_type == "Proprietary_ID":
                                    report_row.proprietary_id = pub_id.value
                            if pub_id_str != "": report_row.publisher_id = pub_id_str

                            # Authors
                            authors_str = ""
                            item_contributor: ItemContributorModel
                            for item_contributor in report_item.item_contributors:
                                if item_contributor.item_type == "Author":
                                    authors_str += f"{item_contributor.name} ({item_contributor.identifier}); "
                            if authors_str != "": report_row.authors = authors_str

                            # Publication date
                            item_date: TypeValueModel
                            for item_date in report_item.item_dates:
                                if item_date.item_type == "Publication_Date":
                                    report_row.publication_date = item_date.value

                            # Article version
                            item_attribute: TypeValueModel
                            for item_attribute in report_item.item_attributes:
                                if item_attribute.item_type == "Article_Version":
                                    report_row.article_version = item_attribute.value

                            # Base IDs
                            item_id: TypeValueModel
                            for item_id in report_item.item_ids:
                                item_type = item_id.item_type

                                if item_type == "DOI":
                                    report_row.doi = item_id.value
                                elif item_type == "Proprietary" or item_type == "Proprietary_ID":
                                    report_row.proprietary_id = item_id.value
                                elif item_type == "ISBN":
                                    report_row.isbn = item_id.value
                                elif item_type == "Print_ISSN":
                                    report_row.print_issn = item_id.value
                                elif item_type == "Online_ISSN":
                                    report_row.online_issn = item_id.value
                                elif item_type == "Linking_ISSN":
                                    report_row.linking_issn = item_id.value
                                elif item_type == "URI":
                                    report_row.uri = item_id.value

                            # Parent
                            if report_item.item_parent is not None:
                                item_parent: ItemParentModel
                                item_parent = report_item.item_parent
                                if item_parent.item_name != "": report_row.parent_title = item_parent.item_name
                                if item_parent.data_type != "": report_row.parent_data_type = item_parent.data_type

                                # Authors
                                authors_str = ""
                                item_contributor: ItemContributorModel
                                for item_contributor in item_parent.item_contributors:
                                    if item_contributor.item_type == "Author":
                                        authors_str += f"{item_contributor.name} ({item_contributor.identifier}); "
                                if authors_str != "": report_row.parent_authors = authors_str

                                # Publication date
                                item_date: TypeValueModel
                                for item_date in item_parent.item_dates:
                                    if item_date.item_type == "Publication_Date" or item_date.item_type == "Pub_Date":
                                        report_row.parent_publication_date = item_date.value

                                # Article version
                                item_attribute: TypeValueModel
                                for item_attribute in item_parent.item_attributes:
                                    if item_attribute.item_type == "Article_Version":
                                        report_row.parent_article_version = item_attribute.value

                                # Parent IDs
                                item_id: TypeValueModel
                                for item_id in item_parent.item_ids:
                                    item_type = item_id.item_type

                                    if item_type == "DOI":
                                        report_row.parent_doi = item_id.value
                                    elif item_type == "Proprietary" or item_type == "Proprietary_ID":
                                        report_row.parent_proprietary_id = item_id.value
                                    elif item_type == "ISBN":
                                        report_row.parent_isbn = item_id.value
                                    elif item_type == "Print_ISSN":
                                        report_row.parent_print_issn = item_id.value
                                    elif item_type == "Online_ISSN":
                                        report_row.parent_online_issn = item_id.value
                                    elif item_type == "URI":
                                        report_row.parent_uri = item_id.value

                        else:
                            if SHOW_DEBUG_MESSAGES: print(
                                f"Unexpected report type while processing instance of {report_type} for {self.vendor.name}")

                        row_dict[metric_type] = report_row

                    month_counts = row_dict[metric_type].month_counts
                    month_counts[begin_month] += instance.count

                    row_dict[metric_type].total_count += instance.count

            for row in row_dict.values():
                report_rows.append(row)

        self.save_csv_file(report_model.report_header, report_rows)

    def save_csv_file(self, report_header, report_rows: list):
        report_type = report_header.report_id
        major_report_type = report_header.major_report_type
        file_dir = f"{CSV_DIR}/{self.begin_date.toString('yyyy')}/{self.vendor.name}/"
        file_name = f"{self.begin_date.toString('yyyy')}_{self.vendor.name}_{report_type}.csv"
        file_path = f"{file_dir}/{file_name}"

        if not path.isdir(file_dir):
            makedirs(file_dir)

        csv_file = open(file_dir + file_name, 'w', encoding="utf-8", newline='')

        # region Report Header

        csv_writer = csv.writer(csv_file, delimiter=",")
        csv_writer.writerow(["Report_Name", report_header.report_name])
        csv_writer.writerow(["Report_ID", report_header.report_id])
        csv_writer.writerow(["Release", report_header.release])
        csv_writer.writerow(["Institution_Name", report_header.institution_name])

        institution_ids_str = ""
        for institution_id in report_header.institution_ids:
            institution_ids_str += f"{institution_id.item_type}={institution_id.value}; "
        csv_writer.writerow(["Institution_ID", institution_ids_str])

        metric_types_str = ""
        reporting_period_str = ""
        report_filters_str = ""
        for report_filter in report_header.report_filters:
            report_filters_str += f"{report_filter.name}={report_filter.value}; "
            if report_filter.name == "Metric_Type":
                metric_types_str += f"{report_filter.value}; "
            if report_filter.name == "Begin_Date" or report_filter.name == "End_Date":
                reporting_period_str += f"{report_filter.name}={report_filter.value}; "
        csv_writer.writerow(["Metric_Types", metric_types_str])
        csv_writer.writerow(["Report_Filters", report_filters_str])

        report_attributes_str = ""
        for report_attribute in report_header.report_attributes:
            report_attributes_str += f"{report_attribute.name}={report_attribute.value}; "
        csv_writer.writerow(["Report_Attributes", report_attributes_str])

        exceptions_str = ""
        for exception in report_header.exceptions:
            exceptions_str += f"{exception.code}={exception.message}; "
        csv_writer.writerow(["Exceptions", exceptions_str])

        csv_writer.writerow(["Reporting_Period", reporting_period_str])
        csv_writer.writerow(["Created", report_header.created])
        csv_writer.writerow(["Created_By", report_header.created_by])
        csv_writer.writerow([])

        # endregion

        # region Report Body

        column_names = []
        row_dicts = []

        if report_type == "PR":
            column_names += ["Platform", "Data_Type", "Access_Method"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Platform": row.platform,
                            "Data_Type": row.data_type,
                            "Access_Method": row.access_method,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

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
            column_names += ["Database", "Publisher", "Publisher_ID", "Platform", "Propriety_ID", "Data_Type",
                             "Access_Method"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Database": row.database,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "Propriety_ID": row.proprietary_id,
                            "Data_Type": row.data_type,
                            "Access_Method": row.access_method,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "DR_D1":
            column_names += ["Database", "Publisher", "Publisher_ID", "Platform", "Propriety_ID"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Database": row.database,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "Propriety_ID": row.proprietary_id,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "DR_D2":
            column_names += ["Database", "Publisher", "Publisher_ID", "Platform", "Propriety_ID"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Database": row.database,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "Propriety_ID": row.proprietary_id,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "ISBN",
                             "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "Data_Type", "Section_Type", "YOP",
                             "Access_Type", "Access_Method"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Propriety_ID": row.proprietary_id,
                            "ISBN": row.isbn,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "Linking_ISSN": row.linking_issn,
                            "URI": row.uri,
                            "Data_Type": row.data_type,
                            "Section_Type": row.section_type,
                            "YOP": row.yop,
                            "Access_Type": row.access_type,
                            "Access_Method": row.access_method,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_B1" or report_type == "TR_B2":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "ISBN",
                             "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "YOP"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Propriety_ID": row.proprietary_id,
                            "ISBN": row.isbn,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "Linking_ISSN": row.linking_issn,
                            "URI": row.uri,
                            "YOP": row.yop,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_B3":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "ISBN",
                             "Print_ISSN", "Online_ISSN", "Linking_ISSN", "URI", "YOP", "Access_Type"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Propriety_ID": row.proprietary_id,
                            "ISBN": row.isbn,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "Linking_ISSN": row.linking_issn,
                            "URI": row.uri,
                            "YOP": row.yop,
                            "Access_Type": row.access_type,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_J1" or report_type == "TR_J2":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "Print_ISSN",
                             "Online_ISSN", "Linking_ISSN", "URI"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Propriety_ID": row.proprietary_id,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "Linking_ISSN": row.linking_issn,
                            "URI": row.uri,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_J3":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "Print_ISSN",
                             "Online_ISSN", "Linking_ISSN", "URI", "Access_Type"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Propriety_ID": row.proprietary_id,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "Linking_ISSN": row.linking_issn,
                            "URI": row.uri,
                            "Access_Type": row.access_type,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "TR_J4":
            column_names += ["Title", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "Print_ISSN",
                             "Online_ISSN", "Linking_ISSN", "URI", "YOP"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Title": row.title,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Propriety_ID": row.proprietary_id,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "Linking_ISSN": row.linking_issn,
                            "URI": row.uri,
                            "YOP": row.yop,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "IR":
            column_names += ["Item", "Publisher", "Publisher_ID", "Platform", "Authors", "Publication_Date",
                             "Article_version", "DOI", "Propriety_ID", "ISBN", "Print_ISSN", "Online_ISSN",
                             "Linking_ISSN", "URI", "Parent_Title", "Parent_Authors", "Parent_Publication_Date",
                             "Parent_Article_Version", "Parent_Data_Type", "Parent_DOI", "Parent_Proprietary_ID",
                             "Parent_ISBN", "Parent_Print_ISSN", "Parent_Online_ISSN", "Parent_URI", "Data_Type",
                             "YOP", "Access_Type", "Access_Method"]

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
                            "Propriety_ID": row.proprietary_id,
                            "ISBN": row.isbn,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "Linking_ISSN": row.linking_issn,
                            "URI": row.uri,
                            "Parent_Title": row.parent_title,
                            "Parent_Authors": row.parent_authors,
                            "Parent_Publication_Date": row.parent_publication_date,
                            "Parent_Article_Version": row.parent_article_version,
                            "Parent_Data_Type": row.uri,
                            "Parent_DOI": row.parent_doi,
                            "Parent_Proprietary_ID": row.parent_proprietary_id,
                            "Parent_ISBN": row.parent_isbn,
                            "Parent_Print_ISSN": row.parent_print_issn,
                            "Parent_Online_ISSN": row.parent_online_issn,
                            "Parent_URI": row.parent_uri,
                            "Data_Type": row.data_type,
                            "YOP": row.yop,
                            "Access_Type": row.access_type,
                            "Access_Method": row.access_method,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        elif report_type == "IR_A1":
            column_names += ["Item", "Publisher", "Publisher_ID", "Platform", "Authors", "Publication_Date",
                             "Article_version", "DOI", "Propriety_ID", "Print_ISSN", "Online_ISSN", "Linking_ISSN",
                             "URI", "Parent_Title", "Parent_Authors", "Parent_Article_Version", "Parent_DOI",
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
                            "Propriety_ID": row.proprietary_id,
                            "Print_ISSN": row.print_issn,
                            "Online_ISSN": row.online_issn,
                            "Linking_ISSN": row.linking_issn,
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
            column_names += ["Item", "Publisher", "Publisher_ID", "Platform", "DOI", "Propriety_ID", "URI"]

            row: ReportRow
            for row in report_rows:
                row_dict = {"Item": row.item,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "DOI": row.doi,
                            "Propriety_ID": row.proprietary_id,
                            "URI": row.uri,
                            "Metric_Type": row.metric_type,
                            "Reporting_Period_Total": row.total_count}
                row_dict.update(row.month_counts)

                row_dicts.append(row_dict)

        column_names += [
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
        csv_dict_writer = csv.DictWriter(csv_file, column_names)
        csv_dict_writer.writeheader()
        csv_dict_writer.writerows(row_dicts)

        # endregion

        csv_file.close()

        self.process_result.message = f"Saved as: {file_name}"

    def notify_worker_finished(self):
        self.worker_finished_signal.emit(self.worker_id)
