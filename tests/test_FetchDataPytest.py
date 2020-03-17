import sys
import pytest
from os import path
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QStandardItemModel
from ui import MainWindow
from FetchData import FetchReportsAbstract
from FetchData import FetchReportsController
from FetchData import FetchSpecialReportsController
from FetchData import VendorWorker
from FetchData import ReportWorker
from ManageVendors import Vendor
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


@pytest.fixture
def abstract_FP(qtbot, settings):  # FetchReportsAbstract without populated vendor list
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    c = FetchReportsAbstract([], settings)
    yield c


@pytest.fixture
def abstract_FP_v(qtbot, vendors, settings):  # FetchReportsAbstract with populated vendor list
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    c = FetchReportsAbstract(vendors, settings)
    yield c


@pytest.fixture
def controller_FP(qtbot, settings):  # FetchReportsController without populated vendor list
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    c = FetchReportsController([], settings, window_ui)
    yield c

@pytest.fixture
def controller_FP_v(qtbot, vendors, settings):  # FetchReportsController with populated vendor list
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    c = FetchReportsController(vendors, settings, window_ui)
    yield c


@pytest.fixture
def controller_FSP(qtbot, settings):  # FetchSpecialReportsController without populated vendor list
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    c = FetchSpecialReportsController([], settings, window_ui)
    yield c

@pytest.fixture
def controller_FSP_v(qtbot, vendors, settings):  # FetchSpecialReportsController with populated vendor list
    window = QMainWindow()
    window_ui = MainWindow.Ui_mainWindow()
    window_ui.setupUi(window)

    c = FetchSpecialReportsController(vendors, settings, window_ui)
    yield c


def test_on_vendors_changed(abstract_FP, vendors):
    abstract_FP.on_vendors_changed(vendors)

    assert abstract_FP.selected_vendor_index == -1
    assert len(abstract_FP.vendors) == len(vendors)
    assert abstract_FP.vendor_list_model.rowCount() == len(vendors)

def test_update_vendors(abstract_FP, vendors):
    abstract_FP.update_vendors(vendors)

    assert len(abstract_FP.vendors) == len(vendors)
    for i in range(len(abstract_FP.vendors)):
        assert abstract_FP.vendors[i].name == vendors[i].name

def test_update_vendors_ui_AFP(abstract_FP, vendors):
    abstract_FP.update_vendors(vendors)

    vendor_list_model = abstract_FP.vendor_list_model
    assert vendor_list_model.rowCount() == 0

    abstract_FP.update_vendors_ui()
    assert vendor_list_model.rowCount() == len(abstract_FP.vendors)
    for i in range(len(abstract_FP.vendors)):
        assert vendor_list_model.item(i, 0).text() == abstract_FP.vendors[i].name

def test_update_vendors_ui_CFP(controller_FP, vendors):
    controller_FP.update_vendors(vendors)

    vendor_list_model = controller_FP.vendor_list_model
    assert vendor_list_model.rowCount() == 0

    controller_FP.update_vendors_ui()
    assert vendor_list_model.rowCount() == len(controller_FP.vendors)
    for i in range(len(controller_FP.vendors)):
        assert vendor_list_model.item(i, 0).text() == controller_FP.vendors[i].name

def test_update_vendors_ui_CFSP(controller_FSP, vendors):
    controller_FSP.update_vendors(vendors)

    vendor_list_model = controller_FSP.vendor_list_model
    assert vendor_list_model.rowCount() == 0

    controller_FSP.update_vendors_ui()
    assert vendor_list_model.rowCount() == len(controller_FSP.vendors)
    for i in range(len(controller_FSP.vendors)):
        assert vendor_list_model.item(i, 0).text() == controller_FSP.vendors[i].name

def test_on_date_changed(controller_FP_v):
    test_date = QDate.currentDate()
    controller_FP_v.on_date_changed(test_date)

    assert controller_FP_v.date == test_date

def test_on_date_changed(controller_FSP_v):
    test_date = QDate.currentDate()
    controller_FSP_v.on_date_changed(test_date)

    assert controller_FSP_v.date == test_date