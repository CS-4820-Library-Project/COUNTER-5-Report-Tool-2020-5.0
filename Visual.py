import xlsxwriter
from datetime import date
import csv
import os
import shlex
from PyQt5.QtWidgets import QFileDialog
import ManageDB
from ui import MainWindow


class VisualController:
    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        # set up report types combobox
        self.report_parameter = main_window_ui.search_report_parameter_combobox_2
        self.report_parameter.addItems(ManageDB.DATABASE_REPORTS)
        self.report_parameter.addItems(ManageDB.ITEM_REPORTS)
        self.report_parameter.addItems(ManageDB.PLATFORM_REPORTS)
        self.report_parameter.addItems(ManageDB.TITLE_REPORTS)

        # set up radio buttons
        self.h_bar_radio = main_window_ui.radioButton
        self.v_bar_radio = main_window_ui.radioButton_3
        self.line_radio = main_window_ui.radioButton_4

        # set up start year dateedit
        self.start_year_parameter = main_window_ui.search_start_year_parameter_dateedit_2
        self.start_year_parameter.setDate(date.today())

        # set up end year dateedit
        self.end_year_parameter = main_window_ui.search_end_year_parameter_dateedit_2
        self.end_year_parameter.setDate(date.today())

        self.name = main_window_ui.name_lineEdit
        self.metric = main_window_ui.metric_type_lineEdit

        # set up the search clauses
        self.and_clause_parameters = None

        # set up create chart button
        self.create_chart_button = main_window_ui.create_chart_button
        self.create_chart_button.clicked.connect(self.createChart)

        # set up customize chart field
        self.chart_title_edit = main_window_ui.chart_title_lineEdit
        self.file_name_edit = main_window_ui.file_name_lineEdit
        self.horizontal_axis_edit = main_window_ui.horizontal_axis_lineEdit
        self.vertical_axis_edit = main_window_ui.vertical_axis_lineEdit
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

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter('TSV files (*.tsv)')
        if dialog.exec_():
            file_name = dialog.selectedFiles()[0]
            if file_name[-4:].lower() != '.tsv' and file_name != '':
                file_name += '.tsv'
            connection = ManageDB.create_connection(ManageDB.DATABASE_LOCATION)
            if connection is not None:
                self.results = ManageDB.run_select_sql(connection, sql_text)
                self.results.insert(0, headers)
                file = open(file_name, 'w', newline="", encoding='utf-8')
                if file.mode == 'w':
                    output = csv.writer(file, delimiter='\t', quotechar='\"')
                    for row in self.results:
                        output.writerow(row)

                    open_file_switcher = {'nt': (lambda: os.startfile(file_name)),
                                          # TODO check file_name for special characters and quote
                                          'posix': (lambda: os.system("open " + shlex.quote(file_name)))}
                    open_file_switcher[os.name]()
                else:
                    print('Error: could not open file ' + file_name)

                connection.close()
            else:
                print('Error, no connection')
        else:
            print('Error, no file location selected')

        self.process_data()

    def process_data(self):
        m = len(self.results)
        for i in range(0, m):
            data1 = []
            print(self.results[i])
            n = len(self.results[i])
            for j in range(5, n):
                data1.append(self.results[i][j])
            self.data.append(data1)
        #testing to make sure its working good
        print(self.data[0])
        print(self.data[1])
        #print(self.data[2])
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
        self.worksheet.write_column('B2', self.data[1])
        # self.worksheet.write_column('C2', self.data[2])
        # Create a new bar chart.
        chart1 = self.workbook.add_chart({'type': 'bar'})

        # Configure the first series.
        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$13',
            'values': '=Sheet1!$B$2:$B$13',
        })

        # # Configure a second series. Note use of alternative syntax to define ranges.
        # chart1.add_series({
        #     'name': ['Sheet1', 0, 2],
        #     'categories': ['Sheet1', 1, 0, 6, 0],
        #     'values': ['Sheet1', 1, 2, 6, 2],
        # })

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
        #self.workbook = xlsxwriter.Workbook('./all_data/charts/' + file_name + '_vbar.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        bold = self.workbook.add_format({'bold': 1})
        # Add the worksheet data that the charts will refer to.
        headings = [vertical_axis_title, 'Total 1', 'Total 2']
        self.worksheet.write_row('A1', headings, bold)
        self.worksheet.write_column('A2', self.data[0])
        self.worksheet.write_column('B2', self.data[1])
        # self.worksheet.write_column('C2', self.data[2])
        # Create a new bar chart.
        chart1 = self.workbook.add_chart({'type': 'column'})

        # Configure the first series.
        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$13',
            'values': '=Sheet1!$B$2:$B$13',
        })

        # # Configure a second series. Note use of alternative syntax to define ranges.
        # chart1.add_series({
        #     'name': ['Sheet1', 0, 2],
        #     'categories': ['Sheet1', 1, 0, 6, 0],
        #     'values': ['Sheet1', 1, 2, 6, 2],
        # })

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
        #self.workbook = xlsxwriter.Workbook('./all_data/charts/' + file_name + '_line.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        bold = self.workbook.add_format({'bold': 1})
        # Add the worksheet data that the charts will refer to.
        headings = [vertical_axis_title, 'Total 1', 'Total 2']
        self.worksheet.write_row('A1', headings, bold)
        self.worksheet.write_column('A2', self.data[0])
        self.worksheet.write_column('B2', self.data[1])
        # self.worksheet.write_column('C2', self.data[2])
        # Create a new bar chart.
        chart1 = self.workbook.add_chart({'type': 'line'})

        # Configure the first series.
        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$13',
            'values': '=Sheet1!$B$2:$B$13',
        })

        # # Configure a second series. Note use of alternative syntax to define ranges.
        # chart1.add_series({
        #     'name': ['Sheet1', 0, 2],
        #     'categories': ['Sheet1', 1, 0, 6, 0],
        #     'values': ['Sheet1', 1, 2, 6, 2],
        # })

        # Add a chart title and some axis labels.
        chart1.set_title({'name': chart_title})
        chart1.set_x_axis({'name': horizontal_axis_title})
        chart1.set_y_axis({'name': vertical_axis_title})

        # Set an Excel chart style.
        chart1.set_style(11)

        # Insert the chart into the worksheet (with an offset).
        self.worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})
        self.workbook.close()
