import xlsxwriter
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QButtonGroup

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
        self.cost_ratio_combo_box.addItems(["Cost in Local Currency with Tax",
                                            "Cost in Local Currency",
                                            "Cost in Original Currency"])

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
        if report_type in DATABASE_REPORTS:
            self.name_label.setText('Database')
        elif report_type in ITEM_REPORTS:
            self.name_label.setText('Item')
        elif report_type in PLATFORM_REPORTS:
            self.name_label.setText('Platform')
        elif report_type in TITLE_REPORTS:
            self.name_label.setText('Title')

    def update_name_combo_box(self):
        report_type = self.report_combo_box.currentText()
        vendor_name = self.vendor_combo_box.currentText()

        if not (report_type and vendor_name):
            return

        names = self.get_names(report_type, vendor_name)
        self.name_combo_box.clear()
        self.name_combo_box.addItems(names)

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
        data = None
        if curr_option == "Monthly":
            data = self.do_monthly_calculation(report_type, vendor_name)
        elif curr_option == "Yearly":
            print("Not yet supported")
        elif curr_option == "Top #":
            print("Not yet supported")
        elif curr_option == "Cost Ratio":
            print("Not yet supported")
        else:
            GeneralUtils.show_message("Select a calculation option")
            return

        if not data:
            print("Unable to generate chart")

        curr_chart_type = self.chart_button_group.checkedButton().text()
        if curr_chart_type == "Vertical Bar":
            self.create_vertical_bar_chart(data)

        elif curr_chart_type == "Horizontal Bar":
            print("Not yet supported")
        elif curr_chart_type == "Line":
            print("Not yet supported")
        else:
            GeneralUtils.show_message("Select a calculation option")
            return

    def do_monthly_calculation(self, report_type: str, vendor_name: str):
        name = self.name_combo_box.currentText()
        if not name:
            GeneralUtils.show_message(f"Select a {self.name_label.text()}")
            return
        metric_type = self.metric_type_combo_box.currentText()
        if not metric_type:
            GeneralUtils.show_message(f"Select a metric type")
            return

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
            return

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

    def create_vertical_bar_chart(self, data: dict):
        chart_title = self.chart_title_line_edit.text()
        horizontal_axis_title = self.horizontal_axis_line_edit.text()
        vertical_axis_title = self.vertical_axis_line_edit.text()

        file_path = GeneralUtils.choose_save(EXCEL_FILTER)
        if not file_path:
            return
        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': True})

        # Fill with month names
        row = 1
        for month in MONTHS:
            month_name = MONTHS[month].capitalize()
            worksheet.write(row, 0, month_name)
            row += 1

        # Fill with data
        column = 1
        for year in data:
            worksheet.write(0, column, year, bold)

            row = 1
            months = data[year]
            for month in MONTHS:
                if month in months:
                    worksheet.write(row, column, months[month])
                else:
                    worksheet.write(row, column, 0)
                row += 1

            column += 1

        chart_type = "column"
        chart = workbook.add_chart({'type': chart_type})

        workbook.close()
        GeneralUtils.open_file_or_dir(file_path)

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
