import csv
from datetime import datetime, timezone
from os import path, makedirs

from PyQt5.QtCore import QDate

import GeneralUtils
from Constants import COUNTER_4_REPORT_TYPES, MajorReportType
from FetchData import ReportRow, ReportHeaderModel, TypeValueModel, NameValueModel, ReportWorker
from ManageVendors import Vendor


class Counter4ReportHeader:
    def __init__(self, report_type: str, customer: str, institution_id: str, reporting_period: str, date_run: str):
        self.report_type = report_type
        self.customer = customer
        self.institution_id = institution_id
        self.reporting_period = reporting_period
        self.date_run = date_run


class Counter4ReportModel:
    def __init__(self, report_header: Counter4ReportHeader, header_list: list, row_dicts: list):
        self.report_header = report_header
        self.header_list = header_list
        self.row_dicts = row_dicts


def get_c5_equivalent(counter4_report_type: str) -> str:
    return COUNTER_4_REPORT_TYPES[counter4_report_type]


class Counter4To5Converter:
    def __init__(self, vendor: Vendor, c4_report_types: str, file_paths: list, save_dir: str, date: QDate):
        self.vendor = vendor
        self.c4_report_types = c4_report_types
        self.file_paths = file_paths
        self.save_dir = save_dir
        self.begin_date = QDate(date.year(), 1, 1)
        self.end_date = QDate(date.year(), 12, 31)
        self.target_c5_report_type = get_c5_equivalent(c4_report_types)
        self.target_c5_major_report_type = GeneralUtils.get_major_report_type(self.target_c5_report_type)

        self.final_rows_dict = {}

    def do_conversion(self) -> str:
        # Convert files to report models and report rows
        c4_report_types_processed = []
        c4_customer = ""
        c4_institution_id = ""
        for file_path in self.file_paths:
            report_model = self.c4_file_to_c4_model(file_path)
            c4_report_header = report_model.report_header
            short_c4_report_type = self.get_short_c4_report_type(c4_report_header.report_type)
            if short_c4_report_type not in self.c4_report_types:
                continue

            c4_report_types_processed.append(short_c4_report_type)
            c4_customer = c4_report_header.customer
            c4_institution_id = c4_report_header.institution_id
            c4_report_types_processed.append(short_c4_report_type)
            self.c4_model_to_rows(report_model)

        # Create a COUNTER 5 header
        if not c4_report_types_processed:
            raise Exception("No valid COUNTER 4 report selected for this operation")
        c4_report_types_processed = sorted(c4_report_types_processed)
        c5_report_header = self.get_c5_report_header(self.target_c5_report_type,
                                                     ", ".join(c4_report_types_processed),
                                                     c4_customer,
                                                     c4_institution_id)

        # Finalize and sort all rows
        final_report_rows = [row for row in self.final_rows_dict.values()]
        final_report_rows = ReportWorker.sort_rows(final_report_rows, self.target_c5_major_report_type)

        # Create the final COUNTER 5 file
        file_path = self.create_c5_file(c5_report_header, final_report_rows)

        return file_path

    def c4_file_to_c4_model(self, file_path: str) -> Counter4ReportModel:
        file = open(file_path, 'r', encoding="utf-8")

        extension = file_path[-4:]
        delimiter = ""
        if extension == ".csv":
            delimiter = ","
        elif extension == ".tsv":
            delimiter = "\t"

        # Process process report header into model
        csv_reader = csv.reader(file, delimiter=delimiter)

        report_type = ""
        customer = ""
        institution_id = ""
        reporting_period = ""
        date_run = ""

        curr_line = 1
        last_header_line = 7

        for row in csv_reader:
            if curr_line == 1:
                report_type = row[0]
            elif curr_line == 2:
                customer = row[0]
            elif curr_line == 3:
                institution_id = row[0]
            elif curr_line == 4 and row[0].lower() != "period covered by report:":
                file.close()
                raise Exception("'Period covered by Report:' missing from header line 4")
            elif curr_line == 5:
                reporting_period = row[0]
            elif curr_line == 6 and row[0].lower() != "date run:":
                file.close()
                raise Exception("'Date run:' missing from header line 6")
            elif curr_line == 7:
                date_run = row[0]
                is_valid_date = QDate().fromString(date_run, "yyyy-MM-dd").isValid() or \
                                QDate().fromString(date_run, "MM-dd-yy").isValid() or \
                                QDate().fromString(date_run, "M-d-yy").isValid()
                if not is_valid_date:
                    file.close()
                    raise Exception("Invalid date on line 7")

            curr_line += 1

            if curr_line > last_header_line:
                break

        if curr_line <= last_header_line:
            file.close()
            raise Exception("Not enough lines in report header")

        report_header = Counter4ReportHeader(report_type, customer, institution_id, reporting_period, date_run)

        # Process process report rows into model
        csv_dict_reader = csv.DictReader(file, delimiter=delimiter)
        header_dict = csv_dict_reader.fieldnames
        row_dicts = []

        for row in csv_dict_reader:
            row_dicts.append(row)

        report_model = Counter4ReportModel(report_header, header_dict, row_dicts)

        file.close()

        return report_model

    def c4_model_to_rows(self, report_model: Counter4ReportModel):
        short_c4_report_type = self.get_short_c4_report_type(report_model.report_header.report_type)

        for row_dict in report_model.row_dicts:
            report_row = self.convert_c4_row_to_c5(short_c4_report_type, row_dict)

            if report_row.total_count == 0:  # Exclude rows with reporting total of 0
                continue

            if self.target_c5_major_report_type == MajorReportType.DATABASE:
                if report_row.database.lower().startswith("total for all"):  # Exclude total rows
                    continue

                if (report_row.database, report_row.metric_type) not in self.final_rows_dict:
                    self.final_rows_dict[report_row.database, report_row.metric_type] = report_row
                else:
                    existing_row: ReportRow = self.final_rows_dict[report_row.database, report_row.metric_type]
                    existing_metric_type_total = existing_row.total_count
                    new_metric_type_total = report_row.total_count

                    if existing_row.metric_type == "Total_Item_Investigations":
                        if new_metric_type_total > existing_metric_type_total:
                            self.final_rows_dict[report_row.database, report_row.metric_type] = report_row

            elif self.target_c5_major_report_type == MajorReportType.TITLE:
                if report_row.title.lower().startswith("total for all"):  # Exclude total rows
                    continue

                if (report_row.title, report_row.metric_type) not in self.final_rows_dict:
                    self.final_rows_dict[report_row.title, report_row.metric_type] = report_row
                else:
                    existing_row: ReportRow = self.final_rows_dict[report_row.title, report_row.metric_type]
                    existing_metric_type_total = existing_row.total_count
                    new_metric_type_total = report_row.total_count

                    if existing_row.metric_type == "Total_Item_Investigations":
                        if new_metric_type_total > existing_metric_type_total:
                            self.final_rows_dict[report_row.title, report_row.metric_type] = report_row

            elif self.target_c5_major_report_type == MajorReportType.PLATFORM:
                self.final_rows_dict[report_row.platform, report_row.metric_type] = report_row

    def convert_c4_row_to_c5(self, c4_report_type: str, row_dict: dict) -> ReportRow:
        report_row = ReportRow(self.begin_date, self.end_date)

        if self.target_c5_major_report_type == MajorReportType.DATABASE:
            if "Database" in row_dict:
                report_row.database = row_dict["Database"]
            if "Publisher" in row_dict:
                report_row.publisher = row_dict["Publisher"]
            if "Platform" in row_dict:
                report_row.platform = row_dict["Platform"]

            # Metric type
            if c4_report_type == "DB1":
                if "User Activity" in row_dict:
                    ua = row_dict["User Activity"]
                    if ua == "Regular Searches":
                        report_row.metric_type = "Searches_Regular"
                    elif ua == "Searches-federated and automated":
                        report_row.metric_type = "Searches_Automated"
                    elif ua == "Result Clicks" or ua == "Record Views":
                        report_row.metric_type = "Total_Item_Investigations"
            elif c4_report_type == "DB2":
                if "Access Denied Category" in row_dict:
                    adc = row_dict["Access Denied Category"]
                    if "limit exceded" in adc or "limit exceeded" in adc:
                        report_row.metric_type = "Limit_Exceeded"
                    elif "not licenced" in adc or "not licensed" in adc:
                        report_row.metric_type = "No_License"

        elif self.target_c5_major_report_type == MajorReportType.TITLE:
            if "" in row_dict:
                report_row.title = row_dict[""]
            if "Title" in row_dict:
                report_row.title = row_dict["Title"]
            if "Journal" in row_dict:
                report_row.title = row_dict["Journal"]
            if "Publisher" in row_dict:
                report_row.publisher = row_dict["Publisher"]
            if "Platform" in row_dict:
                report_row.platform = row_dict["Publisher"]
            if "Book DOI" in row_dict:
                report_row.doi = row_dict["Book DOI"]
            if "Journal DOI" in row_dict:
                report_row.doi = row_dict["Journal DOI"]
            if "Proprietary Identifier" in row_dict:
                report_row.proprietary_id = row_dict["Proprietary Identifier"]
            if "ISBN" in row_dict:
                report_row.isbn = row_dict["ISBN"]
            if "ISSN" in row_dict:
                report_row.online_issn = row_dict["ISSN"]
            if "Print ISSN" in row_dict:
                report_row.print_issn = row_dict["Print ISSN"]
            if "Online ISSN" in row_dict:
                report_row.print_issn = row_dict["Online ISSN"]

            # Metric type
            if c4_report_type == "BR1":
                report_row.metric_type = "Unique_Title_Requests"
            elif c4_report_type == "BR2" or c4_report_type == "JR1":
                report_row.metric_type = "Total_Item_Requests"
            elif c4_report_type == "BR3" or c4_report_type == "JR2":
                if "Access Denied Category" in row_dict:
                    adc = row_dict["Access Denied Category"]
                    if "limit exceded" in adc or "limit exceeded" in adc:
                        report_row.metric_type = "Limit_Exceeded"
                    elif "not licenced" in adc or "not licensed" in adc:
                        report_row.metric_type = "No_License"

        elif self.target_c5_major_report_type == MajorReportType.PLATFORM:
            if "Platform" in row_dict:
                report_row.platform = row_dict["Platform"]
            if "Publisher" in row_dict:
                report_row.publisher = row_dict["Publisher"]

            # Metric type
            if c4_report_type == "PR1":
                if "User Activity" in row_dict:
                    ua = row_dict["User Activity"]
                    if ua == "Regular Searches":
                        report_row.metric_type = "Searches_Regular"
                    elif ua == "Searches-federated and automated":
                        report_row.metric_type = "Searches_Automated"
                    elif ua == "Result Clicks" or ua == "Record Views":
                        report_row.metric_type = "Total_Item_Investigations"

        if "Reporting Period Total" in row_dict:
            report_row.total_count = int(row_dict["Reporting Period Total"])

        # Month Columns
        year = int(self.begin_date.toString("yyyy"))
        for i in range(0, 12):
            month = QDate(year, i + 1, 1).toString("MMM")
            month_year = f"{month}-{year}"
            if month_year in row_dict:
                report_row.month_counts[month_year] = row_dict[month_year]

        return report_row

    def get_c5_report_header(self, target_c5_report_type, c4_report_types: str, customer: str,
                             institution_id: str) -> ReportHeaderModel:
        return ReportHeaderModel(self.get_long_c5_report_type(target_c5_report_type),
                                 target_c5_report_type,
                                 "5",
                                 customer,
                                 [TypeValueModel("Institution_ID", institution_id)],
                                 self.get_c5_header_report_filters(target_c5_report_type),
                                 [],
                                 [],
                                 self.get_c5_header_created(),
                                 self.get_c5_header_created_by(c4_report_types))

    def create_c5_file(self, c5_report_header: ReportHeaderModel, report_rows: list) -> str:
        file_path = self.save_dir + "temp_converted_c5_file.tsv"

        if not path.isdir(self.save_dir):
            makedirs(self.save_dir)

        file = open(file_path, 'w', encoding="utf-8", newline='')

        ReportWorker.add_report_header_to_file(c5_report_header, file, True)
        ReportWorker.add_report_rows_to_file(self.target_c5_report_type, report_rows, self.begin_date, self.end_date,
                                             file, False)

        file.close()

        return file_path

    @staticmethod
    def get_short_c4_report_type(long_c4_report_type: str) -> str:
        short_report_type = ""
        if long_c4_report_type == "Book Report 1 (R4)":
            short_report_type = "BR1"
        elif long_c4_report_type == "Book Report 2 (R4)":
            short_report_type = "BR2"
        elif long_c4_report_type == "Book Report 3 (R4)":
            short_report_type = "BR3"
        elif long_c4_report_type == "Database Report 1 (R4)":
            short_report_type = "DB1"
        elif long_c4_report_type == "Database Report 2 (R4)":
            short_report_type = "DB2"
        elif long_c4_report_type == "Journal Report 1 (R4)":
            short_report_type = "JR1"
        elif long_c4_report_type == "Journal Report 2 (R4)":
            short_report_type = "JR2"
        elif long_c4_report_type == "Platform Report 1 (R4)":
            short_report_type = "PR1"

        return short_report_type

    @staticmethod
    def get_long_c5_report_type(short_c5_report_type: str) -> str:
        long_c5_report_type = ""
        if short_c5_report_type == "DR":
            long_c5_report_type = "Database Master Report"
        elif short_c5_report_type == "DR_D1":
            long_c5_report_type = "Database Search and Item Usage"
        elif short_c5_report_type == "DR_D2":
            long_c5_report_type = "Database Access Denied"
        elif short_c5_report_type == "TR":
            long_c5_report_type = "Title Master Report"
        elif short_c5_report_type == "TR_B1":
            long_c5_report_type = "Book Requests (Excluding OA_Gold)"
        elif short_c5_report_type == "TR_B2":
            long_c5_report_type = "Book Access Denied"
        elif short_c5_report_type == "TR_J1":
            long_c5_report_type = "Journal Requests (Excluding OA_Gold)"
        elif short_c5_report_type == "TR_J2":
            long_c5_report_type = "Journal Access Denied"
        elif short_c5_report_type == "PR_P1":
            long_c5_report_type = "Platform Usage"

        return long_c5_report_type

    def get_c5_header_report_filters(self, target_c5_report_type: str) -> list:
        filters = []
        if target_c5_report_type == "DR_D1":
            filters = [NameValueModel("Access_Method", "Regular"),
                       NameValueModel("Metric_Type", "Searches_Automated|Searches_Federated|Searches_Regular|"
                                                     "Total_Item_Investigations|Total_Item_Requests")]
        elif target_c5_report_type == "DR_D2":
            filters = [NameValueModel("Access_Method", "Regular"),
                       NameValueModel("Metric_Type", "Limit_Exceeded|No_License")]
        elif target_c5_report_type == "PR_P1":
            filters = [NameValueModel("Access_Method", "Regular"),
                       NameValueModel("Metric_Type", "Searches_Platform|Total_Item_Requests|Unique_Item_Requests|"
                                                     "Unique_Title_Requests")]
        elif target_c5_report_type == "TR_B1":
            filters = [NameValueModel("Data_Type", "Book"),
                       NameValueModel("Access_Type", "Controlled"),
                       NameValueModel("Access_Method", "Regular"),
                       NameValueModel("Metric_Type", "Total_Item_Requests|Unique_Title_Requests")]
        elif target_c5_report_type == "TR_B2":
            filters = [NameValueModel("Data_Type", "Book"),
                       NameValueModel("Access_Method", "Regular"),
                       NameValueModel("Metric_Type", "Limit_Exceeded|No_License")]
        elif target_c5_report_type == "TR_J1":
            filters = [NameValueModel("Data_Type", "Journal"),
                       NameValueModel("Access_Type", "Controlled"),
                       NameValueModel("Access_Method", "Regular"),
                       NameValueModel("Metric_Type", "Total_Item_Requests|Unique_Item_Requests")]
        elif target_c5_report_type == "TR_J2":
            filters = [NameValueModel("Data_Type", "Journal"),
                       NameValueModel("Access_Method", "Regular"),
                       NameValueModel("Metric_Type", "Limit_Exceeded|No_License")]

        filters += [NameValueModel("Begin_Date", self.begin_date.toString("yyyy-MM-dd")),
                    NameValueModel("End_Date", self.end_date.toString("yyyy-MM-dd"))]

        return filters

    @staticmethod
    def get_c5_header_created() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_c5_header_created_by(self, short_c4_report_type: str) -> str:
        return f"COUNTER 5 Report Tool, converted from {self.vendor.name} COP4 {short_c4_report_type}"