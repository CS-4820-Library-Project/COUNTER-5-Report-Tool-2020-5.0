"""This module handles all operations involving importing reports."""

import shutil
import platform
import ctypes
import csv
from os import path, makedirs
from PyQt5.QtCore import QModelIndex, QDate, Qt
from PyQt5.QtWidgets import QWidget, QDialog, QDialogButtonBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtWidgets

import GeneralUtils
from Constants import *
from ui import ImportReportTab, ReportResultWidget
from ManageVendors import Vendor
from FetchData import ALL_REPORTS, CompletionStatus, ReportRow
from Settings import SettingsModel
from ManageDB import UpdateDatabaseWorker

# COUNTER_4_REPORT_TYPES = ("BR1", "BR2", "BR3", "DB1", "DB2", "JR1", "JR2", "JR5", "PR1")
COUNTER_4_REPORT_TYPES = {
    "BR1": "TR_B1",
    "BR2": "TR_B1",
    "BR3": "TR_B2",
    "JR1": "TR_J1",
    "JR2": "TR_J2",
    "BR1, BR2": "TR_B1",
    "BR1, BR2, BR3, JR1, JR2": "TR"
}


class Counter4ReportHeader:
    def __init__(self, report_type: str, customer: str, institution_id: str, reporting_period: str, date_run: str):
        self.report_type = report_type
        self.customer = customer
        self.institution_id = institution_id
        self.reporting_period = reporting_period
        self.date_run = date_run


class Counter4ReportModel:
    def __init__(self, report_header: Counter4ReportHeader, header_list: list, row_dicts: list):
        self.report_header = report_header
        self.header_list = header_list
        self.row_dicts = row_dicts


class ProcessResult:
    """This holds the results of an import process

    :param vendor: The target vendor
    :param report_type: The target report type
    """
    def __init__(self, vendor: Vendor, report_type: str):
        self.vendor = vendor
        self.report_type = report_type
        self.completion_status = CompletionStatus.SUCCESSFUL
        self.message = ""
        self.file_name = ""
        self.file_dir = ""
        self.file_path = ""


def get_counter5_equivalent(counter4_report_type: str) -> str:
    return COUNTER_4_REPORT_TYPES[counter4_report_type]


class ImportReportController:
    """Controls the Import Report tab

    :param vendors: The list of vendors in the system
    :param settings: The user's settings
    :param import_report_widget: The import report widget.
    :param import_report_ui: The UI for the import_report_widget.
    """
    def __init__(self, vendors: list, settings: SettingsModel, import_report_widget: QWidget,
                 import_report_ui: ImportReportTab.Ui_import_report_tab):

        # region General
        self.import_report_widget = import_report_widget
        self.vendors = vendors
        self.date = QDate.currentDate()
        self.selected_vendor_index = -1
        self.selected_c5_report_type_index = -1
        self.selected_c4_report_type_index = -1
        self.c5_selected_file_path: str = ""
        self.c4_selected_file_paths: list = []
        self.settings = settings
        self.result_dialog = None
        # endregion

        # region Vendors
        self.vendor_combo_box = import_report_ui.vendor_combo_box
        self.vendor_list_model = QStandardItemModel(self.vendor_combo_box)
        self.vendor_combo_box.setModel(self.vendor_list_model)
        self.vendor_combo_box.currentIndexChanged.connect(self.on_vendor_selected)
        self.update_vendors_ui()
        self.selected_vendor_index = self.vendor_combo_box.currentIndex()
        # endregion

        # region Counter 5
        self.c5_report_type_combo_box = import_report_ui.c5_report_type_combo_box
        self.c5_report_type_model = QStandardItemModel(self.c5_report_type_combo_box)
        self.c5_report_type_combo_box.setModel(self.c5_report_type_model)
        self.c5_report_type_combo_box.currentIndexChanged.connect(self.on_c5_report_type_selected)

        for report_type in ALL_REPORTS:
            item = QStandardItem(report_type)
            item.setEditable(False)
            self.c5_report_type_model.appendRow(item)

        self.selected_c5_report_type_index = self.c5_report_type_combo_box.currentIndex()

        self.c5_select_file_btn = import_report_ui.c5_select_file_button
        self.c5_select_file_btn.clicked.connect(self.on_c5_select_file_clicked)

        self.c5_selected_file_edit = import_report_ui.c5_selected_file_edit
        # endregion

        # region Counter 4
        self.c4_report_type_combo_box = import_report_ui.c4_report_type_combo_box
        self.c4_report_type_model = QStandardItemModel(self.c4_report_type_combo_box)
        self.c4_report_type_combo_box.setModel(self.c4_report_type_model)
        self.c4_report_type_combo_box.currentIndexChanged.connect(self.on_c4_report_type_selected)
        self.c4_report_type_equiv_label = import_report_ui.c4_report_type_equiv_label

        for report_type in COUNTER_4_REPORT_TYPES.keys():
            item = QStandardItem(report_type)
            item.setEditable(False)
            self.c4_report_type_model.appendRow(item)

        self.selected_c4_report_type_index = self.c4_report_type_combo_box.currentIndex()
        self.c4_report_type_equiv_label.setText(get_counter5_equivalent(self.c4_report_type_combo_box.currentText()))

        self.c4_select_file_btn = import_report_ui.c4_select_file_button
        self.c4_select_file_btn.clicked.connect(self.on_c4_select_file_clicked)

        self.c4_selected_file_edit = import_report_ui.c4_selected_file_edit

        # endregion

        # region Date
        self.year_date_edit = import_report_ui.report_year_date_edit
        self.year_date_edit.setDate(self.date)
        self.year_date_edit.dateChanged.connect(self.on_date_changed)

        self.import_report_button = import_report_ui.import_report_button
        self.import_report_button.clicked.connect(self.on_import_clicked)
        # endregion

    def on_vendors_changed(self, vendors: list):
        """Handles the signal emitted when the system's vendor list is updated

        :param vendors: An updated list of the system's vendors
        """
        self.update_vendors(vendors)
        self.update_vendors_ui()
        self.selected_vendor_index = self.vendor_combo_box.currentIndex()

    def update_vendors(self, vendors: list):
        """ Updates the local copy of vendors that support report import

        :param vendors: A list of vendors
        """
        self.vendors = vendors

    def update_vendors_ui(self):
        """Updates the UI to show vendors that support report import"""
        self.vendor_list_model.clear()
        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

    def on_vendor_selected(self, index: int):
        """Handles the signal emitted when a vendor is selected"""
        self.selected_vendor_index = index

    def on_c5_report_type_selected(self, index: int):
        """Handles the signal emitted when a report type is selected"""
        self.selected_c5_report_type_index = index

    def on_c4_report_type_selected(self, index: int):
        """Handles the signal emitted when a report type is selected"""
        self.selected_c4_report_type_index = index
        self.c4_report_type_equiv_label.setText(get_counter5_equivalent(self.c4_report_type_combo_box.currentText()))

    def on_date_changed(self, date: QDate):
        """Handles the signal emitted when the target date is changed"""
        self.date = date

    def on_c5_select_file_clicked(self):
        """Handles the signal emitted when the select file button is clicked"""
        file_path = GeneralUtils.choose_file(TSV_FILTER + CSV_FILTER)
        if file_path:
            self.c5_selected_file_path = file_path
            file_name = file_path.split("/")[-1]
            self.c5_selected_file_edit.setText(file_name)

    def on_c4_select_file_clicked(self):
        """Handles the signal emitted when the select file button is clicked"""
        file_paths = GeneralUtils.choose_files(TSV_AND_CSV_FILTER)
        if file_paths:
            self.c4_selected_file_paths = file_paths
            file_names = [file_path.split("/")[-1] for file_path in file_paths]
            self.c4_selected_file_edit.setText(", ".join(file_names))

            cc = Counter4ToCounter5(self.c4_report_type_combo_box.currentText(), file_paths)
            cc.work()

    def on_import_clicked(self):
        """Handles the signal emitted when the import button is clicked"""
        if self.selected_vendor_index == -1:
            GeneralUtils.show_message("Select a vendor")
            return
        elif self.selected_c5_report_type_index == -1:
            GeneralUtils.show_message("Select a report type")
            return
        elif self.c5_selected_file_path == "":
            GeneralUtils.show_message("Select a file")
            return

        vendor = self.vendors[self.selected_vendor_index]
        report_type = ALL_REPORTS[self.selected_c5_report_type_index]

        process_result = self.import_report(vendor, report_type)
        self.show_result(process_result)

    def import_report(self, vendor: Vendor, report_type: str) -> ProcessResult:
        """ Imports the selected file using the selected parameters

        :param vendor: The target vendor
        :param report_type: The target report type
        :raises Exception: If anything goes wrong while importing the report
        """
        process_result = ProcessResult(vendor, report_type)

        try:

            dest_file_dir = GeneralUtils.get_yearly_file_dir(self.settings.yearly_directory, vendor.name, self.date)
            dest_file_name = GeneralUtils.get_yearly_file_name(vendor.name, report_type, self.date)
            dest_file_path = f"{dest_file_dir}{dest_file_name}"

            # Verify that dest_file_dir exists
            if not path.isdir(dest_file_dir):
                makedirs(dest_file_dir)

            # Validate report header
            delimiter = DELIMITERS[self.c5_selected_file_path[-4:].lower()]
            file = open(self.c5_selected_file_path, 'r', encoding='utf-8-sig')
            reader = csv.reader(file, delimiter=delimiter, quotechar='\"')
            if file.mode == 'r':
                header = {}
                for row in range(HEADER_ROWS):  # reads header row data
                    cells = next(reader)
                    if cells:
                        key = cells[0].lower()
                        if key != HEADER_ENTRIES[row]:
                            raise Exception('File has invalid header (missing row ' + HEADER_ENTRIES[row] + ')')
                        else:
                            header[key] = cells[1].strip()
                    else:
                        raise Exception('File has invalid header (missing row ' + HEADER_ENTRIES[row] + ')')
                for row in range(BLANK_ROWS):
                    cells = next(reader)
                    if cells:
                        if cells[0].strip():
                            raise Exception('File has invalid header (not enough blank rows)')
                if header['report_id'] != report_type:
                    raise Exception('File has invalid header (wrong Report_Id)')
                if not header['created']:
                    raise Exception('File has invalid header (no Created date)')
            else:
                raise Exception('Could not open file')

            # Copy selected_file_path to dest_file_path
            self.copy_file(self.c5_selected_file_path, dest_file_path)

            process_result.file_dir = dest_file_dir
            process_result.file_name = dest_file_name
            process_result.file_path = dest_file_path
            process_result.completion_status = CompletionStatus.SUCCESSFUL

            # Save protected tsv file
            protected_file_dir = f"{PROTECTED_DATABASE_FILE_DIR}{self.date.toString('yyyy')}/{vendor.name}/"
            if not path.isdir(protected_file_dir):
                makedirs(protected_file_dir)
                if platform.system() == "Windows":
                    ctypes.windll.kernel32.SetFileAttributesW(PROTECTED_DATABASE_FILE_DIR, 2)  # Hide folder

            protected_file_path = f"{protected_file_dir}{dest_file_name}"
            self.copy_file(self.c5_selected_file_path, protected_file_path)

            # Add file to database
            database_worker = UpdateDatabaseWorker([{'file': protected_file_path,
                                                     'vendor': vendor.name,
                                                     'year': int(self.date.toString('yyyy'))}],
                                                   False)
            database_worker.work()

        except Exception as e:
            process_result.message = f"Exception: {e}"
            process_result.completion_status = CompletionStatus.FAILED

        return process_result

    def copy_file(self, origin_path: str, dest_path: str):
        """Copies a file from origin_path to dest_path"""
        shutil.copy2(origin_path, dest_path)

    def show_result(self, process_result: ProcessResult):
        """Shows the result of the import process to the user

        :param process_result: The result of the import process
        """
        self.result_dialog = QDialog(self.import_report_widget, flags=Qt.WindowCloseButtonHint)
        self.result_dialog.setWindowTitle("Import Result")
        vertical_layout = QtWidgets.QVBoxLayout(self.result_dialog)
        vertical_layout.setContentsMargins(5, 5, 5, 5)

        report_result_widget = QWidget(self.result_dialog)
        report_result_ui = ReportResultWidget.Ui_ReportResultWidget()
        report_result_ui.setupUi(report_result_widget)

        button_box = QtWidgets.QDialogButtonBox(QDialogButtonBox.Ok, self.result_dialog)
        button_box.setCenterButtons(True)
        button_box.accepted.connect(self.result_dialog.accept)

        vendor = process_result.vendor
        report_type = process_result.report_type

        report_result_ui.report_type_label.setText(f"{vendor.name} - {report_type}")
        report_result_ui.success_label.setText(process_result.completion_status.value)

        if process_result.completion_status == CompletionStatus.SUCCESSFUL:
            report_result_ui.message_label.hide()
            report_result_ui.retry_frame.hide()

            report_result_ui.file_label.setText(f"Saved as: {process_result.file_name}")
            report_result_ui.file_label.mousePressEvent = \
                lambda event: GeneralUtils.open_file_or_dir(process_result.file_path)

            report_result_ui.folder_button.clicked.connect(
                lambda: GeneralUtils.open_file_or_dir(process_result.file_dir))

            report_result_ui.success_label.setText("Successful!")
            report_result_ui.retry_frame.hide()

        elif process_result.completion_status == CompletionStatus.FAILED:
            report_result_ui.file_frame.hide()
            report_result_ui.retry_frame.hide()

            report_result_ui.message_label.setText(process_result.message)

        vertical_layout.addWidget(report_result_widget)
        vertical_layout.addWidget(button_box)
        self.result_dialog.show()


class Counter4ToCounter5:
    def __init__(self, c4_report_type: str, file_paths: list):
        self.c4_report_type = c4_report_type
        self.target_report_type = get_counter5_equivalent(c4_report_type)
        self.file_paths = file_paths

        self.final_row_dicts = {}

    def work(self):
        # open each file
        # read each file in to the model
        for file_path in self.file_paths:
            report_model = self.c4_file_to_c4_model(file_path)
            print()

    def c4_file_to_c4_model(self, file_path: str) -> Counter4ReportModel:
        # print(file_path[-4:])
        file = open(file_path, 'r', encoding="utf-8")

        extension = file_path[-4:]
        delimiter = ""
        if extension == ".csv":
            delimiter = ","
        elif extension == ".tsv":
            delimiter = "\t"

        # Process process report header into model
        csv_reader = csv.reader(file, delimiter=delimiter)

        report_type = ""
        customer = ""
        institution_id = ""
        reporting_period = ""
        date_run = ""

        curr_line = 1
        last_header_line = 7

        for row in csv_reader:
            # print(row[0])

            if curr_line == 1:
                report_type = row[0]
            elif curr_line == 2:
                customer = row[0]
            elif curr_line == 3:
                institution_id = row[0]
            elif curr_line == 5:
                reporting_period = row[0]
            elif curr_line == 7:
                date_run = row[0]

            curr_line += 1

            if curr_line > last_header_line:
                break

        report_header = Counter4ReportHeader(report_type, customer, institution_id, reporting_period, date_run)

        # Process process report into model
        csv_dict_reader = csv.DictReader(file, delimiter=delimiter)
        header_dict = csv_dict_reader.fieldnames
        row_dicts = []

        for row in csv_dict_reader:
            # print(row)
            row_dicts.append(row)

        report_model = Counter4ReportModel(report_header, header_dict, row_dicts)

        file.close()

        return report_model




