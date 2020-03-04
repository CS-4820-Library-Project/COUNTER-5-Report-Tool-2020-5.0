import csv
import os
import shlex
import sip
import json
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QComboBox, QLineEdit, QFileDialog

import ManageDB
import DataStorage
from ui import MainWindow, SearchAndClauseFrame, SearchOrClauseFrame


class SearchController:
    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        self.main_window = main_window_ui

        # set up report types combobox
        self.report_parameter = main_window_ui.search_report_parameter_combobox
        self.report_parameter.addItems(ManageDB.DATABASE_REPORTS)
        self.report_parameter.addItems(ManageDB.ITEM_REPORTS)
        self.report_parameter.addItems(ManageDB.PLATFORM_REPORTS)
        self.report_parameter.addItems(ManageDB.TITLE_REPORTS)

        # set up start year dateedit
        self.start_year_parameter = main_window_ui.search_start_year_parameter_dateedit
        self.start_year_parameter.setDate(QDate.currentDate())

        # set up end year dateedit
        self.end_year_parameter = main_window_ui.search_end_year_parameter_dateedit
        self.end_year_parameter.setDate(QDate.currentDate())

        # set up search button
        self.search_button = main_window_ui.search_button
        self.search_button.clicked.connect(self.search)

        self.open_results_checkbox = main_window_ui.search_open_results_checkbox

        # set up export button
        self.export_button = main_window_ui.search_export_button
        self.export_button.clicked.connect(self.export_parameters)

        # set up import button
        self.import_button = main_window_ui.search_import_button
        self.import_button.clicked.connect(self.import_parameters)

        # set up add and clause button
        def add_and_and_or_clause():
            and_clause = self.add_and_clause()
            self.add_or_clause(and_clause)

        self.add_and_button = main_window_ui.search_add_and_button
        self.add_and_button.clicked.connect(add_and_and_or_clause)

        # resets the search clauses when the report type is changed
        def refresh_and_add_clauses():
            self.refresh_clauses()
            add_and_and_or_clause()
        self.report_parameter.currentTextChanged.connect(refresh_and_add_clauses)

        self.and_clause_parameters = None
        refresh_and_add_clauses()

    def refresh_clauses(self):  # resets the search clauses
        self.and_clause_parameters = QFrame()
        self.and_clause_parameters.setLayout(QVBoxLayout())
        self.main_window.search_and_clause_parameters_scrollarea.setWidget(self.and_clause_parameters)

    def add_and_clause(self):
        and_clause = QFrame()
        and_clause_ui = SearchAndClauseFrame.Ui_search_and_clause_parameter_frame()
        and_clause_ui.setupUi(and_clause)

        # set up add or clause button
        def add_or_to_this_and():
            self.add_or_clause(and_clause_ui)

        and_clause_ui.search_add_or_clause_button.clicked.connect(add_or_to_this_and)

        # set up remove current and clause button
        def remove_this_and():
            self.and_clause_parameters.layout().removeWidget(and_clause)
            sip.delete(and_clause)

        and_clause_ui.search_remove_and_clause_button.clicked.connect(remove_this_and)

        # add to the layout
        self.and_clause_parameters.layout().addWidget(and_clause)

        return and_clause_ui

    def add_or_clause(self, and_clause):
        or_clause = QFrame()
        or_clause_ui = SearchOrClauseFrame.Ui_search_or_clause_parameter_frame()
        or_clause_ui.setupUi(or_clause)

        # fill field combobox
        field_combobox = or_clause_ui.search_field_parameter_combobox
        for field in ManageDB.get_report_fields_list(self.report_parameter.currentText(), True):
            if 'calculation' not in field.keys() and field['name'] not in ManageDB.FIELDS_NOT_IN_SEARCH:
                field_combobox.addItem(field['name'])

        # TODO make value check for type

        # fill comparison operator combobox
        comparison_combobox = or_clause_ui.search_comparison_parameter_combobox
        comparison_combobox.addItems(('=', '<=', '<', '>=', '>', 'LIKE'))

        # set up remove current or clause button
        def remove_this_or():
            and_clause.search_or_clause_parameters_frame.layout().removeWidget(or_clause)
            sip.delete(or_clause)

        or_clause_ui.search_remove_or_clause_button.clicked.connect(remove_this_or)

        # add to parent and clause's layout
        and_clause.search_or_clause_parameters_frame.layout().addWidget(or_clause)

        return or_clause_ui

    def export_parameters(self): # export current search parameters to selected file
        parameters = self.get_search_parameters()
        print(parameters)
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter('JSON files (*.dat)')
        if dialog.exec_():
            file_name = dialog.selectedFiles()[0]
            if file_name[-4:].lower() != '.dat' and file_name != '':
                file_name += '.tsv'
            file = open(file_name, 'w', encoding='utf-8')
            if file.mode == 'w':
                json.dump(parameters, file)

    def import_parameters(self): # import search parameters from selected file
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('JSON files (*.dat)')
        if dialog.exec_():
            fields = json.loads(DataStorage.read_json_file(dialog.selectedFiles()[0]))
            print(fields)
            self.report_parameter.setCurrentText(fields['report'])
            self.start_year_parameter.setDate(QDate(fields['start_year'], 1, 1))
            self.end_year_parameter.setDate(QDate(fields['end_year'], 1, 1))
            clauses = fields['search_parameters']
            print(clauses)
            self.refresh_clauses()
            for clause in clauses:
                and_clause = self.add_and_clause()
                for sub_clause in clause:
                    or_clause = self.add_or_clause(and_clause)
                    or_clause.search_field_parameter_combobox.setCurrentText(sub_clause['field'])
                    or_clause.search_comparison_parameter_combobox.setCurrentText(sub_clause['comparison'])
                    or_clause.search_value_parameter_lineedit.setText(sub_clause['value'])

    def search(self):  # submit search result to database and open results
        parameters = self.get_search_parameters()

        # sql query to get search results
        sql_text = ManageDB.search_sql_text(parameters['report'], parameters['start_year'],
                                            parameters['end_year'], parameters['search_parameters'])
        print(sql_text)  # testing

        headers = []
        for field in ManageDB.get_report_fields_list(parameters['report'], True):
            headers.append(field['name'])

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter('TSV files (*.tsv)')
        if dialog.exec_():
            file_name = dialog.selectedFiles()[0]
            if file_name[-4:].lower() != '.tsv' and file_name != '':
                file_name += '.tsv'
            connection = ManageDB.create_connection(ManageDB.DATABASE_LOCATION)
            if connection is not None:
                results = ManageDB.run_select_sql(connection, sql_text)
                results.insert(0, headers)
                print(results)
                file = open(file_name, 'w', newline="", encoding='utf-8')
                if file.mode == 'w':
                    output = csv.writer(file, delimiter='\t', quotechar='\"')
                    for row in results:
                        output.writerow(row)

                    open_file_switcher = {'nt': (lambda: os.startfile(file_name)),
                                          # TODO check file_name for special characters and quote
                                          'posix': (lambda: os.system("open " + shlex.quote(file_name)))}
                    if self.open_results_checkbox.isChecked():
                        open_file_switcher[os.name]()
                else:
                    print('Error: could not open file ' + file_name)

                connection.close()
            else:
                print('Error, no connection')
        else:
            print('Error, no file location selected')

    def get_search_parameters(self):
        # get report type
        report = self.report_parameter.currentText()
        # get start year
        start_year = int(self.start_year_parameter.text())
        # get end year
        end_year = int(self.end_year_parameter.text())

        search_parameters = []
        for and_widget in self.and_clause_parameters.findChildren(QFrame, 'search_and_clause_parameter_frame'):
            # iterate over and clauses
            print('and: ' + str(and_widget.objectName()) + ' ' + str(and_widget))  # testing
            or_clause_parameters = and_widget.findChild(QFrame, 'search_or_clause_parameters_frame')
            or_clauses = []
            for or_widget in or_clause_parameters.findChildren(QFrame, 'search_or_clause_parameter_frame'):
                # iterate over child or clauses
                print('\tor: ' + str(or_widget.objectName()) + ' ' + str(or_widget))  # testing
                # get parameters for clause
                field_parameter = or_widget.findChild(QComboBox, 'search_field_parameter_combobox').currentText()
                comparison_parameter = or_widget.findChild(QComboBox,
                                                           'search_comparison_parameter_combobox').currentText()
                value_parameter = or_widget.findChild(QLineEdit, 'search_value_parameter_lineedit').text()
                # TODO check for special characters
                or_clauses.append(
                    {'field': field_parameter, 'comparison': comparison_parameter, 'value': value_parameter})
            search_parameters.append(or_clauses)

        return {'report': report, 'start_year': start_year, 'end_year': end_year,
                'search_parameters': search_parameters}
