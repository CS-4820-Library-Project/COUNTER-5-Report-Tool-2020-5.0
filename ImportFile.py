import shutil
import webbrowser
from os import path, makedirs
from PyQt5.QtCore import QModelIndex, QDate, Qt
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtWidgets
from ui import MainWindow, MessageDialog, ReportResultWidget
from FetchData import REPORT_TYPES
from Settings import SettingsModel


class ImportFileController:
    def __init__(self, vendors: list, settings: SettingsModel, main_window_ui: MainWindow.Ui_mainWindow):

        # region General
        self.vendors = vendors
        self.date = QDate.currentDate()
        self.selected_vendor_index = -1
        self.selected_report_type_index = -1
        self.selected_file_name: str = ""
        self.selected_file_path: str = ""
        self.settings = settings
        self.result_dialog = None
        # endregion

        # region Vendors
        self.vendor_list_view = main_window_ui.vendors_list_view_import
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        self.vendor_list_view.clicked.connect(self.on_vendor_selected)
        self.update_vendors_ui()
        # endregion

        # region Report Types
        self.report_type_list_view = main_window_ui.report_types_list_view_import
        self.report_type_list_model = QStandardItemModel(self.report_type_list_view)
        self.report_type_list_view.setModel(self.report_type_list_model)
        self.report_type_list_view.clicked.connect(self.on_report_type_selected)
        for report_type in REPORT_TYPES:
            item = QStandardItem(report_type)
            item.setEditable(False)
            self.report_type_list_model.appendRow(item)
        # endregion

        # region Others
        self.year_date_edit = main_window_ui.report_year_date_edit
        self.year_date_edit.setDate(self.date)
        self.year_date_edit.dateChanged.connect(self.on_date_changed)

        self.select_file_btn = main_window_ui.select_file_button
        self.select_file_btn.clicked.connect(self.open_file_select_dialog)

        self.selected_file_label = main_window_ui.selected_file_label

        self.import_file_button = main_window_ui.import_file_button
        self.import_file_button.clicked.connect(self.import_file)
        # endregion

    def on_vendors_changed(self, vendors: list):
        self.vendors = vendors
        self.selected_vendor_index = -1
        self.update_vendors_ui()

    def update_vendors_ui(self):
        self.vendor_list_model.clear()
        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

    def on_vendor_selected(self, model_index: QModelIndex):
        self.selected_vendor_index = model_index.row()

    def on_report_type_selected(self, model_index: QModelIndex):
        self.selected_report_type_index = model_index.row()

    def on_date_changed(self, date: QDate):
        self.date = date

    def open_file_select_dialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("All TSV files (*.tsv)")
        if dialog.exec_():
            self.selected_file_path = dialog.selectedFiles()[0]
            arr = self.selected_file_path.split("/")
            self.selected_file_name = arr[len(arr) - 1]
            self.selected_file_label.setText(self.selected_file_name)

    def import_file(self):
        if self.selected_vendor_index == -1:
            self.show_message("Select a vendor")
            return
        elif self.selected_report_type_index == -1:
            self.show_message("Select a report type")
            return
        elif self.selected_file_path == "":
            self.show_message("Select a file")
            return

        try:
            vendor = self.vendors[self.selected_vendor_index]
            report_type = REPORT_TYPES[self.selected_report_type_index]
            dest_file_dir = f"{self.settings.yearly_directory}{self.date.toString('yyyy')}/{vendor.name}/"
            dest_file_name = f"{self.date.toString('yyyy')}_{vendor.name}_{report_type}.tsv"
            dest_file_path = f"{dest_file_dir}{dest_file_name}"

            if not path.isdir(dest_file_dir):
                makedirs(dest_file_dir)

            shutil.copy2(self.selected_file_path, dest_file_path)

            # Show result
            self.result_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
            self.result_dialog.setWindowTitle("Import Result")
            vertical_layout = QtWidgets.QVBoxLayout(self.result_dialog)
            vertical_layout.setContentsMargins(5, 5, 5, 5)

            report_result_widget = QWidget(self.result_dialog)
            report_result_ui = ReportResultWidget.Ui_ReportResultWidget()
            report_result_ui.setupUi(report_result_widget)

            report_result_ui.report_type_label.setText(f"{vendor.name} - {report_type}")
            report_result_ui.message_label.hide()
            report_result_ui.file_label.setText(f"Saved as: {dest_file_name}")
            report_result_ui.file_label.mousePressEvent = lambda event: self.open_explorer(dest_file_path)
            report_result_ui.success_label.setText("Successful!")
            report_result_ui.retry_frame.hide()

            vertical_layout.addWidget(report_result_widget)
            self.result_dialog.show()
        except Exception as e:
            self.show_message(f"Exception: {e}")

    def show_message(self, message: str):
        message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        message_dialog_ui = MessageDialog.Ui_message_dialog()
        message_dialog_ui.setupUi(message_dialog)

        message_label = message_dialog_ui.message_label
        message_label.setText(message)

        message_dialog.exec_()

    def open_explorer(self, file_dir: str):
        webbrowser.open(path.realpath(file_dir))


