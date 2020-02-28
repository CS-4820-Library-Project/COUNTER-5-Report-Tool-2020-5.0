import sip, csv
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QComboBox, QLineEdit
from datetime import date
import ManageDB
from ui import MainWindow, SearchAndClauseFrame, SearchOrClauseFrame


class SearchController:
    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        # set up report types combobox
        self.report_parameter = main_window_ui.search_report_parameter_combobox
        self.report_parameter.addItems(ManageDB.DATABASE_REPORTS)
        self.report_parameter.addItems(ManageDB.ITEM_REPORTS)
        self.report_parameter.addItems(ManageDB.PLATFORM_REPORTS)
        self.report_parameter.addItems(ManageDB.TITLE_REPORTS)

        # set up start year dateedit
        self.start_year_parameter = main_window_ui.search_start_year_parameter_dateedit
        self.start_year_parameter.setDate(date.today())

        # set up end year dateedit
        self.end_year_parameter = main_window_ui.search_end_year_parameter_dateedit
        self.end_year_parameter.setDate(date.today())

        # set up the search clauses
        self.and_clause_parameters = None

        def refresh_clauses():
            self.refresh_clauses(main_window_ui)

        refresh_clauses()

        # resets the search clauses when the report type is changed
        self.report_parameter.currentTextChanged.connect(refresh_clauses)

        # set up search button
        self.search_button = main_window_ui.search_button
        self.search_button.clicked.connect(self.search)

        def restore_database():
            ManageDB.setup_database(True)
            ManageDB.insert_all_files()

        self.restore_database_button = main_window_ui.search_restore_database_button
        self.restore_database_button.clicked.connect(restore_database)

        # set up add and clause button
        self.add_and_button = main_window_ui.search_add_and_button
        self.add_and_button.clicked.connect(self.add_and_clause)

    def refresh_clauses(self, main_window_ui: MainWindow.Ui_mainWindow):  # resets the search clauses
        self.and_clause_parameters = QFrame()
        self.and_clause_parameters.setLayout(QVBoxLayout())
        main_window_ui.search_and_clause_parameters_scrollarea.setWidget(self.and_clause_parameters)
        self.add_and_clause()

    def add_and_clause(self):
        and_clause = QFrame()
        and_clause_ui = SearchAndClauseFrame.Ui_search_and_clause_parameter_frame()
        and_clause_ui.setupUi(and_clause)

        # add one blank clause
        self.add_or_clause(and_clause_ui)

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

    def add_or_clause(self, and_clause):
        or_clause = QFrame()
        or_clause_ui = SearchOrClauseFrame.Ui_search_or_clause_parameter_frame()
        or_clause_ui.setupUi(or_clause)

        # fill field combobox
        field_combobox = or_clause_ui.search_field_parameter_combobox
        for field in ManageDB.get_report_fields_list(self.report_parameter.currentText(), True):
            if 'calculation' not in field.keys() and field['name'] not in ManageDB.FIELDS_NOT_IN_SEARCH:
                field_combobox.addItem(field['name'])

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

    def search(self):  # submit search result to database and open results
        # get report type
        report = self.report_parameter.currentText()
        # get start year
        start_year = self.start_year_parameter.text()
        # get end year
        end_year = self.end_year_parameter.text()

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
                or_clauses.append(
                    {'field': field_parameter, 'comparison': comparison_parameter, 'value': value_parameter})
            search_parameters.append(or_clauses)

        # sql query to get search results
        sql_text = ManageDB.search_sql_text(report, start_year, end_year, search_parameters)
        print(sql_text)  # testing

        headers = []
        for field in ManageDB.get_report_fields_list(report, True):
            headers.append(field['name'])

        # get results
        connection = ManageDB.create_connection(ManageDB.DATABASE_LOCATION)
        if connection is not None:
            results = ManageDB.run_select_sql(connection, sql_text)
            results.insert(0, headers)
            print(results)
            with open('output.tsv', 'w', newline="") as output:
                tsv_output = csv.writer(output, delimiter='\t')
                for row in results:
                    tsv_output.writerow(row)
            connection.close()
        else:
            print("Error, no connection")
