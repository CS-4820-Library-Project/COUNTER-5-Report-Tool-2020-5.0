"""This module handles all operations involving importing reports."""

import shutil
import platform
import ctypes
import csv
from tempfile import TemporaryDirectory
from os import path, makedirs
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QWidget, QDialog, QDialogButtonBox, QLabel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtWidgets

import GeneralUtils
from Constants import *
from Counter4 import Counter4To5Converter
from ui import ImportReportTab, ReportResultWidget
from ManageVendors import Vendor
from FetchData import CompletionStatus
from Settings import SettingsModel
from ManageDB import UpdateDatabaseWorker


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


def get_c5_equivalent(counter4_report_type: str) -> str:
    return COUNTER_4_REPORT_EQUIVALENTS[counter4_report_type]


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

        self.c5_import_report_button = import_report_ui.c5_import_report_button
        self.c5_import_report_button.clicked.connect(self.on_c5_import_clicked)
        # endregion

        # region Counter 4
        self.c4_report_type_combo_box = import_report_ui.c4_report_type_combo_box
        self.c4_report_type_model = QStandardItemModel(self.c4_report_type_combo_box)
        self.c4_report_type_combo_box.setModel(self.c4_report_type_model)
        self.c4_report_type_combo_box.currentIndexChanged.connect(self.on_c4_report_type_selected)
        self.c4_report_type_equiv_label = import_report_ui.c4_report_type_equiv_label

        for report_type in COUNTER_4_REPORT_EQUIVALENTS.keys():
            item = QStandardItem(report_type)
            item.setEditable(False)
            self.c4_report_type_model.appendRow(item)

        self.selected_c4_report_type_index = self.c4_report_type_combo_box.currentIndex()
        self.c4_report_type_equiv_label.setText(get_c5_equivalent(self.c4_report_type_combo_box.currentText()))

        self.c4_select_file_btn = import_report_ui.c4_select_file_button
        self.c4_select_file_btn.clicked.connect(self.on_c4_select_file_clicked)

        self.c4_selected_files_frame = import_report_ui.c4_selected_files_frame
        self.c4_selected_files_frame_layout = self.c4_selected_files_frame.layout()

        self.c4_import_report_button = import_report_ui.c4_import_report_button
        self.c4_import_report_button.clicked.connect(self.on_c4_import_clicked)

        # endregion

        # region Date
        self.year_date_edit = import_report_ui.report_year_date_edit
        self.year_date_edit.setDate(self.date)
        self.year_date_edit.dateChanged.connect(self.on_date_changed)
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
        self.c4_report_type_equiv_label.setText(get_c5_equivalent(self.c4_report_type_combo_box.currentText()))

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

            # Remove existing options from ui
            for i in reversed(range(self.c4_selected_files_frame_layout.count())):
                widget = self.c4_selected_files_frame_layout.itemAt(i).widget()
                # remove it from the layout list
                self.c4_selected_files_frame_layout.removeWidget(widget)
                # remove it from the gui
                widget.deleteLater()

            # Add new file names
            for file_name in file_names:
                label = QLabel(file_name)
                self.c4_selected_files_frame_layout.addWidget(label)

    def on_c5_import_clicked(self):
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

        process_result = self.import_report(vendor, report_type, self.c5_selected_file_path)
        self.show_results([process_result])

    def on_c4_import_clicked(self):
        """Handles the signal emitted when the import button is clicked"""
        if self.selected_vendor_index == -1:
            GeneralUtils.show_message("Select a vendor")
            return
        elif not self.c4_selected_file_paths:
            GeneralUtils.show_message("Select a file")
            return

        vendor = self.vendors[self.selected_vendor_index]
        report_types = get_c5_equivalent(self.c4_report_type_combo_box.currentText())

        # Check if target C5 file already exists
        existing_report_types = []
        for report_type in report_types.split(", "):
            if self.check_if_c5_report_exists(vendor.name, report_type):
                existing_report_types.append(report_type)

        # Confirm overwrite
        if existing_report_types:
            if not GeneralUtils.ask_confirmation(f"COUNTER 5 [{', '.join(existing_report_types)}] already exist in the "
                                                 "database for this vendor, do you want to overwrite them?"):
                return

        with TemporaryDirectory("") as dir_path:
            converter = Counter4To5Converter(self.vendors[self.selected_vendor_index],
                                             self.c4_report_type_combo_box.currentText(),
                                             self.c4_selected_file_paths,
                                             dir_path + path.sep,
                                             self.year_date_edit.date())
            try:
                c5_file_paths = converter.do_conversion()
            except Exception as e:
                process_result = ProcessResult(vendor, report_types)
                process_result.completion_status = CompletionStatus.FAILED
                process_result.message = "Error converting file. " + str(e)
                self.show_results([process_result])
                return

            process_results = []
            for report_type in c5_file_paths:
                file_path = c5_file_paths[report_type]
                process_result = self.import_report(vendor, report_type, file_path)
                process_results.append(process_result)
                print(process_result.file_path)

            self.show_results(process_results)

    def import_report(self, vendor: Vendor, report_type: str, origin_file_path: str) -> ProcessResult:
        """ Imports the selected file using the selected parameters

        :param vendor: The target vendor
        :param report_type: The target report type
        :param origin_file_path: The path of the file to be imported
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
            delimiter = DELIMITERS[origin_file_path[-4:].lower()]
            file = open(origin_file_path, 'r', encoding='utf-8-sig')
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
            self.copy_file(origin_file_path, dest_file_path)

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
            self.copy_file(origin_file_path, protected_file_path)

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

    def check_if_c5_report_exists(self, vendor_name, report_type) -> bool:
        protected_file_dir = f"{PROTECTED_DATABASE_FILE_DIR}{self.date.toString('yyyy')}/{vendor_name}/"
        protected_file_name = GeneralUtils.get_yearly_file_name(vendor_name, report_type, self.date)
        protected_file_path = f"{protected_file_dir}{protected_file_name}"

        return path.isfile(protected_file_path)

    def copy_file(self, origin_path: str, dest_path: str):
        """Copies a file from origin_path to dest_path"""
        shutil.copy2(origin_path, dest_path)

    def show_results(self, process_results: list):
        """Shows the result of the import process to the user

        :param process_results: The results of the import process
        """
        self.result_dialog = QDialog(self.import_report_widget, flags=Qt.WindowCloseButtonHint)
        self.result_dialog.setWindowTitle("Import Result")
        vertical_layout = QtWidgets.QVBoxLayout(self.result_dialog)
        vertical_layout.setContentsMargins(5, 5, 5, 5)

        for process_result in process_results:
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
                    lambda event, file_path = process_result.file_path: GeneralUtils.open_file_or_dir(file_path)

                report_result_ui.folder_button.clicked.connect(
                    lambda: GeneralUtils.open_file_or_dir(process_result.file_dir))

                report_result_ui.success_label.setText("Successful!")
                report_result_ui.retry_frame.hide()

            elif process_result.completion_status == CompletionStatus.FAILED:
                report_result_ui.file_frame.hide()
                report_result_ui.retry_frame.hide()

                report_result_ui.message_label.setText(process_result.message)

            vertical_layout.addWidget(report_result_widget)

        button_box = QtWidgets.QDialogButtonBox(QDialogButtonBox.Ok, self.result_dialog)
        button_box.setCenterButtons(True)
        button_box.accepted.connect(self.result_dialog.accept)
        vertical_layout.addWidget(button_box)

        self.result_dialog.show()
