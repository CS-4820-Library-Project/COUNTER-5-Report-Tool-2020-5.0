import calendar
import datetime
import json

import xlsxwriter
from datetime import date

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QDialog
from jinja2.runtime import to_string

import GeneralUtils
import ManageDB
import ManageVendors
from ui import MessageDialog, VisualTab
from VariableConstants import *


class VisualController:
    def __init__(self, visual_ui: VisualTab.Ui_visual_tab):
        # set up report combobox
        self.report_parameter = visual_ui.search_report_parameter_combobox_2
        self.calculation_parameter = visual_ui.calculation_type_combobox
        self.calculation_parameter.addItems(CALCULATION_TYPE_ALL)
        self.cost_parameter = visual_ui.cost_ratio_option_combobox
        self.cost_parameter.addItems(COST_TYPE_ALL)
        self.report_parameter.addItems(ALL_REPORTS)
        # self.report_parameter.activated[str].connect(self.on_report_type_combo_activated)
        self.report_parameter.currentTextChanged[str].connect(self.on_report_parameter_changed)

        #frame
        self.frame_cost = visual_ui.edit_cost_ratio_frame
        self.frame_cost.setEnabled(False)
        if self.calculation_parameter.currentText() == 'Cost Ratio':
            self.frame_cost.setEnabled(True)
        # set up chart type radio buttons
        self.h_bar_radio = visual_ui.radioButton
        self.v_bar_radio = visual_ui.radioButton_3
        self.v_bar_radio.setChecked(True)
        self.line_radio = visual_ui.radioButton_4

        # set up options radio buttons

        # set up start year dateedit
        self.start_year_parameter = visual_ui.search_start_year_parameter_dateedit_2
        self.start_year_parameter.setDate(date.today())

        # set up end year dateedit
        self.end_year_parameter = visual_ui.search_end_year_parameter_dateedit_2
        self.end_year_parameter.setDate(date.today())

        self.name_label = visual_ui.visual_name_label
        self.name_combobox = visual_ui.visual_name_parameter_combobox
        self.name = None
        self.metric = visual_ui.metric_Type_comboBox
        self.metric.addItems(DATABASE_REPORTS_METRIC)

        self.vendor = visual_ui.visual_vendor_parameter_combobox
        self.vendor.currentTextChanged.connect(self.on_vendor_changed)
        self.vendor_parameter = None
        vendors_json_string = GeneralUtils.read_json_file(ManageVendors.VENDORS_FILE_PATH)
        vendor_dicts = json.loads(vendors_json_string)
        self.vendor.clear()
        self.vendor.addItems([vendor_dict['name'] for vendor_dict in vendor_dicts])

        # set up the search clauses
        self.and_clause_parameters = None

        # set up create chart button
        self.create_chart_button = visual_ui.create_chart_button
        self.create_chart_button.clicked.connect(self.createChart)

        # set up customize chart field
        self.chart_title_edit = visual_ui.chart_title_lineEdit
        self.file_name_edit = visual_ui.file_name_lineEdit
        self.horizontal_axis_edit = visual_ui.horizontal_axis_lineEdit
        self.vertical_axis_edit = visual_ui.vertical_axis_lineEdit

        self.data = []
        self.top_num = None
        self.results = None

    def load_vendor_list(self, vendors: list):
        self.vendor.clear()
        self.vendor.addItems([vendor.name for vendor in vendors])

    # def on_report_type_combo_activated(self, text):
    #     self.metric.clear()
    #     if text in DATABASE_REPORTS:
    #         self.metric.addItems(DATABASE_REPORTS_METRIC)
    #         self.name_label.setText('Database')
    #     if text in ITEM_REPORTS:
    #         self.metric.addItems(ITEM_REPORTS_METRIC)
    #         self.name_label.setText('Item')
    #     if text in PLATFORM_REPORTS:
    #         self.metric.addItems(PLATFORM_REPORTS_METRIC)
    #         self.name_label.setText('Platform')
    #     if text in TITLE_REPORTS:
    #         self.metric.addItems(TITLE_REPORTS_METRIC)
    #         self.name_label.setText('Title')

    def on_report_parameter_changed(self, text):
        # self.report_parameter = self.report_parameter.currentText()
        # self.name_label.setText(NAME_FIELD_SWITCHER[self.report_parameter.currentText].capitalize())
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
        self.vendor_parameter = self.vendor.currentText()
        if self.report_parameter.currentText():
            self.fill_names()

    def fill_names(self):
        self.name_combobox.clear()
        results = []
        sql_text, data = ManageDB.get_names_sql_text(self.report_parameter.currentText(), self.vendor.currentText())
        print(sql_text)
        connection = ManageDB.create_connection(DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text, data)
            print(results)
            connection.close()
            self.name_combobox.addItems([result[0] for result in results])
        else:
            print('Error, no connection')

    def createChart(self):  # submit search result to database and open results

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
        self.top_num = 0
        print(self.calculation_parameter.currentText())

        message = ""
        message1 = ""
        message2 = ""
        message3 = ""
        if name == "":
            message1 = "Enter/Select " + self.name_label.text() + "\n"
        if start_year > end_year:
            currentYear = datetime.datetime.now().year
            message3 = " Start Year must be less than End Year - AND - Years cannot be greater than " + to_string(currentYear) + "\n"
        message = message1 + message3
        if message != "":
            message = "To Create Chart Check the following: \n" + message
            self.messageDialog(message)

        if self.calculation_parameter.currentText() == 'Monthly':
            # sql query to get search results
            sql_text, data = ManageDB.chart_search_sql_text(report, start_year, end_year, name, metric)
            print(sql_text)  # testing
            headers = tuple([field['name'] for field in ManageDB.get_chart_report_fields_list(report)])
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                self.results = ManageDB.run_select_sql(connection, sql_text, data)
                print(self.results)

                self.results.insert(0, headers)
                print(self.results)
                connection.close()
            else:
                print('Error, no connection')
            if len(self.results) > 1:
                self.process_default_data()
            elif name != "" and start_year <= end_year:
                message4 = name + " of " + metric + " NOT FOUND in " + report + " for the chosen year range!"
                self.messageDialog(message4)

        if self.calculation_parameter.currentText() == 'Top 5':
            self.top_num = 5
        if self.calculation_parameter.currentText() == 'Top 10':
            self.top_num = 10
        if self.calculation_parameter.currentText() == 'Top 15':
            self.top_num = 15

        if self.top_num == 5 or self.top_num == 10 or self.top_num == 15:
            print(self.top_num) #testing
            sql_text, data = ManageDB.chart_top_number_search_sql_text(report, start_year, end_year, name, metric,
                                                                       self.top_num)
            headers = tuple([field['name'] for field in ManageDB.get_top_number_chart_report_fields_list(report)])
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                self.results = ManageDB.run_select_sql(connection, sql_text, data)
                print(self.results)

                self.results.insert(0, headers)
                print(self.results)
                connection.close()
            else:
                print('Error, no connection')
            if len(self.results) > 1:
                self.process_top_X_data()
            elif name != "" and (self.h_bar_radio.isChecked() != False or self.v_bar_radio.isChecked() != False or self.line_radio.isChecked() != False) and start_year <= end_year:
                message5 = name + " of " + metric + " NOT FOUND in " + report + " for the chosen year range!"
                self.messageDialog(message5)

    def messageDialog(self, text):
        message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        message_dialog_ui = MessageDialog.Ui_message_dialog()
        message_dialog_ui.setupUi(message_dialog)

        message_label = message_dialog_ui.message_label
        message_label.setText(text)

        message_dialog.exec_()

    # process_data distributes the usage data in an array accordingly
    def process_default_data(self):
        m = len(self.results)
        print(m)
        # # if m == 1:
        # #     message = "DATA NOT FOUND"
        #     self.messageDialog(message)
        # message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        # message_dialog_ui = MessageDialog.Ui_message_dialog()
        # message_dialog_ui.setupUi(message_dialog)
        #
        # message_label = message_dialog_ui.message_label
        # message_label.setText("PLEASE ENTER A VALID INPUT")
        #
        # message_dialog.exec_()

        self.legendEntry = []  # legend entry data
        for i in range(1, m):
            print(self.results[i][3])
            self.legendEntry.append(self.results[i][3])

        # data is an array with the sorted usage figures
        self.data = []
        for i in range(0, m):
            data1 = []
            print(self.results[i])
            n = len(self.results[i])
            for j in range(4, n):
                data1.append(self.results[i][j])
            self.data.append(data1)
        # testing to make sure its working good
        print(self.data[0])  # this is the first column in the excel file/vertical axis data in the chart
        print(self.data[1])
        # print(self.data[2])
        print(len(self.data))
        self.chart_type()

    def process_top_X_data(self):
        m = len(self.results)

        self.legendEntry = []  # legend entry data
        self.legendEntry.append(self.results[0][5])
        self.legendEntry.append(self.results[0][7])

        # data is an array with the sorted usage figures
        self.data = []
        data1 = []
        data2 = []
        data3 = []
        for i in range(1, m):
            a = to_string(calendar.month_name[self.results[i][4]])
            b = to_string(self.results[i][3])
            data = a + '-' + b
            print(data)
            # data = self.results[i][4]
            data1.append(data)
        self.data.append(data1)
        for i in range(1, m):
            print(self.results[i])
            metri = self.results[i][5]
            data2.append(metri)
        self.data.append(data2)
        for i in range(1, m):
            print(self.results[i])
            rank = self.results[i][7]
            data3.append(rank)
        self.data.append(data3)
        # testing to make sure its working good
        print(self.data[0])  # this is the first column in the excel file/vertical axis data in the chart
        print(self.data[1])
        print(self.data[2])
        print(len(self.data))
        print(len(self.data[0]))
        self.chart_type()

    def chart_type(self):
        if self.h_bar_radio.isChecked():
            self.horizontal_bar_chart()

        if self.v_bar_radio.isChecked():
            self.vertical_bar_chart()

        if self.line_radio.isChecked():
            self.line_chart()

    # get file name and titles from user
    def customizeChart(self):
        file_name = self.file_name_edit.text()
        chart_title = self.chart_title_edit.text()
        horizontal_axis_title = self.horizontal_axis_edit.text()
        vertical_axis_title = self.vertical_axis_edit.text()
        return file_name, chart_title, horizontal_axis_title, vertical_axis_title

    # get directory to save file from user
    @staticmethod
    def chooseDirectory():
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0] + "/"
            return directory

    # add titles to chart and styles
    @staticmethod
    def add_Customize(chart1, chart_title, horizontal_axis_title, vertical_axis_title):
        # Add a chart title and some axis labels.
        chart1.set_title({'name': chart_title})
        chart1.set_x_axis({'name': horizontal_axis_title})
        chart1.set_y_axis({'name': vertical_axis_title})
        # Set an Excel chart style.
        chart1.set_style(11)

    # create file with ext and add sheet to file
    @staticmethod
    def createFile(directory, file_name, ext):
        # create xlsx file
        workbook = xlsxwriter.Workbook(directory + file_name + ext + '.xlsx')
        # add sheet to xlsx file
        worksheet = workbook.add_worksheet()
        return workbook, worksheet

    # Add the worksheet data that the charts will refer to.
    def populateData(self, vertical_axis_title, worksheet, workbook):
        bold = workbook.add_format({'bold': 1})
        headings = [vertical_axis_title]
        for i in range(0, len(self.legendEntry)):
            headings.append(self.legendEntry[i])
        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', self.data[0])
        n = ord('A') + 1
        for i in range(1, len(self.data)):
            worksheet.write_column(chr(n) + '2', self.data[i])
            n = n + 1

    # create chart and add series to it
    def configureSeries(self, workbook, chart_type):
        chart1 = workbook.add_chart({'type': chart_type})

        # Configure the first series.
        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$18',
            'values': '=Sheet1!$B$2:$B$18',
        })

        # Configure a second series. Note use of alternative syntax to define ranges.
        if self.top_num is None:
            m = 2
            for i in range(2, len(self.data)):
                chart1.add_series({
                    'name': ['Sheet1', 0, m],
                    'categories': ['Sheet1', 1, 0, 18, 0],
                    'values': ['Sheet1', 1, m, 18, m],
                })
                m = m + 1
        return chart1

    def horizontal_bar_chart(self):

        # get file name and titles from customizeChart
        file_name, chart_title, horizontal_axis_title, vertical_axis_title = self.customizeChart()

        # get directory to save file
        directory = self.chooseDirectory()

        # create xlsx file and add sheet file
        workbook, worksheet = self.createFile(directory, file_name, '_hbar')

        # add data to worksheet
        self.populateData(vertical_axis_title, worksheet, workbook)

        # create horizontal bar chart and add series to it
        chart1 = self.configureSeries(workbook, 'bar')

        # Add a chart title and some axis labels.
        self.add_Customize(chart1, chart_title, horizontal_axis_title, vertical_axis_title)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})
        workbook.close()

    def vertical_bar_chart(self):

        # get file name and titles from customizeChart
        file_name, chart_title, horizontal_axis_title, vertical_axis_title = self.customizeChart()

        # get directory to save file
        directory = self.chooseDirectory()

        # create xlsx file and add sheet file
        workbook, worksheet = self.createFile(directory, file_name, '_vbar')

        # add data to worksheet
        self.populateData(vertical_axis_title, worksheet, workbook)

        # create horizontal bar chart and add series to it
        chart1 = self.configureSeries(workbook, 'column')

        # Add a chart title and some axis labels.
        self.add_Customize(chart1, chart_title, horizontal_axis_title, vertical_axis_title)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})
        workbook.close()

    def line_chart(self):

        # get file name and titles from customizeChart
        file_name, chart_title, horizontal_axis_title, vertical_axis_title = self.customizeChart()

        # get directory to save file
        directory = self.chooseDirectory()

        # create xlsx file and add sheet file
        workbook, worksheet = self.createFile(directory, file_name, '_line')

        # Add data to worksheet
        self.populateData(vertical_axis_title, worksheet, workbook)

        # create horizontal bar chart and add series to it
        chart1 = self.configureSeries(workbook, 'line')

        # Add a chart title and some axis labels.
        self.add_Customize(chart1, chart_title, horizontal_axis_title, vertical_axis_title)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})
        workbook.close()
