import webbrowser
import shlex
import platform
from os import path, makedirs, system
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog


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
    except IOError as e:
        print(e)
    finally:
        return json_string


def show_message(message: str, parent: QWidget = None):
    message_box = QMessageBox(parent)
    message_box.setMinimumSize(800, 800)
    message_box.setWindowTitle("Message")
    message_box.setText(message)
    message_box.exec_()


def open_file_or_dir(target_path: str):
    if path.exists(target_path):
        if platform.system() == "Darwin":
            system("open " + shlex.quote(target_path))
        else:
            webbrowser.open_new_tab(path.realpath(target_path))
    else:
        show_message(f"\'{target_path}\' does not exist")


def choose_file(name_filter: str) -> str:
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter(name_filter)
    if dialog.exec_():
        return dialog.selectedFiles()[0]


def open_in_browser(url: str):
    webbrowser.open_new_tab(url)
