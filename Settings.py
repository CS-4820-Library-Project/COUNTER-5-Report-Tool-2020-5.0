import json
from enum import Enum
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QWidget
from ui import SettingsTab, MessageDialog
import ManageDB
import GeneralUtils
from GeneralUtils import JsonModel
from UpdateDatabaseProgressDialogController import UpdateDatabaseProgressDialogController

SETTINGS_FILE_DIR = "./all_data/settings/"
SETTINGS_FILE_NAME = "settings.dat"


class Setting(Enum):
    YEARLY_DIR = 0
    OTHER_DIR = 1
    REQUEST_INTERVAL = 2
    REQUEST_TIMEOUT = 3
    CONCURRENT_VENDORS = 4
    CONCURRENT_REPORTS = 5
    EMPTY_CELL = 6
    USER_AGENT = 7


# Default Settings
YEARLY_DIR = "./all_data/yearly_files/"
OTHER_DIR = "./all_data/other_files/"
REQUEST_INTERVAL = 3  # Seconds
REQUEST_TIMEOUT = 120  # Seconds
CONCURRENT_VENDORS = 5
CONCURRENT_REPORTS = 5
EMPTY_CELL = ""
USER_AGENT = "Mozilla/5.0 Firefox/73.0 Chrome/80.0.3987.132 Safari/605.1.15"


class SettingsModel(JsonModel):
    def __init__(self, yearly_directory: str, other_directory: str, request_interval: int, request_timeout: int,
                 concurrent_vendors: int, concurrent_reports: int, empty_cell: str, user_agent: str):
        self.yearly_directory = yearly_directory
        self.other_directory = other_directory
        self.request_interval = request_interval
        self.request_timeout = request_timeout
        self.concurrent_vendors = concurrent_vendors
        self.concurrent_reports = concurrent_reports
        self.empty_cell = empty_cell
        self.user_agent = user_agent

    @classmethod
    def from_json(cls, json_dict: dict):
        yearly_directory = json_dict["yearly_directory"]\
            if "yearly_directory" in json_dict else YEARLY_DIR
        other_directory = json_dict["other_directory"]\
            if "other_directory" in json_dict else OTHER_DIR
        request_interval = int(json_dict["request_interval"])\
            if "request_interval" in json_dict else REQUEST_INTERVAL
        request_timeout = int(json_dict["request_timeout"])\
            if "request_timeout" in json_dict else REQUEST_TIMEOUT
        concurrent_vendors = int(json_dict["concurrent_vendors"])\
            if "concurrent_vendors" in json_dict else CONCURRENT_VENDORS
        concurrent_reports = int(json_dict["concurrent_reports"])\
            if "concurrent_reports" in json_dict else CONCURRENT_REPORTS
        empty_cell = json_dict["empty_cell"]\
            if "empty_cell" in json_dict else EMPTY_CELL
        user_agent = json_dict["user_agent"]\
            if "user_agent" in json_dict else USER_AGENT

        return cls(yearly_directory, other_directory, request_interval, request_timeout, concurrent_vendors,
                   concurrent_reports, empty_cell, user_agent)


def show_message(message: str):
    message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
    message_dialog_ui = MessageDialog.Ui_message_dialog()
    message_dialog_ui.setupUi(message_dialog)

    message_label = message_dialog_ui.message_label
    message_label.setText(message)

    message_dialog.exec_()


class SettingsController:
    def __init__(self, settings_widget: QWidget, settings_ui: SettingsTab.Ui_settings_tab):
        # region General
        self.settings_widget = settings_widget

        json_string = GeneralUtils.read_json_file(SETTINGS_FILE_DIR + SETTINGS_FILE_NAME)
        json_dict = json.loads(json_string)
        self.settings = SettingsModel.from_json(json_dict)
        # endregion

        # region Reports
        self.yearly_dir_edit = settings_ui.yearly_directory_edit
        self.other_dir_edit = settings_ui.other_directory_edit
        self.request_interval_spin_box = settings_ui.request_interval_spin_box
        self.request_timeout_spin_box = settings_ui.request_timeout_spin_box
        self.concurrent_vendors_spin_box = settings_ui.concurrent_vendors_spin_box
        self.concurrent_reports_spin_box = settings_ui.concurrent_reports_spin_box
        self.empty_cell_edit = settings_ui.empty_cell_edit
        self.user_agent_edit = settings_ui.user_agent_edit

        self.yearly_dir_edit.setText(self.settings.yearly_directory)
        self.other_dir_edit.setText(self.settings.other_directory)
        self.request_interval_spin_box.setValue(self.settings.request_interval)
        self.request_timeout_spin_box.setValue(self.settings.request_timeout)
        self.concurrent_vendors_spin_box.setValue(self.settings.concurrent_vendors)
        self.concurrent_reports_spin_box.setValue(self.settings.concurrent_reports)
        self.empty_cell_edit.setText(self.settings.empty_cell)
        self.user_agent_edit.setText(self.settings.user_agent)

        # region Reports Help Messages
        settings_ui.yearly_directory_help_button.clicked.connect(
            lambda: show_message("This is where yearly files will be saved by default"))
        settings_ui.other_directory_help_button.clicked.connect(
            lambda: show_message("This is where special and non-yearly files will be saved by default"))
        settings_ui.request_interval_help_button.clicked.connect(
            lambda: show_message("The amount of time to wait between a vendor's report requests"))
        settings_ui.request_timeout_help_button.clicked.connect(
            lambda: show_message("The amount of time to wait before cancelling a request"))
        settings_ui.concurrent_vendors_help_button.clicked.connect(
            lambda: show_message("The maximum number of vendors to work on at the same time"))
        settings_ui.concurrent_reports_help_button.clicked.connect(
            lambda: show_message("The maximum number of reports to work on at the same time, per vendor"))
        settings_ui.empty_cell_help_button.clicked.connect(
            lambda: show_message("Empty cells will be replaced by whatever is in here"))
        settings_ui.user_agent_help_button.clicked.connect(
            lambda: show_message("Some vendors only support specific user-agents otherwise, they return error HTTP "
                                 "error codes. Values should be separated by a space"))
        # endregion

        # set up restore database button
        self.is_restoring_database = False
        self.update_database_dialog = UpdateDatabaseProgressDialogController(self.settings_widget)
        self.restore_database_button = settings_ui.settings_restore_database_button
        self.restore_database_button.clicked.connect(self.on_restore_database)

        settings_ui.save_button.clicked.connect(self.on_save_button_clicked)

    def open_file_select_dialog(self, setting: Setting):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0] + "/"
            if setting == Setting.YEARLY_DIR:
                self.yearly_dir_edit.setText(directory)
            elif setting == Setting.OTHER_DIR:
                self.other_dir_edit.setText(directory)

    def on_save_button_clicked(self):
        self.update_settings()
        self.save_settings_to_disk()
        show_message("Changes saved!")

    def update_settings(self):
        self.settings.yearly_directory = self.yearly_dir_edit.text()
        self.settings.other_directory = self.other_dir_edit.text()
        self.settings.request_interval = self.request_interval_spin_box.value()
        self.settings.request_timeout = self.request_timeout_spin_box.value()
        self.settings.concurrent_vendors = self.concurrent_vendors_spin_box.value()
        self.settings.concurrent_reports = self.concurrent_reports_spin_box.value()
        self.settings.empty_cell = self.empty_cell_edit.text()
        self.settings.user_agent = self.user_agent_edit.text()

    def save_settings_to_disk(self):
        json_string = json.dumps(self.settings, default=lambda o: o.__dict__)
        GeneralUtils.save_json_file(SETTINGS_FILE_DIR, SETTINGS_FILE_NAME, json_string)

    def on_restore_database(self):
        if not self.is_restoring_database:  # check if already running
            self.is_restoring_database = True
            self.update_database_dialog.update_database(ManageDB.get_all_reports() + ManageDB.get_all_cost_files(),
                                                        True)
            self.is_restoring_database = False
        else:
            print('Error, already running')
