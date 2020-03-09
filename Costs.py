from PyQt5.QtCore import QDate

import ManageDB
from ui import MainWindow


class CostsController:
    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        self.main_window = main_window_ui

        # set up report types combobox
        self.report_parameter = main_window_ui.costs_report_parameter_combobox
        self.report_parameter.addItems(ManageDB.REPORT_TYPE_SWITCHER.keys())

        # set up year dateedit
        self.year_parameter = main_window_ui.costs_year_parameter_dateedit
        self.year_parameter.setDate(QDate.currentDate())

        # set up vendor combobox
        self.vendor_parameter = main_window_ui.costs_vendor_parameter_combobox

        # set up names combobox
        self.name_parameter = main_window_ui.costs_name_parameter_combobox
