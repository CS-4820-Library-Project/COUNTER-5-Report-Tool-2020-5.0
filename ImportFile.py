import csv
from collections import OrderedDict
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QModelIndex, QDate, Qt
from PyQt5.QtWidgets import QListView, QPushButton, QDateEdit, QDialog, QFileDialog, QLabel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from ui import MainWindow, MessageDialog
from Search import SearchController
import FetchData


class ImportFileController:
    def __init__(self, vendors: list, search_controller: SearchController, main_window_ui: MainWindow.Ui_mainWindow):

        self.vendors = vendors
        self.search_controller = search_controller
        self.date = QDate.currentDate()
        self.selected_vendor_index = -1
        self.selected_report_type = -1
        self.selected_file_name: str = ""
        self.selected_file_path: str = ""

        self.vendor_list_view = main_window_ui.vendors_list_view_import
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        self.vendor_list_view.clicked.connect(self.on_vendor_selected)
        self.update_vendors_ui()

        self.report_type_list_view = main_window_ui.report_types_list_view_import
        self.report_type_list_model = QStandardItemModel(self.report_type_list_view)
        self.report_type_list_view.setModel(self.report_type_list_model)
        self.report_type_list_view.clicked.connect(self.on_report_type_selected)
        for report_type in FetchData.REPORT_TYPES:
            item = QStandardItem(report_type)
            item.setEditable(False)
            self.report_type_list_model.appendRow(item)

        self.year_date_edit = main_window_ui.report_year_date_edit
        self.year_date_edit.setDate(self.date)
        self.year_date_edit.dateChanged.connect(self.on_date_changed)

        self.select_file_btn = main_window_ui.select_file_button
        self.select_file_btn.clicked.connect(self.open_file_select_dialog)

        self.selected_file_label = main_window_ui.selected_file_label

        self.import_file_button = main_window_ui.import_file_button
        self.import_file_button.clicked.connect(self.import_csv_file)

    def on_vendors_changed(self):
        self.selected_vendor_index = -1
        self.update_vendors_ui()

    def update_vendors_ui(self):
        self.vendor_list_model.removeRows(0, self.vendor_list_model.rowCount())
        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

    def on_vendor_selected(self, model_index: QModelIndex):
        self.selected_vendor_index = model_index.row()

    def on_report_type_selected(self, model_index: QModelIndex):
        self.selected_report_type = model_index.row()

    def on_date_changed(self, date: QDate):
        self.date = date

    def open_file_select_dialog(self):
        print("Select file")
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("All CSV files (*.csv)")
        if dialog.exec_():
            self.selected_file_path = dialog.selectedFiles()[0]
            arr = self.selected_file_path.split("/")
            self.selected_file_name = arr[len(arr) - 1]
            self.selected_file_label.setText(self.selected_file_name)

    def import_csv_file(self):
        print("import file")
        if self.selected_vendor_index == -1:
            self.show_message("Select a vendor")
            return
        elif self.selected_report_type == -1:
            self.show_message("Select a report type")
            return
        elif self.selected_file_name == "":
            self.show_message("Select a file")
            return

        try:
            print()
        except csv.Error as e:
            self.show_message(f"csv error: {e}")
        except Exception as e:
            self.show_message(f"Exception: {e}")

    def show_message(self, message: str):
        message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        message_dialog_ui = MessageDialog.Ui_message_dialog()
        message_dialog_ui.setupUi(message_dialog)

        message_label = message_dialog_ui.message_label
        message_label.setText(message)

        message_dialog.exec_()


