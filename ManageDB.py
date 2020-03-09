import sqlite3
import os
import csv

# database report definitions
DATABASE_REPORTS = ('DR', 'DR_D1', 'DR_D2')
DATABASE_REPORT_FIELDS = ({'name': 'database',
                           'type': 'TEXT',
                           'options': ('NOT NULL', 'CHECK(database <> \"\")'),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'publisher',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'publisher_id',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'platform',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'proprietary_id',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'data_type',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR',)},
                          {'name': 'access_method',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR',)})

# item report definitions
ITEM_REPORTS = ('IR', 'IR_A1', 'IR_M1')
ITEM_REPORT_FIELDS = ({'name': 'item',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'publisher',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'publisher_id',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'platform',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'authors',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'publication_date',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'doi',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'proprietary_id',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'isbn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'print_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'online_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'uri',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'parent_title',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_authors',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_publication_date',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'parent_article_version',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_data_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'parent_doi',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_proprietary_id',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_isbn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'parent_print_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_online_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_uri',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'component_title',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_authors',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_publication_date',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_data_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_doi',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_proprietary_id',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_isbn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_print_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_online_issn',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'component_uri',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'data_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'yop',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)},
                      {'name': 'access_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'access_method',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR',)})

# platform report definitions
PLATFORM_REPORTS = ('PR', 'PR_P1')
PLATFORM_REPORT_FIELDS = ({'name': 'platform',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('PR', 'PR_P1')},
                          {'name': 'data_type',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('PR',)},
                          {'name': 'access_type',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('PR',)})

# title report definitions
TITLE_REPORTS = ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')
TITLE_REPORT_FIELDS = ({'name': 'title',
                        'type': 'TEXT',
                        'options': ('NOT NULL', 'CHECK(title <> \"\")'),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'publisher',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'publisher_id',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'platform',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'doi',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'proprietary_id',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'isbn',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3')},
                       {'name': 'print_issn',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'online_issn',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'uri',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'data_type',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR',)},
                       {'name': 'section_type',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR',)},
                       {'name': 'yop',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J4')},
                       {'name': 'access_type',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B3', 'TR_J3')},
                       {'name': 'access_method',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR',)})

# fields that all reports have
ALL_REPORT_FIELDS = ({'name': 'metric_type',
                      'type': 'TEXT',
                      'options': ('NOT NULL', 'CHECK(metric_type <> \"\")')},
                     {'name': 'vendor',
                      'type': 'TEXT',
                      'options': ('NOT NULL', 'CHECK(vendor <> \"\")')},
                     {'name': 'year',
                      'type': 'INTEGER',
                      'options': ('NOT NULL', 'CHECK(LENGTH(year) = 4)')},
                     {'name': 'month',
                      'type': 'INTEGER',
                      'options': ('NOT NULL', 'CHECK(month BETWEEN 1 AND 12)')},
                     {'name': 'metric',
                      'type': 'INTEGER',
                      'options': ('NOT NULL', 'CHECK(metric > 0)')},
                     {'name': 'updated_on',
                      'type': 'TEXT',
                      'options': ('NOT NULL',)},
                     {'name': 'file',
                      'type': 'TEXT',
                      'options': ('NOT NULL',)})

# cost table fields
COST_FIELDS = ({'name': 'cost_in_original_currency',
                'type': 'REAL',
                'options': ('NOT NULL', 'CHECK(cost_in_original_currency >= 0)')},
               {'name': 'original_currency',
                'type': 'TEXT',
                'options': ('NOT NULL', 'CHECK(original_currency <> \"\")')},
               {'name': 'cost_in_local_currency',
                'type': 'REAL',
                'options': ('NOT NULL', 'CHECK(cost_in_local_currency >= 0)')},
               {'name': 'cost_in_local_currency_with_tax',
                'type': 'REAL',
                'options': ('NOT NULL', 'CHECK(cost_in_local_currency_with_tax >= 0)')})

ALL_REPORTS = DATABASE_REPORTS + ITEM_REPORTS + PLATFORM_REPORTS + TITLE_REPORTS
REPORT_TYPE_SWITCHER = {'DR': {'reports': DATABASE_REPORTS, 'report_fields': DATABASE_REPORT_FIELDS},
                        'IR': {'reports': ITEM_REPORTS, 'report_fields': ITEM_REPORT_FIELDS},
                        'PR': {'reports': PLATFORM_REPORTS, 'report_fields': PLATFORM_REPORT_FIELDS},
                        'TR': {'reports': TITLE_REPORTS, 'report_fields': TITLE_REPORT_FIELDS}}
NAME_FIELD_SWITCHER = {'DR': 'database', 'IR': 'item', 'PR': 'platform', 'TR': 'title'}

MONTHS = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june',
          7: 'july', 8: 'august', 9: 'september', 10: 'october', 11: 'november', 12: 'december'}

YEAR_TOTAL = 'reporting_period_total'

VIEW_SUFFIX = '_view'
COST_TABLE_SUFFIX = '_costs'

FIELDS_NOT_IN_VIEWS = ('month', 'metric', 'updated_on')
FIELDS_NOT_IN_KEYS = ('metric', 'updated_on')
FIELDS_NOT_IN_SEARCH = ('year',)

COSTS_KEY_FIELDS = ('vendor', 'year')

DATABASE_FOLDER = r'./all_data/search/'
DATABASE_LOCATION = DATABASE_FOLDER + r'search.db'
FILE_LOCATION = r'./all_data/DO_NOT_MODIFY/'
FILE_SUBDIRECTORY_ORDER = ('year', 'vendor')

HEADER_ROWS = 12
BLANK_ROWS = 1
DELIMITERS = {'.tsv': '\t', '.csv': ','}


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
    for key in sorted(MONTHS):  # month columns
        fields.append({'name': MONTHS[key], 'type': 'INTEGER',
                       'calculation': 'COALESCE(SUM(CASE ' + 'month' + ' WHEN ' + str(
                           key) + ' THEN ' + 'metric' + ' END), 0)'})
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
    types = {}
    for field in report_fields:  # fields specific to this report
        fields.append(field['name'])
        types[field['name']] = field['type']
    sql_replace_text += ', '.join(fields) + ')'
    sql_replace_text += '\nVALUES'
    placeholders = []
    for key in fields:  # gets parameter slots
        placeholders.append('?')
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


def replace_cost_sql_text(report, data):
    sql_replace_text = 'REPLACE INTO ' + report + COST_TABLE_SUFFIX + '('
    report_fields = get_cost_fields_list(report)
    fields = []
    types = {}
    for field in report_fields:  # fields specific to this report
        fields.append(field['name'])
        types[field['name']] = field['type']
    sql_replace_text += ', '.join(fields) + ')'
    sql_replace_text += '\nVALUES'
    placeholders = []
    for key in fields:  # gets parameter slots
        placeholders.append('?')
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
    return {'sql_replace': sql_replace_text, 'data': values}


def read_report_file(file_name, vendor,
                     year):  # reads a specific csv/tsv file and returns the report type and the values for inserting
    delimiter = DELIMITERS[file_name[-4:].lower()]
    file = open(file_name, 'r', encoding='utf-8')
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
                        for i in range(last_column):  # read rows before months
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


def get_all_reports():
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


def insert_single_file(file_path, vendor, year):
    data = read_report_file(file_path, vendor, year)
    replace = replace_sql_text(data['file'], data['report'], data['values'])

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        run_insert_sql(connection, replace['sql_delete'], replace['sql_replace'], replace['data'])
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
    for clause in clauses:
        sub_clauses_text = []
        for sub_clause in clause:
            sub_clauses_text.append(
                sub_clause['field'] + ' ' + sub_clause['comparison'] + ' \'' + str(sub_clause['value']) + '\'')
            # TODO make parameterized query
        clauses_texts.append('(' + ' OR '.join(sub_clauses_text) + ')')
    sql_text += '\n\t' + '\n\tAND '.join(clauses_texts)
    sql_text += ';'
    return sql_text


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
    print(clauses)
    clauses_texts = []
    for clause in clauses:
        clauses_texts.append(clause['field'] + ' ' + clause['comparison'] + ' \'' + str(clause['value']) + '\'')
        # TODO make parameterized query
    sql_text += '\n\t' + '\n\tAND '.join(clauses_texts)
    sql_text += ';'
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


def run_sql(connection, sql_text):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_text)
    except sqlite3.Error as error:
        print(error)


def run_insert_sql(connection, sql_delete_text, sql_insert_text, data):
    try:
        cursor = connection.cursor()
        if sql_delete_text:
            cursor.execute(sql_delete_text)
        cursor.executemany(sql_insert_text, data)
        connection.commit()
    except sqlite3.Error as error:
        print(error)


def run_select_sql(connection, sql_text):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_text)
        return cursor.fetchall()
    except sqlite3.Error as error:
        print(error)
        return None


def setup_database(drop_tables):
    if not os.path.exists(DATABASE_FOLDER):
        os.mkdir(DATABASE_FOLDER)
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


def test_chart_search():
    headers = []
    for field in get_chart_report_fields_list('DR_D1'):
        headers.append(field['name'])
    sql_text = chart_search_sql_text('DR_D1', 2019, 2020, '19th Century British Pamphlets', 'Searches_Automated')
    print(sql_text)
    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        results = run_select_sql(connection, sql_text)
        results.insert(0, headers)
        print(results)
