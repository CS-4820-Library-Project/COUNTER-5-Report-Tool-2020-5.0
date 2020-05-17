import json
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import QModelIndex

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

        self.refresh_button = costs_ui.costs_load_button
        self.refresh_button.clicked.connect(self.on_refresh_clicked)

        self.clear_button = costs_ui.costs_clear_button
        self.clear_button.clicked.connect(self.clear_cost_fields)




        # NEw NEw
        self.available_costs_combo_box = costs_ui.available_costs_combo_box
        self.available_costs_combo_box.currentIndexChanged.connect(self.on_available_cost_clicked)
        self.available_costs = []

        self.update_cost_frame = costs_ui.update_cost_frame

        current_date = QDate.currentDate()
        self.start_year_date_edit = costs_ui.start_year_date_edit
        self.start_year_date_edit.setDate(current_date)
        self.end_year_date_edit = costs_ui.end_year_date_edit
        self.end_year_date_edit.setDate(current_date)

        self.start_month_combo_box = costs_ui.start_month_combo_box
        self.end_month_combo_box = costs_ui.end_month_combo_box

        for month in MONTH_NAMES:
            self.start_month_combo_box.addItem(month)
            self.end_month_combo_box.addItem(month)

        self.start_month_combo_box.setCurrentIndex(current_date.month() - 1)
        self.end_month_combo_box.setCurrentIndex(current_date.month() - 1)




        vendors_json_string = read_json_file(ManageVendors.VENDORS_FILE_PATH)
        vendor_dicts = json.loads(vendors_json_string)
        self.vendor_parameter_combobox.clear()
        self.vendor_parameter_combobox.addItems([vendor_dict[NAME_KEY] for vendor_dict in vendor_dicts])

        self.report_parameter_combobox.currentTextChanged.connect(self.on_report_parameter_changed)
        self.vendor_parameter_combobox.currentTextChanged.connect(self.on_vendor_parameter_changed)
        self.name_parameter_combobox.currentTextChanged.connect(self.on_name_parameter_changed)

        self.names = []
        self.costs_names = []

        self.on_report_parameter_changed()
        self.vendor_parameter = self.vendor_parameter_combobox.currentText()
        self.fill_names()

        self.cost_in_original_currency_doublespinbox.valueChanged.connect(self.on_cost_in_original_currency_changed)
        self.original_currency_combobox.currentTextChanged.connect(self.on_original_currency_changed)
        self.cost_in_local_currency_doublespinbox.valueChanged.connect(self.on_cost_in_local_currency_changed)
        self.cost_in_local_currency_with_tax_doublespinbox.valueChanged.connect(
            self.on_cost_in_local_currency_with_tax_changed)

        self.import_costs_button = costs_ui.costs_import_costs_button
        self.import_costs_button.clicked.connect(self.import_costs)
        self.import_costs_button.setEnabled(False)

        self.populate_data()

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

        self.populate_data()

    def on_vendor_parameter_changed(self):
        """Invoked when the vendor parameter changes"""
        self.vendor_parameter = self.vendor_parameter_combobox.currentText()
        if self.report_parameter:
            self.fill_names()

        self.populate_data()

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
                                                                                self.start_year_date_edit.date().year(),
                                                                                self.end_year_date_edit.date().year())
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
            self.name_parameter = self.name_parameter_combobox.currentText()
        else:
            print('Error, no connection')

    def on_name_parameter_changed(self):
        """Invoked when the name field parameter changes"""
        self.name_parameter = self.name_parameter_combobox.currentText()
        enable = False
        if self.name_parameter:
            enable = True

        self.cost_in_original_currency_doublespinbox.setEnabled(enable)
        self.original_currency_combobox.setEnabled(enable)
        self.cost_in_local_currency_doublespinbox.setEnabled(enable)
        self.cost_in_local_currency_with_tax_doublespinbox.setEnabled(enable)

        self.populate_data()

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

    def on_available_cost_clicked(self, index: int):
        self.populate_cost_fields()

    def populate_data(self):
        results = self.get_costs()
        # Sort results by date
        # results = sorted(results, key=lambda result: (result[4], result[5]))
        curr_cost = 0
        self.available_costs = []
        for result in results:
            if curr_cost != result[0] or not self.available_costs:
                cost_group = {"original_curr": result[0],  # Original cost
                               "curr": result[1],  # Currency
                               "local_curr": result[2],  # Local cost
                               "local_tax_curr": result[3],  # Local cost with tax
                               "start_year": result[7],
                               "start_month": result[8],
                               "end_year": result[7],
                               "end_month": result[8]}
                self.available_costs.append(cost_group)
            else:
                cost_group = self.available_costs[-1]
                cost_group["end_year"] = result[7]
                cost_group["end_month"] = result[8]

            curr_cost = result[0]

        self.populate_available_costs()
        self.populate_cost_fields()

    def populate_available_costs(self):
        self.available_costs_combo_box.clear()

        for price_group in self.available_costs:
            self.available_costs_combo_box.addItem(
                f"From {price_group['start_year']}-{price_group['start_month']:02d} "
                f"to {price_group['end_year']}-{price_group['end_month']:02d}, "
                f"Cost: {price_group['curr']} {price_group['original_curr']}")

    def populate_cost_fields(self):
        curr_cost_index = self.available_costs_combo_box.currentIndex()
        if curr_cost_index >= 0:  # Reset fields
            price_group = self.available_costs[curr_cost_index]
            self.start_year_date_edit.setDate(QDate(price_group['start_year'], 1, 1))
            self.end_year_date_edit.setDate(QDate(price_group['end_year'], 1, 1))

            self.start_month_combo_box.setCurrentIndex(int(price_group['start_month']) - 1)
            self.end_month_combo_box.setCurrentIndex(int(price_group['end_month']) - 1)

            self.cost_in_original_currency_doublespinbox.setValue(price_group['original_curr'])
            self.original_currency_combobox.setCurrentText(price_group['curr'])
            self.cost_in_local_currency_doublespinbox.setValue(price_group['local_curr'])
            self.cost_in_local_currency_with_tax_doublespinbox.setValue(price_group['local_tax_curr'])
            self.cost_in_original_currency_doublespinbox.repaint()

        else:
            self.clear_cost_fields()

        self.update_cost_frame.setDisabled(not self.name_parameter)

    def clear_cost_fields(self):
        """Empties the costs fields"""

        current_date = QDate.currentDate()
        start_date = QDate(current_date.year(), 1, 1)
        end_date = QDate(current_date.year(), 12, 1)
        self.start_year_date_edit.setDate(start_date)
        self.end_year_date_edit.setDate(end_date)

        self.start_month_combo_box.setCurrentIndex(start_date.month() - 1)
        self.end_month_combo_box.setCurrentIndex(end_date.month() - 1)

        self.cost_in_original_currency_doublespinbox.setValue(0)
        self.original_currency_combobox.setCurrentText("")
        self.cost_in_local_currency_doublespinbox.setValue(0)
        self.cost_in_local_currency_with_tax_doublespinbox.setValue(0)
        self.cost_in_original_currency_doublespinbox.repaint()

    def save_costs(self):
        """Saves the cost data: if it is nonzero, add it to the database; if it is zero, delete it from the database"""

        sql_data = []  # list(tuple(sql_test, data))
        is_inserting = self.cost_in_original_currency > 0 and self.original_currency != '' \
                       and self.cost_in_local_currency > 0 and self.cost_in_local_currency_with_tax > 0
        is_deleting = self.cost_in_original_currency == 0 and self.original_currency == '' \
                      and self.cost_in_local_currency == 0 and self.cost_in_local_currency_with_tax == 0

        # Get the number of months to be processed
        begin_date = QDate(self.start_year_date_edit.date().year(), self.start_month_combo_box.currentIndex() + 1, 1)
        end_date = QDate(self.end_year_date_edit.date().year(), self.end_month_combo_box.currentIndex() + 1, 1)

        if begin_date.year() == end_date.year():
            num_months = (end_date.month() - begin_date.month()) + 1
        else:
            num_months = (12 - begin_date.month() + end_date.month()) + 1
            num_years = end_date.year() - begin_date.year()
            num_months += (num_years - 1) * 12

        original_currency_cpm = self.cost_in_original_currency / num_months
        local_currency_cpm = self.cost_in_local_currency / num_months
        local_currency_tax_cpm = self.cost_in_local_currency_with_tax / num_months

        # Get sql_text and data for every month in the range
        for i in range(num_months):
            date = begin_date.addMonths(i)
            curr_month = date.month()
            curr_year = date.year()
            if is_inserting:
                sql_text, data = ManageDB.replace_costs_sql_text(
                    self.report_parameter,
                    ({NAME_FIELD_SWITCHER[self.report_parameter]: self.name_parameter,
                      'vendor': self.vendor_parameter,
                      'year': curr_year,
                      'month': curr_month,
                      'cost_in_original_currency': self.cost_in_original_currency,
                      'original_currency': self.original_currency,
                      'cost_in_local_currency': self.cost_in_local_currency,
                      'cost_in_local_currency_with_tax': self.cost_in_local_currency_with_tax,
                      'cost_in_original_currency_per_month': original_currency_cpm,
                      'cost_in_local_currency_per_month': local_currency_cpm,
                      'cost_in_local_currency_with_tax_per_month': local_currency_tax_cpm},))
                sql_data.append((sql_text, data))

            elif is_deleting:
                sql_text, data = ManageDB.delete_costs_sql_text(self.report_parameter, self.vendor_parameter,
                                                                curr_month, curr_year, self.name_parameter)
                sql_data.append((sql_text, data))

        if is_inserting or is_deleting:
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                for sql_text, data in sql_data:
                    ManageDB.run_sql(connection, sql_text, data, False)
                connection.close()
                ManageDB.backup_costs_data(self.report_parameter)
                if is_inserting:
                    show_message('Data inserted/replaced')
                elif is_deleting:
                    show_message('Data removed')
        else:
            show_message('Invalid entry')

        self.populate_data()

    def on_refresh_clicked(self):
        self.populate_cost_fields()

    def get_costs(self) -> list:
        """Fills the costs fields with data from the database"""

        if not self.report_parameter:
            print("Report parameter is empty")
            return []
        if not self.vendor_parameter:
            print("Vendor parameter is empty")
            return []
        if not self.name_parameter:
            print("Name parameter is empty")
            return []

        sql_text, data = ManageDB.get_costs_sql_text(self.report_parameter, self.vendor_parameter, self.name_parameter)
        results = []
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)
            # if not results:
            #     results.append((0.0, '', 0.0, 0.0))
            connection.close()

        return results if results else []
        # values = {}
        # index = 0
        # for field in COST_FIELDS:
        #     values[field[NAME_KEY]] = results[0][index]
        #     index += 1
        # self.cost_in_original_currency_doublespinbox.setValue(values['cost_in_original_currency'])
        # self.original_currency_combobox.setCurrentText(values['original_currency'])
        # self.cost_in_local_currency_doublespinbox.setValue(values['cost_in_local_currency'])
        # self.cost_in_local_currency_with_tax_doublespinbox.setValue(values['cost_in_local_currency_with_tax'])
        # self.cost_in_original_currency_doublespinbox.repaint()

    # def clear_costs(self):
    #     """Empties the costs fields"""
    #     self.cost_in_original_currency_doublespinbox.setValue(0.0)
    #     self.original_currency_combobox.setCurrentText('')
    #     self.cost_in_local_currency_doublespinbox.setValue(0.0)
    #     self.cost_in_local_currency_with_tax_doublespinbox.setValue(0.0)

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
