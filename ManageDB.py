import sqlite3
import os
import csv
from typing import Tuple, Dict, Sequence, Any, Union
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel

from Constants import *
from ui import UpdateDatabaseProgressDialog


def get_report_fields_list(report: str) -> Sequence[Dict[str, Any]]:
    """Gets the fields in the report table

    :param report: the kind of the report
    :returns: list of fields in this report's table"""
    report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
    fields = []
    for field in report_fields:  # fields specific to this report
        if report in field[REPORTS_KEY]:
            fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]})
    return tuple(fields)


def get_view_report_fields_list(report: str) -> Sequence[Dict[str, Any]]:
    """Gets the fields in the report month view

    :param report: the kind of the report
    :returns: list of fields in this report's month view"""
    report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
    fields = []
    for field in report_fields:  # fields specific to this report
        if report in field[REPORTS_KEY]:
            fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY],
                           SOURCE_KEY: report})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        if field[NAME_KEY] not in FIELDS_NOT_IN_VIEWS:
            fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY],
                           SOURCE_KEY: report})
    for field in COST_FIELDS:  # cost table fields
        fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY],
                       SOURCE_KEY: report[:2] + COST_TABLE_SUFFIX})
    fields.append({NAME_KEY: YEAR_TOTAL, TYPE_KEY: 'INTEGER', CALCULATION_KEY: 'SUM(' + 'metric' + ')',
                   SOURCE_KEY: 'joined'})
    for key in sorted(MONTHS):  # month columns
        fields.append({NAME_KEY: MONTHS[key], TYPE_KEY: 'INTEGER',
                       CALCULATION_KEY: 'COALESCE(SUM(CASE ' + 'month' + ' WHEN ' + str(
                           key) + ' THEN ' + 'metric' + ' END), 0)', SOURCE_KEY: 'joined'})
    return tuple(fields)


def get_chart_report_fields_list(report: str) -> Sequence[Dict[str, Any]]:
    """Gets the fields in the report chart

    :param report: the kind of the report
    :returns: list of fields in this report's chart"""
    fields = []
    name_field = get_field_attributes(report, NAME_FIELD_SWITCHER[report[:2]])  # name field only
    fields.append(
        {NAME_KEY: name_field[NAME_KEY], TYPE_KEY: name_field[TYPE_KEY], OPTIONS_KEY: name_field[OPTIONS_KEY]})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        if field[NAME_KEY] not in FIELDS_NOT_IN_CHARTS:
            fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]})
    for field in COST_FIELDS:  # cost table fields
        fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]})
    fields.append({NAME_KEY: YEAR_TOTAL, TYPE_KEY: 'INTEGER', OPTIONS_KEY: ()})
    for key in sorted(MONTHS):  # month columns
        fields.append({NAME_KEY: MONTHS[key], TYPE_KEY: 'INTEGER', OPTIONS_KEY: ()})
    return tuple(fields)


def get_top_number_chart_report_fields_list(report: str) -> Sequence[Dict[str, Any]]:
    """Gets the fields in the report top # chart

    :param report: the kind of the report
    :returns: list of fields in this report's top # chart"""
    fields = []
    name_field = get_field_attributes(report, NAME_FIELD_SWITCHER[report[:2]])  # name field only
    fields.append({NAME_KEY: name_field[NAME_KEY], TYPE_KEY: name_field[TYPE_KEY], OPTIONS_KEY: name_field[OPTIONS_KEY],
                   SOURCE_KEY: 'data'})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        if field[NAME_KEY] not in FIELDS_NOT_IN_CHARTS:
            fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY],
                           SOURCE_KEY: 'data'})
    for field in COST_FIELDS:  # cost table fields
        fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY],
                       SOURCE_KEY: 'data'})
    fields.append({NAME_KEY: YEAR_TOTAL, TYPE_KEY: 'INTEGER', OPTIONS_KEY: (), SOURCE_KEY: 'data'})
    for key in sorted(MONTHS):  # month columns
        fields.append({NAME_KEY: MONTHS[key], TYPE_KEY: 'INTEGER', OPTIONS_KEY: (), SOURCE_KEY: 'data'})
    fields.append({NAME_KEY: 'total_of_' + YEAR_TOTAL, TYPE_KEY: 'INTEGER', CALCULATION_KEY: 'SUM(' + YEAR_TOTAL + ')',
                   SOURCE_KEY: 'totals'})
    fields.append(
        {NAME_KEY: RANKING, TYPE_KEY: 'INTEGER', CALCULATION_KEY: 'RANK() OVER(ORDER BY ' + 'total_of_' + YEAR_TOTAL
                                                                  + ' DESC)', SOURCE_KEY: 'joined'})
    return tuple(fields)


def get_cost_fields_list(report_type: str) -> Sequence[Dict[str, Any]]:
    """Gets the fields in the report type cost table

    :param report_type: the type of the report (master report name)
    :returns: list of fields in this report type's cost table"""
    fields = []
    name_field = get_field_attributes(report_type, NAME_FIELD_SWITCHER[report_type])  # name field only
    fields.append(
        {NAME_KEY: name_field[NAME_KEY], TYPE_KEY: name_field[TYPE_KEY], OPTIONS_KEY: name_field[OPTIONS_KEY]})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        if field[NAME_KEY] in COSTS_KEY_FIELDS:
            fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]})
    for field in COST_FIELDS:  # cost table fields
        fields.append({NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]})
    return tuple(fields)


def get_field_attributes(report: str, field_name: str) -> Union[Dict[str, Any], None]:
    """Gets the field attributes

    :param report: the kind of the report
    :param field_name: the name of the field
    :returns: attributes of the field"""
    report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
    for field in report_fields:
        if field[NAME_KEY] == field_name:
            return {NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]}
    for field in ALL_REPORT_FIELDS:
        if field[NAME_KEY] == field_name:
            return {NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]}
    for field in COST_FIELDS:
        if field[NAME_KEY] == field_name:
            return {NAME_KEY: field[NAME_KEY], TYPE_KEY: field[TYPE_KEY], OPTIONS_KEY: field[OPTIONS_KEY]}
    return None


def create_table_sql_texts(report: str) -> str:
    """Makes the SQL statement to create the tables from the table definition

    :param report: the kind of the report
    :returns: the sql statement"""
    sql_text = 'CREATE TABLE IF NOT EXISTS ' + report + '('
    report_fields = get_report_fields_list(report)
    fields_and_options = []
    key_fields = []
    for field in report_fields:
        field_text = field[NAME_KEY] + ' ' + field[TYPE_KEY]
        if field[OPTIONS_KEY]:
            field_text += ' ' + ' '.join(field[OPTIONS_KEY])
        fields_and_options.append(field_text)
        if field[NAME_KEY] not in FIELDS_NOT_IN_KEYS:
            key_fields.append(field[NAME_KEY])
    sql_text += '\n\t' + ', \n\t'.join(fields_and_options) + ',\n\tPRIMARY KEY(' + ', '.join(key_fields) + '));'
    return sql_text


def create_view_sql_texts(report: str) -> str:
    """Makes the SQL statement to create the views from the table definition

    :param report: the kind of the report
    :returns: the sql statement"""
    name_field = get_field_attributes(report[:2], NAME_FIELD_SWITCHER[report[:2]])
    sql_text = 'CREATE VIEW IF NOT EXISTS ' + report + VIEW_SUFFIX + ' AS SELECT'
    report_fields = get_view_report_fields_list(report)
    fields = []
    calcs = []
    key_fields = []
    for field in report_fields:
        if CALCULATION_KEY not in field.keys():
            field_text = ''
            if field[NAME_KEY] in COSTS_KEY_FIELDS or field[NAME_KEY] == name_field[NAME_KEY]:
                key_fields.append(field[NAME_KEY])
                field_text = report + '.'
            field_text += field[NAME_KEY]
            fields.append(field_text)
        else:
            calcs.append(field[CALCULATION_KEY] + ' AS ' + field[NAME_KEY])
    sql_text += '\n\t' + ', \n\t'.join(fields) + ', \n\t' + ', \n\t'.join(calcs)
    sql_text += '\nFROM ' + report + ' LEFT JOIN ' + report[:2] + COST_TABLE_SUFFIX
    join_clauses = []
    for key_field in key_fields:
        join_clauses.append(report + '.' + key_field + ' = ' + report[:2] + COST_TABLE_SUFFIX + '.' + key_field)
    sql_text += ' ON ' + ' AND '.join(join_clauses)
    sql_text += '\nGROUP BY ' + ', '.join(fields) + ';'
    return sql_text


def create_cost_table_sql_texts(report_type: str) -> str:
    """Makes the SQL statement to create the cost tables from the table definition

    :param report_type: the type of the report (master report name)
    :returns: the sql statement"""
    sql_text = 'CREATE TABLE IF NOT EXISTS ' + report_type + COST_TABLE_SUFFIX + '('
    report_fields = get_cost_fields_list(report_type)
    name_field = get_field_attributes(report_type, NAME_FIELD_SWITCHER[report_type])
    fields_and_options = []
    key_fields = []
    for field in report_fields:
        field_text = field[NAME_KEY] + ' ' + field[TYPE_KEY]
        if field[OPTIONS_KEY]:
            field_text += ' ' + ' '.join(field[OPTIONS_KEY])
        fields_and_options.append(field_text)
        if field[NAME_KEY] in COSTS_KEY_FIELDS or field[NAME_KEY] == name_field[NAME_KEY]:
            key_fields.append(field[NAME_KEY])
    sql_text += '\n\t' + ', \n\t'.join(fields_and_options)
    sql_text += ',\n\tPRIMARY KEY(' + ', '.join(key_fields) + '));'
    return sql_text


def replace_sql_text(file_name: str, report: str, data: Sequence[Dict[str, Any]]) \
        -> Tuple[str, Sequence[Sequence[Any]], str, Sequence[Sequence[Any]]]:
    """Makes the SQL statements to delete old data from a table and 'replace or insert' data into a table

    :param file_name: the name of the file the data is from
    :param report: the kind of the report
    :param data: the data from the file
    :returns: (sql_delete_text, delete_values, sql_replace_text, replace_values) a Tuple with the parameterized SQL
        statement to delete the old data, the values for it, the parameterized SQL statement to 'replace or insert'
        data into the table, and the values for it"""
    sql_replace_text = 'REPLACE INTO ' + report + '('
    report_fields = get_report_fields_list(report)
    fields = []
    for field in report_fields:
        fields.append(field[NAME_KEY])
    sql_replace_text += ', '.join(fields) + ')'
    sql_replace_text += '\nVALUES'
    placeholders = ['?'] * len(fields)
    sql_replace_text += '(' + ', '.join(placeholders) + ');'
    replace_values = []
    for row in data:  # gets data to fill parameters
        row_values = []
        for key in fields:
            value = None
            if row.get(key):
                value = row.get(key)
            else:
                value = ''  # if empty, use empty string
            row_values.append(value)
        replace_values.append(row_values)
    sql_delete_text = 'DELETE FROM ' + report + ' WHERE ' + 'file' + ' = ?;'
    delete_values = ((file_name,),)
    return sql_delete_text, tuple(delete_values), sql_replace_text, tuple(replace_values)


def update_vendor_name_sql_text(table: str, old_name: str, new_name: str) -> Tuple[str, Sequence[Sequence[Any]]]:
    """Makes the SQL statement to update the vendor's name in a table

    :param table: the name of the table to replace in
    :param old_name: the old name of the vendor
    :param new_name: the new name of the vendor
    :returns: (sql_text, values) a Tuple with the parameterized SQL statement to update the vendor name in the table,
        and the values for it"""
    sql_text = 'UPDATE ' + table + ' SET'
    values = []
    sql_text += '\n\t' + 'vendor' + ' = ?'
    values.append(new_name)
    if not table.endswith(COST_TABLE_SUFFIX):
        sql_text += ',\n\t' + 'file' + ' = ' + 'REPLACE(' + 'file' + ', ' + '\"_\" || ? || \"_\"'
        values.append(old_name)
        sql_text += ', ' + '\"_\" || ? || \"_\")'
        values.append(new_name)
    sql_text += '\nWHERE ' + 'vendor' + ' = ?;'
    values.append(old_name)
    return sql_text, (values,)


def update_vendor_in_all_tables(old_name: str, new_name: str):
    """Updates the vendor's name in all tables

    :param old_name: the old name of the vendor
    :param new_name: the new name of the vendor"""
    sql_texts = []
    for table in ALL_REPORTS:
        sql_text, data = update_vendor_name_sql_text(table, old_name, new_name)
        sql_texts.append({'sql_text': sql_text, 'data': data})
    for cost_table in REPORT_TYPE_SWITCHER.keys():
        sql_text, data = update_vendor_name_sql_text(cost_table + COST_TABLE_SUFFIX, old_name, new_name)
        sql_texts.append({'sql_text': sql_text, 'data': data})

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        for sql_text in sql_texts:
            run_sql(connection, sql_text['sql_text'], sql_text['data'])
        connection.close()
    else:
        print('Error, no connection')


def replace_costs_sql_text(report_type: str, data: Sequence[Dict[str, Any]]) -> Tuple[str, Sequence[Sequence[Any]]]:
    """Makes the SQL statement to 'replace or insert' data into a cost table

    :param report_type: the type of the report (master report name)
    :param data: the new data for the table
    :returns: (sql_text, values) a Tuple with the parameterized SQL statement to 'replace or insert' the costs, and the
        values for it"""
    sql_text = 'REPLACE INTO ' + report_type + COST_TABLE_SUFFIX + '('
    report_fields = get_cost_fields_list(report_type)
    fields = []
    for field in report_fields:
        fields.append(field[NAME_KEY])
    sql_text += ', '.join(fields) + ')'
    sql_text += '\nVALUES'
    placeholders = ['?'] * len(fields)
    sql_text += '(' + ', '.join(placeholders) + ');'
    values = []
    for row in data:  # gets data to fill parameters
        row_values = []
        for key in fields:
            value = None
            if row.get(key):
                value = row.get(key)
            else:
                value = ''  # if empty, use empty string
            row_values.append(value)
        values.append(row_values)
    return sql_text, tuple(values)


def delete_costs_sql_text(report_type: str, vendor: str, year: int, name: str) -> Tuple[str, Sequence[Sequence[Any]]]:
    """Makes the SQL statement to delete data from a cost table

    :param report_type: the type of the report (master report name)
    :param vendor: the vendor name of the cost
    :param year: the year of the cost
    :param name: the name the cost is associated with (database/item/platform/title)
    :returns: (sql_text, values) a Tuple with the parameterized SQL statement to delete the costs row, and the values
        for it"""
    name_field = NAME_FIELD_SWITCHER[report_type]
    values = []
    sql_text = 'DELETE FROM ' + report_type + COST_TABLE_SUFFIX
    sql_text += '\nWHERE '
    sql_text += '\n\t' + 'vendor' + ' = ?'
    values.append(vendor)
    sql_text += '\n\tAND ' + 'year' + ' = ?'
    values.append(year)
    sql_text += '\n\tAND ' + name_field + ' = ?;'
    values.append(name)
    return sql_text, (values,)


def read_report_file(file_name: str, vendor: str, year: int) -> Union[Tuple[str, str, Sequence[Dict[str, Any]]],
                                                                      None]:
    """Reads a specific csv/tsv file and returns the kind of report and the values for inserting

    :param file_name: the name of the file the data is from
    :param vendor: the vendor name of the data in the file
    :param year: the year of the data in the file
    :returns: (file_name, report, values) a Tuple with the file name, the kind of report, and the data from the file"""
    delimiter = DELIMITERS[file_name[-4:].lower()]
    file = open(file_name, 'r', encoding='utf-8-sig')
    reader = csv.reader(file, delimiter=delimiter, quotechar='\"')
    if file.mode == 'r':
        header = {}
        for row in range(HEADER_ROWS):  # reads header row data
            cells = next(reader)
            key = cells[0].lower()
            if len(cells) > 1:
                header[key] = cells[1].strip()
            else:
                header[key] = None
        # print(header)
        for row in range(BLANK_ROWS):
            next(reader)
        column_headers = next(reader)
        column_headers = list(map((lambda column_header: column_header.lower()), column_headers))
        # print(column_headers)
        values = []
        for cells in list(reader):
            for month in MONTHS:  # makes value from each month with metric > 0 for each row
                month_header = MONTHS[month][:3].lower() + '-' + str(year)
                if month_header in column_headers:
                    current_month = column_headers.index(month_header)
                    metric = int(cells[current_month])
                    if metric > 0:
                        value = {}
                        last_column = column_headers.index(YEAR_TOTAL)
                        for i in range(last_column):  # read columns before months
                            value[column_headers[i]] = cells[i]
                        if not value['metric_type']:  # if no metric type column, use the metric type from header
                            value['metric_type'] = header['metric_types']
                        # additional fields
                        value['year'] = year
                        value['month'] = month
                        value['metric'] = int(cells[current_month])
                        value['vendor'] = vendor
                        value['updated_on'] = header['created']
                        value['file'] = os.path.basename(file.name)
                        values.append(value)
        return os.path.basename(file.name), header['report_id'], tuple(values)
    else:
        print('Error: could not open file ' + file_name)


def read_costs_file(file_name: str) -> Union[Sequence[Dict[str, Any]], None]:
    """Reads a specific csv/tsv cost file and returns the values for inserting

    :param file_name: the name of the file the data is from
    :returns: list of values from the file"""
    delimiter = DELIMITERS[file_name[-4:].lower()]
    file = open(file_name, 'r', encoding='utf-8-sig')
    reader = csv.reader(file, delimiter=delimiter, quotechar='\"')
    if file.mode == 'r':
        column_headers = next(reader)
        column_headers = list(map((lambda column_header: column_header.lower()), column_headers))
        values = []
        for cells in list(reader):
            value = {}
            for i in range(len(cells)):  # read columns
                value[column_headers[i]] = cells[i]
            values.append(value)
        return tuple(values)
    else:
        print('Error: could not open file ' + file_name)


def get_all_report_files() -> Sequence[Dict[str, Any]]:
    """Gets the list of the report files in the protected directory

    :returns: list of report files"""
    files = []
    for upper_directory in os.scandir(PROTECTED_DATABASE_FILE_DIR):  # iterate over all files in FILE_LOCATION
        if upper_directory.is_dir():
            for lower_directory in os.scandir(upper_directory):
                if lower_directory.is_dir():
                    directory_data = {FILE_SUBDIRECTORY_ORDER[0]: upper_directory.name,
                                      FILE_SUBDIRECTORY_ORDER[1]: lower_directory.name}  # get data from directory names
                    for file in os.scandir(lower_directory):
                        if file.name[-4:] in DELIMITERS:
                            files.append({'file': file.path, 'vendor': directory_data['vendor'],
                                          'year': directory_data['year']})
    return tuple(files)


def get_all_cost_files() -> Sequence[Dict[str, Any]]:
    """Gets the list of the cost files in the costs directory

    :returns: list of cost files"""
    files = []
    for file in os.scandir(COSTS_SAVE_FOLDER):
        if file.name[-4:] in DELIMITERS:
            files.append({'file': file.path, 'report': file.name[:2]})
    return tuple(files)


def insert_single_file(file_path: str, vendor: str, year: int):
    """Inserts a single file's data into the database

    :param file_path: the path of the file the data is from
    :param vendor: the vendor name of the data in the file
    :param year: the year of the data in the file"""
    file, report, read_data = read_report_file(file_path, vendor, year)
    delete, delete_data, replace, replace_data = replace_sql_text(file, report, read_data)

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        run_sql(connection, delete, delete_data)
        run_sql(connection, replace, replace_data)
        connection.close()
    else:
        print('Error, no connection')


def insert_single_cost_file(report_type: str, file_path: str):
    """Inserts a single file's data into the database

    :param report_type: the type of the report (master report name)
    :param file_path: the path of the file the data is from"""
    read_data = read_costs_file(file_path)
    sql_text, data = replace_costs_sql_text(report_type, read_data)

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        run_sql(connection, sql_text, data)
        connection.close()
    else:
        print('Error, no connection')


def search_sql_text(report: str, start_year: int, end_year: int,
                    search_parameters: Sequence[Sequence[Dict[str, Any]]]) -> Tuple[str, Sequence[Any]]:
    """Makes the SQL statement to search the database based on a search

    :param report: the kind of the report
    :param start_year: the starting year of the search
    :param end_year: the ending year of the search
    :param search_parameters: list of search parameters in POS form
    :returns: (sql_text, values) a Tuple with the parameterized SQL statement to search the database, and the values
        for it"""
    sql_text = 'SELECT * FROM ' + report + VIEW_SUFFIX
    sql_text += '\nWHERE'
    clauses = [[{FIELD_KEY: 'year', COMPARISON_KEY: '>=', VALUE_KEY: start_year}],
               [{FIELD_KEY: 'year', COMPARISON_KEY: '<=', VALUE_KEY: end_year}]]
    clauses.extend(search_parameters)
    print(clauses)
    clauses_texts = []
    data = []
    for clause in clauses:
        sub_clauses_text = []
        for sub_clause in clause:
            current_text = sub_clause[FIELD_KEY] + ' ' + sub_clause[COMPARISON_KEY]
            if sub_clause[COMPARISON_KEY] not in NON_COMPARISONS:
                current_text += ' ?'
                data.append(sub_clause[VALUE_KEY])
            sub_clauses_text.append(current_text)
        clauses_texts.append('(' + ' OR '.join(sub_clauses_text) + ')')
    sql_text += '\n\t' + '\n\tAND '.join(clauses_texts)
    sql_text += ';'
    return sql_text, tuple(data)


def chart_search_sql_text(report: str, start_year: int, end_year: int, name: str, metric_type: str, vendor: str) \
        -> Tuple[str, Sequence[Any]]:
    """Makes the SQL statement to search the database for chart data

    :param report: the kind of the report
    :param start_year: the starting year of the search
    :param end_year: the ending year of the search
    :param name: the name field (database/item/platform/title) value
    :param metric_type: the metric type value
    :param vendor: the vendor name you want to search for
    :returns: (sql_text, values) a Tuple with the parameterized SQL statement to search the database, and the values
        for it"""
    sql_text = 'SELECT'
    chart_fields = get_chart_report_fields_list(report)
    fields = []
    for field in chart_fields:
        fields.append(field[NAME_KEY])
    sql_text += '\n\t' + ', '.join(fields)
    sql_text += '\nFROM ' + report + VIEW_SUFFIX
    sql_text += '\nWHERE'
    clauses = [{FIELD_KEY: 'year', COMPARISON_KEY: '>=', VALUE_KEY: start_year},
               {FIELD_KEY: 'year', COMPARISON_KEY: '<=', VALUE_KEY: end_year},
               {FIELD_KEY: chart_fields[0][NAME_KEY], COMPARISON_KEY: 'LIKE', VALUE_KEY: name},
               {FIELD_KEY: 'metric_type', COMPARISON_KEY: 'LIKE', VALUE_KEY: metric_type},
               {FIELD_KEY: 'vendor', COMPARISON_KEY: 'LIKE', VALUE_KEY: vendor}]
    clauses_texts = []
    data = []
    for clause in clauses:
        clauses_texts.append(clause[FIELD_KEY] + ' ' + clause[COMPARISON_KEY] + ' ?')
        data.append(clause[VALUE_KEY])
    sql_text += '\n\t' + '\n\tAND '.join(clauses_texts)
    sql_text += ';'
    return sql_text, tuple(data)


def top_number_chart_search_sql_text(report: str, start_year: int, end_year: int, metric_type: str,
                                     vendor: str = None, number: int = None) -> Tuple[str, Sequence[Any]]:
    """Makes the SQL statement to search the database for chart data

    :param report: the kind of the report
    :param start_year: the starting year of the search
    :param end_year: the ending year of the search
    :param metric_type: the metric type value
    :param vendor: the vendor name you want to search for
    :param number: the number to show of the top months
    :returns: (sql_text, values) a Tuple with the parameterized SQL statement to search the database, and the values
        for it"""
    name_field = get_field_attributes(report[:2], NAME_FIELD_SWITCHER[report[:2]])
    chart_fields = get_top_number_chart_report_fields_list(report)
    sql_text = 'SELECT ' + '\n\t' + ',\n\t'.join(['data.' + field[NAME_KEY] for field in chart_fields
                                                  if field[SOURCE_KEY] == 'data'])
    sql_text += ',\n\t' + ',\n\t'.join(['totals.' + field[NAME_KEY] for field in chart_fields
                                        if field[SOURCE_KEY] == 'totals'])
    joined_fields = []
    data_fields = []
    totals_fields = [name_field[NAME_KEY]] + list(CHART_KEY_FIELDS)
    key_fields = []
    for field in chart_fields:
        if field[NAME_KEY] in CHART_KEY_FIELDS or field[NAME_KEY] == name_field[NAME_KEY]:
            key_fields.append(field[NAME_KEY])
        if field[SOURCE_KEY] == 'joined':
            if CALCULATION_KEY not in field.keys():
                joined_fields.append(field[NAME_KEY])
            else:
                joined_fields.append(field[CALCULATION_KEY] + ' AS ' + field[NAME_KEY])
        if field[SOURCE_KEY] == 'data':
            if CALCULATION_KEY not in field.keys():
                data_fields.append(field[NAME_KEY])
            else:
                data_fields.append(field[CALCULATION_KEY] + ' AS ' + field[NAME_KEY])
        if field[SOURCE_KEY] == 'totals':
            if CALCULATION_KEY not in field.keys():
                totals_fields.append(field[NAME_KEY])
            else:
                totals_fields.append(field[CALCULATION_KEY] + ' AS ' + field[NAME_KEY])
    sql_text += ',\n\t' + ',\n\t'.join(joined_fields)
    sql_text += '\nFROM \n\t(SELECT ' + ', '.join(data_fields)
    sql_text += '\n\tFROM ' + report + VIEW_SUFFIX
    sql_text += '\n\tWHERE'
    clauses = [{FIELD_KEY: 'year', COMPARISON_KEY: '>=', VALUE_KEY: start_year},
               {FIELD_KEY: 'year', COMPARISON_KEY: '<=', VALUE_KEY: end_year},
               {FIELD_KEY: 'metric_type', COMPARISON_KEY: 'LIKE', VALUE_KEY: metric_type}]
    if vendor:
        clauses.append({FIELD_KEY: 'vendor', COMPARISON_KEY: 'LIKE', VALUE_KEY: vendor})
    clauses_texts = []
    data = []
    for clause in clauses:
        clauses_texts.append(clause[FIELD_KEY] + ' ' + clause[COMPARISON_KEY] + ' ?')
        data.append(clause[VALUE_KEY])
    sql_text += '\n\t\t' + '\n\t\tAND '.join(clauses_texts)
    sql_text += ') AS ' + 'data' + ' JOIN '
    sql_text += '\n\t(SELECT ' + ', '.join(totals_fields)
    sql_text += '\n\tFROM ' + report + VIEW_SUFFIX
    sql_text += '\n\tWHERE'
    sql_text += '\n\t\t' + '\n\t\tAND '.join(clauses_texts)
    sql_text += '\n\tGROUP BY ' + ', '.join(key_fields)
    data += data
    sql_text += ') AS ' + 'totals'
    join_clauses = []
    for key_field in key_fields:
        join_clauses.append('data.' + key_field + ' = ' + 'totals.' + key_field)
    sql_text += ' ON ' + ' AND '.join(join_clauses)
    if number is not None:
        sql_text += '\nWHERE ' + RANKING + ' <= ' + '?'
        data.append(number)
    sql_text += ';'
    return sql_text, tuple(data)


def get_names_sql_text(report: str, vendor: str) -> Tuple[str, Sequence[Any]]:
    """Makes the SQL statement to get all the unique name values for a report and vendor

    :param report: the kind of the report
    :param vendor: the vendor name of the data in the file
    :returns: (sql_text, values) a Tuple with the parameterized SQL statement to search the database, and the values
        for it"""
    name_field = NAME_FIELD_SWITCHER[report[:2]]

    sql_text = 'SELECT DISTINCT ' + name_field + ' FROM ' + report \
               + ' WHERE ' + name_field + ' <> \"\" AND ' + 'vendor' + ' LIKE ?' \
               + ' ORDER BY ' + name_field + ' COLLATE NOCASE ASC;'
    return sql_text, (vendor,)


def get_costs_sql_text(report_type: str, vendor: str, year: int, name: str) -> Tuple[str, Sequence[Any]]:
    """Makes the SQL statement to get costs from the database

    :param report_type: the type of the report (master report name)
    :param vendor: the vendor name of the cost
    :param year: the year of the cost
    :param name: the name the cost is associated with (database/item/platform/title)
    :returns: (sql_text, values) a Tuple with the parameterized SQL statement to search the database, and the values
        for it"""
    name_field = NAME_FIELD_SWITCHER[report_type]
    values = []
    sql_text = 'SELECT'
    fields = [field[NAME_KEY] for field in COST_FIELDS]
    sql_text += '\n\t' + ',\n\t'.join(fields) + '\nFROM ' + report_type + COST_TABLE_SUFFIX
    sql_text += '\nWHERE '
    sql_text += '\n\t' + 'vendor' + ' = ?'
    values.append(vendor)
    sql_text += '\n\tAND ' + 'year' + ' = ?'
    values.append(year)
    sql_text += '\n\tAND ' + name_field + ' = ?;'
    values.append(name)
    return sql_text, tuple(values)


def create_connection(db_file: str) -> sqlite3.Connection:
    """Creates the connection to the database

    :param db_file: the file the database is in
    :returns: the connection to the database"""
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        # print(sqlite3.version)
        return connection
    except sqlite3.Error as error:
        print(error)
        connection.close()
    return connection


def run_sql(connection: sqlite3.Connection, sql_text: str, data: Sequence[Sequence[Any]] = None):
    """Runs the SQL statement to modify the database

    :param connection: the connection to the database
    :param sql_text: the SQL statement
    :param data: the parameters to the SQL statement"""
    try:
        cursor = connection.cursor()
        if data is not None:
            cursor.executemany(sql_text, data)
        else:
            cursor.execute(sql_text)
        connection.commit()
    except sqlite3.Error as error:
        print(error)


def run_select_sql(connection: sqlite3.Connection, sql_text: str, data: Sequence[Any] = None) \
        -> Union[Sequence[Sequence[Any]], None]:
    """Runs the SQL statement to get data from the database

    :param connection: the connection to the database
    :param sql_text: the SQL statement
    :param data: the parameters to the SQL statement
    :returns: a list of rows that return from the statement"""
    try:
        cursor = connection.cursor()
        if data is not None:
            cursor.execute(sql_text, data)
        else:
            cursor.execute(sql_text)
        return cursor.fetchall()
    except sqlite3.Error as error:
        print(error)


def setup_database(drop_tables: bool):
    """Sets up the database

    :param drop_tables: whether to drop the tables before creating them"""
    sql_texts = {}
    sql_texts.update({report: create_table_sql_texts(report) for report in ALL_REPORTS})
    sql_texts.update({report_type + COST_TABLE_SUFFIX: create_cost_table_sql_texts(report_type) for report_type in
                      REPORT_TYPE_SWITCHER.keys()})
    sql_texts.update({report + VIEW_SUFFIX: create_view_sql_texts(report) for report in ALL_REPORTS})
    for key in sql_texts:  # testing
        print(sql_texts[key])

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        for key in sql_texts:
            if drop_tables:
                print('DROP ' + key)
                run_sql(connection,
                        'DROP ' + ('VIEW' if key.endswith(VIEW_SUFFIX) else 'TABLE') + ' IF EXISTS ' + key + ';')
            print('CREATE ' + key)
            run_sql(connection, sql_texts[key])
        connection.close()
    else:
        print('Error, no connection')


def first_time_setup():
    """Sets up the folders and database when the program is set up for the first time"""
    if not os.path.exists(DATABASE_FOLDER):
        os.makedirs(DATABASE_FOLDER)
    if not os.path.exists(DATABASE_LOCATION):
        setup_database(False)
    if not os.path.exists(COSTS_SAVE_FOLDER):
        os.makedirs(COSTS_SAVE_FOLDER)


def backup_costs_data(report_type: str):
    """Backs up the data in the costs table in a file in the costs directory

    :param report_type: the type of the report (master report name)"""
    if not os.path.exists(COSTS_SAVE_FOLDER):
        os.mkdir(COSTS_SAVE_FOLDER)
    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        headers = []
        for field in get_cost_fields_list(report_type):
            headers.append(field[NAME_KEY])
        sql_text = 'SELECT ' + ', '.join(headers) + ' FROM ' + report_type + COST_TABLE_SUFFIX
        sql_text += ' ORDER BY ' + ', '.join(COSTS_KEY_FIELDS) + ', ' + NAME_FIELD_SWITCHER[report_type] + ';'
        print(sql_text)
        results = run_select_sql(connection, sql_text)
        results.insert(0, headers)
        file = open(COSTS_SAVE_FOLDER + report_type + COST_TABLE_SUFFIX + '.tsv', 'w', newline="", encoding='utf-8-sig')
        if file.mode == 'w':
            output = csv.writer(file, delimiter='\t', quotechar='\"')
            for row in results:
                output.writerow(row)
        connection.close()
    else:
        print('Error, no connection')


def test_chart_search():
    """temporary method to show how to use chart_search_sql_text"""
    headers = tuple([field[NAME_KEY] for field in get_chart_report_fields_list('DR_D1')])
    sql_text, data = chart_search_sql_text('DR_D1', 2019, 2020, '19th Century British Pamphlets', 'Searches_Automated',
                                           'EBSCO')
    print(sql_text)
    print(data)
    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        results = run_select_sql(connection, sql_text, data)
        results.insert(0, headers)
        # print(results)
        for row in results:
            print(row)


def test_top_number_chart_search():
    """temporary method to show how to use top_number_chart_search_sql_text"""
    headers = tuple([field[NAME_KEY] for field in get_top_number_chart_report_fields_list('DR_D1')])
    sql_text, data = top_number_chart_search_sql_text('DR_D1', 2017, 2020, 'Searches_Automated', 'EBSCO', 10)
    print(sql_text)
    print(data)
    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        results = run_select_sql(connection, sql_text, data)
        results.insert(0, headers)
        # print(results)
        for row in results:
            print(row)


class UpdateDatabaseProgressDialogController:
    """Controls the Update Database Progress Dialog"""

    def __init__(self, parent_widget: QObject = None):
        self.parent_widget = parent_widget
        self.update_database_progress_dialog = None

        self.update_database_thread = None

        self.database_worker = None

        self.update_status_label = None
        self.update_progress_bar = None
        self.update_task_finished_widget = None
        self.update_task_finished_scrollarea = None

        self.is_updating_database = False

    def update_database(self, files: Sequence[Dict[str, Any]], recreate_tables: bool):
        """Updates the database with the given files

        :param files: a list of files to insert into the database
        :param recreate_tables: whether or not to drop the tables and recreated the tables before inserting"""
        self.update_database_progress_dialog = QDialog(self.parent_widget)

        dialog_ui = UpdateDatabaseProgressDialog.Ui_restore_database_dialog()
        dialog_ui.setupUi(self.update_database_progress_dialog)

        self.update_status_label = dialog_ui.status_label
        self.update_progress_bar = dialog_ui.progressbar
        self.update_task_finished_scrollarea = dialog_ui.scrollarea

        self.update_task_finished_widget = QWidget()
        self.update_task_finished_widget.setLayout(QVBoxLayout())
        self.update_task_finished_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.update_task_finished_scrollarea.setWidget(self.update_task_finished_widget)

        self.update_progress_bar.setMaximum(len(files))

        self.update_database_progress_dialog.show()

        self.update_database_thread = QThread()

        self.database_worker = UpdateDatabaseWorker(files, recreate_tables)

        self.database_worker.status_changed_signal.connect(lambda status: self.on_status_changed(status))
        self.database_worker.progress_changed_signal.connect(lambda progress: self.on_progress_changed(progress))
        self.database_worker.task_finished_signal.connect(lambda task: self.on_task_finished(task))
        self.database_worker.worker_finished_signal.connect(lambda code: self.on_thread_finish(code))

        self.database_worker.moveToThread(self.update_database_thread)

        self.update_database_thread.started.connect(self.database_worker.work)

        self.update_database_thread.start()

    def on_status_changed(self, status: str):
        """Invoked when the status of the worker changes

        :param status: the new status of the worker"""
        self.update_status_label.setText(status)

    def on_progress_changed(self, progress: int):
        """Invoked when the progress of the worker changes

        :param progress: the new progress completed"""
        self.update_progress_bar.setValue(progress)

    def on_task_finished(self, task: str):
        """Invoked when the worker finishes a task

        :param task: the name of the task that was completed"""
        label = QLabel(task)
        self.update_task_finished_widget.layout().addWidget(label)

    def on_thread_finish(self, code: int):
        """Invoked when the worker's thread finishes

        :param code: the exit code of the thread"""
        print(code)  # testing
        # exit thread
        self.update_database_thread.quit()
        self.update_database_thread.wait()


class UpdateDatabaseWorker(QObject):
    """The worker that updates the database

    :param files: a list of files to insert into the database
    :param recreate_tables: whether or not to drop the tables and recreated the tables before inserting"""
    worker_finished_signal = pyqtSignal(int)
    status_changed_signal = pyqtSignal(str)
    progress_changed_signal = pyqtSignal(int)
    task_finished_signal = pyqtSignal(str)

    def __init__(self, files: Sequence[Dict[str, Any]], recreate_tables: bool):
        super().__init__()
        self.recreate_tables = recreate_tables
        self.files = files

    def work(self):
        """Performs the work of the worker"""
        current = 0
        if self.recreate_tables:
            self.status_changed_signal.emit('Recreating tables...')
            setup_database(True)
            current += 1
            self.progress_changed_signal.emit(current)
            self.task_finished_signal.emit('Recreated tables')
        else:
            self.progress_changed_signal.emit(len(self.files))
        self.status_changed_signal.emit('Filling tables...')
        for file in self.files:
            filename = os.path.basename(file['file'])
            print('READ ' + filename)
            if not filename[:-4].endswith(COST_TABLE_SUFFIX):
                insert_single_file(file['file'], file['vendor'], file['year'])
            else:
                insert_single_cost_file(file['report'], file['file'])
            self.task_finished_signal.emit(filename)
            current += 1
            self.progress_changed_signal.emit(current)
        self.status_changed_signal.emit('Done')
        self.worker_finished_signal.emit(0)


test_top_number_chart_search()
