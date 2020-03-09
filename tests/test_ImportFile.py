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
                                  Settings.EMPTY_CELL,
                                  Settings.USER_AGENT)


@pytest.fixture
def controller(qtbot, settings):  # ImportFileController without populated vendor list
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    c = ImportFileController([], settings, window_ui)
    yield c


@pytest.fixture
def controller_v(qtbot, vendors, settings):  # ImportFileController with populated vendor list
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    c = ImportFileController(vendors, settings, window_ui)
    yield c


def test_on_vendors_changed(controller, vendors):
    controller.on_vendors_changed(vendors)

    assert controller.selected_vendor_index == -1
    assert len(controller.vendors) == len(vendors)
    assert controller.vendor_list_model.rowCount() == len(vendors)


def test_update_vendors(controller, vendors):
    controller.update_vendors(vendors)

    assert len(controller.vendors) == len(vendors)
    for i in range(len(controller.vendors)):
        assert controller.vendors[i].name == vendors[i].name


def test_update_vendors_ui(controller, vendors):
    controller.update_vendors(vendors)

    vendor_list_model = controller.vendor_list_model
    assert vendor_list_model.rowCount() == 0

    controller.update_vendors_ui()
    assert vendor_list_model.rowCount() == len(controller.vendors)
    for i in range(len(controller.vendors)):
        assert vendor_list_model.item(i, 0).text() == controller.vendors[i].name


def test_on_vendor_selected(controller_v, vendors, settings):
    index_to_select = 5
    model_index = QStandardItemModel.createIndex(QStandardItemModel(), index_to_select, 0)
    controller_v.on_vendor_selected(model_index)

    assert controller_v.selected_vendor_index == index_to_select


def test_on_report_type_selected(controller_v):

    index_to_select = 3
    model_index = QStandardItemModel.createIndex(QStandardItemModel(), index_to_select, 0)
    controller_v.on_report_type_selected(model_index)

    assert controller_v.selected_report_type_index == index_to_select


def test_on_date_changed(controller_v):
    test_date = QDate.currentDate()
    controller_v.on_date_changed(test_date)

    assert controller_v.date == test_date


def test_on_import_clicked(controller_v):
    # No vendor selected
    controller_v.on_import_clicked()
    controller_v.selected_vendor_index = 1

    # No report type selected
    controller_v.on_import_clicked()
    controller_v.selected_report_type_index = 1

    vendor = controller_v.vendors[controller_v.selected_vendor_index]
    report_type = REPORT_TYPES[controller_v.selected_report_type_index]
    file_dir = f"{controller_v.settings.yearly_directory}{controller_v.date.toString('yyyy')}/{vendor.name}/"
    file_name = f"{controller_v.date.toString('yyyy')}_{vendor.name}_{report_type}.tsv"
    file_path = file_dir + file_name

    # No file selected
    controller_v.on_import_clicked()

    # Invalid file selected
    controller_v.selected_file_path = "./data/invalid_file"
    controller_v.on_import_clicked()

    # Valid file selected
    controller_v.selected_file_path = "./data/test_file_for_import.tsv"
    controller_v.on_import_clicked()
    assert path.isfile(file_path)


def test_import_file(controller_v):
    controller_v.selected_vendor_index = 1
    controller_v.selected_report_type_index = 1

    vendor = controller_v.vendors[controller_v.selected_vendor_index]
    report_type = REPORT_TYPES[controller_v.selected_report_type_index]
    file_dir = f"{controller_v.settings.yearly_directory}{controller_v.date.toString('yyyy')}/{vendor.name}/"
    file_name = f"{controller_v.date.toString('yyyy')}_{vendor.name}_{report_type}.tsv"
    file_path = file_dir + file_name

    # No file selected
    assert controller_v.import_file(vendor, report_type).completion_status == CompletionStatus.FAILED

    # Invalid file selected
    controller_v.selected_file_path = "./data/invalid_file"
    assert controller_v.import_file(vendor, report_type).completion_status == CompletionStatus.FAILED

    # Valid file selected
    controller_v.selected_file_path = "./data/test_file_for_import.tsv"
    assert controller_v.import_file(vendor, report_type).completion_status == CompletionStatus.SUCCESSFUL
    assert path.isfile(file_path)


def test_open_file(controller_v):
    # Invalid file/folder
    controller_v.open_explorer("./data/invalid_file")

    # Valid file
    controller_v.open_explorer("./data/test_file_for_import.tsv")

    # Valid folder
    controller_v.open_explorer("./data/")





