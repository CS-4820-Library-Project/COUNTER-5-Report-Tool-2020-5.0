from enum import Enum
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QFileDialog
from ui import MainWindow, MessageDialog
from JsonUtils import JsonModel
import json
import DataStorage

SETTINGS_FILE_DIR = "./all_data/settings/"
SETTINGS_FILE_NAME = "settings.dat"


class Setting(Enum):
    YEARLY_DIR = 0
    OTHER_DIR = 1
    REQUEST_INTERVAL = 2
    CONCURRENT_VENDORS = 3
    CONCURRENT_REPORTS = 4
    EMPTY_CELL = 5


# Default Settings
YEARLY_DIR = "./all_data/yearly_files/"
OTHER_DIR = "./all_data/other_files/"
REQUEST_INTERVAL = 3  # Seconds
CONCURRENT_VENDORS = 5
CONCURRENT_REPORTS = 5
EMPTY_CELL = ""


class SettingsModel(JsonModel):
    def __init__(self, yearly_directory: str, other_directory: str, request_interval: int,
                 concurrent_vendors: int, concurrent_reports: int, empty_cell: str):
        self.yearly_directory = yearly_directory
        self.other_directory = other_directory
        self.request_interval = request_interval
        self.concurrent_vendors = concurrent_vendors
        self.concurrent_reports = concurrent_reports
        self.empty_cell = empty_cell

    @classmethod
    def from_json(cls, json_dict: dict):
        yearly_directory = json_dict["yearly_directory"]\
            if "yearly_directory" in json_dict else YEARLY_DIR
        other_directory = json_dict["other_directory"]\
            if "other_directory" in json_dict else OTHER_DIR
        request_interval = int(json_dict["request_interval"])\
            if "request_interval" in json_dict else REQUEST_INTERVAL
        concurrent_vendors = int(json_dict["concurrent_vendors"])\
            if "concurrent_vendors" in json_dict else CONCURRENT_VENDORS
        concurrent_reports = int(json_dict["concurrent_reports"])\
            if "concurrent_reports" in json_dict else CONCURRENT_REPORTS
        empty_cell = json_dict["empty_cell"]\
            if "empty_cell" in json_dict else EMPTY_CELL

        return cls(yearly_directory, other_directory, request_interval, concurrent_vendors,
                   concurrent_reports, empty_cell)


def show_message(message: str):
    message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
    message_dialog_ui = MessageDialog.Ui_message_dialog()
    message_dialog_ui.setupUi(message_dialog)

    message_label = message_dialog_ui.message_label
    message_label.setText(message)

    message_dialog.exec_()


class SettingsController:
    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        # region General
        json_string = DataStorage.read_json_file(SETTINGS_FILE_DIR + SETTINGS_FILE_NAME)
        json_dict = json.loads(json_string)
        self.settings = SettingsModel.from_json(json_dict)
        # endregion

        # region Reports
        self.yearly_dir_edit = main_window_ui.yearly_directory_edit
        self.other_dir_edit = main_window_ui.other_directory_edit

        main_window_ui.yearly_directory_button.clicked.connect(
            lambda: self.open_file_select_dialog(Setting.YEARLY_DIR))
        main_window_ui.other_directory_button.clicked.connect(
            lambda: self.open_file_select_dialog(Setting.OTHER_DIR))

        self.yearly_dir_edit.setText(self.settings.yearly_directory)
        self.other_dir_edit.setText(self.settings.other_directory)
        main_window_ui.request_interval_spin_box.setValue(self.settings.request_interval)
        main_window_ui.concurrent_vendors_spin_box.setValue(self.settings.concurrent_vendors)
        main_window_ui.concurrent_reports_spin_box.setValue(self.settings.concurrent_reports)
        main_window_ui.empty_cell_edit.setText(self.settings.empty_cell)

        self.yearly_dir_edit.textEdited.connect(
            lambda text: self.on_setting_changed(Setting.YEARLY_DIR, text))
        self.other_dir_edit.textEdited.connect(
            lambda text: self.on_setting_changed(Setting.OTHER_DIR, text))
        main_window_ui.request_interval_spin_box.valueChanged.connect(
            lambda value: self.on_setting_changed(Setting.REQUEST_INTERVAL, value))
        main_window_ui.concurrent_vendors_spin_box.valueChanged.connect(
            lambda value: self.on_setting_changed(Setting.CONCURRENT_VENDORS, value))
        main_window_ui.concurrent_reports_spin_box.valueChanged.connect(
            lambda value: self.on_setting_changed(Setting.CONCURRENT_REPORTS, value))
        main_window_ui.empty_cell_edit.textEdited.connect(
            lambda text: self.on_setting_changed(Setting.EMPTY_CELL, text))
        # endregion

        # region Reports Help Messages
        main_window_ui.yearly_directory_help_button.clicked.connect(
            lambda: show_message("This is where yearly files will be saved by default"))
        main_window_ui.other_directory_help_button.clicked.connect(
            lambda: show_message("This is where special and non-yearly files will be saved by default"))
        main_window_ui.request_interval_help_button.clicked.connect(
            lambda: show_message("The amount of time to wait between a vendor's report requests"))
        main_window_ui.concurrent_vendors_help_button.clicked.connect(
            lambda: show_message("The maximum number of vendors to work on at the same time"))
        main_window_ui.concurrent_reports_help_button.clicked.connect(
            lambda: show_message("The maximum number of reports to work on at the same time, per vendor"))
        main_window_ui.empty_cell_help_button.clicked.connect(
            lambda: show_message("Empty cells will be replaced by whatever is in here"))
        # endregion

    def on_setting_changed(self, setting: Setting, setting_value):
        if setting == Setting.YEARLY_DIR:
            self.settings.yearly_directory = setting_value
        elif setting == Setting.OTHER_DIR:
            self.settings.other_directory = setting_value
        elif setting == Setting.REQUEST_INTERVAL:
            self.settings.request_interval = int(setting_value)
        elif setting == Setting.CONCURRENT_VENDORS:
            self.settings.concurrent_vendors = int(setting_value)
        elif setting == Setting.CONCURRENT_REPORTS:
            self.settings.concurrent_reports = int(setting_value)
        elif setting == Setting.EMPTY_CELL:
            self.settings.empty_cell = setting_value

        self.save_settings_to_disk()

    def open_file_select_dialog(self, setting: Setting):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0] + "/"
            if setting == Setting.YEARLY_DIR:
                self.yearly_dir_edit.setText(directory)
            elif setting == Setting.OTHER_DIR:
                self.other_dir_edit.setText(directory)

            self.on_setting_changed(setting, directory)

    def save_settings_to_disk(self):
        json_string = json.dumps(self.settings, default=lambda o: o.__dict__)
        DataStorage.save_json_file(SETTINGS_FILE_DIR, SETTINGS_FILE_NAME, json_string)
