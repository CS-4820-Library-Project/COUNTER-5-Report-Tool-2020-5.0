# databse report definitions
DATABASE_REPORTS = ('DR', 'DR_D1', 'DR_D2')
DATABASE_REPORT_FIELDS = ({'name': 'database',
                           'type': 'TEXT',
                           'options': ('NOT NULL',),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'publisher',
                           'type': 'TEXT',
                           'options': (),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'publisher_id',
                           'type': 'TEXT',
                           'options': (),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'platform',
                           'type': 'TEXT',
                           'options': (),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'proprietary_id',
                           'type': 'TEXT',
                           'options': (),
                           'reports': ('DR', 'DR_D1', 'DR_D2')},
                          {'name': 'data_type',
                           'type': 'TEXT',
                           'options': (),
                           'reports': ('DR',)},
                          {'name': 'access_method',
                           'type': 'TEXT',
                           'options': (),
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
                       'options': (),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'publisher_id',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'platform',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'authors',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'publication_date',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'doi',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'proprietary_id',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'isbn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'print_issn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'online_issn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'uri',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1', 'IR_M1')},
                      {'name': 'parent_title',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_authors',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_publication_date',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'parent_article_version',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_data_type',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'parent_doi',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_proprietary_id',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_isbn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'parent_print_issn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_online_issn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'parent_uri',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'component_title',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_authors',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_publication_date',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_data_type',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_doi',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_proprietary_id',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_isbn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_print_issn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_online_issn',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'component_uri',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'data_type',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'yop',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR',)},
                      {'name': 'access_type',
                       'type': 'TEXT',
                       'options': (),
                       'reports': ('IR', 'IR_A1')},
                      {'name': 'access_method',
                       'type': 'TEXT',
                       'options': (),
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
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'publisher_id',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'platform',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'doi',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'proprietary_id',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'isbn',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3')},
                       {'name': 'print_issn',
                        'type': '',
                        'options': ('TEXT',),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'online_issn',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'uri',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4')},
                       {'name': 'data_type',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR',)},
                       {'name': 'section_type',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR',)},
                       {'name': 'yop',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B1', 'TR_B2', 'TR_B3', 'TR_J4')},
                       {'name': 'access_type',
                        'type': 'TEXT',
                        'options': (),
                        'reports': ('TR', 'TR_B3', 'TR_J3')},
                       {'name': 'access_method',
                        'type': 'TEXT',
                        'options': (),
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

MONTHS = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june',
          7: 'july', 8: 'august', 9: 'september', 10: 'october', 11: 'november', 12: 'december'}

DATABASE_LOCATION = r"./all_data/search/search.db"

def create_table_sql_texts(reports,
                           report_fields):  # makes the SQL statements to create the tables from the table definition
    sql_texts = {}
    for report in reports:
        sql_text = 'CREATE TABLE IF NOT EXISTS ' + report + '('
        fields_and_options = []
        for field in report_fields:  # fields specific to this report
            if report in field['reports']:
                field_text = '\n\t' + field['name'] + ' ' + field['type']
                if field['options']:
                    field_text += ' ' + ' '.join(field['options'])
                fields_and_options.append(field_text)
        for field in ALL_REPORT_FIELDS:  # fields in all reports
            field_text = '\n\t' + field['name'] + ' ' + field['type']
            if field['options']:
                field_text += ' ' + ' '.join(field['options'])
            fields_and_options.append(field_text)
        sql_text += ', '.join(fields_and_options) + ');'
        sql_texts[report] = sql_text
    return sql_texts


def create_view_sql_texts(reports,
                          report_fields):  # makes the SQL statements to create the views from the table definition
    sql_texts = {}
    for report in reports:
        sql_text = 'CREATE VIEW IF NOT EXISTS ' + report + '_view AS SELECT'
        fields = []
        for field in report_fields:  # fields specific to this report
            if report in field['reports']:
                field_text = '\n\t' + field['name']
                fields.append(field_text)
        for field in ALL_REPORT_FIELDS:  # fields in all reports
            if field['name'] not in ('month', 'metric', 'updated_on'):
                field_text = '\n\t' + field['name']
                fields.append(field_text)
        calcs = []
        for key in sorted(MONTHS):
            calc_text = '\n\tSUM(CASE ' + 'month' + ' WHEN ' + str(key)
            calc_text += ' THEN ' + 'metric' + ' END) AS ' + MONTHS[key]
            calcs.append(calc_text)
        sql_text += ', '.join(fields) + ', ' + ', '.join(calcs)
        sql_text += '\nFROM ' + report
        sql_text += '\nGROUP BY ' + ', '.join(fields) + ';'
        sql_texts[report + '_view'] = sql_text
    return sql_texts

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

def setup_database():
    sql_texts = {}
    sql_texts.update(create_table_sql_texts(ITEM_REPORTS, ITEM_REPORT_FIELDS))
    sql_texts.update(create_view_sql_texts(ITEM_REPORTS, ITEM_REPORT_FIELDS))
    sql_texts.update(create_table_sql_texts(TITLE_REPORTS, TITLE_REPORT_FIELDS))
    sql_texts.update(create_view_sql_texts(TITLE_REPORTS, TITLE_REPORT_FIELDS))
    sql_texts.update(create_table_sql_texts(DATABASE_REPORTS, DATABASE_REPORT_FIELDS))
    sql_texts.update(create_view_sql_texts(DATABASE_REPORTS, DATABASE_REPORT_FIELDS))
    for key in sorted(sql_texts):  # testing
        print(sql_texts[key])

    connection = create_connection(DATABASE_LOCATION)
    if connection is not None:
        for key in sorted(sql_texts):
            print('DROP ' + key)
            run_sql(connection, 'DROP ' + ('VIEW' if key.endswith("_view") else 'TABLE') + ' IF EXISTS ' + key + ';')
            print('CREATE ' + key)
            run_sql(connection, sql_texts[key])
    else:
        print("Error, no connection")

setup_database()
