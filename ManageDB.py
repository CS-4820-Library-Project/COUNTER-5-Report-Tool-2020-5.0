# database report definitions
DATABASE_REPORTS = ('DR', 'DR_D1', 'DR_D2')
DATABASE_REPORT_FIELDS = ({'name': 'database',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
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
                           'reports': ('DR',)},
                          {'name': 'metric_type',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')})

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
                       'reports': ('IR',)},
                      {'name': 'metric_type',
                       'type': 'TEXT',
                       'options': ('NOT NULL',),
                       'reports': ('IR', 'IR_A1', 'IR_M1')})

# title report definitions
TITLE_REPORTS = ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')
TITLE_REPORT_FIELDS = ({'name': 'title',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
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
                        'reports': ('TR',)},
                       {'name': 'metric_type',
                        'type': 'TEXT',
                        'options': ('NOT NULL',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')})

# fields that all reports have
ALL_REPORT_FIELDS = ({'name': 'vendor',
                      'type': 'TEXT',
                      'options': ('NOT NULL',)},
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
                      'options': ('NOT NULL',)})

REPORT_TYPE_SWITCHER = {'DR': {'reports': DATABASE_REPORTS, 'report_fields': DATABASE_REPORT_FIELDS},
                        'IR': {'reports': ITEM_REPORTS, 'report_fields': ITEM_REPORT_FIELDS},
                        'TR': {'reports': TITLE_REPORTS, 'report_fields': TITLE_REPORT_FIELDS}}

MONTHS = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june',
          7: 'july', 8: 'august', 9: 'september', 10: 'october', 11: 'november', 12: 'december'}

YEAR_TOTAL = 'reporting_period_total'

VIEW_SUFFIX = '_view'

FIELDS_NOT_IN_VIEWS = ('month', 'metric', 'updated_on')
FIELDS_NOT_IN_KEYS = ('metric', 'updated_on')

DATABASE_LOCATION = r'./all_data/search/search.db'
FILE_LOCATION = './all_data/normal_tsv_files/'

HEADER_ROWS = 12
BLANK_ROWS = 1
DELIMITERS = {'tsv': '\t', 'csv': ','}


def create_table_sql_texts(reports):  # makes the SQL statements to create the tables from the table definition
    sql_texts = {}
    for report in reports:
        sql_text = 'CREATE TABLE IF NOT EXISTS ' + report + '('
        report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
        fields_and_options = []
        key_fields = []
        for field in report_fields:  # fields specific to this report
            if report in field['reports']:
                field_text = field['name'] + ' ' + field['type']
                if field['options']:
                    field_text += ' ' + ' '.join(field['options'])
                fields_and_options.append(field_text)
                key_fields.append(field['name'])
        for field in ALL_REPORT_FIELDS:  # fields in all reports
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
        sql_text = 'CREATE VIEW IF NOT EXISTS ' + report + VIEW_SUFFIX + ' AS SELECT'
        report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
        fields = []
        for field in report_fields:  # fields specific to this report
            if report in field['reports']:
                fields.append(field['name'])
        for field in ALL_REPORT_FIELDS:  # fields in all reports
            if field['name'] not in FIELDS_NOT_IN_VIEWS:
                fields.append(field['name'])
        calcs = []
        for key in sorted(MONTHS):  # month columns
            calc_text = 'COALESCE(SUM(CASE ' + 'month' + ' WHEN ' + str(key)
            calc_text += ' THEN ' + 'metric' + ' END), 0) AS ' + MONTHS[key]
            calcs.append(calc_text)
        calcs.append('SUM(' + 'metric' + ') AS ' + YEAR_TOTAL)  # year total column
        sql_text += '\n\t' + ', \n\t'.join(fields) + ', \n\t' + ', \n\t'.join(calcs)
        sql_text += '\nFROM ' + report
        sql_text += '\nGROUP BY ' + ', '.join(fields) + ';'
        sql_texts[report + VIEW_SUFFIX] = sql_text
    return sql_texts


def replace_sql_text(report, data):  # makes the sql statement to 'replace or insert' data into a table
    sql_text = 'REPLACE INTO ' + report + '('
    report_fields = REPORT_TYPE_SWITCHER[report[:2]]['report_fields']
    fields = []
    types = {}
    for field in report_fields:  # fields specific to this report
        if report in field['reports']:
            fields.append(field['name'])
            types[field['name']] = field['type']
    for field in ALL_REPORT_FIELDS:  # fields in all reports
        fields.append(field['name'])
        types[field['name']] = field['type']
    sql_text += ', '.join(fields) + ')'
    sql_text += '\nVALUES'
    values_texts = []
    for row in data:
        values = []
        for key in fields:
            value = None
            if row.get(key):
                if types[key] == 'TEXT':
                    value = '\"' + row.get(key) + '\"'
                else:
                    value = str(row.get(key))
            else:
                value = '\"\"'
            values.append(value)
        values_texts.append('(' + ', '.join(values) + ')')
    sql_text += '\n\t' + ', \n\t'.join(values_texts)
    sql_text += ';'
    return sql_text


def read_report_file(file_name,
                     vendor):  # reads a specific csv/tsv file and returns the report type and the values for inserting
    delimiter = DELIMITERS[file_name[-3:]]
    file = open(file_name, 'r', encoding='utf-8')
    results = {}
    if file.mode == 'r':
        lines = file.readlines()
        header = {}
        for line in lines[:HEADER_ROWS - 1]:  # reads header row data
            cells = line.strip().split(delimiter)
            key = cells[0].strip().lower()
            if len(cells) > 1:
                header[key] = cells[1].strip()
            else:
                header[key] = None
        print(header)
        results['report'] = header['report_id']
        column_headers = lines[HEADER_ROWS + BLANK_ROWS].strip().lower().split(delimiter)
        values = []
        for line in lines[HEADER_ROWS + BLANK_ROWS + 1:]:
            cells = line.strip().split(delimiter)
            month = 1
            for column in range(len(MONTHS)):  # makes value from each month with metric > 0 for each row
                current_column = len(column_headers) - len(MONTHS) + month - 1
                metric = int(cells[current_column])
                if metric > 0:
                    value = {}
                    for i in range(len(column_headers) - len(MONTHS) - 1):  # read rows before months
                        value[column_headers[i]] = cells[i]
                    if not value['metric_type']:  # if no metric type column, use the metric type from header
                        value['metric_type'] = header['metric_types']
                    current_header = column_headers[current_column]
                    # additional fields
                    value['year'] = int(current_header[-4:])
                    value['month'] = month
                    value['metric'] = int(cells[current_column])
                    value['vendor'] = vendor
                    value['updated_on'] = header['created']
                    values.append(value)
                month += 1
        results['values'] = values
        return results
    else:
        print('Error: could not open file ' + file_name)
        return None


def search_sql_text(report, start_year, end_year, search_parameters):  # makes the sql statement to search the database; search_parameters in POS form
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
        clauses_texts.append('(' + ' OR '.join(sub_clauses_text) + ')')
    sql_text += '\n\t' + '\n\tAND '.join(clauses_texts)
    sql_text += ';'
    return sql_text


import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print(sqlite3.version)
        return connection
    except Error as error:
        print(error)
        connection.close()
    return connection


def run_sql(connection, sql_text):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_text)
    except Error as error:
        print(error)


def run_select_sql(connection, sql_text):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_text)
        return cursor.fetchall()
    except Error as error:
        print(error)
        return None


def setup_database(drop_tables):
    sql_texts = {}
    sql_texts.update(create_table_sql_texts(ITEM_REPORTS))
    sql_texts.update(create_view_sql_texts(ITEM_REPORTS))
    sql_texts.update(create_table_sql_texts(TITLE_REPORTS))
    sql_texts.update(create_view_sql_texts(TITLE_REPORTS))
    sql_texts.update(create_table_sql_texts(DATABASE_REPORTS))
    sql_texts.update(create_view_sql_texts(DATABASE_REPORTS))
    for key in sorted(sql_texts):  # testing
        print(sql_texts[key])

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        for key in sorted(sql_texts):
            if drop_tables:
                print('DROP ' + key)
                run_sql(connection,
                        'DROP ' + ('VIEW' if key.endswith(VIEW_SUFFIX) else 'TABLE') + ' IF EXISTS ' + key + ';')
            print('CREATE ' + key)
            run_sql(connection, sql_texts[key])
        connection.close()
    else:
        print("Error, no connection")


def test_insert():
    data = read_report_file(FILE_LOCATION + '2019/EBSCO/2019_EBSCO_DR_D1.tsv', 'EBSCO')
    replace = replace_sql_text(data['report'], data['values'])
    print(replace)  # testing

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        run_sql(connection, replace)
        connection.commit()
        connection.close()
    else:
        print("Error, no connection")


def test_search():
    search = search_sql_text('DR_D1', 2019, 2019,
                             [[{'field': 'database', 'comparison': 'like', 'value': '19th Century%'}],
                              [{'field': 'publisher', 'comparison': '=', 'value': 'JSTOR'},
                               {'field': 'platform', 'comparison': '=', 'value': 'EBSCOhost'}]])
    print(search)  # testing

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        print(run_select_sql(connection, search))
        connection.close()
    else:
        print("Error, no connection")


setup_database(True)
test_insert()
test_search()
