from xlsxwriter.exceptions import FileCreateError
from xlsxwriter.workbook import Workbook, Worksheet, Format
from vincent.colors import brews
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QButtonGroup
from PyQt5.QtGui import QStandardItem, QFont, QStandardItemModel

import ManageDB
import GeneralUtils
from Constants import *
from Settings import SettingsModel
from ui import VisualTab


class VisualController:
    """Controls the Visual tab

        :param visual_ui: The UI for visual_widget.
        """

    def __init__(self, vendors: list, settings: SettingsModel, tab_widget: QWidget, visual_ui: VisualTab.Ui_visual_tab):
        self.settings = settings
        self.tab_widget = tab_widget

        self.report_combo_box = visual_ui.report_combo_box
        self.report_combo_box.addItems(ALL_REPORTS)
        self.report_combo_box.currentTextChanged.connect(self.on_report_parameter_changed)

        self.vendor_combo_box = visual_ui.vendor_combo_box
        self.vendor_combo_box.addItems([vendor.name for vendor in vendors])
        self.vendor_combo_box.currentTextChanged.connect(self.on_vendor_parameter_changed)

        current_date = QDate.currentDate()
        self.start_year_date_edit = visual_ui.start_year_date_edit
        self.start_year_date_edit.setDate(current_date)
        self.end_year_date_edit = visual_ui.end_year_date_edit
        self.end_year_date_edit.setDate(current_date)

        self.start_month_combo_box = visual_ui.start_month_combo_box
        self.end_month_combo_box = visual_ui.end_month_combo_box

        for month in MONTH_NAMES:
            self.start_month_combo_box.addItem(month)
            self.end_month_combo_box.addItem(month)

        self.end_month_combo_box.setCurrentIndex(len(MONTH_NAMES) - 1)

        self.chart_button_group = QButtonGroup()
        self.chart_button_group.addButton(visual_ui.vertical_bar_radio_button)
        self.chart_button_group.addButton(visual_ui.horizontal_bar_radio_button)
        self.chart_button_group.addButton(visual_ui.line_radio_button)
        self.chart_button_group.buttons()[0].setChecked(True)

        self.calculation_button_group = QButtonGroup()
        self.calculation_button_group.addButton(visual_ui.monthly_radio_button)
        self.calculation_button_group.addButton(visual_ui.yearly_radio_button)
        self.calculation_button_group.addButton(visual_ui.top_radio_button)
        self.calculation_button_group.addButton(visual_ui.cost_ratio_radio_button)
        self.calculation_button_group.buttons()[0].setChecked(True)
        self.calculation_button_group.buttonClicked.connect(self.on_calculation_button_clicked)

        self.chart_title_line_edit = visual_ui.chart_title_line_edit
        self.horizontal_axis_line_edit = visual_ui.horizontal_axis_line_edit
        self.vertical_axis_line_edit = visual_ui.vertical_axis_line_edit

        self.metric_type_label = visual_ui.metric_type_label
        self.metric_type_combo_box = visual_ui.metric_type_combo_box
        self.name_label = visual_ui.name_label
        self.name_combo_box = visual_ui.name_combo_box
        self.top_label = visual_ui.top_label
        self.top_spin_box = visual_ui.top_spin_box
        self.cost_ratio_label = visual_ui.cost_ratio_label
        self.cost_ratio_combo_box = visual_ui.cost_ratio_combo_box
        self.cost_ratio_combo_box.addItems(["Cost In Original Currency",
                                            "Cost In Local Currency With Tax",
                                            "Cost In Local Currency"])

        self.option_views = {"metric_type": [self.metric_type_label, self.metric_type_combo_box],
                             "name": [self.name_label, self.name_combo_box],
                             "top": [self.top_label, self.top_spin_box],
                             "cost_ratio": [self.cost_ratio_label, self.cost_ratio_combo_box]}

        self.monthly_option_views = ["metric_type", "name"]
        self.yearly_option_views = ["metric_type", "name"]
        self.top_option_views = ["metric_type", "top"]
        self.cost_ratio_option_views = ["metric_type", "name", "cost_ratio"]

        self.open_file_check_box = visual_ui.open_file_checkBox
        self.open_folder_check_box = visual_ui.open_folder_checkBox
        self.create_chart_button = visual_ui.create_chart_button
        self.create_chart_button.clicked.connect(self.on_create_chart_clicked)

        report_type = self.report_combo_box.currentText()
        self.update_metric_type_combo_box(report_type)
        self.update_name_label(report_type)
        self.update_name_combo_box()
        self.update_option_views()

    def on_vendors_changed(self, vendors: list):
        """Handles the signal emitted when the system's vendor list is updated

        :param vendors: An updated list of the system's vendors
        """
        self.vendor_combo_box.clear()
        self.vendor_combo_box.addItems([vendor.name for vendor in vendors])

    def on_database_updated(self):
        self.update_name_combo_box()

    def on_report_parameter_changed(self, report_type):
        """Invoke when report type is changed"""
        self.update_metric_type_combo_box(report_type)
        self.update_name_label(report_type)
        self.update_name_combo_box()

    def on_vendor_parameter_changed(self, vendor_name):
        """Invoked when vendor is changed"""
        self.update_name_combo_box()

    def on_calculation_button_clicked(self):
        self.update_option_views()

    def on_create_chart_clicked(self):
        report_type = self.report_combo_box.currentText()
        if not report_type:
            GeneralUtils.show_message("Select a report type")
            return
        vendor_name = self.vendor_combo_box.currentText()
        if not report_type:
            GeneralUtils.show_message("Select a vendor")
            return

        curr_option = self.calculation_button_group.checkedButton().text()
        if curr_option == "Monthly":
            data = self.do_monthly_calculation(report_type, vendor_name)
        elif curr_option == "Yearly":
            data = self.do_yearly_calculation(report_type, vendor_name)
        elif curr_option == "Top #":
            data = self.do_top_num_calculation(report_type, vendor_name)
        elif curr_option == "Cost Ratio":
            data = self.do_cost_ratio_calculation(report_type, vendor_name)
        else:
            GeneralUtils.show_message("Select a calculation option")
            return

        if not data:
            print("Unable to generate data for chart")
            return

        try:
            file_path = GeneralUtils.choose_save(EXCEL_FILTER)
            if not file_path:
                return
            if not file_path.lower().endswith(".xlsx"):
                file_path += ".xlsx"

            curr_chart_type = self.chart_button_group.checkedButton().text()
            if curr_chart_type == "Vertical Bar":
                self.create_chart("column", data, file_path)
            elif curr_chart_type == "Horizontal Bar":
                self.create_chart("bar", data, file_path)
            elif curr_chart_type == "Line":
                self.create_chart("line", data, file_path)
            else:
                GeneralUtils.show_message("Select a calculation option")
                return

            if self.open_file_check_box.isChecked():
                GeneralUtils.open_file_or_dir(file_path)

            dir_path = "/".join(file_path.split("/")[:-1])
            if self.open_folder_check_box.isChecked():
                GeneralUtils.open_file_or_dir(dir_path)

        except FileCreateError as e:
            GeneralUtils.show_message("Unable to write to the selected file.\n"
                                      "Please close the file if it is open in Excel")

        except Exception as e:
            GeneralUtils.show_message("Unable to write to the selected file.\n"
                                      "Exception: " + str(e))

    def update_metric_type_combo_box(self, report_type: str):
        self.metric_type_combo_box.clear()
        if report_type in DATABASE_REPORTS:
            self.metric_type_combo_box.addItems(DATABASE_REPORTS_METRIC)
        elif report_type in ITEM_REPORTS:
            self.metric_type_combo_box.addItems(ITEM_REPORTS_METRIC)
        elif report_type in PLATFORM_REPORTS:
            self.metric_type_combo_box.addItems(PLATFORM_REPORTS_METRIC)
        elif report_type in TITLE_REPORTS:
            self.metric_type_combo_box.addItems(TITLE_REPORTS_METRIC)

    def update_name_label(self, report_type):
        name_field = NAME_FIELD_SWITCHER[report_type[:2]].capitalize()
        self.name_label.setText(name_field)

    def update_name_combo_box(self):
        report_type = self.report_combo_box.currentText()
        vendor_name = self.vendor_combo_box.currentText()
        start_year = self.start_year_date_edit.date().year()
        end_year = self.end_year_date_edit.date().year()

        if not (report_type and vendor_name):
            return

        names = self.get_names(report_type, vendor_name)
        costs_names = self.get_names_with_cost(report_type, vendor_name, start_year, end_year)
        self.name_combo_box.clear()

        cost_font = QFont()
        cost_font.setBold(True)
        model = QStandardItemModel()
        for name in names:
            item = QStandardItem(name)
            if name in costs_names:
                item.setFont(cost_font)

            model.appendRow(item)
        self.name_combo_box.setModel(model)

    def update_option_views(self):
        curr_option = self.calculation_button_group.checkedButton().text()

        def update_views(option_names: list):
            for option_name in self.option_views:
                show_views = option_name in option_names
                views = self.option_views[option_name]
                for view in views:
                    view.setVisible(show_views)

        if curr_option == "Monthly":
            update_views(self.monthly_option_views)
        elif curr_option == "Yearly":
            update_views(self.yearly_option_views)
        elif curr_option == "Top #":
            update_views(self.top_option_views)
        elif curr_option == "Cost Ratio":
            update_views(self.cost_ratio_option_views)

    def do_monthly_calculation(self, report_type: str, vendor_name: str) -> dict:
        name = self.name_combo_box.currentText()
        if not name:
            GeneralUtils.show_message(f"Select a {self.name_label.text()}")
            return {}
        metric_type = self.metric_type_combo_box.currentText()
        if not metric_type:
            GeneralUtils.show_message(f"Select a metric type")
            return {}

        start_year = self.start_year_date_edit.date().year()
        start_month = self.start_month_combo_box.currentIndex() + 1
        end_year = self.end_year_date_edit.date().year()
        end_month = self.end_month_combo_box.currentIndex() + 1

        sql_text, data = ManageDB.monthly_chart_search_sql_text(report_type, vendor_name, name, metric_type,
                                                                start_month, start_year, end_month, end_year)
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        results = None
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)
            connection.close()
        else:
            print('Error, no connection')

        if not results:
            GeneralUtils.show_message("No data found for this query")
            return {}

        year_data = {}
        for result in results:
            year = result[1]
            month = result[2]
            metric = result[3]

            if year not in year_data:
                year_data[year] = {month: metric}
            else:
                year_data[year][month] = metric

        return year_data

    def do_yearly_calculation(self, report_type: str, vendor_name: str) -> dict:
        name = self.name_combo_box.currentText()
        if not name:
            GeneralUtils.show_message(f"Select a {self.name_label.text()}")
            return {}
        metric_type = self.metric_type_combo_box.currentText()
        if not metric_type:
            GeneralUtils.show_message(f"Select a metric type")
            return {}

        start_year = self.start_year_date_edit.date().year()
        start_month = self.start_month_combo_box.currentIndex() + 1
        end_year = self.end_year_date_edit.date().year()
        end_month = self.end_month_combo_box.currentIndex() + 1

        if start_month != 1 or end_month != 12:
            if not GeneralUtils.ask_confirmation("Yearly type with non-calendar-year date range may produce odd "
                                                 "results - Continue anyway? "):
                return {}

        sql_text, data = ManageDB.yearly_chart_search_sql_text(report_type, vendor_name, name, metric_type,
                                                               start_month, start_year, end_month, end_year)
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        results = None
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)
            connection.close()
        else:
            print('Error, no connection')

        if not results:
            GeneralUtils.show_message("No data found for this query")
            return {}

        year_data = {}
        for result in results:
            year = result[1]
            metric = result[2]

            year_data[year] = metric

        return year_data

    def do_top_num_calculation(self, report_type: str, vendor_name: str) -> dict:
        top_num = self.top_spin_box.value()
        metric_type = self.metric_type_combo_box.currentText()
        if not metric_type:
            GeneralUtils.show_message(f"Select a metric type")
            return {}

        start_year = self.start_year_date_edit.date().year()
        start_month = self.start_month_combo_box.currentIndex() + 1
        end_year = self.end_year_date_edit.date().year()
        end_month = self.end_month_combo_box.currentIndex() + 1

        sql_text, data = ManageDB.top_number_chart_search_sql_text(report_type, vendor_name, metric_type, top_num,
                                                                   start_month, start_year, end_month, end_year)
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        results = None
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)
            connection.close()
        else:
            print('Error, no connection')

        if not results:
            GeneralUtils.show_message("No data found for this query")
            return {}

        data = {}
        for result in results:
            name = result[0]
            metric = result[1]

            data[name] = metric

        return data

    def do_cost_ratio_calculation(self, report_type: str, vendor_name: str) -> dict:
        cost_ratio_option = self.cost_ratio_combo_box.currentText()
        if not cost_ratio_option:
            GeneralUtils.show_message(f"Select a cost ratio option")
            return {}
        name = self.name_combo_box.currentText()
        if not name:
            GeneralUtils.show_message(f"Select a {self.name_label.text()}")
            return {}
        metric_type = self.metric_type_combo_box.currentText()
        if not metric_type:
            GeneralUtils.show_message(f"Select a metric type")
            return {}

        start_year = self.start_year_date_edit.date().year()
        start_month = self.start_month_combo_box.currentIndex() + 1
        end_year = self.end_year_date_edit.date().year()
        end_month = self.end_month_combo_box.currentIndex() + 1

        cost_sql_text, cost_data = ManageDB.cost_chart_search_sql_text(
            report_type, vendor_name, name, metric_type, start_month, start_year, end_month, end_year)
        search_sql_text, search_data = ManageDB.monthly_chart_search_sql_text(
            report_type, vendor_name, name, metric_type, start_month, start_year, end_month, end_year)
        cost_results = []
        search_results = []

        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            cost_results = ManageDB.run_select_sql(connection, cost_sql_text, cost_data)
            search_results = ManageDB.run_select_sql(connection, search_sql_text, search_data)
            connection.close()
        else:
            print('Error, no connection')

        if not cost_results:
            # print("No cost result")
            GeneralUtils.show_message("No cost data found for this query")
            return {}
        if not search_results:
            # print("No search result")
            GeneralUtils.show_message("No search data found for this query")
            return {}

        is_original_currency = self.cost_ratio_combo_box.currentText() == 'Cost In Original Currency'
        is_local_currency = self.cost_ratio_combo_box.currentText() == 'Cost In Local Currency'
        is_local_currency_tax = self.cost_ratio_combo_box.currentText() == 'Cost In Local Currency With Tax'

        search_dict = {}
        for result in search_results:
            search_dict[(result[1], result[2])] = result

        costs_dict = {}
        for result in cost_results:
            costs_dict[(result[5], result[6])] = result

        year_data = {}
        for year, month in search_dict:
            if year not in year_data:
                year_data[year] = [0.0, 0.0, 0.0]

            metric = search_dict[year, month][3]
            if metric == 0:
                continue

            year_data[year][2] += metric

            if (year, month) in costs_dict:
                cost_in_original_currency = costs_dict[year, month][1]
                # original_currency = costs_dict[year, month][2]
                cost_in_local_currency = costs_dict[year, month][3]
                cost_in_local_currency_with_tax = costs_dict[year, month][4]

                if is_original_currency:
                    year_data[year][1] += cost_in_original_currency
                elif is_local_currency:
                    year_data[year][1] += cost_in_local_currency
                elif is_local_currency_tax:
                    year_data[year][1] += cost_in_local_currency_with_tax

                year_data[year][0] = year_data[year][1] / year_data[year][2]

        return year_data

    def create_chart(self, chart_type: str, data: dict, file_path: str):
        workbook = Workbook(file_path)
        worksheet = workbook.add_worksheet()
        chart = workbook.add_chart({"type": chart_type})
        bold_format = workbook.add_format({"bold": True})

        curr_option = self.calculation_button_group.checkedButton().text()
        if curr_option == "Monthly":
            num_categories, num_value_columns, chart_start_column = \
                self.populate_monthly_chart(data, worksheet, bold_format)
        elif curr_option == "Yearly":
            num_categories, num_value_columns, chart_start_column = \
                self.populate_yearly_chart(data, worksheet, bold_format)
        elif curr_option == "Top #":
            num_categories, num_value_columns, chart_start_column = \
                self.populate_top_num_chart(data, worksheet, bold_format)
        elif curr_option == "Cost Ratio":
            num_categories, num_value_columns, chart_start_column = \
                self.populate_cost_ratio_chart(data, worksheet, bold_format)
        else:
            GeneralUtils.show_message("Select a calculation option")
            return

        start_category_index = 3
        end_category_index = num_categories + start_category_index - 1
        for i in range(1, num_value_columns):
            # [sheet_name, first_row, first_col, last_row, last_col]
            chart.add_series({
                "name": ["Sheet1", 2, i],
                "categories": ["Sheet1", start_category_index, 0, end_category_index, 0],
                "values": ["Sheet1", start_category_index, i, end_category_index, i],
                "fill": {"color": brews[CHART_COLOR_SET][i]}
            })

        self.customize_chart(chart)
        worksheet.write(0, 0, f"Created by COUNTER 5 Report Tool on {QDate.currentDate().toString('yyyy-MM-dd')}")
        chart_options = {'x_scale': 2, 'y_scale': 2}
        worksheet.insert_chart(3, chart_start_column, chart, chart_options)

        workbook.close()

    def populate_monthly_chart(self, data: dict, worksheet: Worksheet, bold_format: Format) -> (int, int, int):
        start_year = self.start_year_date_edit.date().year()
        start_month = self.start_month_combo_box.currentIndex() + 1
        end_year = self.end_year_date_edit.date().year()
        end_month = self.end_month_combo_box.currentIndex() + 1

        num_months = (end_year - start_year) * 12 + \
                     (end_month - start_month) + 1

        num_categories = 12
        num_value_columns = int(num_months / 12) + 1
        chart_start_column = num_value_columns + 2

        # Fill with month names
        begin_date = QDate(start_year, start_month, 1)
        row = 3
        for i in range(12):
            curr_date = begin_date.addMonths(i)
            worksheet.write(row, 0, curr_date.toString("MMMM"))
            row += 1

        # Fill with data
        start_row = 3
        start_column = 1
        for i in range(num_months):
            curr_date = begin_date.addMonths(i)

            chart_month_index = (i % 12) + start_row
            chart_year_index = int(i / 12) + start_column

            year_index = int(i / 12)
            col_start_date = begin_date.addYears(year_index)
            col_end_date = begin_date.addYears(year_index + 1).addMonths(-1)

            worksheet.write(2, chart_year_index,
                            f"{col_start_date.toString('MMMM yyyy')}-{col_end_date.toString('MMMM yyyy')}",
                            bold_format)

            if curr_date.year() in data:
                if curr_date.month() in data[curr_date.year()]:
                    metric = data[curr_date.year()][curr_date.month()]
                else:
                    metric = 0

            else:
                metric = 0

            worksheet.write(chart_month_index, chart_year_index, metric)

        # # Fill with month names
        # for month in MONTHS:
        #     month_name = MONTHS[month].capitalize()
        #     worksheet.write(row, 0, month_name)
        #     row += 1
        #
        # column = 1
        # for year in data:
        #     num_value_columns += 1
        #     chart_start_column += 1
        #     worksheet.write(2, column, year, bold_format)
        #
        #     row = 3
        #     months = data[year]
        #     for month in MONTHS:
        #         if month in months:
        #             metric = months[month]
        #         else:
        #             metric = 0
        #
        #         worksheet.write(row, column, metric)
        #         row += 1
        #
        #     column += 1

        return num_categories, num_value_columns, chart_start_column

    def populate_yearly_chart(self, data: dict, worksheet: Worksheet, bold_format: Format) -> (int, int, int):
        metric_type = self.metric_type_combo_box.currentText()
        if not metric_type:
            GeneralUtils.show_message(f"Select a metric type")
            return

        num_categories = len(data.keys())
        num_value_columns = 1
        chart_start_column = 3

        worksheet.write(2, 1, metric_type, bold_format)
        row = 3
        for year in data:
            worksheet.write(row, 0, year)
            worksheet.write(row, 1, data[year])
            row += 1

        return num_categories, num_value_columns, chart_start_column

    def populate_top_num_chart(self, data: dict, worksheet: Worksheet, bold_format: Format) -> (int, int, int):
        metric_type = self.metric_type_combo_box.currentText()
        if not metric_type:
            GeneralUtils.show_message(f"Select a metric type")
            return

        num_categories = len(data.keys())
        num_value_columns = 1
        chart_start_column = 3

        worksheet.write(2, 1, metric_type, bold_format)
        row = 3
        for name in data:
            worksheet.write(row, 0, name)
            worksheet.write(row, 1, data[name])
            row += 1

        return num_categories, num_value_columns, chart_start_column

    def populate_cost_ratio_chart(self, data: dict, worksheet: Worksheet, bold_format: Format) -> (int, int, int):
        metric_type = self.metric_type_combo_box.currentText()
        if not metric_type:
            GeneralUtils.show_message(f"Select a metric type")
            return

        num_categories = len(data)
        num_value_columns = 1
        chart_start_column = 5

        cost_ratio_option = self.cost_ratio_combo_box.currentText()

        worksheet.write(2, 1, cost_ratio_option + " Per Metric", bold_format)
        worksheet.write(2, 2, cost_ratio_option, bold_format)
        worksheet.write(2, 3, metric_type, bold_format)

        row = 3
        for year in data:
            worksheet.write(row, 0, year)
            worksheet.write(row, 1, data[year][0])
            worksheet.write(row, 2, data[year][1])
            worksheet.write(row, 3, data[year][2])
            row += 1

        return num_categories, num_value_columns, chart_start_column

    def customize_chart(self, chart):
        title = self.chart_title_line_edit.text()
        hor_axis_title = self.horizontal_axis_line_edit.text()
        ver_axis_title = self.vertical_axis_line_edit.text()

        vendor_name = self.vendor_combo_box.currentText()

        curr_option = self.calculation_button_group.checkedButton().text()
        if curr_option == "Monthly":
            hor_axis_title = hor_axis_title if hor_axis_title else "Month"
            title = title if title else self.name_combo_box.currentText() + f" - {vendor_name}"
        elif curr_option == "Yearly":
            hor_axis_title = hor_axis_title if hor_axis_title else "Year"
            title = title if title else self.name_combo_box.currentText() + f" - {vendor_name}"
        elif curr_option == "Top #":
            hor_axis_title = hor_axis_title if hor_axis_title else self.name_label.text()
            top_num = self.top_spin_box.value()
            if top_num > 0:
                title = title if title else f"Top {top_num} {self.metric_type_combo_box.currentText()} - {vendor_name}"
            else:
                title = title if title else f"Top {self.metric_type_combo_box.currentText()} - {vendor_name}"
        elif curr_option == "Cost Ratio":
            hor_axis_title = hor_axis_title if hor_axis_title else "Year"
            title = title if title else f"{self.cost_ratio_combo_box.currentText()} Per Metric For " \
                                        f"{self.metric_type_combo_box.currentText()} - {vendor_name}"
        else:
            GeneralUtils.show_message("Select a calculation option")
            return

        ver_axis_title = ver_axis_title if ver_axis_title else self.metric_type_combo_box.currentText()

        chart.set_title({'name': title})
        chart.set_x_axis({'name': hor_axis_title})
        chart.set_y_axis({'name': ver_axis_title})

        chart.set_style(11)

    @staticmethod
    def get_names(report_type: str, vendor_name: str) -> list:
        sql_text, data = ManageDB.get_names_sql_text(report_type, vendor_name)
        results = None
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)

        return [result[0] for result in results] if results else []

    @staticmethod
    def get_names_with_cost(report_type: str, vendor_name: str, start_year: int, end_year: int):
        sql_text, data = ManageDB.get_names_with_costs_sql_text(report_type, vendor_name, start_year, end_year)
        results = None
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)

        return [result[0] for result in results] if results else []
