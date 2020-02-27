import sys
import pytest
from os import path
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QStandardItemModel
from ui import MainWindow
from ImportFile import ImportFileController
from ManageVendors import Vendor
from FetchData import REPORT_TYPES, CompletionStatus
import Settings
import DataStorage
import json


@pytest.fixture(scope='session')
def qapp_args():
    return sys.argv


@pytest.fixture(scope='session')
def vendors() -> list:
    assert path.exists("./data/vendor_manager/vendors.dat"), \
        "test vendor.dat should be placed in ./tests/data/vendor_manager/"

    vendor_list = []
    vendors_json_string = DataStorage.read_json_file("./data/vendor_manager/vendors.dat")
    vendor_dicts = json.loads(vendors_json_string)
    for json_dict in vendor_dicts:
        vendor = Vendor.from_json(json_dict)
        vendor_list.append(vendor)

    return vendor_list


@pytest.fixture(scope='session')
def settings() -> Settings.SettingsModel:
    return Settings.SettingsModel(Settings.YEARLY_DIR,
                                  Settings.OTHER_DIR,
                                  Settings.REQUEST_INTERVAL,
                                  Settings.REQUEST_TIMEOUT,
                                  Settings.CONCURRENT_VENDORS,
                                  Settings.CONCURRENT_REPORTS,
                                  Settings.EMPTY_CELL)


def test_on_vendors_changed(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController([], settings, window_ui)
    controller.on_vendors_changed(vendors)

    assert controller.selected_vendor_index == -1
    assert len(controller.vendors) == len(vendors)
    assert controller.vendor_list_model.rowCount() == len(vendors)


def test_update_vendors(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController([], settings, window_ui)

    controller.update_vendors(vendors)
    assert len(controller.vendors) == len(vendors)
    for i in range(len(controller.vendors)):
        assert controller.vendors[i].name == vendors[i].name


def test_update_vendors_ui(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController([], settings, window_ui)
    controller.update_vendors(vendors)

    vendor_list_model = controller.vendor_list_model
    assert vendor_list_model.rowCount() == 0

    controller.update_vendors_ui()
    assert vendor_list_model.rowCount() == len(controller.vendors)
    for i in range(len(controller.vendors)):
        assert vendor_list_model.item(i, 0).text() == controller.vendors[i].name


def test_on_vendor_selected(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController([], settings, window_ui)
    controller.update_vendors(vendors)

    index_to_select = 5
    model_index = QStandardItemModel.createIndex(QStandardItemModel(), index_to_select, 0)
    controller.on_vendor_selected(model_index)

    assert controller.selected_vendor_index == index_to_select


def test_on_report_type_selected(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController([], settings, window_ui)
    controller.update_vendors(vendors)

    index_to_select = 3
    model_index = QStandardItemModel.createIndex(QStandardItemModel(), index_to_select, 0)
    controller.on_report_type_selected(model_index)

    assert controller.selected_report_type_index == index_to_select


def test_on_date_changed(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController(vendors, settings, window_ui)

    test_date = QDate.currentDate()
    controller.on_date_changed(test_date)

    assert controller.date == test_date


def test_on_import_clicked(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController(vendors, settings, window_ui)
    controller.update_vendors(vendors)

    # No vendor selected
    controller.on_import_clicked()
    controller.selected_vendor_index = 1

    # No report type selected
    controller.on_import_clicked()
    controller.selected_report_type_index = 1

    vendor = controller.vendors[controller.selected_vendor_index]
    report_type = REPORT_TYPES[controller.selected_report_type_index]
    file_dir = f"{controller.settings.yearly_directory}{controller.date.toString('yyyy')}/{vendor.name}/"
    file_name = f"{controller.date.toString('yyyy')}_{vendor.name}_{report_type}.tsv"
    file_path = file_dir + file_name

    # No file selected
    controller.on_import_clicked()

    # Invalid file selected
    controller.selected_file_path = "./data/invalid_file"
    controller.on_import_clicked()

    # Valid file selected
    controller.selected_file_path = "./data/test_file_for_import.tsv"
    controller.on_import_clicked()
    assert path.isfile(file_path)


def test_import_file(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController(vendors, settings, window_ui)
    controller.update_vendors(vendors)

    controller.selected_vendor_index = 1
    controller.selected_report_type_index = 1

    vendor = controller.vendors[controller.selected_vendor_index]
    report_type = REPORT_TYPES[controller.selected_report_type_index]
    file_dir = f"{controller.settings.yearly_directory}{controller.date.toString('yyyy')}/{vendor.name}/"
    file_name = f"{controller.date.toString('yyyy')}_{vendor.name}_{report_type}.tsv"
    file_path = file_dir + file_name

    # No file selected
    assert controller.import_file(vendor, report_type).completion_status == CompletionStatus.FAILED

    # Invalid file selected
    controller.selected_file_path = "./data/invalid_file"
    assert controller.import_file(vendor, report_type).completion_status == CompletionStatus.FAILED

    # Valid file selected
    controller.selected_file_path = "./data/test_file_for_import.tsv"
    assert controller.import_file(vendor, report_type).completion_status == CompletionStatus.SUCCESSFUL
    assert path.isfile(file_path)


def test_open_file(qtbot, vendors, settings):
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    controller = ImportFileController(vendors, settings, window_ui)

    # Invalid file/folder
    controller.open_explorer("./data/invalid_file")

    # Valid file
    controller.open_explorer("./data/test_file_for_import.tsv")

    # Valid folder
    controller.open_explorer("./data/")





