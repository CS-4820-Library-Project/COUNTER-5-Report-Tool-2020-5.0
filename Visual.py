from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QButtonGroup

import ManageDB
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

        self.vendor_combo_box = visual_ui.vendor_combo_box
        self.vendor_combo_box.addItems([vendor.name for vendor in vendors])

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

        self.options = {"metric_type": [self.metric_type_label, self.metric_type_combo_box],
                        "name": [self.name_label, self.name_combo_box],
                        "top": [self.top_label, self.top_spin_box],
                        "cost_ratio": [self.cost_ratio_label, self.cost_ratio_combo_box]}

        self.open_file_check_box = visual_ui.open_file_checkBox
        self.open_folder_check_box = visual_ui.open_folder_checkBox
        self.create_chart_button = visual_ui.create_chart_button

    def on_vendors_changed(self, vendors: list):
        """Handles the signal emitted when the system's vendor list is updated

        :param vendors: An updated list of the system's vendors
        """
        self.vendor_combo_box.clear()
        self.vendor_combo_box.addItems([vendor.name for vendor in vendors])

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

    def on_report_parameter_changed(self, report_type):
        """Invoke when report type is changed"""
        self.update_metric_type_combo_box(report_type)
        self.update_name_label(report_type)

    @staticmethod
    def get_names(report_type: str, vendor_name: str) -> list:
        sql_text, data = ManageDB.get_names_sql_text(report_type, vendor_name)
        results = None
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)

        return [result[0] for result in results] if results else []

    def get_names_with_cost(self, report_type: str, vendor_name: str):
        print()