import csv
import os
import sip
import json
from typing import Tuple, Dict, Sequence, Any
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QComboBox, QLineEdit, QSpacerItem, QSizePolicy

import ManageDB
from Settings import SettingsModel
from ui import SearchTab, SearchAndClauseFrame, SearchOrClauseFrame
from Constants import *
from GeneralUtils import *


class SearchController:
    """Controls the Search tab

    :param search_ui: the UI for the search_widget
    :param settings: the user's settings"""

    def __init__(self, search_ui: SearchTab.Ui_search_tab, settings: SettingsModel):
        self.main_window = search_ui
        self.settings = settings

        # set up report types combobox
        self.report_parameter = search_ui.search_report_parameter_combobox
        self.report_parameter.addItems(ALL_REPORTS)

        # set up start year dateedit
        self.start_year_parameter = search_ui.search_start_year_parameter_dateedit
        self.start_year_parameter.setDate(QDate.currentDate())

        # set up end year dateedit
        self.end_year_parameter = search_ui.search_end_year_parameter_dateedit
        self.end_year_parameter.setDate(QDate.currentDate())

        # set up search button
        self.search_button = search_ui.search_button
        self.search_button.clicked.connect(self.search)

        self.open_results_file_radioButton = search_ui.open_file_radioButton
        self.open_results_folder_radioButton = search_ui.open_folder_radioButton
        self.open_results_both_radioButton = search_ui.open_both_radioButton
        self.dont_open_results_radioButton = search_ui.dont_open_radioButton

        # set up export button
        self.export_button = search_ui.search_export_button
        self.export_button.clicked.connect(self.export_parameters)

        # set up import button
        self.import_button = search_ui.search_import_button
        self.import_button.clicked.connect(self.import_parameters)

        # set up add and clause button
        def add_and_and_or_clause():
            """Invoked to add an and clause containing an or clause to the search"""
            and_clause = self.add_and_clause()
            self.add_or_clause(and_clause)

        self.add_and_button = search_ui.search_add_and_button
        self.add_and_button.clicked.connect(add_and_and_or_clause)

        # resets the search clauses when the report type is changed
        def refresh_and_add_clauses():
            """Resets the search clauses, then adds an and clause containing an or clause"""
            self.refresh_clauses()
            add_and_and_or_clause()

        self.report_parameter.currentTextChanged.connect(refresh_and_add_clauses)

        self.and_clause_parameters_scrollarea = search_ui.search_and_clause_parameters_scrollarea
        self.and_clause_parameters_frame = None
        refresh_and_add_clauses()

    def update_settings(self, settings: SettingsModel):
        """Called when the settings are saved

        :param settings: the new settings"""
        self.settings = settings

    def refresh_clauses(self):
        """Resets the search clauses"""
        self.and_clause_parameters_frame = QFrame()
        self.and_clause_parameters_frame.setLayout(QVBoxLayout())
        self.and_clause_parameters_frame.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding,
                                                                      QSizePolicy.Expanding))
        self.and_clause_parameters_scrollarea.setWidget(self.and_clause_parameters_frame)

    def add_and_clause(self) -> SearchAndClauseFrame.Ui_search_and_clause_parameter_frame:
        """Adds an and clause to the search"""
        and_clause = QFrame()
        and_clause_ui = SearchAndClauseFrame.Ui_search_and_clause_parameter_frame()
        and_clause_ui.setupUi(and_clause)

        # set up add or clause button
        def add_or_to_this_and():
            """Adds an or clause to this and clause"""
            self.add_or_clause(and_clause_ui)

        and_clause_ui.search_add_or_clause_button.clicked.connect(add_or_to_this_and)

        # set up remove current and clause button
        def remove_this_and():
            """Removes this and clause"""
            self.and_clause_parameters_frame.layout().removeWidget(and_clause)
            sip.delete(and_clause)

        and_clause_ui.search_remove_and_clause_button.clicked.connect(remove_this_and)

        # add to the layout
        self.and_clause_parameters_frame.layout().insertWidget(self.and_clause_parameters_frame.layout().count() - 1,
                                                               and_clause)

        return and_clause_ui

    def add_or_clause(self, and_clause: SearchAndClauseFrame.Ui_search_and_clause_parameter_frame) \
            -> SearchOrClauseFrame.Ui_search_or_clause_parameter_frame:
        """Adds an or clause to the search

        :param and_clause: the and clause the or clause is added to"""
        or_clause = QFrame()
        or_clause_ui = SearchOrClauseFrame.Ui_search_or_clause_parameter_frame()
        or_clause_ui.setupUi(or_clause)

        # fill field combobox
        field_combobox = or_clause_ui.search_field_parameter_combobox
        for field in ManageDB.get_view_report_fields_list(self.report_parameter.currentText()):
            if field[NAME_KEY] not in FIELDS_NOT_IN_SEARCH_DROPDOWN:
                field_combobox.addItem(field[NAME_KEY], field['type'])

        type_label = or_clause_ui.search_type_label

        value_lineedit = or_clause_ui.search_value_parameter_lineedit

        def on_field_changed():
            """Invoked when the field parameter is changed"""
            type_label.setText(field_combobox.currentData().capitalize() + " Input")
            value_lineedit.setText(None)
            if field_combobox.currentData() == 'INTEGER':
                value_lineedit.setValidator(QIntValidator())
            elif field_combobox.currentData() == 'REAL':
                value_lineedit.setValidator(QDoubleValidator())
            else:
                value_lineedit.setValidator(None)

        field_combobox.currentTextChanged.connect(on_field_changed)
        on_field_changed()

        # fill comparison operator combobox
        comparison_combobox = or_clause_ui.search_comparison_parameter_combobox
        comparison_combobox.addItems(COMPARISON_OPERATORS)
        comparison_combobox.addItems(NON_COMPARISONS)

        def on_comparison_changed():
            """Invoked when the comparison parameter is changed"""
            if comparison_combobox.currentText() in NON_COMPARISONS:
                value_lineedit.setText(None)
                value_lineedit.setEnabled(False)
            else:
                value_lineedit.setEnabled(True)

        comparison_combobox.currentTextChanged.connect(on_comparison_changed)

        # set up remove current or clause button
        def remove_this_or():
            """Removes this or clause"""
            and_clause.search_or_clause_parameters_frame.layout().removeWidget(or_clause)
            sip.delete(or_clause)

        or_clause_ui.search_remove_or_clause_button.clicked.connect(remove_this_or)

        # add to parent and clause's layout
        and_clause.search_or_clause_parameters_frame.layout().addWidget(or_clause)

        return or_clause_ui

    def export_parameters(self):
        """Exports the current search parameters to the selected file"""
        file_name = choose_save(JSON_FILTER)
        if file_name != '':
            if not file_name.lower().endswith('.dat'):
                file_name += '.dat'
            report, start_year, end_year, search_parameters = self.get_search_parameters()
            file = open(file_name, 'w', encoding='utf-8-sig')
            if file.mode == 'w':
                json.dump({'report': report, 'start_year': start_year, 'end_year': end_year,
                           'search_parameters': search_parameters}, file)
                show_message('Search saved to ' + file_name)
        else:
            print('Error, no file location selected')

    def import_parameters(self):
        """Imports a new set of search parameters from the selected file"""
        file_name = choose_file(JSON_FILTER)
        if file_name != '':
            fields = json.loads(read_json_file(file_name))
            self.report_parameter.setCurrentText(fields['report'])
            self.start_year_parameter.setDate(QDate(fields['start_year'], 1, 1))
            self.end_year_parameter.setDate(QDate(fields['end_year'], 1, 1))
            clauses = fields['search_parameters']
            self.refresh_clauses()
            for clause in clauses:
                and_clause = self.add_and_clause()
                for sub_clause in clause:
                    or_clause = self.add_or_clause(and_clause)
                    or_clause.search_field_parameter_combobox.setCurrentText(sub_clause[FIELD_KEY])
                    or_clause.search_comparison_parameter_combobox.setCurrentText(sub_clause[COMPARISON_KEY])
                    or_clause.search_value_parameter_lineedit.setText(sub_clause[VALUE_KEY])

    def search(self):
        """Queries the database based on the current search parameters and saves the results to the selected file"""
        report, start_year, end_year, search_parameters = self.get_search_parameters()

        # sql query to get search results
        sql_text, data = ManageDB.search_sql_text(report, start_year, end_year, search_parameters)

        headers = []
        for field in ManageDB.get_view_report_fields_list(report):
            headers.append(field[NAME_KEY])

        file_name = choose_save(TSV_FILTER)
        if file_name != '':
            if not file_name.lower().endswith('.tsv'):
                file_name += '.tsv'
            connection = ManageDB.create_connection(DATABASE_LOCATION)
            if connection is not None:
                results = ManageDB.run_select_sql(connection, sql_text, data)
                results.insert(0, headers)
                if self.settings.show_debug_messages: print(results)
                file = open(file_name, 'w', newline="", encoding='utf-8-sig')
                if file.mode == 'w':
                    output = csv.writer(file, delimiter='\t', quotechar='\"')
                    for row in results:
                        output.writerow(row)

                    if self.open_results_file_radioButton.isChecked() or self.open_results_both_radioButton.isChecked():
                        open_file_or_dir(file_name)

                    if self.open_results_folder_radioButton.isChecked() \
                            or self.open_results_both_radioButton.isChecked():
                        open_file_or_dir(os.path.dirname(file_name))

                    if self.dont_open_results_radioButton.isChecked():
                        show_message('Results saved to ' + file_name)

                else:
                    print('Error: could not open file ' + file_name)

                connection.close()
            else:
                print('Error, no connection')
        else:
            print('Error, no file location selected')

    def get_search_parameters(self) -> Tuple[str, int, int, Sequence[Sequence[Dict[str, Any]]]]:
        """Reads the current search parameters from the UI

        :returns: (report, start_year, end_year, search_parameters) a Tuple with the kind of report selected, the
            starting year selected, the ending year selected, and a list of the search parameters in POS form (and of
            ors)"""
        # get report type
        report = self.report_parameter.currentText()
        # get start year
        start_year = int(self.start_year_parameter.text())
        # get end year
        end_year = int(self.end_year_parameter.text())

        search_parameters = []
        for and_widget in self.and_clause_parameters_frame.findChildren(QFrame, 'search_and_clause_parameter_frame'):
            # iterate over and clauses
            or_clause_parameters = and_widget.findChild(QFrame, 'search_or_clause_parameters_frame')
            or_clauses = []
            for or_widget in or_clause_parameters.findChildren(QFrame, 'search_or_clause_parameter_frame'):
                # iterate over child or clauses
                # get parameters for clause
                field_parameter_combobox = or_widget.findChild(QComboBox, 'search_field_parameter_combobox')
                field_parameter = field_parameter_combobox.currentText()
                comparison_parameter_combobox = or_widget.findChild(QComboBox, 'search_comparison_parameter_combobox')
                comparison_parameter = comparison_parameter_combobox.currentText()
                value_parameter_lineedit = or_widget.findChild(QLineEdit, 'search_value_parameter_lineedit')
                value_parameter = None
                if comparison_parameter in NON_COMPARISONS:
                    pass
                elif field_parameter_combobox.currentData() == 'INTEGER':
                    value_parameter = int(value_parameter_lineedit.text())
                elif field_parameter_combobox.currentData() == 'REAL':
                    value_parameter = float(value_parameter_lineedit.text())
                else:
                    value_parameter = value_parameter_lineedit.text()
                or_clauses.append(
                    {FIELD_KEY: field_parameter, COMPARISON_KEY: comparison_parameter, VALUE_KEY: value_parameter})
            search_parameters.append(or_clauses)

        return report, start_year, end_year, search_parameters
