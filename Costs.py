from PyQt5.QtCore import QDate

import ManageDB
from ui import MainWindow


class CostsController:
    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        self.main_window = main_window_ui

        # set parameters
        self.report_parameter = main_window_ui.costs_report_parameter_combobox
        self.report_parameter.addItems(ManageDB.REPORT_TYPE_SWITCHER.keys())

        self.year_parameter = main_window_ui.costs_year_parameter_dateedit
        self.year_parameter.setDate(QDate.currentDate())

        self.vendor_parameter = main_window_ui.costs_vendor_parameter_combobox

        self.name_label = main_window_ui.costs_name_parameter_label
        self.name_parameter = main_window_ui.costs_name_parameter_combobox

        # set up values
        self.cost_in_original_currency = main_window_ui.costs_cost_in_original_currency_lineedit

        self.original_currency = main_window_ui.costs_original_currency_value_combobox

        self.cost_in_local_currency = main_window_ui.costs_cost_in_local_currency_lineedit

        self.cost_in_local_currency_with_tax = main_window_ui.costs_cost_in_local_currency_with_tax_lineedit

        # set up buttons
        self.insert_button = main_window_ui.costs_insert_button
        self.insert_button.clicked.connect(self.insert_costs)

        self.load_button = main_window_ui.costs_load_button
        self.load_button.clicked.connect(self.load_costs)

        def set_name():
            self.name_label.setText(ManageDB.NAME_FIELD_SWITCHER[self.report_parameter.currentText()].capitalize())

        self.report_parameter.currentTextChanged.connect(set_name)
        set_name()

    def insert_costs(self):
        print('insert_costs')

    def load_costs(self):
        print('load_costs')
