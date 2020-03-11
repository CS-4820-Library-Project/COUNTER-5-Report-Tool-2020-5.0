from enum import Enum
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QDialog, QFileDialog, QLabel, QVBoxLayout, QSizePolicy, QWidget
from ui import SettingsTab, MessageDialog, UpdateDatabaseProgressDialog
from JsonUtils import JsonModel
import json
import DataStorage
import ManageDB

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
    def __init__(self, settings_ui: SettingsTab.Ui_settings_tab):
        # region General
        json_string = DataStorage.read_json_file(SETTINGS_FILE_DIR + SETTINGS_FILE_NAME)
        json_dict = json.loads(json_string)
        self.settings = SettingsModel.from_json(json_dict)
        # endregion

        # region Reports
        self.yearly_dir_edit = settings_ui.yearly_directory_edit
        self.other_dir_edit = settings_ui.other_directory_edit

        settings_ui.yearly_directory_button.clicked.connect(
            lambda: self.open_file_select_dialog(Setting.YEARLY_DIR))
        settings_ui.other_directory_button.clicked.connect(
            lambda: self.open_file_select_dialog(Setting.OTHER_DIR))

        self.yearly_dir_edit.setText(self.settings.yearly_directory)
        self.other_dir_edit.setText(self.settings.other_directory)
        settings_ui.request_interval_spin_box.setValue(self.settings.request_interval)
        settings_ui.request_timeout_spin_box.setValue(self.settings.request_timeout)
        settings_ui.concurrent_vendors_spin_box.setValue(self.settings.concurrent_vendors)
        settings_ui.concurrent_reports_spin_box.setValue(self.settings.concurrent_reports)
        settings_ui.empty_cell_edit.setText(self.settings.empty_cell)
        settings_ui.user_agent_edit.setText(self.settings.user_agent)

        self.yearly_dir_edit.textEdited.connect(
            lambda text: self.on_setting_changed(Setting.YEARLY_DIR, text))
        self.other_dir_edit.textEdited.connect(
            lambda text: self.on_setting_changed(Setting.OTHER_DIR, text))
        settings_ui.request_interval_spin_box.valueChanged.connect(
            lambda value: self.on_setting_changed(Setting.REQUEST_INTERVAL, value))
        settings_ui.request_timeout_spin_box.valueChanged.connect(
            lambda value: self.on_setting_changed(Setting.REQUEST_TIMEOUT, value))
        settings_ui.concurrent_vendors_spin_box.valueChanged.connect(
            lambda value: self.on_setting_changed(Setting.CONCURRENT_VENDORS, value))
        settings_ui.concurrent_reports_spin_box.valueChanged.connect(
            lambda value: self.on_setting_changed(Setting.CONCURRENT_REPORTS, value))
        settings_ui.empty_cell_edit.textEdited.connect(
            lambda text: self.on_setting_changed(Setting.EMPTY_CELL, text))
        settings_ui.user_agent_edit.textEdited.connect(
            lambda text: self.on_setting_changed(Setting.USER_AGENT, text))
        # endregion

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
        self.restore_database_button = settings_ui.settings_restore_database_button

        self.restore_database_progress_dialog = None

        self.restore_database_thread = None

        self.database_worker = None

        self.restore_status_label = None
        self.restore_progress_bar = None
        self.restore_task_finished_widget = None
        self.restore_task_finished_scrollarea = None

        self.restore_database_button.clicked.connect(self.on_restore_database_clicked)

        self.is_restoring_database = False

    def on_setting_changed(self, setting: Setting, setting_value):
        if setting == Setting.YEARLY_DIR:
            self.settings.yearly_directory = setting_value
        elif setting == Setting.OTHER_DIR:
            self.settings.other_directory = setting_value
        elif setting == Setting.REQUEST_INTERVAL:
            self.settings.request_interval = int(setting_value)
        elif setting == Setting.REQUEST_TIMEOUT:
            self.settings.request_timeout = int(setting_value)
        elif setting == Setting.CONCURRENT_VENDORS:
            self.settings.concurrent_vendors = int(setting_value)
        elif setting == Setting.CONCURRENT_REPORTS:
            self.settings.concurrent_reports = int(setting_value)
        elif setting == Setting.EMPTY_CELL:
            self.settings.empty_cell = setting_value
        elif setting == Setting.USER_AGENT:
            self.settings.user_agent = setting_value

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

    def on_restore_database_clicked(self):
        if not self.is_restoring_database:  # check if already running
            self.is_restoring_database = True
            self.restore_database()
            self.is_restoring_database = False
        else:
            print('Error, already running')

    def restore_database(self):
        files = ManageDB.get_all_reports()  # get list of all files

        self.restore_database_progress_dialog = QDialog()

        dialog_ui = UpdateDatabaseProgressDialog.Ui_restore_database_dialog()
        dialog_ui.setupUi(self.restore_database_progress_dialog)

        self.restore_status_label = dialog_ui.status_label
        self.restore_progress_bar = dialog_ui.progressbar
        self.restore_task_finished_scrollarea = dialog_ui.scrollarea

        self.restore_task_finished_widget = QWidget()
        self.restore_task_finished_widget.setLayout(QVBoxLayout())
        self.restore_task_finished_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.restore_task_finished_scrollarea.setWidget(self.restore_task_finished_widget)

        self.restore_progress_bar.setMaximum(len(files) + 1)

        self.restore_database_progress_dialog.show()

        self.restore_database_thread = QThread()

        self.database_worker = ManageDB.UpdateDatabaseWorker(files, True)

        self.database_worker.status_changed_signal.connect(lambda status: on_status_changed(status))
        self.database_worker.progress_changed_signal.connect(lambda progress: on_progress_changed(progress))
        self.database_worker.task_finished_signal.connect(lambda task: on_task_finished(task))
        self.database_worker.worker_finished_signal.connect(lambda code: on_thread_finish(code))

        self.database_worker.moveToThread(self.restore_database_thread)

        self.restore_database_thread.started.connect(self.database_worker.work)

        self.restore_database_thread.start()

        def on_status_changed(status: str):
            self.restore_status_label.setText(status)

        def on_progress_changed(progress: int):
            self.restore_progress_bar.setValue(progress)

        def on_task_finished(task: str):
            label = QLabel(task)
            label.setMinimumSize(label.sizeHint())
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.restore_task_finished_widget.layout().addWidget(label)

        def on_thread_finish(code):
            print(code)  # testing
            # exit thread
            self.restore_database_thread.quit()
            self.restore_database_thread.wait()
