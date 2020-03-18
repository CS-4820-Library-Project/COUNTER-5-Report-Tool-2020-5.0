import xlsxwriter
from datetime import date
import csv
import os
import shlex

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QDialog
import ManageDB
from ui import MainWindow, MessageDialog, VisualTab


class VisualController:
    def __init__(self, visual_ui: VisualTab.Ui_visual_tab):
        # set up report types combobox
        self.report_parameter = visual_ui.search_report_parameter_combobox_2
        self.report_parameter.addItems(ManageDB.DATABASE_REPORTS)
        self.report_parameter.addItems(ManageDB.ITEM_REPORTS)
        self.report_parameter.addItems(ManageDB.PLATFORM_REPORTS)
        self.report_parameter.addItems(ManageDB.TITLE_REPORTS)

        # set up radio buttons
        self.h_bar_radio = visual_ui.radioButton
        self.v_bar_radio = visual_ui.radioButton_3
        self.line_radio = visual_ui.radioButton_4

        # set up start year dateedit
        self.start_year_parameter = visual_ui.search_start_year_parameter_dateedit_2
        self.start_year_parameter.setDate(date.today())

        # set up end year dateedit
        self.end_year_parameter = visual_ui.search_end_year_parameter_dateedit_2
        self.end_year_parameter.setDate(date.today())

        self.name = visual_ui.name_lineEdit
        self.metric = visual_ui.metric_type_lineEdit

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

    def createChart(self):  # submit search result to database and open results
        # get report type
        report = self.report_parameter.currentText()
        # get start year
        start_year = self.start_year_parameter.text()
        # get end year
        end_year = self.end_year_parameter.text()
        # get name
        name = self.name.text()
        metric = self.metric.text()

        # sql query to get search results
        sql_text = ManageDB.chart_search_sql_text(report, start_year, end_year, name, metric)
        print(sql_text)  # testing

        headers = []
        for field in ManageDB.get_chart_report_fields_list(report):
            headers.append(field['name'])
        connection = ManageDB.create_connection(ManageDB.DATABASE_LOCATION)
        if connection is not None:
            self.results = ManageDB.run_select_sql(connection, sql_text)
            print(self.results)

            self.results.insert(0, headers)
            print(self.results)
            connection.close()
        else:
            print('Error, no connection')
        self.process_data()

    # process_data distributes the usage data in an array accordingly
    def process_data(self):
        m = len(self.results)
        print(m)
        if m == 1:
            message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
            message_dialog_ui = MessageDialog.Ui_message_dialog()
            message_dialog_ui.setupUi(message_dialog)

            message_label = message_dialog_ui.message_label
            message_label.setText("PLEASE ENTER A VALID INPUT")

            message_dialog.exec_()
        self.data = []
        for i in range(0, m):
            data1 = []
            print(self.results[i])
            n = len(self.results[i])
            for j in range(5, n):
                data1.append(self.results[i][j])
            self.data.append(data1)
        # testing to make sure its working good
        print(self.data[0])
        print(self.data[1])
        # print(self.data[2])
        print(len(self.data))
        self.chart_type()

    def chart_type(self):
        if self.h_bar_radio.isChecked():
            self.horizontal_bar_chart()

        if self.v_bar_radio.isChecked():
            self.vertical_bar_chart()

        if self.line_radio.isChecked():
            self.line_chart()

    def horizontal_bar_chart(self):

        # get file name and titles from user
        file_name = self.file_name_edit.text()
        chart_title = self.chart_title_edit.text()
        horizontal_axis_title = self.horizontal_axis_edit.text()
        vertical_axis_title = self.vertical_axis_edit.text()

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0] + "/"
        self.workbook = xlsxwriter.Workbook(directory + file_name + '_hbar.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        bold = self.workbook.add_format({'bold': 1})
        # Add the worksheet data that the charts will refer to.
        headings = [vertical_axis_title, 'Total 1', 'Total 2']
        self.worksheet.write_row('A1', headings, bold)
        self.worksheet.write_column('A2', self.data[0])
        # self.worksheet.write_column('B2', self.data[1])
        n = ord('A') + 1
        for i in range(1, len(self.data)):
            self.worksheet.write_column(chr(n) + '2', self.data[i])
            n = n + 1

        # Create a new bar chart.
        chart1 = self.workbook.add_chart({'type': 'bar'})

        # Configure the first series.
        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$13',
            'values': '=Sheet1!$B$2:$B$13',
        })

        # Configure a second series. Note use of alternative syntax to define ranges.
        for i in range(2, len(self.data)):
            chart1.add_series({
                'name': ['Sheet1', 0, 2],
                'categories': ['Sheet1', 1, 0, 6, 0],
                'values': ['Sheet1', 1, 2, 6, 2],
            })

        # Add a chart title and some axis labels.
        chart1.set_title({'name': chart_title})
        chart1.set_x_axis({'name': horizontal_axis_title})
        chart1.set_y_axis({'name': vertical_axis_title})

        # Set an Excel chart style.
        chart1.set_style(11)

        # Insert the chart into the worksheet (with an offset).
        self.worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})
        self.workbook.close()

    def vertical_bar_chart(self):
        # get file name and titles from user
        file_name = self.file_name_edit.text()
        chart_title = self.chart_title_edit.text()
        horizontal_axis_title = self.horizontal_axis_edit.text()
        vertical_axis_title = self.vertical_axis_edit.text()

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0] + "/"
        self.workbook = xlsxwriter.Workbook(directory + file_name + '_vbar.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        bold = self.workbook.add_format({'bold': 1})
        # Add the worksheet data that the charts will refer to.
        headings = [vertical_axis_title, 'Total 1', 'Total 2']
        self.worksheet.write_row('A1', headings, bold)
        self.worksheet.write_column('A2', self.data[0])
        n = ord('A') + 1
        for i in range(1, len(self.data)):
            self.worksheet.write_column(chr(n) + '2', self.data[i])
            n = n + 1

        # Create a new bar chart.
        chart1 = self.workbook.add_chart({'type': 'column'})

        # Configure the first series.
        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$13',
            'values': '=Sheet1!$B$2:$B$13',
        })

        # Configure a second series. Note use of alternative syntax to define ranges.
        for i in range(2, len(self.data)):
            chart1.add_series({
                'name': ['Sheet1', 0, 2],
                'categories': ['Sheet1', 1, 0, 6, 0],
                'values': ['Sheet1', 1, 2, 6, 2],
            })

        # Add a chart title and some axis labels.
        chart1.set_title({'name': chart_title})
        chart1.set_x_axis({'name': horizontal_axis_title})
        chart1.set_y_axis({'name': vertical_axis_title})

        # Set an Excel chart style.
        chart1.set_style(11)

        # Insert the chart into the worksheet (with an offset).
        self.worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})
        self.workbook.close()

    def line_chart(self):

        # get file name and titles from user
        file_name = self.file_name_edit.text()
        chart_title = self.chart_title_edit.text()
        horizontal_axis_title = self.horizontal_axis_edit.text()
        vertical_axis_title = self.vertical_axis_edit.text()

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0] + "/"
        self.workbook = xlsxwriter.Workbook(directory + file_name + '_line.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        bold = self.workbook.add_format({'bold': 1})
        # Add the worksheet data that the charts will refer to.
        headings = [vertical_axis_title, 'Total 1', 'Total 2']
        self.worksheet.write_row('A1', headings, bold)
        self.worksheet.write_column('A2', self.data[0])
        n = ord('A') + 1
        for i in range(1, len(self.data)):
            self.worksheet.write_column(chr(n) + '2', self.data[i])
            n = n + 1

        # Create a new bar chart.
        chart1 = self.workbook.add_chart({'type': 'line'})

        # Configure the first series.
        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$13',
            'values': '=Sheet1!$B$2:$B$13',
        })

        # Configure a second series. Note use of alternative syntax to define ranges.
        for i in range(2, len(self.data)):
            chart1.add_series({
                'name': ['Sheet1', 0, 2],
                'categories': ['Sheet1', 1, 0, 6, 0],
                'values': ['Sheet1', 1, 2, 6, 2],
            })

        # Add a chart title and some axis labels.
        chart1.set_title({'name': chart_title})
        chart1.set_x_axis({'name': horizontal_axis_title})
        chart1.set_y_axis({'name': vertical_axis_title})

        # Set an Excel chart style.
        chart1.set_style(11)

        # Insert the chart into the worksheet (with an offset).
        self.worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})
        self.workbook.close()