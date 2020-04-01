"""This module handles all operations involving importing reports."""

import shutil
import platform
import ctypes
import csv
from os import path, makedirs
from PyQt5.QtCore import QModelIndex, QDate, Qt
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5 import QtWidgets

import GeneralUtils
from Constants import *
from ui import ImportReportTab, ReportResultWidget
from ManageVendors import Vendor
from FetchData import ALL_REPORTS, CompletionStatus
from Settings import SettingsModel
from ManageDB import UpdateDatabaseProgressDialogController


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
        self.selected_report_type_index = -1
        self.selected_file_path: str = ""
        self.settings = settings
        self.result_dialog = None
        # endregion

        # region Vendors
        self.vendor_list_view = import_report_ui.vendors_list_view_import
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        self.vendor_list_view.clicked.connect(self.on_vendor_selected)
        self.update_vendors_ui()
        # endregion

        # region Report Types
        self.report_type_list_view = import_report_ui.report_types_list_view_import
        self.report_type_list_model = QStandardItemModel(self.report_type_list_view)
        self.report_type_list_view.setModel(self.report_type_list_model)
        self.report_type_list_view.clicked.connect(self.on_report_type_selected)
        for report_type in ALL_REPORTS:
            item = QStandardItem(report_type)
            item.setEditable(False)
            self.report_type_list_model.appendRow(item)
        # endregion

        # region Others
        self.year_date_edit = import_report_ui.report_year_date_edit
        self.year_date_edit.setDate(self.date)
        self.year_date_edit.dateChanged.connect(self.on_date_changed)

        self.select_file_btn = import_report_ui.select_file_button
        self.select_file_btn.clicked.connect(self.on_select_file_clicked)

        self.selected_file_edit = import_report_ui.selected_file_edit

        self.import_report_button = import_report_ui.import_report_button
        self.import_report_button.clicked.connect(self.on_import_clicked)
        # endregion

        # set up restore database button
        self.is_restoring_database = False
        self.update_database_dialog = UpdateDatabaseProgressDialogController(self.import_report_widget)

    def on_vendors_changed(self, vendors: list):
        """Handles the signal emitted when the system's vendor list is updated

        :param vendors: An updated list of the system's vendors
        """
        self.selected_vendor_index = -1
        self.update_vendors(vendors)
        self.update_vendors_ui()

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

    def on_vendor_selected(self, model_index: QModelIndex):
        """Handles the signal emitted when a vendor is selected"""
        self.selected_vendor_index = model_index.row()

    def on_report_type_selected(self, model_index: QModelIndex):
        """Handles the signal emitted when a report type is selected"""
        self.selected_report_type_index = model_index.row()

    def on_date_changed(self, date: QDate):
        """Handles the signal emitted when the target date is changed"""
        self.date = date

    def on_select_file_clicked(self):
        """Handles the signal emitted when the select file button is clicked"""
        file_path = GeneralUtils.choose_file(TSV_FILTER + CSV_FILTER)
        if file_path:
            self.selected_file_path = file_path
            self.selected_file_edit.setText(file_path)

    def on_import_clicked(self):
        """Handles the signal emitted when the import button is clicked"""
        if self.selected_vendor_index == -1:
            GeneralUtils.show_message("Select a vendor")
            return
        elif self.selected_report_type_index == -1:
            GeneralUtils.show_message("Select a report type")
            return
        elif self.selected_file_path == "":
            GeneralUtils.show_message("Select a file")
            return

        vendor = self.vendors[self.selected_vendor_index]
        report_type = ALL_REPORTS[self.selected_report_type_index]

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
            dest_file_dir = f"{self.settings.yearly_directory}{self.date.toString('yyyy')}/{vendor.name}/"
            dest_file_name = f"{self.date.toString('yyyy')}_{vendor.name}_{report_type}.tsv"
            dest_file_path = f"{dest_file_dir}{dest_file_name}"

            # Verify that dest_file_dir exists
            if not path.isdir(dest_file_dir):
                makedirs(dest_file_dir)

            delimiter = DELIMITERS[self.selected_file_path[-4:].lower()]
            file = open(self.selected_file_path, 'r', encoding='utf-8-sig')
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
                print(report_type)
                if header['report_id'] != report_type:
                    raise Exception('File has invalid header (wrong Report_Id)')
                if not header['created']:
                    raise Exception('File has invalid header (no Created date)')
            else:
                raise Exception('Could not open file')

            # Copy selected_file_path to dest_file_path
            self.copy_file(self.selected_file_path, dest_file_path)

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
            self.copy_file(self.selected_file_path, protected_file_path)

            # Add file to database
            self.is_restoring_database = True
            self.update_database_dialog.update_database([{'file': protected_file_path,
                                                          'vendor': vendor.name,
                                                          'year': int(self.date.toString('yyyy'))}],
                                                        False)
            self.is_restoring_database = False

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

            folder_pixmap = QPixmap("./ui/resources/folder_icon.png")
            report_result_ui.folder_button.setIcon(QIcon(folder_pixmap))
            report_result_ui.folder_button.clicked.connect(
                lambda: GeneralUtils.open_file_or_dir(process_result.file_dir))

            report_result_ui.success_label.setText("Successful!")
            report_result_ui.retry_frame.hide()

        elif process_result.completion_status == CompletionStatus.FAILED:
            report_result_ui.file_frame.hide()
            report_result_ui.retry_frame.hide()

            report_result_ui.message_label.setText(process_result.message)

        vertical_layout.addWidget(report_result_widget)
        self.result_dialog.show()


