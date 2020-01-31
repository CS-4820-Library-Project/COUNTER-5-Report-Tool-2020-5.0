from enum import Enum
from urllib.parse import urlencode
from os import path, makedirs
import csv
import json
import requests
import sys
import os

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QDate, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QPushButton, QDateEdit, QDialog, QWidget, QProgressBar, QLabel, QVBoxLayout, \
    QDialogButtonBox, QButtonGroup, QCheckBox

from ui import MainWindow, MessageDialog, FetchProgressDialog, ReportResultWidget, VendorResultsWidget, DisclaimerDialog
from JsonUtils import JsonModel
from ManageVendors import Vendor
from Search import SearchController

SHOW_DEBUG_MESSAGES = False
TIME_BETWEEN_VENDOR_REQUESTS = 3  # Seconds
CONCURRENT_VENDOR_PROCESSES = 5
CONCURRENT_REPORT_PROCESSES = 5
EMPTY_CELL = ""
NORMAL_TSV_DIR = "./all_data/normal_tsv_files/"
SPECIAL_TSV_DIR = "./all_data/special_tsv_files/"

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
    PLATFORM = "PR"
    DATABASE = "DR"
    TITLE = "TR"
    ITEM = "IR"
    INVALID = "INVALID"


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


def show_message(message: str):
    message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
    message_dialog_ui = MessageDialog.Ui_message_dialog()
    message_dialog_ui.setupUi(message_dialog)

    message_label = message_dialog_ui.message_label
    message_label.setText(message)

    message_dialog.exec_()


class CompletionStatus(Enum):
    SUCCESSFUL = "Successful!"
    FAILED = "Failed!"
    CANCELLED = "Cancelled!"


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

        instances = get_models("Instance", InstanceModel, json_dict)

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
    def __init__(self, code: int = None, message: str = None, severity: str = None, data: str = None):
        self.code = code
        self.message = message
        self.severity = severity
        self.data = data

    @classmethod
    def from_json(cls, json_dict: dict):
        code = int(json_dict["Code"]) if "Code" in json_dict else None
        message = json_dict["Message"] if "Message" in json_dict else None
        severity = json_dict["Severity"] if "Severity" in json_dict else None
        data = json_dict["Data"] if "Data" in json_dict else None

        return cls(code, message, severity, data)


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

        institution_ids = get_models("Institution_ID", TypeValueModel, json_dict)
        report_filters = get_models("Report_Filters", NameValueModel, json_dict)
        report_attributes = get_models("Report_Attributes", NameValueModel, json_dict)
        exceptions = get_models("Exceptions", ExceptionModel, json_dict)

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
                raise RetryLaterException(f"Code: {exception.code}"
                                          f"\nMessage: {exception.message}"
                                          f"\nData: {exception.data}")
            if count == 0:
                exception_messages += f"Code: {exception.code}" \
                                      f"\nMessage: {exception.message}" \
                                      f"\nData: {exception.data}"
            else:
                exception_messages += f"\nCode: {exception.code}" \
                                      f"\nMessage: {exception.message}" \
                                      f"\nData: {exception.data}"
            count += 1

        code = int(json_dict["Code"]) if "Code" in json_dict else None
        message = json_dict["Message"] if "Message" in json_dict else None
        data = json_dict["Data"] if "Data" in json_dict else None
        if code is not None:
            if code == 1011:  # Report Queued for Processing
                raise RetryLaterException(f"Code: {code}"
                                          f"\nMessage: {message}"
                                          f"\nData: {data}")
            if count == 0:
                exception_messages += f"Code: {code}" \
                                      f"\nMessage: {message}" \
                                      f"\nData: {data}"
            else:
                exception_messages += f"\nCode: {code}" \
                                      f"\nMessage: {message}" \
                                      f"\nData: {data}"
            count += 1

        if "Report_Header" in json_dict:
            report_header = ReportHeaderModel.from_json(json_dict["Report_Header"])
            if report_header.exceptions is not None:
                if len(report_header.exceptions) > 0:
                    exception: ExceptionModel
                    for exception in report_header.exceptions:
                        if exception.code == 1011:  # Report Queued for Processing
                            raise RetryLaterException(f"Code: {exception.code}"
                                                      f"\nMessage: {exception.message}"
                                                      f"\nData: {exception.data}")
                        if count == 0:
                            exception_messages += f"Code: {exception.code}" \
                                                  f"\nMessage: {exception.message}" \
                                                  f"\nData: {exception.data}"
                        else:
                            exception_messages += f"\nCode: {exception.code}" \
                                                  f"\nMessage: {exception.message}" \
                                                  f"\nData: {exception.data}"
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

        performances = get_models("Performance", PerformanceModel, json_dict)

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

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        publisher_ids = get_models("Publisher_ID", TypeValueModel, json_dict)
        performances = get_models("Performance", PerformanceModel, json_dict)

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

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        publisher_ids = get_models("Publisher_ID", TypeValueModel, json_dict)
        performances = get_models("Performance", PerformanceModel, json_dict)

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

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        item_contributors = get_models("Item_Contributors", ItemContributorModel, json_dict)
        item_dates = get_models("Item_Dates", TypeValueModel, json_dict)
        item_attributes = get_models("Item_Attributes", TypeValueModel, json_dict)

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

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        item_contributors = get_models("Item_Contributors", ItemContributorModel, json_dict)
        item_dates = get_models("Item_Dates", TypeValueModel, json_dict)
        item_attributes = get_models("Item_Attributes", TypeValueModel, json_dict)
        performances = get_models("Performance", PerformanceModel, json_dict)

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

        item_ids = get_models("Item_ID", TypeValueModel, json_dict)
        item_contributors = get_models("Item_Contributors", ItemContributorModel, json_dict)
        item_dates = get_models("Item_Dates", TypeValueModel, json_dict)
        item_attributes = get_models("Item_Attributes", TypeValueModel, json_dict)
        publisher_ids = get_models("Publisher_ID", TypeValueModel, json_dict)
        item_components = get_models("Item_Component", ItemComponentModel, json_dict)
        performances = get_models("Performance", PerformanceModel, json_dict)

        return cls(item, item_ids, item_contributors, item_dates, item_attributes, platform, publisher, publisher_ids,
                   item_parent, item_components, data_type, yop, access_type, access_method, performances)


def get_models(model_key: str, model_type, json_dict: dict) -> list:
    # This converts json formatted lists into a list of the specified model_type
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


class ReportRow:
    def __init__(self, begin_date: QDate, end_date: QDate):
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

        self.month_counts = {}
        for i in range(12):
            curr_date: QDate
            if QDate(begin_date.year(), i + 1, 1) < begin_date:
                curr_date = QDate(end_date.year(), i + 1, 1)
            else:
                curr_date = QDate(begin_date.year(), i + 1, 1)

            self.month_counts[curr_date.toString("MMM-yyyy")] = 0

        self.total_count = 0


class Attributes:
    def __init__(self):
        # PR, DR, TR, IR
        self.data_type = False
        self.access_method = False
        # TR, IR
        self.yop = False
        self.access_type = False
        # TR
        self.section_type = False
        # IR
        self.authors = False
        self.publication_date = False
        self.article_version = False
        self.include_component_details = False
        self.include_parent_details = False


class RequestData:
    def __init__(self, vendor: Vendor, target_report_types: list, begin_date: QDate, end_date: QDate, save_dir: str,
                 attributes: Attributes = None):
        self.vendor = vendor
        self.target_report_types = target_report_types
        self.begin_date = begin_date
        self.end_date = end_date
        self.save_dir = save_dir
        self.attributes = attributes


class ProcessResult:
    def __init__(self, vendor: Vendor, report_type: str = None):
        self.vendor = vendor
        self.report_type = report_type
        self.completion_status = CompletionStatus.SUCCESSFUL
        self.message = "All Good"
        self.retry = False
        self.file_path = None


class RetryLaterException(Exception):
    pass


# endregion


class FetchReportsController:
    def __init__(self, vendors: list, search_controller: SearchController, main_window_ui: MainWindow.Ui_mainWindow):

        # region General
        self.search_controller = search_controller
        self.vendors = vendors
        self.selected_data = []  # List of ReportData Objects
        self.retry_data = []  # List of (Vendor, list[report_types])>
        self.vendor_workers = {}  # <k = worker_id, v = (VendorWorker, Thread)>
        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0
        self.begin_date = QDate()
        self.end_date = QDate()
        current_date = QDate.currentDate()
        self.basic_begin_date = QDate(current_date.year(), 1, current_date.day())
        self.adv_begin_date = QDate(current_date.year(), 1, current_date.day())
        if current_date.month() != 1:  # If not January
            self.basic_end_date = QDate(current_date.year(), current_date.month() - 1, current_date.day())
            self.adv_end_date = QDate(current_date.year(), current_date.month() - 1, current_date.day())
        else:
            self.basic_end_date = QDate(current_date)
            self.adv_end_date = QDate(current_date)

        self.is_last_fetch_advanced = False
        self.is_cancelling = False
        # endregion

        # region Start Fetch Buttons
        self.fetch_all_btn = main_window_ui.fetch_all_data_button
        self.fetch_all_btn.clicked.connect(self.fetch_all_basic_data)

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
        self.tool_button = main_window_ui.toolButton
        self.tool_button.clicked.connect(self.tool_button_click)

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
        self.begin_date_edit = main_window_ui.begin_date_edit_fetch
        self.begin_date_edit.setDate(self.adv_begin_date)
        self.begin_date_edit.dateChanged.connect(lambda date: self.on_date_changed(date, "adv_begin"))
        self.end_date_edit = main_window_ui.end_date_edit_fetch
        self.end_date_edit.setDate(self.adv_end_date)
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

    def fetch_all_basic_data(self):
        if self.total_processes > 0:
            show_message(f"Waiting for pending processes to complete...")
            if SHOW_DEBUG_MESSAGES: print(f"Waiting for pending processes to complete...")
            return

        if len(self.vendors) == 0:
            show_message("Vendor list is empty")
            return

        self.begin_date = self.basic_begin_date
        self.end_date = self.basic_end_date

        self.selected_data = []
        for i in range(len(self.vendors)):
            request_data = RequestData(self.vendors[i], REPORT_TYPES, self.begin_date, self.end_date,
                                       NORMAL_TSV_DIR)
            self.selected_data.append(request_data)

        self.is_last_fetch_advanced = False
        self.start_progress_dialog()
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        while self.started_processes < len(self.selected_data) and self.started_processes < CONCURRENT_VENDOR_PROCESSES:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1

    def fetch_advanced_data(self):
        if self.total_processes > 0:
            show_message(f"Waiting for pending processes to complete...")
            if SHOW_DEBUG_MESSAGES: print(f"Waiting for pending processes to complete...")
            return

        if len(self.vendors) == 0:
            show_message("Vendor list is empty")
            return

        self.begin_date = self.adv_begin_date
        self.end_date = self.adv_end_date

        self.selected_data = []
        selected_report_types = []
        for i in range(len(REPORT_TYPES)):
            if self.report_type_list_model.item(i).checkState() == Qt.Checked:
                selected_report_types.append(REPORT_TYPES[i])
        if len(selected_report_types) == 0:
            show_message("No report type selected")
            return

        for i in range(len(self.vendors)):
            if self.vendor_list_model.item(i).checkState() == Qt.Checked:
                request_data = RequestData(self.vendors[i], selected_report_types, self.begin_date, self.end_date,
                                           NORMAL_TSV_DIR)
                self.selected_data.append(request_data)
        if len(self.selected_data) == 0:
            show_message("No vendor selected")
            return

        self.start_progress_dialog()
        self.is_last_fetch_advanced = False
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        while self.started_processes < len(self.selected_data) and self.started_processes < CONCURRENT_VENDOR_PROCESSES:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1

    def fetch_vendor_data(self, request_data: RequestData):
        worker_id = request_data.vendor.name
        if worker_id in self.vendor_workers: return  # Avoid processing a vendor twice

        vendor_worker = VendorWorker(worker_id, self.search_controller, request_data)
        vendor_worker.worker_finished_signal.connect(self.on_vendor_worker_finished)
        vendor_thread = QThread()
        self.vendor_workers[worker_id] = vendor_worker, vendor_thread
        vendor_worker.moveToThread(vendor_thread)
        vendor_thread.started.connect(vendor_worker.work)
        vendor_thread.start()

        if SHOW_DEBUG_MESSAGES: print(f"{worker_id}: Added a process, total processes: {self.total_processes}")
        self.update_results_ui(request_data.vendor)

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
        report_result_ui.message_label.mousePressEvent = \
            lambda event: self.open_explorer(event, process_result.file_path)

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
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
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
            show_message("No report selected")
            return

        self.selected_data = []
        for vendor, report_types in self.retry_data:
            request_data = RequestData(vendor, report_types, self.begin_date, self.end_date, NORMAL_TSV_DIR)
            self.selected_data.append(request_data)

        self.start_progress_dialog()
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        while self.started_processes < len(self.selected_data) and self.started_processes < CONCURRENT_VENDOR_PROCESSES:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
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

    def tool_button_click(self):
        disclaimer_dialog = QDialog()
        disclaimer_dialog_ui = DisclaimerDialog.Ui_dialog()
        disclaimer_dialog_ui.setupUi(disclaimer_dialog)

        disclaimer_dialog.exec_()

    def open_explorer(self, event, path: str):

        if path is not None:

            file_path = ""
            file_path_list = path.split('/')

            for index in range(len(file_path_list)):

                if index != (len(file_path_list)-1):
                    file_path = str(file_path) + '\\' + str(file_path_list[index])


            current_Working_Directory = os.getcwd()
            open_Explorer_Path = current_Working_Directory + file_path

            os.system("start explorer %s" % open_Explorer_Path)


class FetchSpecialReportsController:
    def __init__(self, vendors: list, search_controller: SearchController, main_window_ui: MainWindow.Ui_mainWindow):
        # region General
        self.search_controller = search_controller
        self.vendors = vendors
        self.selected_data = []  # List of ReportData Objects
        self.selected_report_type = None
        self.selected_attributes = Attributes()
        self.attribute_options = {
            MajorReportType.PLATFORM: ["Data_Type", "Access_Method"],
            MajorReportType.DATABASE: ["Data_Type", "Access_Method"],
            MajorReportType.TITLE: ["Data_Type", "Section_Type", "YOP", "Access_Type", "Access_Method"],
            MajorReportType.ITEM: ["Authors", "Publication_Date", "Article_Version", "Data_Type", "YOP", "Access_Type",
                                   "Access_Method", "Include_Parent_Details", "Include_Component_Details"]
        }
        self.retry_data = []  # List of (Vendor, list[report_types])>
        self.vendor_workers = {}  # <k = worker_id, v = (VendorWorker, Thread)>
        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0
        current_date = QDate.currentDate()
        self.begin_date = QDate(current_date.year(), 1, current_date.day())
        if current_date.month() != 1:  # If not January
            self.end_date = QDate(current_date.year(), current_date.month() - 1, current_date.day())
        else:
            self.end_date = QDate(current_date)
        self.is_cancelling = False
        # endregion

        # region Start Fetch Button
        self.fetch_special_btn = main_window_ui.fetch_special_data_button
        self.fetch_special_btn.clicked.connect(self.fetch_special_data)
        # endregion

        # region Vendors
        self.vendor_list_view = main_window_ui.vendors_list_view_special
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        for vendor in vendors:
            item = QStandardItem(vendor.name)
            item.setCheckable(True)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

        self.select_vendors_btn = main_window_ui.select_vendors_button_special
        self.select_vendors_btn.clicked.connect(self.select_all_vendors)
        self.deselect_vendors_btn = main_window_ui.deselect_vendors_button_special
        self.deselect_vendors_btn.clicked.connect(self.deselect_all_vendors)
        # endregion

        # region Attributes
        self.attributes_frame = main_window_ui.attributes_frame
        self.attributes_layout = self.attributes_frame.layout()
        # endregion

        # region Report Types
        self.pr_radio_button = main_window_ui.pr_radio_button
        self.dr_radio_button = main_window_ui.dr_radio_button
        self.tr_radio_button = main_window_ui.tr_radio_button
        self.ir_radio_button = main_window_ui.ir_radio_button

        self.pr_radio_button.clicked.connect(lambda checked: self.on_report_type_selected(MajorReportType.PLATFORM))
        self.dr_radio_button.clicked.connect(lambda checked: self.on_report_type_selected(MajorReportType.DATABASE))
        self.tr_radio_button.clicked.connect(lambda checked: self.on_report_type_selected(MajorReportType.TITLE))
        self.ir_radio_button.clicked.connect(lambda checked: self.on_report_type_selected(MajorReportType.ITEM))

        self.pr_radio_button.setChecked(True)
        self.on_report_type_selected(MajorReportType.PLATFORM)

        # endregion

        # region Date Edits
        self.begin_date_edit = main_window_ui.begin_date_edit_special
        self.begin_date_edit.setDate(self.begin_date)
        self.begin_date_edit.dateChanged.connect(lambda date: self.on_date_changed(date, "begin_date"))
        self.end_date_edit = main_window_ui.end_date_edit_special
        self.end_date_edit.setDate(self.end_date)
        self.end_date_edit.dateChanged.connect(lambda date: self.on_date_changed(date, "end_date"))
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
        if date_type == "begin_date":
            self.begin_date = date
            if self.begin_date.year() != self.end_date.year():
                self.end_date.setDate(self.begin_date.year(),
                                      self.end_date.month(),
                                      self.end_date.day())
                self.end_date_edit.setDate(self.end_date)
        elif date_type == "end_date":
            self.end_date = date
            if self.end_date.year() != self.begin_date.year():
                self.begin_date.setDate(self.end_date.year(),
                                        self.begin_date.month(),
                                        self.begin_date.day())
                self.begin_date_edit.setDate(self.begin_date)

    def on_report_type_selected(self, major_report_type: MajorReportType):
        if major_report_type == self.selected_report_type: return

        self.selected_report_type = major_report_type
        self.selected_attributes = Attributes()

        # Remove existing options from ui
        for i in reversed(range(self.attributes_layout.count())):
            widget = self.attributes_layout.itemAt(i).widget()
            # remove it from the layout list
            self.attributes_layout.removeWidget(widget)
            # remove it from the gui
            widget.deleteLater()

        # Add new options
        attribute_options = self.attribute_options[major_report_type]

        for attribute in attribute_options:
            checkbox = QCheckBox(attribute, self.attributes_frame)
            checkbox.toggled.connect(lambda checked, attr=attribute: self.on_attribute_selected(checked, attr))
            self.attributes_layout.addWidget(checkbox)

    def on_attribute_selected(self, checked: bool, attribute: str):
        if checked: setattr(self.selected_attributes, attribute.lower(), True)
        else: setattr(self.selected_attributes, attribute.lower(), False)

    def select_all_vendors(self):
        for i in range(self.vendor_list_model.rowCount()):
            self.vendor_list_model.item(i).setCheckState(Qt.Checked)

    def deselect_all_vendors(self):
        for i in range(self.vendor_list_model.rowCount()):
            self.vendor_list_model.item(i).setCheckState(Qt.Unchecked)

    def fetch_special_data(self):
        if self.total_processes > 0:
            show_message(f"Waiting for pending processes to complete...")
            if SHOW_DEBUG_MESSAGES: print(f"Waiting for pending processes to complete...")
            return

        if len(self.vendors) == 0:
            show_message("Vendor list is empty")
            return

        self.selected_data = []
        selected_report_types = [self.selected_report_type.value]

        for i in range(len(self.vendors)):
            if self.vendor_list_model.item(i).checkState() == Qt.Checked:
                request_data = RequestData(self.vendors[i], selected_report_types, self.begin_date, self.end_date,
                                           SPECIAL_TSV_DIR, self.selected_attributes)
                self.selected_data.append(request_data)
        if len(self.selected_data) == 0:
            show_message("No vendor selected")
            return

        self.start_progress_dialog()
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        while self.started_processes < len(self.selected_data) and self.started_processes < CONCURRENT_VENDOR_PROCESSES:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1

    def fetch_vendor_data(self, request_data: RequestData):
        worker_id = request_data.vendor.name
        if worker_id in self.vendor_workers: return  # Avoid processing a vendor twice

        vendor_worker = VendorWorker(worker_id, self.search_controller, request_data)
        vendor_worker.worker_finished_signal.connect(self.on_vendor_worker_finished)
        vendor_thread = QThread()
        self.vendor_workers[worker_id] = vendor_worker, vendor_thread
        vendor_worker.moveToThread(vendor_thread)
        vendor_thread.started.connect(vendor_worker.work)
        vendor_thread.start()

        if SHOW_DEBUG_MESSAGES: print(f"{worker_id}: Added a process, total processes: {self.total_processes}")
        self.update_results_ui(request_data.vendor)

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
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
            self.started_processes += 1

        elif len(self.vendor_workers) == 0:
            self.finish()

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
            show_message("No report selected")
            return

        self.selected_data = []
        for vendor, report_types in self.retry_data:
            request_data = RequestData(vendor, report_types, self.begin_date, self.end_date, SPECIAL_TSV_DIR,
                                       self.selected_attributes)
            self.selected_data.append(request_data)

        self.start_progress_dialog()
        self.retry_data = []

        self.total_processes = len(self.selected_data)
        self.started_processes = 0
        while self.started_processes < len(self.selected_data) and self.started_processes < CONCURRENT_VENDOR_PROCESSES:
            request_data = self.selected_data[self.started_processes]
            self.fetch_vendor_data(request_data)
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

    def __init__(self, worker_id: str, search_controller: SearchController, request_data: RequestData):
        super().__init__()
        self.worker_id = worker_id
        self.search_controller = search_controller
        self.request_data = request_data
        self.vendor = self.request_data.vendor
        self.target_report_types = self.request_data.target_report_types
        self.reports_to_process = []
        self.started_processes = 0
        self.completed_processes = 0
        self.total_processes = 0

        self.process_result = ProcessResult(self.vendor)
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
            if response.status_code == 200:
                self.process_response(response)
            else:
                self.process_result.completion_status = CompletionStatus.FAILED
                self.process_result.message = f"Unexpected HTTP status code received: {response.status_code}"
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

    def fetch_report(self, vendor: Vendor, report_type: str):
        worker_id = report_type
        if worker_id in self.report_workers: return  # Avoid fetching a report twice, app will crash!!

        report_worker = ReportWorker(worker_id, self.search_controller, report_type, self.request_data)
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

    def __init__(self, worker_id: str, search_controller: SearchController, report_type: str,
                 request_data: RequestData):
        super().__init__()
        self.worker_id = worker_id
        self.search_controller = search_controller
        self.report_type = report_type
        self.vendor = request_data.vendor
        self.begin_date = request_data.begin_date
        self.end_date = request_data.end_date
        self.save_dir = request_data.save_dir
        self.attributes = request_data.attributes

        self.process_result = ProcessResult(self.vendor, self.report_type)

    def work(self):
        if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}-{self.report_type}: Fetching Report")
        request_query = {}
        if self.vendor.customer_id.strip(): request_query["customer_id"] = self.vendor.customer_id
        if self.vendor.requestor_id.strip(): request_query["requestor_id"] = self.vendor.requestor_id
        if self.vendor.api_key.strip(): request_query["api_key"] = self.vendor.api_key
        if self.vendor.platform.strip(): request_query["platform"] = self.vendor.platform
        request_query["begin_date"] = self.begin_date.toString("yyyy-MM")
        request_query["end_date"] = self.end_date.toString("yyyy-MM")

        if self.attributes is not None:
            attributes_str = ""
            attributes_dict = self.attributes.__dict__
            count = 0
            for attribute in attributes_dict.keys():
                if attributes_dict[attribute] and count == 0:
                    attributes_str += attribute
                    count += 1
                elif attributes_dict[attribute] and count > 0:
                    attributes_str += f"|{attribute}"
                    count += 1

            if attributes_str: request_query["attributes_to_show"] = attributes_str

        request_url = f"{self.vendor.base_url}/{self.report_type.lower()}"

        try:
            # Some vendors only work if they think a web browser is making the request...
            response = requests.get(request_url, request_query, headers={'User-Agent': 'Mozilla/5.0'})
            if SHOW_DEBUG_MESSAGES: print(response.url)
            if response.status_code == 200:
                self.process_response(response)
            else:
                self.process_result.completion_status = CompletionStatus.FAILED
                self.process_result.message = f"Unexpected HTTP status code received: {response.status_code}"
            if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}-{self.report_type}: Done")
        except requests.exceptions.RequestException as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = f"Request Exception: {e}"
            if SHOW_DEBUG_MESSAGES: print(
                f"{self.vendor.name}-{self.report_type}: Request Exception: {e}")

        self.notify_worker_finished()

    def process_response(self, response: requests.Response):
        try:
            json_dict = response.json()
            report_model = ReportModel.from_json(json_dict)
            self.process_report_model(report_model)
        except json.JSONDecodeError as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            if e.msg == "Expecting value":
                self.process_result.message = f"Vendor did not return any data"
            else:
                self.process_result.message = f"JSON Exception: {e.msg}"
            if SHOW_DEBUG_MESSAGES: print(
                f"{self.vendor.name}-{self.report_type}: JSON Exception: {e.msg}")
        except RetryLaterException as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = str(e)
            self.process_result.retry = True
            if SHOW_DEBUG_MESSAGES: print(
                f"{self.vendor.name}-{self.report_type}: Retry Later Exception: {e}")
        except Exception as e:
            self.process_result.completion_status = CompletionStatus.FAILED
            self.process_result.message = str(e)
            if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}-{self.report_type}: Exception: {e}")

    def process_report_model(self, report_model: ReportModel):
        report_type = report_model.report_header.report_id
        major_report_type = report_model.report_header.major_report_type
        report_items = report_model.report_items
        report_rows = []
        file_dir = f"{NORMAL_TSV_DIR}/{self.begin_date.toString('yyyy')}/{self.vendor.name}/"
        file_name = f"{self.begin_date.toString('yyyy')}_{self.vendor.name}_{report_type}.tsv"
        file_path = f"{file_dir}/{file_name}"

        if SHOW_DEBUG_MESSAGES: print(f"{self.vendor.name}-{self.report_type}: Processing report")

        for report_item in report_items:
            row_dict = {}  # <k = metric_type, v = ReportRow>

            performance: PerformanceModel
            for performance in report_item.performances:
                begin_month = QDate.fromString(performance.period.begin_date, "yyyy-MM-dd").toString("MMM-yyyy")

                instance: InstanceModel
                for instance in performance.instances:
                    metric_type = instance.metric_type
                    if metric_type not in row_dict:
                        report_row = ReportRow(self.begin_date, self.end_date)
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

        self.save_tsv_file(report_model.report_header, report_rows)

    def save_tsv_file(self, report_header, report_rows: list):
        report_type = report_header.report_id
        major_report_type = report_header.major_report_type
        file_dir = f"{self.save_dir}{self.begin_date.toString('yyyy')}/{self.vendor.name}/"
        file_name = f"{self.begin_date.toString('yyyy')}_{self.vendor.name}_{report_type}.tsv"
        file_path = f"{file_dir}{file_name}"

        if not path.isdir(file_dir):
            makedirs(file_dir)

        tsv_file = open(file_dir + file_name, 'w', encoding="utf-8", newline='')

        # region Report Header

        tsv_writer = csv.writer(tsv_file, delimiter='\t')
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

        # endregion

        if len(report_rows) == 0:
            tsv_file.close()
            self.process_result.message = f"Empty report saved as: {file_name}"
            return

        # region Report Body

        column_names = []
        row_dicts = []

        if report_type == "PR":
            column_names += ["Platform"]
            if self.attributes:
                if self.attributes.data_type: column_names.append("Data_Type")
                if self.attributes.access_method: column_names.append("Access_Method")

            row: ReportRow
            for row in report_rows:
                row_dict = {"Platform": row.platform}
                if self.attributes:
                    if self.attributes.data_type: row_dict["Data_Type"] = row.data_type
                    if self.attributes.access_method: row_dict["Access_Method"] = row.access_method

                row_dict.update({"Metric_Type": row.metric_type,
                                 "Reporting_Period_Total": row.total_count})
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
            column_names += ["Database", "Publisher", "Publisher_ID", "Platform", "Proprietary_ID"]
            if self.attributes:
                if self.attributes.data_type: column_names.append("Data_Type")
                if self.attributes.access_method: column_names.append("Access_Method")

            row: ReportRow
            for row in report_rows:
                row_dict = {"Database": row.database,
                            "Publisher": row.publisher,
                            "Publisher_ID": row.publisher_id,
                            "Platform": row.platform,
                            "Proprietary_ID": row.proprietary_id}

                if self.attributes:
                    if self.attributes.data_type: row_dict["Data_Type"] = row.data_type
                    if self.attributes.access_method: row_dict["Access_Method"] = row.access_method

                row_dict.update({"Metric_Type": row.metric_type,
                                 "Reporting_Period_Total": row.total_count})
                row_dict.update(row.month_counts)

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
            if self.attributes:
                if self.attributes.data_type: column_names.append("Data_Type")
                if self.attributes.section_type: column_names.append("Section_Type")
                if self.attributes.yop: column_names.append("YOP")
                if self.attributes.access_type: column_names.append("Access_Type")
                if self.attributes.access_method: column_names.append("Access_Method")

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

                if self.attributes:
                    if self.attributes.data_type: row_dict["Data_Type"] = row.data_type
                    if self.attributes.section_type: row_dict["Section_Type"] = row.section_type
                    if self.attributes.yop: row_dict["YOP"] = row.yop
                    if self.attributes.access_type: row_dict["Access_Type"] = row.access_type
                    if self.attributes.access_method: row_dict["Access_Method"] = row.access_method

                row_dict.update({"Metric_Type": row.metric_type,
                                 "Reporting_Period_Total": row.total_count})
                row_dict.update(row.month_counts)

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
            if self.attributes:
                if self.attributes.authors: column_names.append("Authors")
                if self.attributes.publication_date: column_names.append("Publication_Date")
                if self.attributes.article_version: column_names.append("Article_version")
            column_names += ["DOI", "Proprietary_ID", "ISBN", "Print_ISSN", "Online_ISSN", "URI"]
            if self.attributes:
                if self.attributes.include_parent_details:
                    column_names += ["Parent_Title", "Parent_Authors", "Parent_Publication_Date",
                                     "Parent_Article_Version", "Parent_Data_Type", "Parent_DOI",
                                     "Parent_Proprietary_ID", "Parent_ISBN", "Parent_Print_ISSN", "Parent_Online_ISSN",
                                     "Parent_URI"]
                if self.attributes.data_type: column_names.append("Data_Type")
                if self.attributes.yop: column_names.append("YOP")
                if self.attributes.access_type: column_names.append("Access_Type")
                if self.attributes.access_method: column_names.append("Access_Method")

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

                if self.attributes:
                    if self.attributes.authors: row_dict["Authors"] = row.authors
                    if self.attributes.publication_date: row_dict["Publication_Date"] = row.publication_date
                    if self.attributes.article_version: row_dict["Article_version"] = row.article_version
                    if self.attributes.include_parent_details:
                        row_dict.update({"Parent_Title": row.parent_title,
                                         "Parent_Authors": row.parent_authors,
                                         "Parent_Publication_Date": row.parent_publication_date,
                                         "Parent_Article_Version": row.parent_article_version,
                                         "Parent_Data_Type": row.uri,
                                         "Parent_DOI": row.parent_doi,
                                         "Parent_Proprietary_ID": row.parent_proprietary_id,
                                         "Parent_ISBN": row.parent_isbn,
                                         "Parent_Print_ISSN": row.parent_print_issn,
                                         "Parent_Online_ISSN": row.parent_online_issn,
                                         "Parent_URI": row.parent_uri})
                    if self.attributes.data_type: row_dict["Data_Type"] = row.data_type
                    if self.attributes.yop: row_dict["YOP"] = row.yop
                    if self.attributes.access_type: row_dict["Access_Type"] = row.access_type
                    if self.attributes.access_method: row_dict["Access_Method"] = row.access_method

                row_dict.update({"Metric_Type": row.metric_type,
                                 "Reporting_Period_Total": row.total_count})
                row_dict.update(row.month_counts)

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
        column_names += report_rows[0].month_counts.keys()
        tsv_dict_writer = csv.DictWriter(tsv_file, column_names, delimiter='\t')
        tsv_dict_writer.writeheader()
        tsv_dict_writer.writerows(row_dicts)

        # endregion

        tsv_file.close()
        self.process_result.message = f"Saved as: {file_name}"
        self.process_result.file_path = file_path

    def notify_worker_finished(self):
        self.worker_finished_signal.emit(self.worker_id)
