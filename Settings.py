from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QFileDialog
from ui import MainWindow, MessageDialog
from JsonUtils import JsonModel
import json
import DataStorage

SETTINGS_FILE_DIR = "./all_data/settings/"
SETTINGS_FILE_NAME = "settings.dat"

# Default Settings
NORMAL_TSV_DIR = "./all_data/normal_tsv_files/"
SPECIAL_TSV_DIR = "./all_data/special_tsv_files/"
REQUEST_INTERVAL = 3  # Seconds
CONCURRENT_VENDOR_PROCESSES = 5
CONCURRENT_REPORT_PROCESSES = 5
EMPTY_CELL = ""


class SettingsModel(JsonModel):
    def __init__(self, general_save_location: str, special_save_location: str, request_interval: int,
                 concurrent_vendors: int, concurrent_reports: int, empty_cell: str):
        self.general_save_location = general_save_location
        self.special_save_location = special_save_location
        self.request_interval = request_interval
        self.concurrent_vendors = concurrent_vendors
        self.concurrent_reports = concurrent_reports
        self.empty_cell = empty_cell

    @classmethod
    def from_json(cls, json_dict: dict):
        general_save_location = json_dict["general_save_location"]\
            if "general_save_location" in json_dict else NORMAL_TSV_DIR
        special_save_location = json_dict["special_save_location"]\
            if "special_save_location" in json_dict else SPECIAL_TSV_DIR
        request_interval = int(json_dict["request_interval"])\
            if "request_interval" in json_dict else REQUEST_INTERVAL
        concurrent_vendors = int(json_dict["concurrent_vendors"])\
            if "concurrent_vendors" in json_dict else CONCURRENT_VENDOR_PROCESSES
        concurrent_reports = int(json_dict["concurrent_reports"])\
            if "concurrent_reports" in json_dict else CONCURRENT_REPORT_PROCESSES
        empty_cell = json_dict["empty_cell"]\
            if "empty_cell" in json_dict else EMPTY_CELL

        return cls(general_save_location, special_save_location, request_interval, concurrent_vendors,
                   concurrent_reports, empty_cell)


def show_message(message: str):
    message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
    message_dialog_ui = MessageDialog.Ui_message_dialog()
    message_dialog_ui.setupUi(message_dialog)

    message_label = message_dialog_ui.message_label
    message_label.setText(message)

    message_dialog.exec_()


class SettingsController(QObject):
    settings_changed_signal = pyqtSignal(SettingsModel)

    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        super().__init__()
        # region General
        settings_json_string = DataStorage.read_json_file(SETTINGS_FILE_DIR + SETTINGS_FILE_NAME)
        settings_dict = json.loads(settings_json_string)
        self.settings_model = SettingsModel.from_json(settings_dict)
        # endregion

        # region Reports
        self.general_save_location_edit = main_window_ui.general_save_location_edit
        self.special_save_location_edit = main_window_ui.special_save_location_edit

        main_window_ui.general_save_location_button.clicked.connect(
            lambda: self.open_file_select_dialog("general_save_location"))
        main_window_ui.special_save_location_button.clicked.connect(
            lambda: self.open_file_select_dialog("special_save_location"))

        self.general_save_location_edit.setText(self.settings_model.general_save_location)
        self.special_save_location_edit.setText(self.settings_model.special_save_location)
        main_window_ui.request_interval_edit.setText(str(self.settings_model.request_interval))
        main_window_ui.concurrent_vendors_edit.setText(str(self.settings_model.concurrent_vendors))
        main_window_ui.concurrent_reports_edit.setText(str(self.settings_model.concurrent_reports))
        main_window_ui.empty_cell_edit.setText(self.settings_model.empty_cell)

        self.general_save_location_edit.textEdited.connect(
            lambda text: self.on_setting_changed("general_save_location", text))
        self.special_save_location_edit.textEdited.connect(
            lambda text: self.on_setting_changed("special_save_location", text))
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
        main_window_ui.general_save_help_button.clicked.connect(
            lambda: show_message("This is where reports from the 'Fetch Reports' tab will be saved by default"))
        main_window_ui.special_save_help_button.clicked.connect(
            lambda: show_message("This is where reports from the 'Fetch Special Reports' tab will be saved by default"))
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
        if setting_key == "general_save_location":
            self.settings_model.general_save_location = setting_value
        elif setting_key == "special_save_location":
            self.settings_model.special_save_location = setting_value
        elif setting_key == "request_interval":
            self.settings_model.request_interval = int(setting_value)
        elif setting_key == "concurrent_vendors":
            self.settings_model.concurrent_vendors = int(setting_value)
        elif setting_key == "concurrent_reports":
            self.settings_model.concurrent_reports = int(setting_value)
        elif setting_key == "empty_cell":
            self.settings_model.empty_cell = setting_value

        self.save_settings_to_disk()
        self.settings_changed_signal.emit(self.settings_model)

    def open_file_select_dialog(self, setting: str):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            save_location = dialog.selectedFiles()[0] + "/"
            if setting == "general_save_location":
                self.general_save_location_edit.setText(save_location)
            elif setting == "special_save_location":
                self.special_save_location_edit.setText(save_location)

            self.on_setting_changed(setting, save_location)

    def save_settings_to_disk(self):
        json_string = json.dumps(self.settings_model, default=lambda o: o.__dict__)
        DataStorage.save_json_file(SETTINGS_FILE_DIR, SETTINGS_FILE_NAME, json_string)
