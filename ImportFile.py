import csv
from collections import OrderedDict
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QModelIndex, QDate, Qt
from PyQt5.QtWidgets import QListView, QPushButton, QDateEdit, QDialog, QFileDialog, QLabel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from ui import MessageDialog
from Search import SearchController
import FetchData


class ImportFileController:
    def __init__(self, vendors: list,
                 search_controller: SearchController,
                 vendor_list_view: QListView,
                 report_type_list_view: QListView,
                 year_date_edit: QDateEdit,
                 select_file_btn: QPushButton,
                 selected_file_label: QLabel,
                 import_file_button: QPushButton):

        self.vendors = vendors
        self.search_controller = search_controller
        self.date = QDate.currentDate()
        self.selected_vendor_index = -1
        self.selected_report_type = -1
        self.selected_file_name: str = ""
        self.selected_file_path: str = ""

        self.vendor_list_view = vendor_list_view
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        self.vendor_list_view.clicked.connect(self.on_vendor_selected)
        for vendor in vendors:
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

        self.report_type_list_view = report_type_list_view
        self.report_type_list_model = QStandardItemModel(self.report_type_list_view)
        self.report_type_list_view.setModel(self.report_type_list_model)
        self.report_type_list_view.clicked.connect(self.on_report_type_selected)
        for report_type in FetchData.REPORT_TYPES:
            item = QStandardItem(report_type)
            item.setEditable(False)
            self.report_type_list_model.appendRow(item)

        self.year_date_edit = year_date_edit
        self.year_date_edit.setDate(self.date)
        self.year_date_edit.dateChanged.connect(self.on_date_changed)

        self.select_file_btn = select_file_btn
        self.select_file_btn.clicked.connect(self.open_file_select_dialog)

        self.selected_file_label = selected_file_label

        self.import_file_button = import_file_button
        self.import_file_button.clicked.connect(self.import_csv_file)

    def on_vendors_size_changed(self):
        self.selected_vendor_index = -1
        self.vendor_list_model.removeRows(0, self.vendor_list_model.rowCount())

        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setCheckable(True)
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


