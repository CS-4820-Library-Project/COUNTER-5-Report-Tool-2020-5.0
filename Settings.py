from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QFileDialog
from ui import MainWindow, MessageDialog
from JsonUtils import JsonModel
import json
import DataStorage

SETTINGS_FILE_DIR = "./all_data/settings/"
SETTINGS_FILE_NAME = "settings.dat"

# Default Settings
GENERAL_TSV_DIR = "./all_data/general_tsv_files/"
SPECIAL_TSV_DIR = "./all_data/special_tsv_files/"
GENERAL_JSON_DIR = "./all_data/general_json_files/"
SPECIAL_JSON_DIR = "./all_data/special_json_files/"
REQUEST_INTERVAL = 3  # Seconds
CONCURRENT_VENDOR_PROCESSES = 5
CONCURRENT_REPORT_PROCESSES = 5
EMPTY_CELL = ""


class SettingsModel(JsonModel):
    def __init__(self, general_tsv_directory: str, special_tsv_directory: str, general_json_directory: str,
                 special_json_directory: str, request_interval: int, concurrent_vendors: int,
                 concurrent_reports: int, empty_cell: str):
        self.general_tsv_directory = general_tsv_directory
        self.special_tsv_directory = special_tsv_directory
        self.general_json_directory = general_json_directory
        self.special_json_directory = special_json_directory
        self.request_interval = request_interval
        self.concurrent_vendors = concurrent_vendors
        self.concurrent_reports = concurrent_reports
        self.empty_cell = empty_cell

    @classmethod
    def from_json(cls, json_dict: dict):
        general_tsv_directory = json_dict["general_tsv_directory"]\
            if "general_tsv_directory" in json_dict else GENERAL_TSV_DIR
        special_tsv_directory = json_dict["special_tsv_directory"]\
            if "special_tsv_directory" in json_dict else SPECIAL_TSV_DIR
        general_json_directory = json_dict["general_json_directory"]\
            if "general_json_directory" in json_dict else GENERAL_JSON_DIR
        special_json_directory = json_dict["special_json_directory"]\
            if "special_json_directory" in json_dict else SPECIAL_JSON_DIR
        request_interval = int(json_dict["request_interval"])\
            if "request_interval" in json_dict else REQUEST_INTERVAL
        concurrent_vendors = int(json_dict["concurrent_vendors"])\
            if "concurrent_vendors" in json_dict else CONCURRENT_VENDOR_PROCESSES
        concurrent_reports = int(json_dict["concurrent_reports"])\
            if "concurrent_reports" in json_dict else CONCURRENT_REPORT_PROCESSES
        empty_cell = json_dict["empty_cell"]\
            if "empty_cell" in json_dict else EMPTY_CELL

        return cls(general_tsv_directory, special_tsv_directory, general_json_directory, special_json_directory,
                   request_interval, concurrent_vendors, concurrent_reports, empty_cell)


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
        settings_json_string = DataStorage.read_json_file(SETTINGS_FILE_DIR + SETTINGS_FILE_NAME)
        settings_dict = json.loads(settings_json_string)
        self.settings = SettingsModel.from_json(settings_dict)
        # endregion

        # region Reports
        self.general_tsv_dir_edit = main_window_ui.general_tsv_directory_edit
        self.special_tsv_dir_edit = main_window_ui.special_tsv_directory_edit
        self.general_json_dir_edit = main_window_ui.general_json_directory_edit
        self.special_json_dir_edit = main_window_ui.special_json_directory_edit

        main_window_ui.general_tsv_directory_button.clicked.connect(
            lambda: self.open_file_select_dialog("general_tsv_directory"))
        main_window_ui.special_tsv_directory_button.clicked.connect(
            lambda: self.open_file_select_dialog("special_tsv_directory"))
        main_window_ui.general_json_directory_button.clicked.connect(
            lambda: self.open_file_select_dialog("general_json_directory"))
        main_window_ui.special_json_directory_button.clicked.connect(
            lambda: self.open_file_select_dialog("special_json_directory"))

        self.general_tsv_dir_edit.setText(self.settings.general_tsv_directory)
        self.special_tsv_dir_edit.setText(self.settings.special_tsv_directory)
        self.general_json_dir_edit.setText(self.settings.general_json_directory)
        self.special_json_dir_edit.setText(self.settings.special_json_directory)
        main_window_ui.request_interval_edit.setText(str(self.settings.request_interval))
        main_window_ui.concurrent_vendors_edit.setText(str(self.settings.concurrent_vendors))
        main_window_ui.concurrent_reports_edit.setText(str(self.settings.concurrent_reports))
        main_window_ui.empty_cell_edit.setText(self.settings.empty_cell)

        self.general_tsv_dir_edit.textEdited.connect(
            lambda text: self.on_setting_changed("general_tsv_directory", text))
        self.special_tsv_dir_edit.textEdited.connect(
            lambda text: self.on_setting_changed("special_tsv_directory", text))
        self.general_json_dir_edit.textEdited.connect(
            lambda text: self.on_setting_changed("general_json_directory", text))
        self.special_json_dir_edit.textEdited.connect(
            lambda text: self.on_setting_changed("special_json_directory", text))
        main_window_ui.request_interval_edit.textEdited.connect(
            lambda text: self.on_setting_changed("request_interval", text))
        main_window_ui.concurrent_vendors_edit.textEdited.connect(
            lambda text: self.on_setting_changed("concurrent_vendors", text))
        main_window_ui.concurrent_reports_edit.textEdited.connect(
            lambda text: self.on_setting_changed("concurrent_reports", text))
        main_window_ui.empty_cell_edit.textEdited.connect(
            lambda text: self.on_setting_changed("empty_cell", text))
        # endregion

        # region Reports Help Messages
        main_window_ui.general_tsv_directory_help_button.clicked.connect(
            lambda: show_message("This is where reports from the 'Fetch Reports' tab will be saved by default"))
        main_window_ui.special_tsv_directory_help_button.clicked.connect(
            lambda: show_message("This is where reports from the 'Fetch Special Reports' tab will be saved by default"))
        main_window_ui.general_json_directory_help_button.clicked.connect(
            lambda: show_message("This is where JSON from the 'Fetch Reports' tab will be saved by default"))
        main_window_ui.special_json_directory_help_button.clicked.connect(
            lambda: show_message("This is where JSON from the 'Fetch Special Reports' tab will be saved by default"))
        main_window_ui.request_interval_help_button.clicked.connect(
            lambda: show_message("The amount of time to wait between each vendor's requests"))
        main_window_ui.concurrent_vendors_help_button.clicked.connect(
            lambda: show_message("The maximum number of vendors to work on at the same time"))
        main_window_ui.concurrent_reports_help_button.clicked.connect(
            lambda: show_message("The maximum number of reports to work on at the same time, per vendor"))
        main_window_ui.empty_cell_help_button.clicked.connect(
            lambda: show_message("Empty cells will be replaced by whatever is in here"))
        # endregion

    def on_setting_changed(self, setting_key: str, setting_value: str):
        if setting_key == "general_tsv_directory":
            self.settings.general_tsv_directory = setting_value
        elif setting_key == "special_tsv_directory":
            self.settings.special_tsv_directory = setting_value
        if setting_key == "general_json_directory":
            self.settings.general_json_directory = setting_value
        elif setting_key == "special_json_directory":
            self.settings.special_json_directory = setting_value
        elif setting_key == "request_interval":
            self.settings.request_interval = int(setting_value)
        elif setting_key == "concurrent_vendors":
            self.settings.concurrent_vendors = int(setting_value)
        elif setting_key == "concurrent_reports":
            self.settings.concurrent_reports = int(setting_value)
        elif setting_key == "empty_cell":
            self.settings.empty_cell = setting_value

        self.save_settings_to_disk()

    def open_file_select_dialog(self, setting: str):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0] + "/"
            if setting == "general_tsv_directory":
                self.general_tsv_dir_edit.setText(directory)
            elif setting == "special_tsv_directory":
                self.special_tsv_dir_edit.setText(directory)
            if setting == "general_json_directory":
                self.general_json_dir_edit.setText(directory)
            elif setting == "special_json_directory":
                self.special_json_dir_edit.setText(directory)

            self.on_setting_changed(setting, directory)

    def save_settings_to_disk(self):
        json_string = json.dumps(self.settings, default=lambda o: o.__dict__)
        DataStorage.save_json_file(SETTINGS_FILE_DIR, SETTINGS_FILE_NAME, json_string)
