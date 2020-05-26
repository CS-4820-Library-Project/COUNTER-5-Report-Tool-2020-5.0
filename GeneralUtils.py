import webbrowser
import shlex
import subprocess
import platform
import csv
from typing import Sequence, Any
from os import path, makedirs, system
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import QDate
from Constants import *

main_window: QWidget = None


class JsonModel:
    def from_json(self, json_dict: dict):
        raise NotImplementedError("from_json method is not implemented")


def save_json_file(file_dir: str, file_name: str, json_string: str):
    try:
        if not path.isdir(file_dir):
            makedirs(file_dir)
        file = open(file_dir + file_name, 'w')
        file.write(json_string)
        file.close()
    except IOError as e:
        print(e)


def read_json_file(file_path: str) -> str:
    json_string = "[]"
    try:
        file = open(file_path, 'r', encoding='utf-8-sig')
        json_string = file.read()
        file.close()
    except IOError:
        pass
    finally:
        return json_string


def show_message(message: str):
    message_box = QMessageBox(main_window)
    message_box.setMinimumSize(800, 800)
    message_box.setWindowTitle("Info")
    message_box.setText(message)
    message_box.exec_()


def ask_confirmation(message: str = 'Are you sure you want to continue?') -> bool:
    reply = QMessageBox.question(main_window, "Confirm", message, QMessageBox.Yes, QMessageBox.No)
    return reply == QMessageBox.Yes


def open_file_or_dir(target_path: str):
    if path.exists(target_path):
        if platform.system() == "Darwin":
            system("open " + shlex.quote(target_path))
        elif platform.system() == "Linux":
            subprocess.call(["xdg-open", target_path])
        else:
            webbrowser.open_new_tab(path.realpath(target_path))
    else:
        show_message(f"\'{target_path}\' does not exist")


def choose_file(name_filters) -> str:
    file_path = ""
    dialog = QFileDialog(main_window)
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilters(name_filters)
    if dialog.exec_():
        file_path = dialog.selectedFiles()[0]

    return file_path


def choose_files(name_filters) -> list:
    file_paths = []
    dialog = QFileDialog(main_window)
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setNameFilters([x for x in name_filters])
    if dialog.exec_():
        file_paths = dialog.selectedFiles()

    return file_paths


def choose_directory() -> str:
    dir_path = ""
    dialog = QFileDialog(main_window)
    dialog.setFileMode(QFileDialog.Directory)
    if dialog.exec_():
        dir_path = dialog.selectedFiles()[0] + "/"

    return dir_path


def choose_save(name_filters) -> str:
    file_path = ""
    dialog = QFileDialog(main_window)
    dialog.setFileMode(QFileDialog.AnyFile)
    dialog.setAcceptMode(QFileDialog.AcceptSave)
    dialog.setNameFilters(name_filters)
    if dialog.exec_():
        file_path = dialog.selectedFiles()[0]

    return file_path


def open_in_browser(url: str):
    webbrowser.open_new_tab(url)


def get_yearly_file_dir(base_path: str, vendor_name: str, begin_date: QDate) -> str:
    return f"{base_path}{begin_date.toString('yyyy')}/{vendor_name}/"


def get_yearly_file_name(vendor_name: str, report_type: str, begin_date: QDate) -> str:
    return f"{begin_date.toString('yyyy')}_{vendor_name}_{report_type}.tsv"


def get_special_file_dir(base_path: str, vendor_name: str) -> str:
    return f"{base_path}{vendor_name}/special/"


def get_special_file_name(vendor_name: str, report_type: str, begin_date: QDate, end_date: QDate) -> str:
    return f"{vendor_name}_{report_type}_{begin_date.toString('yyyy-MMM')}_{end_date.toString('yyyy-MMM')}_S.tsv"


def get_other_file_dir(base_path: str, vendor_name: str) -> str:
    return f"{base_path}{vendor_name}/"


def get_other_file_name(vendor_name: str, report_type: str, begin_date: QDate, end_date: QDate) -> str:
    return f"{vendor_name}_{report_type}_{begin_date.toString('yyyy-MMM')}_{end_date.toString('yyyy-MMM')}.tsv"


def get_major_report_type(report_type: str) -> MajorReportType:
    """Returns a major report type that a report type falls under"""
    if report_type == "PR" or report_type == "PR_P1":
        return MajorReportType.PLATFORM

    elif report_type == "DR" or report_type == "DR_D1" or report_type == "DR_D2":
        return MajorReportType.DATABASE

    elif report_type == "TR" or report_type == "TR_B1" or report_type == "TR_B2" \
            or report_type == "TR_B3" or report_type == "TR_J1" or report_type == "TR_J2" \
            or report_type == "TR_J3" or report_type == "TR_J4":
        return MajorReportType.TITLE

    elif report_type == "IR" or report_type == "IR_A1" or report_type == "IR_M1":
        return MajorReportType.ITEM


def save_data_as_tsv(file_name: str, data: Sequence[Any]):
    """Saves data in a TSV file

    :param file_name: the name and location to save the results at
    :param data: the data to save in the file"""
    file = open(file_name, 'w', newline="", encoding='utf-8')
    if file.mode == 'w':
        output = csv.writer(file, delimiter='\t', quotechar='\"')
        for row in data:
            output.writerow(row)
        file.close()
    else:
        print('Error: could not open file ' + file_name)