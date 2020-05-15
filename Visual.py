"""This module handles all operations involving the visual tab."""

import calendar
import datetime
import json
import os
from _operator import itemgetter
from typing import Sequence

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont

import xlsxwriter
from datetime import date

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QDialog

import GeneralUtils
from GeneralUtils import *
import ManageDB
import ManageVendors
from Settings import SettingsModel
from ui import MessageDialog, VisualTab
from Constants import *


class VisualController:
    """Controls the Visual tab

        :param visual_ui: The UI for visual_widget.
        """

    def __init__(self, visual_ui: VisualTab.Ui_visual_tab, settings: SettingsModel):
        self.settings = settings

        # set up and configure report type combobox
        self.report_parameter = visual_ui.search_report_parameter_combobox_2
        self.report_parameter.addItems(ALL_REPORTS)
        self.report_parameter.currentTextChanged[str].connect(self.on_report_parameter_changed)

        # set up and configure cost ratio combobox
        self.cost_parameter = visual_ui.cost_ratio_option_combobox
        COST_TYPE_ALL = ('Cost in Local Currency with Tax', 'Cost in Local Currency', 'Cost in Original Currency')
        self.cost_parameter.addItems(COST_TYPE_ALL)

        # set up and configure cost ratio frame
        self.frame_cost = visual_ui.edit_cost_ratio_frame
        self.frame_cost.setEnabled(False)

        # set up and configure top num frame
        self.top_num_frame = visual_ui.edit_top_num_frame
        self.top_num_frame.setEnabled(False)

        # set up top num spinbox and configure lower and upper bounds
        self.top_num_edit = visual_ui.top_num_spinbox

        # set up chart type radio buttons
        self.h_bar_radio = visual_ui.radioButton
        self.v_bar_radio = visual_ui.radioButton_3
        self.line_radio = visual_ui.radioButton_4
        self.v_bar_radio.setChecked(True)

        # set up calculations type radio buttons
        self.monthly_radio = visual_ui.monthly_radioButton
        self.yearly_radio = visual_ui.yearly_radioButton
        self.topNum_radio = visual_ui.topnum_radioButton
        self.costRatio_radio = visual_ui.costratio_radioButton

        # configure calculation type radio buttons and connect with method
        self.monthly_radio.setChecked(True)
        self.monthly_radio.toggled.connect(self.on_calculation_type_changed)
        self.yearly_radio.toggled.connect(self.on_calculation_type_changed)
        self.topNum_radio.toggled.connect(self.on_calculation_type_changed)
        self.costRatio_radio.toggled.connect(self.on_calculation_type_changed)

        # set up start year dateedit
        self.start_year_parameter = visual_ui.search_start_year_parameter_dateedit_2
        self.start_year_parameter.setDate(date.today())

        # set up end year dateedit
        self.end_year_parameter = visual_ui.search_end_year_parameter_dateedit_2
        self.end_year_parameter.setDate(date.today())

        # set up name label
        self.name_label = visual_ui.visual_name_label

        # set up name combobox
        self.name_combobox = visual_ui.visual_name_parameter_combobox
        self.name = None
        self.metric = visual_ui.metric_Type_comboBox
        self.metric.addItems(DATABASE_REPORTS_METRIC)

        self.vendor = visual_ui.visual_vendor_parameter_combobox
        self.vendor.currentTextChanged.connect(self.on_vendor_changed)
        self.vendor_parameter = None
        self.vendor_parameter = self.vendor.currentText()
        vendors_json_string = GeneralUtils.read_json_file(ManageVendors.VENDORS_FILE_PATH)
        vendor_dicts = json.loads(vendors_json_string)
        self.vendor.clear()
        self.vendor.addItem("")
        self.vendor.addItems([vendor_dict['name'] for vendor_dict in vendor_dicts])

        # set up the search clauses
        self.and_clause_parameters = None

        # set up create chart button
        self.create_chart_button = visual_ui.create_chart_button
        self.create_chart_button.clicked.connect(self.createChart)

        # set up customize chart field
        self.chart_title_edit = visual_ui.chart_title_lineEdit
        self.horizontal_axis_edit = visual_ui.horizontal_axis_lineEdit
        self.vertical_axis_edit = visual_ui.vertical_axis_lineEdit

        # set up open file and open folder check box
        self.open_file = visual_ui.open_file_checkBox
        self.open_folder = visual_ui.open_folder_checkBox
        self.file_name = None

        self.data = []
        self.temp_results = []
        self.top_num = None
        self.results = []
        self.names = []
        self.costs_names = []

    def update_settings(self, settings: SettingsModel):
        """Called when the settings are saved

        :param settings: the new settings"""
        self.settings = settings
        self.local_currency = self.settings.default_currency
        #self.load_currency_list()

    def database_updated(self, code: int):
        """Called when the database is updated

        :param code: the exit code of the update"""
        self.fill_names()

    def load_vendor_list(self, vendors: Sequence[ManageVendors.Vendor]):
        """Updates the vendor list combobox

        :param vendors: the new list of vendors"""
        self.vendor.clear()
        self.vendor.addItem("")
        self.vendor.addItems([vendor.name for vendor in vendors])

    def on_calculation_type_changed(self):
        """Invoke when calculation type is changed"""
        if self.topNum_radio.isChecked():
            self.top_num_frame.setEnabled(True)
            self.frame_cost.setEnabled(False)
            self.name_combobox.setEnabled(False)
            self.name_label.setEnabled(False)
        if self.costRatio_radio.isChecked():
            self.top_num_frame.setEnabled(False)
            self.frame_cost.setEnabled(True)
            self.name_combobox.setEnabled(True)
            self.name_label.setEnabled(True)
        if self.monthly_radio.isChecked() or self.yearly_radio.isChecked():
            self.top_num_frame.setEnabled(False)
            self.frame_cost.setEnabled(False)
            self.name_combobox.setEnabled(True)
            self.name_label.setEnabled(True)

    def on_report_parameter_changed(self, text):
        """Invoke when report type is changed"""
        self.metric.clear()
        if text in DATABASE_REPORTS:
            self.metric.addItems(DATABASE_REPORTS_METRIC)
            self.name_label.setText('Database')
        if text in ITEM_REPORTS:
            self.metric.addItems(ITEM_REPORTS_METRIC)
            self.name_label.setText('Item')
        if text in PLATFORM_REPORTS:
            self.metric.addItems(PLATFORM_REPORTS_METRIC)
            self.name_label.setText('Platform')
        if text in TITLE_REPORTS:
            self.metric.addItems(TITLE_REPORTS_METRIC)
            self.name_label.setText('Title')
        if self.vendor.currentText():
            self.fill_names()

    def on_vendor_changed(self):
        """Invoke when vendor is changed"""
        self.vendor_parameter = self.vendor.currentText()
        if self.report_parameter.currentText():
            self.fill_names()

    def fill_names(self, only_get_costs_names: bool = False):
        """Fill name field combobox"""
        self.name_combobox.clear()

        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            if not only_get_costs_names:
                names_sql_text, names_data = ManageDB.get_names_sql_text(self.report_parameter.currentText(), self.vendor_parameter)
                names_results = ManageDB.run_select_sql(connection, names_sql_text, names_data)
                if names_results:
                    self.names = [result[0] for result in names_results]
                else:
                    self.names = []
                # if self.settings.show_debug_messages: print(names_results)

            costs_sql_text, costs_data = ManageDB.get_names_with_costs_sql_text(self.report_parameter.currentText(),
                                                                                self.vendor_parameter,
                                                                                int(self.start_year_parameter.text()),
                                                                                int(self.end_year_parameter.text()))
            costs_results = ManageDB.run_select_sql(connection, costs_sql_text, costs_data)
            if costs_results:
                self.costs_names = [result[0] for result in costs_results]
            else:
                self.costs_names = []
            # if self.settings.show_debug_messages: print(costs_results)

            connection.close()
            model = QStandardItemModel()
            for name in self.names:
                item = QStandardItem(name)
                if name in self.costs_names:
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                model.appendRow(item)
            self.name_combobox.setModel(model)
        else:
            print('Error, no connection')

    # submit search result to database and open results
    def createChart(self):
        """Invoke when user click on create chart"""

        # get report type
        report = self.report_parameter.currentText()
        # get start year
        start_year = self.start_year_parameter.text()
        # get end year
        end_year = self.end_year_parameter.text()
        # get name
        name = self.name_combobox.currentText()
        # get metric
        metric = self.metric.currentText()
        # get vendor
        vendor = self.vendor.currentText()
        self.top_num = -1

        self.temp_results = []
        message = ""
        message1 = ""
        message2 = ""
        message3 = ""
        message4 = ""
        if name == "" and self.topNum_radio.isChecked() == False:
            message4 = "- Enter/Choose " + self.name_label.text() + "\n"
        if vendor == "" and self.topNum_radio.isChecked() == False:
            message1 = "- Choose a Vendor \n"
        if start_year > end_year or (int(start_year) > datetime.datetime.now().year or int(end_year) > datetime.datetime.now().year) :
            currentYear = datetime.datetime.now().year
            message3 = "- Start Year must be less than End Year and they cannot be greater than " + str(
                currentYear) + "\n"
        message = message1 + message4 + message3
        if message != "":
            message = "To Create Chart check the following: \n" + message
            GeneralUtils.show_message(message)

        if self.monthly_radio.isChecked() and message == "":
            # sql query to get search results
            sql_text, data = ManageDB.monthly_chart_search_sql_text(report, start_year, end_year, name, metric, vendor)
            # print(sql_text)  # testing
            headers = tuple([field['name'] for field in ManageDB.get_monthly_chart_report_fields_list(report)])
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                self.results = ManageDB.run_select_sql(connection, sql_text, data)
                # print(self.results)

                self.results.insert(0, headers)
                # print(self.results)
                connection.close()
            else:
                print('Error, no connection')
            if len(self.results) > 1 and self.monthly_radio.isChecked():
                self.process_default_data()
                self.open_file_folder()
            if name != "" and start_year <= end_year and len(self.results) <= 1:
                message4 = name + " of " + metric + " NOT FOUND in " + report + " for the chosen year range!"
                GeneralUtils.show_message(message4)

        if self.yearly_radio.isChecked() and message == "":
            # sql query to get search results
            sql_text, data = ManageDB.yearly_chart_search_sql_text(report, start_year, end_year, name, metric, vendor)
            # print(sql_text)  # testing
            headers = tuple([field['name'] for field in ManageDB.get_yearly_chart_report_fields_list(report)])
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                self.results = ManageDB.run_select_sql(connection, sql_text, data)
                # print(self.results)

                self.results.insert(0, headers)
                # print(self.results)
                connection.close()
            else:
                print('Error, no connection')
            if len(self.results) > 1 and self.yearly_radio.isChecked():
                self.process_yearly_data()
                self.open_file_folder()
            if name != "" and start_year <= end_year and len(self.results) <= 1:
                message4 = name + " of " + metric + " NOT FOUND in " + report + " for the chosen year range!"
                GeneralUtils.show_message(message4)

        if self.costRatio_radio.isChecked() and message == "":
            # sql query to get search results
            sql_text, data = ManageDB.cost_chart_search_sql_text(report, start_year, end_year, name, metric, vendor)
            # print(sql_text)  # testing
            headers = tuple([field['name'] for field in ManageDB.get_cost_chart_report_fields_list(report)])
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                self.results = ManageDB.run_select_sql(connection, sql_text, data)
                # print(self.results)

                if not self.results:
                    self.results = []
                self.results.insert(0, headers)
                # print(self.results)
                connection.close()
            else:
                print('Error, no connection')

            if len(self.results) > 1 and self.costRatio_radio.isChecked():
                self.process_cost_ratio_data()
                self.open_file_folder()
            if name != "" and start_year <= end_year and len(self.results) <= 1:
                message4 = name + " of " + metric + " NOT FOUND in " + report + " for the chosen year range!"
                GeneralUtils.show_message(message4)

        if self.topNum_radio.isChecked() and message == "":
            self.top_num = int(self.top_num_edit.text())
            if self.top_num == 0:
                self.top_num = None
            if self.vendor.currentText() == "":
                vendor = None
            sql_text, data = ManageDB.top_number_chart_search_sql_text(report, start_year, end_year, metric, vendor,
                                                                       self.top_num)
            headers = tuple([field['name'] for field in ManageDB.get_top_number_chart_report_fields_list(report)])
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                self.results = ManageDB.run_select_sql(connection, sql_text, data)

                self.results.insert(0, headers)
                connection.close()
            else:
                print('Error, no connection')
            if len(self.results) > 1:
                self.process_top_X_data()
                self.open_file_folder()
            elif start_year <= end_year:
                message5 = self.name_label.text() + " of " + metric + " Not Found in " + report + " for the chosen year range!"
                GeneralUtils.show_message(message5)

    def open_file_folder(self):
        """Invoke to open file or folder"""
        if self.open_folder.isChecked():
            open_file_or_dir(os.path.dirname(self.file_name))
        if self.open_file.isChecked():
            open_file_or_dir(self.file_name)
        if not self.open_file.isChecked():
            show_message('Results saved to ' + self.file_name)

    # process_data distributes the usage data for monthly in an array accordingly
    def process_default_data(self):
        """Invoked when calculation type: monthly is selected"""
        m = len(self.results)
        self.legendEntry = []  # legend entry data
        for i in range(1, m):
            self.legendEntry.append(self.results[i][3])

        # data is an array with the sorted usage figures
        self.data = []
        for i in range(0, m):
            data1 = []
            n = len(self.results[i])
            for j in range(4, n):  # from jan to dec only
                data1.append(self.results[i][j])
            self.data.append(data1)
        # testing to make sure its working good
        # print(self.data[0])  # this is the first column in the excel file/vertical axis data in the chart
        # print(self.data[1])
        # print(len(self.data))
        self.chart_type()

    def process_yearly_data(self):
        """Invoked when calculation type: yearly is selected"""
        m = len(self.results)
        self.legendEntry = []  # legend entry data
        self.legendEntry.append(self.metric.currentText())

        # data is an array with the sorted usage figures
        self.data = []
        data1 = [] # year
        data2 = [] # reporting_period_total
        for i in range(1, m):
            data1.append(self.results[i][3])
        self.data.append(data1)
        for i in range(1, m):
            data2.append(self.results[i][4])
        self.data.append(data2)

        # testing to make sure its working good
        # print(self.data[0])  # this is the first column in the excel file/vertical axis data in the chart
        # print(self.data[1])
        # print(len(self.data))
        self.chart_type()

    def process_cost_ratio_data(self):
        """Invoked when calculation type: cost ratio is selected"""
        m = len(self.results) #length of self.results
        self.legendEntry = []  # legend entry data contains column names

        # data is an array of array with year, cost per metric, total and cost in separate arrays
        self.data = []

        data1 = []  # year
        data2 = []  # cost per metric
        data3 = []  # reporting_period_total
        data4 = []  # cost

        # retrieve year and add it to array
        for i in range(1, m):
            data1.append(self.results[i][3])
        self.data.append(data1)

        # retrieve cost and total and finding cost per metric and adding it to array
        if self.cost_parameter.currentText() == 'Cost in Local Currency with Tax':
            self.legendEntry.append('Cost in Local Currency with Tax Per Metric')
            self.legendEntry.append('Cost in Local Currency with Tax')
            for i in range(1, m):
                cost = self.results[i][7]
                if self.results[i][7] is None:
                    cost = 0
                data4.append(cost)
                data2.append(cost / self.results[i][8])
            self.data.append(data2)
            self.data.append(data4)
        if self.cost_parameter.currentText() == 'Cost in Local Currency':
            self.legendEntry.append('Cost in Local Currency Per Metric')
            self.legendEntry.append('Cost in Local Currency')
            for i in range(1, m):
                cost = self.results[i][6]
                if self.results[i][6] is None:
                    cost = 0
                data4.append(cost)
                data2.append(cost / self.results[i][8])
            self.data.append(data2)
            self.data.append(data4)
        if self.cost_parameter.currentText() == 'Cost in Original Currency':
            self.legendEntry.append('Cost in Original Currency Per Metric')
            self.legendEntry.append('Cost in Original Currency')
            for i in range(1, m):
                cost = self.results[i][4]
                if self.results[i][4] is None:
                    cost = 0
                data4.append(cost)
                data2.append(cost / self.results[i][8])
            self.data.append(data2)
            self.data.append(data4)

        # retrieve reporting_period_total and add it to array
        for i in range(1, m):
            data3.append(self.results[i][8])
        self.data.append(data3)

        # add column header to legend entry
        self.legendEntry.append(self.metric.currentText())

        # testing to see data in array of array
        # print(self.data[0])  # first column in excel (year)
        # print(self.data[1]) # second column (cost per metric)
        # print(self.data[2]) # third column (cost)
        # print(self.data[4]) # fourth column (total)
        # print(len(self.data)) #testing
        self.chart_type()

    def process_top_X_data(self):
        """Invoked when calculation type: top # is selected"""
        m = len(self.results)
        # print(self.results)
        # print(m)
        self.temp_results = []

        self.legendEntry = []  # legend entry data
        self.legendEntry.append(self.results[0][3])
        self.legendEntry.append(self.results[0][4])
        for i in range(1, m):
            self.temp_results.append(self.results[i])
        self.temp_results = sorted(self.temp_results, key=itemgetter(4))
        # print(len(self.temp_results))
        # print(self.temp_results)
        n = len(self.temp_results)

        # data is an array with the sorted usage figures
        self.data = []
        data1 = [] # name(database, title,...)
        data2 = [] # reporting total
        data3 = [] # rankings
        data4 = [] # optional vendor column

        # get all name(database,title,...)
        data = self.temp_results[0][0]
        data1.append(data)
        for i in range(1, n):  # get database
            data = self.temp_results[i][0]
            data1.append(data)
        self.data.append(data1)
        # print(data1)

        # get all reporting total
        metri = self.temp_results[0][3]
        data2.append(metri)
        for i in range(1, n):  # get reporting total
            metri = self.temp_results[i][3]
            data2.append(metri)
        self.data.append(data2)
        # print(data2)

        # get all ranking
        rank = self.temp_results[0][4]
        data3.append(rank)
        for i in range(1, n):
            rank = self.temp_results[i][4]
            data3.append(rank)
        self.data.append(data3)

        # will add vendor column to chart if the user do not enter anything in vendor
        if self.vendor.currentText() == "":
            self.legendEntry.append(self.results[0][2])
            for i in range(0, n):
                rank = self.temp_results[i][2]
                data4.append(rank)
            self.data.append(data4)

        self.chart_type()

    # get chart type checked
    def chart_type(self):
        """Invoked to determine which chart type is selected by user"""
        if self.h_bar_radio.isChecked():
            self.horizontal_bar_chart()

        if self.v_bar_radio.isChecked():
            self.vertical_bar_chart()

        if self.line_radio.isChecked():
            self.line_chart()

    # get file name and titles from user
    def customizeChart(self):
        """Invoked to get information from user to customize chart.

        It is highly recommended that user write the details like year, report type, calculation type,.. in chart title"""
        chart_title = self.chart_title_edit.text()
        horizontal_axis_title = self.horizontal_axis_edit.text()
        vertical_axis_title = self.vertical_axis_edit.text()
        return chart_title, horizontal_axis_title, vertical_axis_title

    # add titles to chart and styles
    @staticmethod
    def add_Customize(chart1, chart_title, horizontal_axis_title, vertical_axis_title):
        """Invoked to add information to customize the chart

        :param chart1: the chart to add details to
        :param chart_title: the chart title
        :param horizontal_axis_title: the horizontal axis title
        :param vertical_axis_title: the vertical axis title"""

        # Add a chart title and some axis labels.
        chart1.set_title({'name': chart_title})
        chart1.set_x_axis({'name': horizontal_axis_title})
        chart1.set_y_axis({'name': vertical_axis_title})
        # Set an Excel chart style.
        chart1.set_style(11)

    # create file with ext and add sheet to file
    def createFile(self):
        """Invoked to create xlsx file"""

        self.file_name = choose_save(EXCEL_FILTER)
        if self.file_name != '':
            if not self.file_name.lower().endswith('.xlsx'):
                self.file_name += '.xlsx'

        workbook = xlsxwriter.Workbook(self.file_name)
        # add sheet to xlsx file
        worksheet = workbook.add_worksheet()
        return workbook, worksheet

    # Add the worksheet data that the charts will refer to.
    def populateData(self, vertical_axis_title, worksheet, workbook):
        """Invoked to create xlsx file

        :param vertical_axis_title: the vertical axis title
        :param worksheet: the worksheet in the xlsx file
        :param workbook: the workbook"""

        bold = workbook.add_format({'bold': 1})
        #headings = [vertical_axis_title]
        headings = [""]
        for i in range(0, len(self.legendEntry)):
            headings.append(self.legendEntry[i])
        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', self.data[0])
        n = ord('A') + 1
        if self.costRatio_radio.isChecked() == False:
            for i in range(1, len(self.data)):
                worksheet.write_column(chr(n) + '2', self.data[i])
                n = n + 1
        if self.costRatio_radio.isChecked() == True:
            # Add a number format for cells with money.
            currency = self.process_currency()
            money = workbook.add_format({'num_format': currency})
            for i in range(1, len(self.data)-1):
                worksheet.write_column(chr(n) + '2', self.data[i], money)
                n = n + 1
            worksheet.write_column(chr(n) + '2', self.data[len(self.data)-1])

    # process currency
    def process_currency(self):
        """Invoke to determine between local or original currency for cost"""
        if self.cost_parameter.currentText() == 'Cost in Local Currency with Tax' or self.cost_parameter.currentText() == 'Cost in Local Currency':
            local_currency = self.settings.default_currency
            currency = self.get_currency_code(local_currency)
        if self.cost_parameter.currentText() == 'Cost in Original Currency':
            original_currency = self.results[1][5]
            currency = self.get_currency_code(original_currency)
        return currency

    # return currency code for excel
    def get_currency_code(self, local_currency):
        """Invoke to find currency being used"""
        if local_currency == 'CAD':
            currency = '[$CAD] #,###.#########################_)'
        if local_currency == 'USD':
            currency = '[$USD] #,###.#########################_)'
        if local_currency == 'EUR':
            currency = '[$EUR] #,###.#########################_)'
        if local_currency == 'JPY':
            currency = '[$JPY] #,###.#########################_)'
        if local_currency == 'GBP':
            currency = '[$GBP] #,###.#########################_)'
        if local_currency == 'CHF':
            currency = '[$CHF] #,###.#########################_)'
        if local_currency == 'AUD':
            currency = '[$AUD] #,###.#########################_)'
        return currency
    # create chart and add series to it
    def configureSeries(self, workbook, chart_type):
        """Invoked to create xlsx file

        :param workbook: the workbook
        :param chart_type: the chart type"""

        chart1 = workbook.add_chart({'type': chart_type})
        n = len(self.data[0])
        # Configure the first series.
        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$'+str(n+1),
            'values': '=Sheet1!$B$2:$B$'+str(n+1),
        })

        # Configure any subsequent series. Note use of alternative syntax to define ranges.
        # no more series will be added if top # and cost ratio are not selected
        if self.top_num == -1 and self.costRatio_radio.isChecked() == False:
            m = 2
            for i in range(2, len(self.data)):
                chart1.add_series({
                    'name': ['Sheet1', 0, m],
                    'categories': ['Sheet1', 1, 0, n, 0],
                    'values': ['Sheet1', 1, m, n, m],
                })
                m = m + 1
        return chart1

    def horizontal_bar_chart(self):
        """Invoked to create a horizontal bar chart"""

        # get titles from customizeChart
        chart_title, horizontal_axis_title, vertical_axis_title = self.customizeChart()

        # create xlsx file and add sheet file
        workbook, worksheet = self.createFile()

        # add data to worksheet
        self.populateData(vertical_axis_title, worksheet, workbook)

        # create horizontal bar chart and add series to it
        chart1 = self.configureSeries(workbook, 'bar')

        # Add a chart title and some axis labels.
        self.add_Customize(chart1, chart_title, horizontal_axis_title, vertical_axis_title)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('F2', chart1, {'x_scale': 2, 'y_scale': 2})
        workbook.close()

        # Completion message
        message_completion = "Done!"
        GeneralUtils.show_message(message_completion)

    def vertical_bar_chart(self):
        """Invoked to create a vertical bar chart"""

        # get titles from customizeChart
        chart_title, horizontal_axis_title, vertical_axis_title = self.customizeChart()

        # create xlsx file and add sheet file
        workbook, worksheet = self.createFile()

        # add data to worksheet
        self.populateData(vertical_axis_title, worksheet, workbook)

        # create horizontal bar chart and add series to it
        chart1 = self.configureSeries(workbook, 'column')

        # Add a chart title and some axis labels.
        self.add_Customize(chart1, chart_title, horizontal_axis_title, vertical_axis_title)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('F2', chart1, {'x_scale': 2, 'y_scale': 2})
        workbook.close()

        # Completion message
        message_completion = "Done!"
        GeneralUtils.show_message(message_completion)

    def line_chart(self):
        """Invoked to create a line chart"""

        # get titles from customizeChart
        chart_title, horizontal_axis_title, vertical_axis_title = self.customizeChart()

        # create xlsx file and add sheet file
        workbook, worksheet = self.createFile()

        # Add data to worksheet
        self.populateData(vertical_axis_title, worksheet, workbook)

        # create horizontal bar chart and add series to it
        chart1 = self.configureSeries(workbook, 'line')

        # Add a chart title and some axis labels.
        self.add_Customize(chart1, chart_title, horizontal_axis_title, vertical_axis_title)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('F2', chart1, {'x_scale': 2, 'y_scale': 2})
        workbook.close()

        # Completion message
        message_completion = "Done!"
        GeneralUtils.show_message(message_completion)
