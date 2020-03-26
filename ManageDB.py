import sqlite3
import os
import csv
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel
from VariableConstants import *
from ui import UpdateDatabaseProgressDialog


def get_report_fields_list(report):
    report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
    fields = []
    for field in report_fields:  # fields specific to this report
        if report in field['reports']:
            fields.append({'name': field['name'], 'type': field['type'], 'options': field['options']})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        fields.append({'name': field['name'], 'type': field['type'], 'options': field['options']})
    return fields


def get_view_report_fields_list(report):
    report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
    fields = []
    for field in report_fields:  # fields specific to this report
        if report in field['reports']:
            fields.append({'name': field['name'], 'type': field['type'], 'options': field['options'], 'source': report})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        if field['name'] not in FIELDS_NOT_IN_VIEWS:
            fields.append({'name': field['name'], 'type': field['type'], 'options': field['options'], 'source': report})
    for field in COST_FIELDS:  # cost table fields
        fields.append({'name': field['name'], 'type': field['type'], 'options': field['options'],
                       'source': report[:2] + COST_TABLE_SUFFIX})
    fields.append({'name': YEAR_TOTAL, 'type': 'INTEGER', 'calculation': 'SUM(' + 'metric' + ')'})
    for key in sorted(MONTHS):  # month columns
        fields.append({'name': MONTHS[key], 'type': 'INTEGER',
                       'calculation': 'COALESCE(SUM(CASE ' + 'month' + ' WHEN ' + str(
                           key) + ' THEN ' + 'metric' + ' END), 0)'})
    return fields


def get_chart_report_fields_list(report):
    fields = []
    name_field = get_field_attributes(report, NAME_FIELD_SWITCHER[report[:2]])
    fields.append({'name': name_field['name'], 'type': name_field['type'], 'options': name_field['options']})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        if field['name'] not in FIELDS_NOT_IN_VIEWS:
            fields.append({'name': field['name'], 'type': field['type'], 'options': field['options']})
    for field in COST_FIELDS:  # cost table fields
        if field['name'] in COST_FIELDS_IN_CHARTS:
            fields.append({'name': field['name'], 'type': field['type'], 'options': field['options']})
    for key in sorted(MONTHS):  # month columns
        fields.append({'name': MONTHS[key], 'type': 'INTEGER',
                       'calculation': 'COALESCE(SUM(CASE ' + 'month' + ' WHEN ' + str(
                           key) + ' THEN ' + 'metric' + ' END), 0)'})
    return fields


def get_top_number_chart_report_fields_list(report):
    fields = []
    name_field = get_field_attributes(report, NAME_FIELD_SWITCHER[report[:2]])
    fields.append({'name': name_field['name'], 'type': name_field['type'], 'options': name_field['options'],
                   'source': report})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        if field['name'] not in FIELDS_NOT_IN_TOP_NUMBER_CHARTS:
            fields.append({'name': field['name'], 'type': field['type'], 'options': field['options'], 'source': report})
    for field in COST_FIELDS:  # cost table fields
        if field['name'] in COST_FIELDS_IN_CHARTS:
            fields.append({'name': field['name'], 'type': field['type'], 'options': field['options'],
                           'source': report[:2] + COST_TABLE_SUFFIX})
    fields.append({'name': RANKING, 'type': 'INTEGER', 'calculation': 'RANK() OVER(ORDER BY ' + 'metric' + ' DESC)'})
    return fields


def get_cost_fields_list(report):
    fields = []
    name_field = get_field_attributes(report, NAME_FIELD_SWITCHER[report[:2]])
    fields.append({'name': name_field['name'], 'type': name_field['type'], 'options': name_field['options']})
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        if field['name'] in COSTS_KEY_FIELDS:
            fields.append({'name': field['name'], 'type': field['type'], 'options': field['options']})
    for field in COST_FIELDS:
        fields.append({'name': field['name'], 'type': field['type'], 'options': field['options']})
    return fields


def get_field_attributes(report, field_name):
    report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
    for field in report_fields:
        if field['name'] == field_name:
            return {'name': field['name'], 'type': field['type'], 'options': field['options']}
    for field in ALL_REPORT_FIELDS:
        if field['name'] == field_name:
            return {'name': field['name'], 'type': field['type'], 'options': field['options']}
    for field in COST_FIELDS:
        if field['name'] == field_name:
            return {'name': field['name'], 'type': field['type'], 'options': field['options']}
    return None


def create_table_sql_texts(reports):  # makes the SQL statements to create the tables from the table definition
    sql_texts = {}
    for report in reports:
        sql_text = 'CREATE TABLE IF NOT EXISTS ' + report + '('
        report_fields = get_report_fields_list(report)
        fields_and_options = []
        key_fields = []
        for field in report_fields:  # fields specific to this report
            field_text = field['name'] + ' ' + field['type']
            if field['options']:
                field_text += ' ' + ' '.join(field['options'])
            fields_and_options.append(field_text)
            if field['name'] not in FIELDS_NOT_IN_KEYS:
                key_fields.append(field['name'])
        sql_text += '\n\t' + ', \n\t'.join(fields_and_options) + ',\n\tPRIMARY KEY(' + ', '.join(key_fields) + '));'
        sql_texts[report] = sql_text
    return sql_texts


def create_view_sql_texts(reports):  # makes the SQL statements to create the views from the table definition
    sql_texts = {}
    for report in reports:
        name_field = get_field_attributes(report[:2], NAME_FIELD_SWITCHER[report[:2]])
        sql_text = 'CREATE VIEW IF NOT EXISTS ' + report + VIEW_SUFFIX + ' AS SELECT'
        report_fields = get_view_report_fields_list(report)
        fields = []
        calcs = []
        key_fields = []
        for field in report_fields:  # fields specific to this report
            if 'calculation' not in field.keys():
                field_text = ''
                if field['name'] in COSTS_KEY_FIELDS or field['name'] == name_field['name']:
                    key_fields.append(field['name'])
                    field_text = report + '.'
                field_text += field['name']
                fields.append(field_text)
            else:
                calcs.append(field['calculation'] + ' AS ' + field['name'])
        sql_text += '\n\t' + ', \n\t'.join(fields) + ', \n\t' + ', \n\t'.join(calcs)
        sql_text += '\nFROM ' + report + ' LEFT JOIN ' + report[:2] + COST_TABLE_SUFFIX
        join_clauses = []
        for key_field in key_fields:
            join_clauses.append(report + '.' + key_field + ' = ' + report[:2] + COST_TABLE_SUFFIX + '.' + key_field)
        sql_text += ' ON ' + ' AND '.join(join_clauses)
        sql_text += '\nGROUP BY ' + ', '.join(fields) + ';'
        sql_texts[report + VIEW_SUFFIX] = sql_text
    return sql_texts


def create_cost_table_sql_texts(report_types):
    sql_texts = {}
    for report_type in report_types:
        sql_text = 'CREATE TABLE IF NOT EXISTS ' + report_type + COST_TABLE_SUFFIX + '('
        report_fields = get_cost_fields_list(report_type)
        name_field = get_field_attributes(report_type, NAME_FIELD_SWITCHER[report_type])
        fields_and_options = []
        key_fields = []
        for field in report_fields:
            field_text = field['name'] + ' ' + field['type']
            if field['options']:
                field_text += ' ' + ' '.join(field['options'])
            fields_and_options.append(field_text)
            if field['name'] in COSTS_KEY_FIELDS or field['name'] == name_field['name']:
                key_fields.append(field['name'])
        sql_text += '\n\t' + ', \n\t'.join(fields_and_options)
        sql_text += ',\n\tPRIMARY KEY(' + ', '.join(key_fields) + '));'
        sql_texts[report_type + COST_TABLE_SUFFIX] = sql_text
    return sql_texts


def replace_sql_text(file_name, report, data):  # makes the sql statement to 'replace or insert' data into a table
    sql_replace_text = 'REPLACE INTO ' + report + '('
    report_fields = get_report_fields_list(report)
    fields = []
    for field in report_fields:  # fields specific to this report
        fields.append(field['name'])
    sql_replace_text += ', '.join(fields) + ')'
    sql_replace_text += '\nVALUES'
    placeholders = ['?'] * len(fields)
    sql_replace_text += '(' + ', '.join(placeholders) + ');'
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
    sql_delete_text = 'DELETE FROM ' + report + ' WHERE ' + 'file' + ' = \"' + file_name + '\";'
    return {'sql_delete': sql_delete_text, 'sql_replace': sql_replace_text, 'data': values}


def update_vendor_name_sql_text(table, old_name, new_name):
    sql_text = 'UPDATE ' + table + ' SET'
    sql_text += '\n\t' + 'vendor' + ' = \"' + new_name + '\"'
    if not table.endswith(COST_TABLE_SUFFIX):
        sql_text += ',\n\t' + 'file' + ' = ' + 'REPLACE(' + 'file' + ', ' + '\"_' + old_name + '_\"'
        sql_text += ', ' + '\"_' + new_name + '_\")'
    sql_text += '\nWHERE ' + 'vendor' + ' = \"' + old_name + '\";'
    return sql_text


def update_vendor_in_all_tables(old_name, new_name):
    sql_texts = []
    for table in ALL_REPORTS:
        sql_texts.append(update_vendor_name_sql_text(table, old_name, new_name))
    for cost_table in REPORT_TYPE_SWITCHER.keys():
        sql_texts.append(update_vendor_name_sql_text(cost_table + COST_TABLE_SUFFIX, old_name, new_name))

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        for sql_text in sql_texts:
            run_sql(connection, sql_text)
        connection.close()
    else:
        print('Error, no connection')


def replace_costs_sql_text(report_type, data):  # makes the sql statement to 'replace or insert' data into a cost table
    sql_replace_text = 'REPLACE INTO ' + report_type + COST_TABLE_SUFFIX + '('
    report_fields = get_cost_fields_list(report_type)
    fields = []
    for field in report_fields:  # fields specific to this report
        fields.append(field['name'])
    sql_replace_text += ', '.join(fields) + ')'
    sql_replace_text += '\nVALUES'
    placeholders = ['?'] * len(fields)
    sql_replace_text += '(' + ', '.join(placeholders) + ');'
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
    return {'sql_text': sql_replace_text, 'data': values}  # sql_delete is not used


def delete_costs_sql_text(report_type, vendor, year, name):  # makes the sql statement to delete data from a cost table
    name_field = NAME_FIELD_SWITCHER[report_type]
    sql_text = 'DELETE FROM ' + report_type + COST_TABLE_SUFFIX
    sql_text += '\nWHERE '
    sql_text += '\n\t' + 'vendor' + ' = \"' + vendor + '\"'
    sql_text += '\n\tAND ' + 'year' + ' = ' + str(year)
    sql_text += '\n\tAND ' + name_field + ' = \"' + name + '\";'
    return {'sql_text': sql_text, 'data': None}  # sql_replace and data are not used


def read_report_file(file_name, vendor,
                     year):  # reads a specific csv/tsv file and returns the report type and the values for inserting
    delimiter = DELIMITERS[file_name[-4:].lower()]
    file = open(file_name, 'r', encoding='utf-8-sig')
    reader = csv.reader(file, delimiter=delimiter, quotechar='\"')
    results = {}
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
        results['file'] = os.path.basename(file.name)
        results['report'] = header['report_id']
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
        results['values'] = values
        return results
    else:
        print('Error: could not open file ' + file_name)
        return None


def read_costs_file(report_type, file_name):
    delimiter = DELIMITERS[file_name[-4:].lower()]
    file = open(file_name, 'r', encoding='utf-8-sig')
    reader = csv.reader(file, delimiter=delimiter, quotechar='\"')
    results = {'report': report_type}
    if file.mode == 'r':
        column_headers = next(reader)
        column_headers = list(map((lambda column_header: column_header.lower()), column_headers))
        values = []
        for cells in list(reader):
            value = {}
            for i in range(len(cells)):  # read columns
                value[column_headers[i]] = cells[i]
            values.append(value)
        results['values'] = values
        return results
    else:
        print('Error: could not open file ' + file_name)
        return None


def get_all_reports():
    # TODO (Chandler): make safer; only look for vendors in the vendor list
    reports = []
    for upper_directory in os.scandir(FILE_LOCATION):  # iterate over all files in FILE_LOCATION
        if upper_directory.is_dir():
            for lower_directory in os.scandir(upper_directory):
                if lower_directory.is_dir():
                    directory_data = {FILE_SUBDIRECTORY_ORDER[0]: upper_directory.name,
                                      FILE_SUBDIRECTORY_ORDER[1]: lower_directory.name}  # get data from directory names
                    for file in os.scandir(lower_directory):
                        if file.name[-4:] in DELIMITERS:
                            reports.append({'file': file.path, 'vendor': directory_data['vendor'],
                                            'year': directory_data['year']})
    return reports


def get_all_cost_files():
    files = []
    for file in os.scandir(COSTS_SAVE_FOLDER):
        if file.name[-4:] in DELIMITERS:
            files.append({'file': file.path, 'report': file.name[:2]})
    return files


def insert_single_file(file_path, vendor, year):
    data = read_report_file(file_path, vendor, year)
    replace = replace_sql_text(data['file'], data['report'], data['values'])

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        run_sql(connection, replace['sql_delete'])
        run_sql(connection, replace['sql_replace'], replace['data'])
        connection.close()
    else:
        print('Error, no connection')


def insert_single_cost_file(report_type, file_path):
    data = read_costs_file(report_type, file_path)
    replace = replace_costs_sql_text(data['report'], data['values'])

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        run_sql(connection, replace['sql_text'], replace['data'])
        connection.close()
    else:
        print('Error, no connection')


def search_sql_text(report, start_year, end_year,
                    search_parameters):  # makes the sql statement to search the database; search_parameters in POS form
    sql_text = 'SELECT * FROM ' + report + VIEW_SUFFIX
    sql_text += '\nWHERE'
    clauses = [[{'field': 'year', 'comparison': '>=', 'value': start_year}],
               [{'field': 'year', 'comparison': '<=', 'value': end_year}]]
    clauses.extend(search_parameters)
    print(clauses)
    clauses_texts = []
    data = []
    for clause in clauses:
        sub_clauses_text = []
        for sub_clause in clause:
            current_text = sub_clause['field'] + ' ' + sub_clause['comparison']
            if sub_clause['comparison'] not in NON_COMPARISONS:
                current_text += ' ?'
                data.append(sub_clause['value'])
            sub_clauses_text.append(current_text)
        clauses_texts.append('(' + ' OR '.join(sub_clauses_text) + ')')
    sql_text += '\n\t' + '\n\tAND '.join(clauses_texts)
    sql_text += ';'
    return {'sql_text': sql_text, 'data': data}


def chart_search_sql_text(report, start_year, end_year,
                          name, metric_type):  # makes the sql statement to search the database for chart data
    sql_text = 'SELECT'
    chart_fields = get_chart_report_fields_list(report)
    fields = []
    for field in chart_fields:
        fields.append(field['name'])
    sql_text += '\n\t' + ', '.join(fields)
    sql_text += '\nFROM ' + report + VIEW_SUFFIX
    sql_text += '\nWHERE'
    clauses = [{'field': 'year', 'comparison': '>=', 'value': start_year},
               {'field': 'year', 'comparison': '<=', 'value': end_year},
               {'field': chart_fields[0]['name'], 'comparison': 'LIKE', 'value': name},
               {'field': 'metric_type', 'comparison': 'LIKE', 'value': metric_type}]
    clauses_texts = []
    data = []
    for clause in clauses:
        clauses_texts.append(clause['field'] + ' ' + clause['comparison'] + ' ?')
        data.append(clause['value'])
    sql_text += '\n\t' + '\n\tAND '.join(clauses_texts)
    sql_text += ';'
    return {'sql_text': sql_text, 'data': data}


def chart_top_number_search_sql_text(report, start_year, end_year, name, metric_type,
                                     number):  # makes the sql statement to search the database for chart data
    name_field = get_field_attributes(report[:2], NAME_FIELD_SWITCHER[report[:2]])
    sql_text = 'SELECT * FROM ('
    sql_text += '\nSELECT'
    chart_fields = get_top_number_chart_report_fields_list(report)
    fields = []
    calcs = []
    key_fields = []
    for field in chart_fields:  # fields specific to this report
        if 'calculation' not in field.keys():
            field_text = ''
            if field['name'] in COSTS_KEY_FIELDS or field['name'] == name_field['name']:
                key_fields.append(field['name'])
                field_text = report + '.'
            field_text += field['name']
            fields.append(field_text)
        else:
            calcs.append(field['calculation'] + ' AS ' + field['name'])
    sql_text += '\n\t' + ', \n\t'.join(fields) + ', \n\t' + ', \n\t'.join(calcs)
    sql_text += '\nFROM ' + report + ' LEFT JOIN ' + report[:2] + COST_TABLE_SUFFIX
    join_clauses = []
    for key_field in key_fields:
        join_clauses.append(report + '.' + key_field + ' = ' + report[:2] + COST_TABLE_SUFFIX + '.' + key_field)
    sql_text += ' ON ' + ' AND '.join(join_clauses)
    sql_text += '\nWHERE'
    clauses = [{'field': report + '.' + 'year', 'comparison': '>=', 'value': start_year},
               {'field': report + '.' + 'year', 'comparison': '<=', 'value': end_year},
               {'field': report + '.' + name_field['name'], 'comparison': 'LIKE', 'value': name},
               {'field': 'metric_type', 'comparison': 'LIKE', 'value': metric_type}]
    clauses_texts = []
    data = []
    for clause in clauses:
        clauses_texts.append(clause['field'] + ' ' + clause['comparison'] + ' ?')
        data.append(clause['value'])
    sql_text += '\n\t' + '\n\tAND '.join(clauses_texts)
    sql_text += ')'
    sql_text += '\nWHERE ' + RANKING + ' <= ' + '?;'
    data.append(number)
    return {'sql_text': sql_text, 'data': data}


def get_names_sql_text(report_type, vendor):
    name_field = NAME_FIELD_SWITCHER[report_type]

    sql_text = 'SELECT DISTINCT ' + name_field + ' FROM ' + report_type \
               + ' WHERE ' + name_field + ' <> \"\" AND ' + 'vendor' + ' LIKE \"' + vendor + '\"' \
               + ' ORDER BY ' + name_field + ' COLLATE NOCASE ASC;'
    return sql_text


def get_costs_sql_text(report_type, vendor, year, name):
    name_field = NAME_FIELD_SWITCHER[report_type]
    sql_text = 'SELECT'
    fields = []
    for field in COST_FIELDS:
        fields.append(field['name'])
    sql_text += '\n\t' + ',\n\t'.join(fields) + '\nFROM ' + report_type + COST_TABLE_SUFFIX
    sql_text += '\nWHERE '
    sql_text += '\n\t' + 'vendor' + ' = \"' + vendor + '\"'
    sql_text += '\n\tAND ' + 'year' + ' = ' + str(year)
    sql_text += '\n\tAND ' + name_field + ' = \"' + name + '\";'
    return sql_text


def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        # print(sqlite3.version)
        return connection
    except sqlite3.Error as error:
        print(error)
        connection.close()
    return connection


def run_sql(connection, sql_text, data=None):
    try:
        cursor = connection.cursor()
        if data is not None:
            cursor.executemany(sql_text, data)
        else:
            cursor.execute(sql_text)
        connection.commit()
    except sqlite3.Error as error:
        print(error)


def run_select_sql(connection, sql_text, data=None):
    try:
        cursor = connection.cursor()
        if data is not None:
            cursor.execute(sql_text, data)
        else:
            cursor.execute(sql_text)
        return cursor.fetchall()
    except sqlite3.Error as error:
        print(error)
        return None


def setup_database(drop_tables):
    sql_texts = {}
    sql_texts.update(create_table_sql_texts(ALL_REPORTS))
    sql_texts.update(create_cost_table_sql_texts(REPORT_TYPE_SWITCHER.keys()))
    sql_texts.update(create_view_sql_texts(ALL_REPORTS))
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
    if not os.path.exists(DATABASE_FOLDER):
        os.makedirs(DATABASE_FOLDER)
    if not os.path.exists(DATABASE_LOCATION):
        setup_database(False)
    if not os.path.exists(COSTS_SAVE_FOLDER):
        os.makedirs(COSTS_SAVE_FOLDER)


def backup_costs_data(report_type):
    if not os.path.exists(COSTS_SAVE_FOLDER):
        os.mkdir(COSTS_SAVE_FOLDER)
    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        headers = []
        for field in get_cost_fields_list(report_type):
            headers.append(field['name'])
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
    headers = []
    for field in get_chart_report_fields_list('DR_D1'):
        headers.append(field['name'])
    search = chart_search_sql_text('DR_D1', 2019, 2020, '19th Century British Pamphlets',
                                   'Searches_Automated')  # changed
    print(search['sql_text'])  # changed
    print(search['data'])  # changed
    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        results = run_select_sql(connection, search['sql_text'], search['data'])  # changed
        results.insert(0, headers)
        print(results)


def test_top_number_chart_search():
    headers = []
    for field in get_top_number_chart_report_fields_list('DR_D1'):
        headers.append(field['name'])
    print(get_chart_report_fields_list('DR_D1'))
    search = chart_top_number_search_sql_text('DR_D1', 2017, 2020, '19th Century British Pamphlets',
                                              'Searches_Automated', 10)
    print(search['sql_text'])
    print(search['data'])
    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        results = run_select_sql(connection, search['sql_text'], search['data'])  # changed
        results.insert(0, headers)
        # print(results)
        for row in results:
            print(row)


class UpdateDatabaseProgressDialogController:

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

    def update_database(self, files, recreate_tables):
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
        self.update_status_label.setText(status)

    def on_progress_changed(self, progress: int):
        self.update_progress_bar.setValue(progress)

    def on_task_finished(self, task: str):
        label = QLabel(task)
        self.update_task_finished_widget.layout().addWidget(label)

    def on_thread_finish(self, code):
        print(code)  # testing
        # exit thread
        self.update_database_thread.quit()
        self.update_database_thread.wait()


class UpdateDatabaseWorker(QObject):
    worker_finished_signal = pyqtSignal(int)
    status_changed_signal = pyqtSignal(str)
    progress_changed_signal = pyqtSignal(int)
    task_finished_signal = pyqtSignal(str)

    def __init__(self, files, recreate_tables):
        super().__init__()
        self.recreate_tables = recreate_tables
        self.files = files

    def work(self):
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
