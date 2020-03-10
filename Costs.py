import json
from PyQt5.QtCore import QDate

import ManageDB, DataStorage, ManageVendors
from ui import MainWindow


class CostsController:
    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        self.main_window = main_window_ui

        # set parameters
        self.report_parameter_combobox = main_window_ui.costs_report_parameter_combobox
        self.report_parameter_combobox.addItems(ManageDB.REPORT_TYPE_SWITCHER.keys())
        self.report_parameter = None

        self.vendor_parameter_combobox = main_window_ui.costs_vendor_parameter_combobox
        vendors_json_string = DataStorage.read_json_file(ManageVendors.VENDORS_FILE_PATH)
        vendor_dicts = json.loads(vendors_json_string)
        self.vendor_parameter_combobox.addItems([vendor_dict['name'] for vendor_dict in vendor_dicts])
        self.vendor_parameter = None

        self.year_parameter_dateedit = main_window_ui.costs_year_parameter_dateedit
        self.year_parameter_dateedit.setDate(QDate.currentDate())
        self.year_parameter = None

        self.name_label = main_window_ui.costs_name_parameter_label
        self.name_parameter_combobox = main_window_ui.costs_name_parameter_combobox
        self.name_parameter = None

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

        self.report_parameter_combobox.currentTextChanged.connect(self.on_report_parameter_changed)
        self.vendor_parameter_combobox.currentTextChanged.connect(self.on_vendor_parameter_changed)
        self.year_parameter_dateedit.dateChanged.connect(self.on_year_parameter_changed)

        self.on_report_parameter_changed()
        self.on_vendor_parameter_changed()
        self.on_year_parameter_changed()

    # TODO enable cost fields when others are filled

    def on_report_parameter_changed(self):
        print('on_report_parameter_changed')
        self.report_parameter = self.report_parameter_combobox.currentText()
        self.name_label.setText(ManageDB.NAME_FIELD_SWITCHER[self.report_parameter].capitalize())
        if self.vendor_parameter:
            self.fill_names()

    def on_vendor_parameter_changed(self):
        print('on_vendor_parameter_changed')
        self.vendor_parameter = self.vendor_parameter_combobox.currentText()
        print(self.vendor_parameter)
        if self.report_parameter:
            self.fill_names()

    def on_year_parameter_changed(self):
        print('on_year_parameter_changed')
        self.year_parameter = int(self.year_parameter_dateedit.text())

    def fill_names(self):
        print('fill_names')
        self.name_parameter_combobox.clear()
        results = []
        sql_text = ManageDB.get_names_sql_text(self.report_parameter, self.vendor_parameter)
        print(sql_text)
        connection = ManageDB.create_connection(ManageDB.DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text)
            print(results)
            connection.close()
        else:
            print('Error, no connection')
        self.name_parameter_combobox.addItems([result[0] for result in results])

    def insert_costs(self):
        print('insert_costs')
        # TODO insert into database

    def load_costs(self):
        print('load_costs')
        # TODO load from database