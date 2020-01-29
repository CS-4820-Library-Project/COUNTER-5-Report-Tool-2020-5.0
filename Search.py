from PyQt5.QtWidgets import QTableView, QCheckBox, QPushButton, QLineEdit, QDialog
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QSize
from JsonUtils import JsonModel
from ui import MainWindow, MessageDialog
import DataStorage
import json

SEARCH_FILE_DIR = "./all_data/search/"
SEARCH_FILE_NAME = "search.dat"

MINIMUM_SEARCH_CHARACTERS = 3


# region Models

class SearchPathModel(JsonModel):
    def __init__(self, file_path: str, year: int, vendor_name: str):
        self.file_path = file_path
        self.year = year
        self.vendor_name = vendor_name

    @classmethod
    def from_json(cls, json_dict: dict):
        file_path = json_dict["file_path"] if "file_path" in json_dict else None
        year = int(json_dict["year"]) if "year" in json_dict else None
        vendor_name = json_dict["vendor_name"] if "vendor_name" in json_dict else None

        return cls(file_path, year, vendor_name)


class SearchTitleRowModel(JsonModel):
    def __init__(self, title: str, online_issn: str, print_issn: str, linking_issn: str, isbn: str, paths: list):
        self.title = title
        self.online_issn = online_issn
        self.print_issn = print_issn
        self.linking_issn = linking_issn
        self.isbn = isbn
        self.paths = paths

    @classmethod
    def from_json(cls, json_dict: dict):
        title = json_dict["title"] if "title" in json_dict else None
        online_issn = json_dict["online_issn"] if "online_issn" in json_dict else None
        print_issn = json_dict["print_issn"] if "print_issn" in json_dict else None
        linking_issn = json_dict["linking_issn"] if "linking_issn" in json_dict else None
        isbn = json_dict["isbn"] if "isbn" in json_dict else None

        paths = list()
        if "paths" in json_dict:
            path_dicts = json_dict["paths"]
            for path_dict in path_dicts:
                paths.append(SearchPathModel.from_json(path_dict))

        return cls(title, online_issn, print_issn, linking_issn, isbn, paths)


class SearchResult:
    def __init__(self, title: str, vendor_name: str, year: int, file_name: str, file_path: str):
        self.title = title
        self.vendor_name = vendor_name
        self.year = year
        self.file_name = file_name
        self.file_path = file_path


class SearchResultTableModel(QAbstractTableModel):
    def __init__(self, headers: list):
        super().__init__()
        self.headers = headers
        self.search_results = list()

    def rowCount(self, parent=QModelIndex()):
        return len(self.search_results)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.row() < len(self.search_results):
            # This assumes that the order of the table's columns match SearchResult's items
            search_result_items = list(self.search_results[index.row()].__dict__.values())

            for i in range(len(search_result_items)):
                if i == index.column():
                    return QVariant(search_result_items[i])

        else:
            return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return QVariant(self.headers[section])

    def append_row(self, search_result: SearchResult):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.search_results.append(search_result)
        self.endInsertRows()

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.search_results = list()
        self.endRemoveRows()


# endregion


class SearchController:
    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        self.search_dict = {}
        self.populate_search_dict()
        self.search_results_model = SearchResultTableModel(headers=["Title", "Vendor", "Year", "File Name"])

        self.search_term_edit = main_window_ui.search_term_edit
        self.title_checkbox = main_window_ui.title_checkbox
        self.issn_checkbox = main_window_ui.issn_checkbox
        self.isbn_checkbox = main_window_ui.isbn_checkbox
        self.search_button = main_window_ui.search_button
        self.search_button.clicked.connect(self.search)

        self.search_table_view = main_window_ui.search_results_table_view
        self.search_table_view.setModel(self.search_results_model)

    def populate_search_dict(self):
        json_string = DataStorage.read_json_file(SEARCH_FILE_DIR + SEARCH_FILE_NAME)
        json_dicts = json.loads(json_string)

        for json_dict in json_dicts:
            search_title_row = SearchTitleRowModel.from_json(json_dict)
            self.search_dict[search_title_row.title] = search_title_row

    def index_word(self, title: str, file_path: str, year: int, vendor_name: str, online_issn: str, print_issn: str,
                   linking_issn: str, isbn: str):
        if title not in self.search_dict:
            search_title_row = SearchTitleRowModel(title, online_issn, print_issn, linking_issn, isbn, list())
            search_title_row.paths.append(SearchPathModel(file_path, year, vendor_name))

            self.search_dict[title] = search_title_row

        else:
            # Avoid adding duplicate paths
            path_found = False
            for path in self.search_dict[title].paths:
                if path.file_path == file_path:
                    path_found = True
                    break

            if not path_found:
                self.search_dict[title].paths.append(SearchPathModel(file_path, year, vendor_name))

    def search(self):
        search_term = self.search_term_edit.text().strip()

        if len(search_term) < MINIMUM_SEARCH_CHARACTERS:
            self.show_message("Enter at least 3 characters")
            return

        all_checked = self.title_checkbox.checkState() == Qt.Checked and \
                      self.issn_checkbox.checkState() == Qt.Checked and \
                      self.isbn_checkbox.checkState() == Qt.Checked
        all_unchecked = self.title_checkbox.checkState() == Qt.Unchecked and \
                        self.issn_checkbox.checkState() == Qt.Unchecked and \
                        self.isbn_checkbox.checkState() == Qt.Unchecked

        is_advanced_search = not (all_checked or all_unchecked)
        self.advanced_search() if is_advanced_search else self.search_all()

    def search_all(self):
        self.search_results_model.clear()

        found = False
        search_term = self.search_term_edit.text().strip().lower()
        search_title_row: SearchTitleRowModel
        for search_title_row in self.search_dict.values():
            if search_term in search_title_row.title.lower() or \
                    search_term in search_title_row.online_issn.lower() or \
                    search_term in search_title_row.print_issn.lower() or \
                    search_term in search_title_row.linking_issn.lower() or \
                    search_term in search_title_row.isbn.lower():

                found = True
                path: SearchPathModel
                for path in search_title_row.paths:
                    file_path_arr = path.file_path.split("/")
                    file_name = file_path_arr[len(file_path_arr) - 1]
                    search_result = SearchResult(search_title_row.title, path.vendor_name, path.year, file_name,
                                                 path.file_path)
                    self.search_results_model.append_row(search_result)

        if not found: self.show_message("Nothing found")

    def advanced_search(self):
        self.search_results_model.clear()

        found = False
        search_term = self.search_term_edit.text().strip().lower()
        title_selected = self.title_checkbox.checkState() == Qt.Checked
        issn_selected = self.issn_checkbox.checkState() == Qt.Checked
        isbn_selected = self.isbn_checkbox.checkState() == Qt.Checked

        search_title_row: SearchTitleRowModel
        for search_title_row in self.search_dict.values():
            if title_selected and search_term in search_title_row.title.lower() or \
                    isbn_selected and search_term in search_title_row.isbn.lower() or \
                    issn_selected and (search_term in search_title_row.online_issn.lower() or
                                       search_term in search_title_row.print_issn.lower() or
                                       search_term in search_title_row.linking_issn.lower()):

                found = True
                path: SearchPathModel
                for path in search_title_row.paths:
                    file_path_arr = path.file_path.split("/")
                    file_name = file_path_arr[len(file_path_arr) - 1]
                    search_result = SearchResult(search_title_row.title, path.vendor_name, path.year, file_name,
                                                 path.file_path)
                    self.search_results_model.append_row(search_result)

        if not found: self.show_message("Nothing found")

    def save_all_data(self):
        print("Updating search index")
        json_string = json.dumps(list(self.search_dict.values()), default=lambda o: o.__dict__)
        DataStorage.save_json_file(SEARCH_FILE_DIR, SEARCH_FILE_NAME, json_string)
        print("Updated search index")

    def show_message(self, message: str):
        message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        message_dialog_ui = MessageDialog.Ui_message_dialog()
        message_dialog_ui.setupUi(message_dialog)

        message_label = message_dialog_ui.message_label
        message_label.setText(message)

        message_dialog.exec_()
