import json

from PyQt5.QtCore import QDate

import DataStorage
import ManageDB
import ManageVendors
from ui import CostsTab


class CostsController:
    def __init__(self, costs_ui: CostsTab.Ui_costs_tab):
        self.costs_ui = costs_ui

        # set parameters
        self.report_parameter_combobox = costs_ui.costs_report_parameter_combobox
        self.report_parameter_combobox.addItems(ManageDB.REPORT_TYPE_SWITCHER.keys())
        self.report_parameter = None

        self.vendor_parameter_combobox = costs_ui.costs_vendor_parameter_combobox
        vendors_json_string = DataStorage.read_json_file(ManageVendors.VENDORS_FILE_PATH)
        vendor_dicts = json.loads(vendors_json_string)
        self.vendor_parameter_combobox.addItems([vendor_dict['name'] for vendor_dict in vendor_dicts])
        self.vendor_parameter = None

        self.year_parameter_dateedit = costs_ui.costs_year_parameter_dateedit
        self.year_parameter_dateedit.setDate(QDate.currentDate())
        self.year_parameter = None

        self.name_label = costs_ui.costs_name_parameter_label
        self.name_parameter_combobox = costs_ui.costs_name_parameter_combobox
        self.name_parameter = None

        # set up values
        self.cost_in_original_currency_doublespinbox = costs_ui.costs_cost_in_original_currency_doublespinbox
        self.cost_in_original_currency = 0.0

        self.original_currency_combobox = costs_ui.costs_original_currency_value_combobox
        self.original_currency = ''

        self.cost_in_local_currency_doublespinbox = costs_ui.costs_cost_in_local_currency_doublespinbox
        self.cost_in_local_currency = 0.0

        self.cost_in_local_currency_with_tax_doublespinbox = \
            costs_ui.costs_cost_in_local_currency_with_tax_doublespinbox
        self.cost_in_local_currency_with_tax = 0.0

        # set up buttons
        self.insert_button = costs_ui.costs_insert_button
        self.insert_button.clicked.connect(self.insert_costs)

        self.load_button = costs_ui.costs_load_button
        self.load_button.clicked.connect(self.load_costs)

        self.report_parameter_combobox.currentTextChanged.connect(self.on_report_parameter_changed)
        self.vendor_parameter_combobox.currentTextChanged.connect(self.on_vendor_parameter_changed)
        self.year_parameter_dateedit.dateChanged.connect(self.on_year_parameter_changed)
        self.name_parameter_combobox.currentTextChanged.connect(self.on_name_parameter_changed)

        self.on_report_parameter_changed()
        self.on_vendor_parameter_changed()
        self.on_year_parameter_changed()

        self.cost_in_original_currency_doublespinbox.valueChanged.connect(self.on_cost_in_original_currency_changed)
        self.original_currency_combobox.currentTextChanged.connect(self.on_original_currency_changed)
        self.cost_in_local_currency_doublespinbox.valueChanged.connect(self.on_cost_in_local_currency_changed)
        self.cost_in_local_currency_with_tax_doublespinbox.valueChanged.connect(
            self.on_cost_in_local_currency_with_tax_changed)

    # TODO (Chandler): enable cost fields when others are filled

    def on_report_parameter_changed(self):
        self.report_parameter = self.report_parameter_combobox.currentText()
        self.name_label.setText(ManageDB.NAME_FIELD_SWITCHER[self.report_parameter].capitalize())
        if self.vendor_parameter:
            self.fill_names()

    def on_vendor_parameter_changed(self):
        self.vendor_parameter = self.vendor_parameter_combobox.currentText()
        print(self.vendor_parameter)
        if self.report_parameter:
            self.fill_names()

    def on_year_parameter_changed(self):
        self.year_parameter = int(self.year_parameter_dateedit.text())

    def fill_names(self):
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

    def on_name_parameter_changed(self):
        self.name_parameter = self.name_parameter_combobox.currentText()
        enable = False
        if self.name_parameter:
            enable = True
        self.cost_in_original_currency_doublespinbox.setEnabled(enable)
        self.original_currency_combobox.setEnabled(enable)
        self.cost_in_local_currency_doublespinbox.setEnabled(enable)
        self.cost_in_local_currency_with_tax_doublespinbox.setEnabled(enable)

    def on_cost_in_original_currency_changed(self):
        self.cost_in_original_currency = self.cost_in_original_currency_doublespinbox.value()

    def on_original_currency_changed(self):
        self.original_currency = self.original_currency_combobox.currentText()

    def on_cost_in_local_currency_changed(self):
        self.cost_in_local_currency = self.cost_in_local_currency_doublespinbox.value()

    def on_cost_in_local_currency_with_tax_changed(self):
        self.cost_in_local_currency_with_tax = self.cost_in_local_currency_with_tax_doublespinbox.value()

    def insert_costs(self):
        print('insert_costs')
        print(self.cost_in_original_currency)
        print(self.original_currency)
        print(self.cost_in_local_currency)
        print(self.cost_in_local_currency_with_tax)
        sql_text = None
        if self.cost_in_original_currency > 0 and self.original_currency != '' \
                and self.cost_in_local_currency > 0 and self.cost_in_local_currency_with_tax > 0:
            sql_text = ManageDB.replace_cost_sql_text(self.report_parameter,
                                                      [{ManageDB.NAME_FIELD_SWITCHER[self.report_parameter]:
                                                            self.name_parameter,
                                                        'vendor': self.vendor_parameter, 'year': self.year_parameter,
                                                        'cost_in_original_currency': self.cost_in_original_currency,
                                                        'original_currency': self.original_currency,
                                                        'cost_in_local_currency': self.cost_in_local_currency,
                                                        'cost_in_local_currency_with_tax':
                                                            self.cost_in_local_currency_with_tax}])
        else:
            sql_text = ManageDB.delete_costs_sql_text(self.report_parameter, self.vendor_parameter, self.year_parameter,
                                                      self.name_parameter)
        print(sql_text)
        connection = ManageDB.create_connection(ManageDB.DATABASE_LOCATION)
        if connection is not None:
            ManageDB.run_insert_sql(connection, sql_text['sql_delete'], sql_text['sql_replace'], sql_text['data'])

    def load_costs(self):
        print('load_costs')
        sql_text = ManageDB.get_costs_sql_text(self.report_parameter, self.vendor_parameter, self.year_parameter,
                                               self.name_parameter)
        print(sql_text)
        results = []
        connection = ManageDB.create_connection(ManageDB.DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text)
            if not results:
                results.append((0.0, '', 0.0, 0.0))
        print(results)
        values = {}
        index = 0
        for field in ManageDB.COST_FIELDS:
            values[field['name']] = results[0][index]
            index += 1
        self.cost_in_original_currency_doublespinbox.setValue(values['cost_in_original_currency'])
        self.original_currency_combobox.setCurrentText(values['original_currency'])
        self.cost_in_local_currency_doublespinbox.setValue(values['cost_in_local_currency'])
        self.cost_in_local_currency_with_tax_doublespinbox.setValue(values['cost_in_local_currency_with_tax'])

    # TODO (Chandler): import/export tsv file with costs
