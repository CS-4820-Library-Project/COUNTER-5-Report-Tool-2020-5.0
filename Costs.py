import json
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QCheckBox, QDialogButtonBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont

import ManageDB
import ManageVendors
from Settings import SettingsModel
from ui import CostsTab
from GeneralUtils import *


class CostsController:
    """Controls the Costs tab

    :param costs_ui: the UI for the costs_widget
    :param settings: the user's settings"""

    def __init__(self, tab_widget: QWidget, costs_ui: CostsTab.Ui_costs_tab, settings: SettingsModel):
        self.costs_ui = costs_ui
        self.settings = settings
        self.tab_widget = tab_widget

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
        self.original_currency = settings.default_currency

        self.cost_in_local_currency_doublespinbox = costs_ui.costs_cost_in_local_currency_doublespinbox
        self.cost_in_local_currency = 0.0

        self.cost_in_local_currency_with_tax_doublespinbox = \
            costs_ui.costs_cost_in_local_currency_with_tax_doublespinbox
        self.cost_in_local_currency_with_tax = 0.0

        # set up buttons
        self.save_costs_button = costs_ui.costs_save_button
        self.save_costs_button.clicked.connect(self.insert_cost)

        self.refresh_button = costs_ui.costs_load_button
        self.refresh_button.clicked.connect(self.on_refresh_clicked)

        self.clear_button = costs_ui.costs_clear_button
        self.clear_button.clicked.connect(self.clear_cost_fields)

        self.available_costs_combo_box = costs_ui.available_costs_combo_box
        self.available_costs_combo_box.currentIndexChanged.connect(self.on_available_cost_clicked)
        self.available_costs = []

        self.delete_cost_button = costs_ui.delete_cost_button
        self.delete_cost_button.clicked.connect(self.delete_current_cost)
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
        self.import_costs_button.clicked.connect(self.on_import_clicked)
        self.export_costs_button = costs_ui.export_costs_button
        self.export_costs_button.clicked.connect(self.on_export_clicked)

        costs_ui.import_help_button.clicked.connect(
            lambda: show_message("If vendor and item names do not exactly match those labels in the search database, "
                                 "your cost data will silently be lost. Avoid this by using only vendor and item names "
                                 "provided in an Export Costs file with 'include items without cost data' selected."))

        self.update_costs()

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

        self.update_costs()

    def on_vendor_parameter_changed(self):
        """Invoked when the vendor parameter changes"""
        self.vendor_parameter = self.vendor_parameter_combobox.currentText()
        if self.report_parameter:
            self.fill_names()

        self.update_costs()

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
            # if self.settings.show_debug_messages: print(costs_results)
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
        self.update_costs()

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
        """Invoked when a cost is selected"""
        self.populate_cost_fields()

    def update_costs(self):
        """Updates the class with latest cost data"""
        valid_parameters = True
        self.available_costs = []
        if not self.report_parameter:
            # print("Report parameter is empty")
            valid_parameters = False
        if not self.vendor_parameter:
            # print("Vendor parameter is empty")
            valid_parameters = False
        if not self.name_parameter:
            # print("Name parameter is empty")
            valid_parameters = False

        if valid_parameters:
            results = self.get_costs(self.report_parameter, self.vendor_parameter, self.name_parameter)
            report_type_name = NAME_FIELD_SWITCHER[self.report_parameter]
            self.available_costs = self.cost_results_to_dicts(results, report_type_name)

        self.populate_available_costs()
        self.populate_cost_fields()

    def populate_available_costs(self):
        """Shows available costs for the current selection"""
        self.available_costs_combo_box.clear()

        for price_group in self.available_costs:
            self.available_costs_combo_box.addItem(
                f"From {price_group['start_year']}-{price_group['start_month']:02d} "
                f"to {price_group['end_year']}-{price_group['end_month']:02d}, "
                f"Cost: {price_group['original_currency']} {price_group['cost_in_original_currency']:.2f}")

    def populate_cost_fields(self):
        """Populates the cost edit fields with selected cost data"""
        curr_cost_index = self.available_costs_combo_box.currentIndex()
        if curr_cost_index >= 0:  # Reset fields
            price_group = self.available_costs[curr_cost_index]
            self.start_year_date_edit.setDate(QDate(price_group['start_year'], 1, 1))
            self.end_year_date_edit.setDate(QDate(price_group['end_year'], 1, 1))

            self.start_month_combo_box.setCurrentIndex(int(price_group['start_month']) - 1)
            self.end_month_combo_box.setCurrentIndex(int(price_group['end_month']) - 1)

            self.cost_in_original_currency_doublespinbox.setValue(price_group['cost_in_original_currency'])
            self.original_currency_combobox.setCurrentText(price_group['original_currency'])
            self.cost_in_local_currency_doublespinbox.setValue(price_group['cost_in_local_currency'])
            self.cost_in_local_currency_with_tax_doublespinbox.setValue(price_group['cost_in_local_currency_with_tax'])

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
        self.original_currency_combobox.setCurrentText(self.settings.default_currency)
        self.cost_in_local_currency_doublespinbox.setValue(0)
        self.cost_in_local_currency_with_tax_doublespinbox.setValue(0)

    def insert_cost(self):
        """Inserts cost data"""

        if self.cost_in_original_currency <= 0 or \
                self.original_currency == '' or \
                self.cost_in_local_currency <= 0 or \
                self.cost_in_local_currency_with_tax <= 0:
            show_message("Fields can't be empty or 0")
            return

        begin_date = QDate(self.start_year_date_edit.date().year(), self.start_month_combo_box.currentIndex() + 1, 1)
        end_date = QDate(self.end_year_date_edit.date().year(), self.end_month_combo_box.currentIndex() + 1, 1)

        if begin_date > end_date:
            show_message('Start Date is higher than End Date')
            return

        values = self.get_insert_sql_values(
            begin_date, end_date, self.report_parameter, self.name_parameter, self.vendor_parameter,
            self.cost_in_original_currency, self.original_currency, self.cost_in_local_currency,
            self.cost_in_local_currency_with_tax)

        sql_text, data = ManageDB.replace_costs_sql_text(self.report_parameter, tuple(values))
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            ManageDB.run_sql(connection, sql_text, data, False)
            connection.close()
            ManageDB.backup_costs_data(self.report_parameter)
            self.update_costs()
            show_message('Cost data inserted/updated')

    def delete_current_cost(self):
        """Deletes the selected cost data"""
        curr_cost_index = self.available_costs_combo_box.currentIndex()
        if curr_cost_index < 0:
            return

        curr_cost = self.available_costs[curr_cost_index]
        begin_date = QDate(curr_cost["start_year"], curr_cost["start_month"], 1)
        end_date = QDate(curr_cost["end_year"], curr_cost["end_month"], 1)

        sql_data = self.get_delete_sql_data(
            begin_date, end_date, self.report_parameter, self.name_parameter, self.vendor_parameter)

        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            for sql_text, data in sql_data:
                ManageDB.run_sql(connection, sql_text, data, False)
            connection.close()
            ManageDB.backup_costs_data(self.report_parameter)
            self.update_costs()
            show_message('Cost data deleted')

    def on_refresh_clicked(self):
        """Invoked when the refresh button is clicked"""
        self.populate_cost_fields()

    def on_import_clicked(self):
        """Invoked when the import button is clicked, imports cost data"""
        dialog = QDialog(self.tab_widget, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        dialog.setWindowTitle("Import Costs")
        layout = QVBoxLayout(dialog)

        report_type_combo_box = QComboBox(dialog)
        report_type_combo_box.addItems(REPORT_TYPE_SWITCHER.keys())

        def import_costs():
            def wash_money(cost):
                cost = re.sub(r'[^\d.]+', '', str(cost))

                return float(cost)

            try:
                file_path = choose_file(TSV_FILTER)
                if not file_path:
                    return

                file = open(file_path, 'r', encoding="utf-8", newline='')
                dict_reader = csv.DictReader(file, delimiter='\t')

                report_type = report_type_combo_box.currentText()
                report_type_name = NAME_FIELD_SWITCHER[report_type]

                connection = ManageDB.create_connection(DATABASE_LOCATION)
                if connection is not None:
                    all_values = []
                    for row in dict_reader:
                        if not row[report_type_name]: continue
                        name = row[report_type_name]

                        if not row["vendor"]: continue
                        vendor = row["vendor"]

                        if not row["start_year"]: continue
                        start_year = int(row["start_year"])

                        if not row["start_month"]: continue
                        start_month = int(row["start_month"])

                        if not row["end_year"]: continue
                        end_year = int(row["end_year"])

                        if not row["end_month"]: continue
                        end_month = int(row["end_month"])

                        if not row["original_currency"]: continue
                        original_currency = str(row["original_currency"])

                        if not row["cost_in_original_currency"]: continue
                        cost_in_original_currency = wash_money(row["cost_in_original_currency"])

                        if not row["cost_in_local_currency"]: continue
                        cost_in_local_currency = wash_money(row["cost_in_local_currency"])

                        if not row["cost_in_local_currency_with_tax"]: continue
                        cost_in_local_currency_with_tax = wash_money(row["cost_in_local_currency_with_tax"])

                        begin_date = QDate(start_year, start_month, 1)
                        end_date = QDate(end_year, end_month, 1)
                        if begin_date > end_date:
                            continue

                        values = self.get_insert_sql_values(
                            begin_date, end_date, report_type, name, vendor, cost_in_original_currency,
                            original_currency, cost_in_local_currency, cost_in_local_currency_with_tax)
                        all_values += values

                    sql_text, data = ManageDB.replace_costs_sql_text(report_type, tuple(all_values))
                    ManageDB.run_sql(connection, sql_text, data, False)

                connection.close()
                file.close()
                ManageDB.backup_costs_data(report_type)
                self.update_costs()
                show_message('Import successful')
                dialog.close()

            except Exception as e:
                show_message(f"File import failed: {e}")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        button_box.accepted.connect(import_costs)
        button_box.rejected.connect(lambda: dialog.close())

        layout.addWidget(report_type_combo_box)
        layout.addWidget(button_box)

        dialog.exec_()

    def on_export_clicked(self):
        """Invoked when the export button is clicked, exports cost data"""
        dialog = QDialog(self.tab_widget, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        dialog.setWindowTitle("Export Costs")
        layout = QVBoxLayout(dialog)
        all_vendors_text = "All Vendors"

        report_type_combo_box = QComboBox(dialog)
        report_type_combo_box.addItems(REPORT_TYPE_SWITCHER.keys())

        vendor_combo_box = QComboBox(dialog)
        vendor_combo_box.addItems([all_vendors_text] + [self.vendor_parameter_combobox.itemText(i)
                                                        for i in range(self.vendor_parameter_combobox.count())])

        fill_check_box = QCheckBox("Include items without cost data", dialog)

        def export_costs():
            report_type = report_type_combo_box.currentText()
            vendor_name = vendor_combo_box.currentText()

            cost_results = self.get_costs(report_type, None if vendor_name == all_vendors_text else vendor_name)

            report_type_name = NAME_FIELD_SWITCHER[report_type]
            cost_dicts = self.cost_results_to_dicts(cost_results, report_type_name)

            # Format currency columns
            for cost_dict in cost_dicts:
                cost_dict["cost_in_original_currency"] = f"{cost_dict['cost_in_original_currency']:,.2f}"
                cost_dict["cost_in_local_currency"] = f"{cost_dict['cost_in_local_currency']:,.2f}"
                cost_dict["cost_in_local_currency_with_tax"] = f"{cost_dict['cost_in_local_currency_with_tax']:,.2f}"

            if fill_check_box.isChecked():
                name_results = self.get_names(report_type, None if vendor_name == all_vendors_text else vendor_name)
                names_with_cost_data = set()
                for cost_dict in cost_dicts:
                    names_with_cost_data.add((cost_dict[report_type_name], cost_dict["vendor"]))

                for name in name_results:
                    if (name[0], name[1]) not in names_with_cost_data:
                        cost_dicts.append({report_type_name: name[0],
                                           "vendor": name[1],
                                           "cost_in_original_currency": None,
                                           "original_currency": None,
                                           "cost_in_local_currency": None,
                                           "cost_in_local_currency_with_tax": None,
                                           "start_year": None,
                                           "start_month": None,
                                           "end_year": None,
                                           "end_month": None})

            try:
                file_path = choose_save(TSV_FILTER)
                if not file_path:
                    return

                file = open(file_path, 'w', encoding="utf-8", newline='')
                column_names = [report_type_name,
                                "vendor",
                                "start_year",
                                "start_month",
                                "end_year",
                                "end_month",
                                "cost_in_original_currency",
                                "original_currency",
                                "cost_in_local_currency",
                                "cost_in_local_currency_with_tax"]

                dict_writer = csv.DictWriter(file, column_names, delimiter='\t')
                dict_writer.writeheader()
                dict_writer.writerows(cost_dicts)

                file.close()
                show_message(f"Exported to {file_path}")
                dialog.close()
            except Exception as e:
                show_message(f"File export failed: {e}")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        button_box.accepted.connect(export_costs)
        button_box.rejected.connect(lambda: dialog.close())

        layout.addWidget(report_type_combo_box)
        layout.addWidget(vendor_combo_box)
        layout.addWidget(fill_check_box)
        layout.addWidget(button_box)
        dialog.exec_()

    @staticmethod
    def get_costs(report_type: str, vendor_name: str = None, name: str = None) -> list:
        """Fills the costs fields with data from the database"""

        sql_text, data = ManageDB.get_costs_sql_text(report_type, vendor_name, name)
        results = []
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)
            connection.close()

        return results if results else []

    @staticmethod
    def get_names(report_type: str, vendor_name: str = None):
        sql_text, data = ManageDB.get_names_sql_text(report_type, vendor_name)
        results = []
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)
            connection.close()

        return results if results else []

    @staticmethod
    def get_insert_sql_values(begin_date: QDate, end_date: QDate, report_type: str, name: str, vendor: str,
                              cost_in_original_currency: float, original_currency: str, cost_in_local_currency: float,
                              cost_in_local_currency_with_tax: float) -> list:

        num_months = (end_date.year() - begin_date.year()) * 12 + \
                     (end_date.month() - begin_date.month()) + 1

        # Get sql values for every month in the range
        values = []
        for i in range(num_months):
            date = begin_date.addMonths(i)
            curr_month = date.month()
            curr_year = date.year()

            values.append({NAME_FIELD_SWITCHER[report_type]: name,
                           'vendor': vendor,
                           'year': curr_year,
                           'month': curr_month,
                           'cost_in_original_currency': cost_in_original_currency / num_months,
                           'original_currency': original_currency,
                           'cost_in_local_currency': cost_in_local_currency / num_months,
                           'cost_in_local_currency_with_tax': cost_in_local_currency_with_tax / num_months})

        # sql_text, data = ManageDB.replace_costs_sql_text(report_type, tuple(values))
        # sql_data.append((sql_text, data))

        return values

    @staticmethod
    def get_delete_sql_data(begin_date: QDate, end_date: QDate, report_type: str, name: str, vendor: str) -> list:
        sql_data = []  # list(tuple(sql_text, data))
        num_months = (end_date.year() - begin_date.year()) * 12 + \
                     (end_date.month() - begin_date.month()) + 1

        # Get sql_text and data for every month in the range
        for i in range(num_months):
            date = begin_date.addMonths(i)
            curr_month = date.month()
            curr_year = date.year()

            sql_text, data = ManageDB.delete_costs_sql_text(report_type, vendor,
                                                            curr_month, curr_year, name)
            sql_data.append((sql_text, data))

        return sql_data

    @staticmethod
    def cost_results_to_dicts(cost_results, report_type_name: str):
        curr_cost = 0
        cost_dicts = []
        for result in cost_results:
            if curr_cost != result[2] or not cost_dicts:
                cost_group = {report_type_name: result[0],
                              "vendor": result[1],
                              "cost_in_original_currency": result[2],
                              "original_currency": result[3],
                              "cost_in_local_currency": result[4],
                              "cost_in_local_currency_with_tax": result[5],
                              "start_year": result[6],
                              "start_month": result[7],
                              "end_year": result[6],
                              "end_month": result[7]}
                cost_dicts.append(cost_group)
            else:
                cost_group = cost_dicts[-1]
                cost_group["cost_in_original_currency"] += result[2]
                cost_group["cost_in_local_currency"] += result[4]
                cost_group["cost_in_local_currency_with_tax"] += result[5]
                cost_group["end_year"] = result[6]
                cost_group["end_month"] = result[7]

            curr_cost = result[2]

        return cost_dicts
