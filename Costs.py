import json
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont

import ManageDB
import ManageVendors
from Settings import SettingsModel
from ui import CostsTab, ReportTypeDialog
from Constants import *
from GeneralUtils import *


class CostsController:
    """Controls the Costs tab

    :param costs_ui: the UI for the costs_widget
    :param settings: the user's settings"""

    def __init__(self, costs_ui: CostsTab.Ui_costs_tab, settings: SettingsModel):
        self.costs_ui = costs_ui
        self.settings = settings

        # set parameters
        self.report_parameter_combobox = costs_ui.costs_report_parameter_combobox
        self.report_parameter_combobox.addItems(REPORT_TYPE_SWITCHER.keys())
        self.report_parameter = None

        self.vendor_parameter_combobox = costs_ui.costs_vendor_parameter_combobox
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
        self.load_currency_list()
        self.original_currency = ''

        self.cost_in_local_currency_doublespinbox = costs_ui.costs_cost_in_local_currency_doublespinbox
        self.cost_in_local_currency = 0.0

        self.cost_in_local_currency_with_tax_doublespinbox = \
            costs_ui.costs_cost_in_local_currency_with_tax_doublespinbox
        self.cost_in_local_currency_with_tax = 0.0

        # set up buttons
        self.save_costs_button = costs_ui.costs_save_button
        self.save_costs_button.clicked.connect(self.save_costs)

        self.load_button = costs_ui.costs_load_button
        self.load_button.clicked.connect(self.load_costs)

        self.clear_button = costs_ui.costs_clear_button
        self.clear_button.clicked.connect(self.clear_costs)




        # NEw NEw
        self.start_year_date_edit = costs_ui.start_year_date_edit
        self.start_year_date_edit.dateChanged.connect(self.on_start_year_changed)
        self.end_year_date_edit = costs_ui.end_year_date_edit
        self.end_year_date_edit.dateChanged.connect(self.on_end_year_changed)

        self.start_month_combo_box = costs_ui.start_month_combo_box
        self.end_month_combo_box = costs_ui.end_month_combo_box

        for month in MONTH_NAMES:
            self.start_month_combo_box.addItem(month)
            self.end_month_combo_box.addItem(month)

        self.start_month_combo_box.currentIndexChanged.connect(self.on_start_month_changed)
        self.end_month_combo_box.currentIndexChanged.connect(self.on_end_month_changed)




        vendors_json_string = read_json_file(ManageVendors.VENDORS_FILE_PATH)
        vendor_dicts = json.loads(vendors_json_string)
        self.vendor_parameter_combobox.clear()
        self.vendor_parameter_combobox.addItems([vendor_dict[NAME_KEY] for vendor_dict in vendor_dicts])

        self.report_parameter_combobox.currentTextChanged.connect(self.on_report_parameter_changed)
        self.vendor_parameter_combobox.currentTextChanged.connect(self.on_vendor_parameter_changed)
        self.year_parameter_dateedit.dateChanged.connect(self.on_year_parameter_changed)
        self.name_parameter_combobox.currentTextChanged.connect(self.on_name_parameter_changed)

        self.names = []
        self.costs_names = []

        self.on_report_parameter_changed()
        self.year_parameter = int(self.year_parameter_dateedit.text())
        self.vendor_parameter = self.vendor_parameter_combobox.currentText()
        self.fill_names()

        self.cost_in_original_currency_doublespinbox.valueChanged.connect(self.on_cost_in_original_currency_changed)
        self.original_currency_combobox.currentTextChanged.connect(self.on_original_currency_changed)
        self.cost_in_local_currency_doublespinbox.valueChanged.connect(self.on_cost_in_local_currency_changed)
        self.cost_in_local_currency_with_tax_doublespinbox.valueChanged.connect(
            self.on_cost_in_local_currency_with_tax_changed)

        self.import_costs_button = costs_ui.costs_import_costs_button
        self.import_costs_button.clicked.connect(self.import_costs)

    def update_settings(self, settings: SettingsModel):
        """Invoked when the settings are saved

        :param settings: the new settings"""
        self.settings = settings
        self.load_currency_list()

    def database_updated(self, code: int):
        """Invoked when the database is updated

        :param code: the exit code of the update"""
        self.fill_names()

    def load_vendor_list(self, vendors: Sequence[ManageVendors.Vendor]):
        """Updates the vendor list combobox

        :param vendors: the new list of vendors"""
        self.vendor_parameter_combobox.clear()
        self.vendor_parameter_combobox.addItems([vendor.name for vendor in vendors])

    def load_currency_list(self):
        """Updates the original currency combobox"""
        self.original_currency_combobox.clear()
        self.original_currency_combobox.addItem(self.settings.default_currency)
        self.original_currency_combobox.addItems([currency for currency in CURRENCY_LIST if currency !=
                                                  self.settings.default_currency])
        self.original_currency_combobox.setCurrentText('')

    def on_report_parameter_changed(self):
        """Invoked when the report parameter changes"""
        self.report_parameter = self.report_parameter_combobox.currentText()
        self.name_label.setText(NAME_FIELD_SWITCHER[self.report_parameter].capitalize())
        if self.vendor_parameter:
            self.fill_names()

    def on_vendor_parameter_changed(self):
        """Invoked when the vendor parameter changes"""
        self.vendor_parameter = self.vendor_parameter_combobox.currentText()
        if self.report_parameter:
            self.fill_names()

    def on_year_parameter_changed(self):
        """Invoked when the year parameter changes"""
        self.year_parameter = int(self.year_parameter_dateedit.text())
        self.load_costs()
        self.fill_names(True)

    def fill_names(self, only_get_costs_names: bool = False):
        """Fills the name field combobox"""
        self.name_parameter_combobox.clear()

        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            if not only_get_costs_names:
                names_sql_text, names_data = ManageDB.get_names_sql_text(self.report_parameter, self.vendor_parameter)
                names_results = ManageDB.run_select_sql(connection, names_sql_text, names_data)
                if names_results:
                    self.names = [result[0] for result in names_results]
                else:
                    self.names = []
                # if self.settings.show_debug_messages: print(names_results)

            costs_sql_text, costs_data = ManageDB.get_names_with_costs_sql_text(self.report_parameter,
                                                                                self.vendor_parameter,
                                                                                self.year_parameter,
                                                                                self.year_parameter)
            costs_results = ManageDB.run_select_sql(connection, costs_sql_text, costs_data)
            connection.close()

            if costs_results:
                self.costs_names = [result[0] for result in costs_results]
            else:
                self.costs_names = []
            if self.settings.show_debug_messages: print(costs_results)
            model = QStandardItemModel()
            for name in self.names:
                item = QStandardItem(name)
                if name in self.costs_names:
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                model.appendRow(item)
            self.name_parameter_combobox.setModel(model)
        else:
            print('Error, no connection')

    def on_name_parameter_changed(self):
        """Invoked when the name field parameter changes"""
        self.name_parameter = self.name_parameter_combobox.currentText()
        enable = False
        if self.name_parameter:
            enable = True
            self.load_costs()
        self.cost_in_original_currency_doublespinbox.setEnabled(enable)
        self.original_currency_combobox.setEnabled(enable)
        self.cost_in_local_currency_doublespinbox.setEnabled(enable)
        self.cost_in_local_currency_with_tax_doublespinbox.setEnabled(enable)

    def on_cost_in_original_currency_changed(self):
        """Invoked when the cost in original currency parameter changes"""
        self.cost_in_original_currency = self.cost_in_original_currency_doublespinbox.value()

    def on_original_currency_changed(self):
        """Invoked when the original currency parameter changes"""
        self.original_currency = self.original_currency_combobox.currentText()

    def on_cost_in_local_currency_changed(self):
        """Invoked when the cost in local currency parameter changes"""
        self.cost_in_local_currency = self.cost_in_local_currency_doublespinbox.value()

    def on_cost_in_local_currency_with_tax_changed(self):
        """Invoked when the cost in local currency with tax parameter changes"""
        self.cost_in_local_currency_with_tax = self.cost_in_local_currency_with_tax_doublespinbox.value()



    def on_start_year_changed(self):
        print()

    def on_end_year_changed(self):
        print()

    def on_start_month_changed(self):
        print()

    def on_end_month_changed(self):
        print()



    def save_costs(self):
        """Saves the cost data: if it is nonzero, add it to the database; if it is zero, delete it from the database"""

        # Get the number of months to be processed
        begin_date = QDate(self.start_year_date_edit.date().year(), self.start_month_combo_box.currentIndex() + 1, 1)
        end_date = QDate(self.end_year_date_edit.date().year(), self.end_month_combo_box.currentIndex() + 1, 1)

        if begin_date.year() == end_date.year():
            num_months = (end_date.month() - begin_date.month()) + 1
        else:
            num_months = (12 - begin_date.month() + end_date.month()) + 1
            num_years = end_date.year() - begin_date.year()
            num_months += (num_years - 1) * 12

        # Get the sql_text and data for each month's insertion
        insertion_sql_data = []
        for i in range(num_months):
            curr_month = begin_date.addMonths(i).month()
            sql_text, data = ManageDB.replace_costs_sql_text(self.report_parameter,
                                                             ({NAME_FIELD_SWITCHER[self.report_parameter]:
                                                                   self.name_parameter,
                                                               'vendor': self.vendor_parameter,
                                                               'year': self.year_parameter,
                                                               'month': curr_month,
                                                               'cost_in_original_currency':
                                                                   self.cost_in_original_currency,
                                                               'original_currency': self.original_currency,
                                                               'cost_in_local_currency': self.cost_in_local_currency,
                                                               'cost_in_local_currency_with_tax':
                                                                   self.cost_in_local_currency_with_tax},))
            insertion_sql_data.append((sql_text, data))
            print(begin_date.toString("MMM-yyyy"))



        sql_text = None
        data = None

        is_inserting = self.cost_in_original_currency > 0 and self.original_currency != '' \
                       and self.cost_in_local_currency > 0 and self.cost_in_local_currency_with_tax > 0

        is_deleting = self.cost_in_original_currency == 0 and self.original_currency == '' \
                      and self.cost_in_local_currency == 0 and self.cost_in_local_currency_with_tax == 0

        if is_inserting:
            sql_text, data = ManageDB.replace_costs_sql_text(self.report_parameter,
                                                             ({NAME_FIELD_SWITCHER[self.report_parameter]:
                                                                   self.name_parameter,
                                                               'vendor': self.vendor_parameter,
                                                               'year': self.year_parameter,
                                                               'month': 5,
                                                               'cost_in_original_currency':
                                                                   self.cost_in_original_currency,
                                                               'original_currency': self.original_currency,
                                                               'cost_in_local_currency': self.cost_in_local_currency,
                                                               'cost_in_local_currency_with_tax':
                                                                   self.cost_in_local_currency_with_tax},))
        elif is_deleting:
            sql_text, data = ManageDB.delete_costs_sql_text(self.report_parameter, self.vendor_parameter,
                                                            self.year_parameter, self.name_parameter)

        if is_inserting or is_deleting:
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                ManageDB.run_sql(connection, sql_text, data)
                connection.close()
                ManageDB.backup_costs_data(self.report_parameter)
                if is_inserting:
                    show_message('Data inserted/replaced')
                elif is_deleting:
                    show_message('Data removed')
        else:
            show_message('Invalid entry')

    def load_costs(self):
        """Fills the costs fields with data from the database"""
        sql_text, data = ManageDB.get_costs_sql_text(self.report_parameter, self.vendor_parameter, self.name_parameter)
        results = []
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)
            if not results:
                results.append((0.0, '', 0.0, 0.0))
            connection.close()
        values = {}
        index = 0
        for field in COST_FIELDS:
            values[field[NAME_KEY]] = results[0][index]
            index += 1
        self.cost_in_original_currency_doublespinbox.setValue(values['cost_in_original_currency'])
        self.original_currency_combobox.setCurrentText(values['original_currency'])
        self.cost_in_local_currency_doublespinbox.setValue(values['cost_in_local_currency'])
        self.cost_in_local_currency_with_tax_doublespinbox.setValue(values['cost_in_local_currency_with_tax'])
        self.cost_in_original_currency_doublespinbox.repaint()

    def clear_costs(self):
        """Empties the costs fields"""
        self.cost_in_original_currency_doublespinbox.setValue(0.0)
        self.original_currency_combobox.setCurrentText('')
        self.cost_in_local_currency_doublespinbox.setValue(0.0)
        self.cost_in_local_currency_with_tax_doublespinbox.setValue(0.0)

    def import_costs(self):
        """Import a file with costs data in it into the database"""
        report_type_dialog = QDialog()
        report_type_dialog_ui = ReportTypeDialog.Ui_report_type_dialog()
        report_type_dialog_ui.setupUi(report_type_dialog)
        report_type_dialog_ui.report_type_combobox.addItems(REPORT_TYPE_SWITCHER.keys())
        report_type_dialog.show()
        if report_type_dialog.exec_():
            report_type = report_type_dialog_ui.report_type_combobox.currentText()
            if report_type != '':
                file_name = choose_file(TSV_FILTER + CSV_FILTER)
                if file_name != '':
                    ManageDB.insert_single_cost_file(report_type, file_name)
                    ManageDB.backup_costs_data(report_type)
                    show_message('File ' + file_name + ' imported')
                else:
                    print('Error, no file location selected')
            else:
                print('Error, no report type selected')
