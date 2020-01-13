from PyQt5.QtWidgets import QDialog, QListView, QPushButton, QLineEdit, QFrame
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QObject, QModelIndex, pyqtSignal
import ui.AddVendorDialog
import json
import DataStorage
from JsonUtils import JsonModel

VENDORS_FILE_DIR = "./all_data/vendor_manager/"
VENDORS_FILE_NAME = "vendors.dat"

# TODO validate data entry


class Vendor(JsonModel):
    def __init__(self, name="", customer_id="", base_url="", requestor_id="", api_key="", platform=""):
        self.name = name
        self.customer_id = customer_id
        self.base_url = base_url
        self.requestor_id = requestor_id
        self.api_key = api_key
        self.platform = platform

    @classmethod
    def from_json(cls, json_dict: dict):

        return cls(json_dict["name"],
                   json_dict["customer_id"],
                   json_dict["base_url"],
                   json_dict["requestor_id"],
                   json_dict["api_key"],
                   json_dict["platform"])


class ManageVendorsController(QObject):
    vendors_changed_signal = pyqtSignal()

    def __init__(self, vendors_list_view: QListView,
                 edit_vendor_frame: QFrame,
                 name_line_edit: QLineEdit,
                 customer_id_line_edit: QLineEdit,
                 base_url_line_edit: QLineEdit,
                 requestor_id_line_edit: QLineEdit,
                 api_key_line_edit: QLineEdit,
                 platform_line_edit: QLineEdit,
                 save_vendor_changes_button: QPushButton,
                 undo_vendor_changes_button: QPushButton,
                 remove_vendor_button: QPushButton,
                 add_vendor_button: QPushButton):

        super().__init__()
        self.edit_vendor_frame = edit_vendor_frame

        self.name_line_edit = name_line_edit
        self.customer_id_line_edit = customer_id_line_edit
        self.base_url_line_edit = base_url_line_edit
        self.requestor_id_line_edit = requestor_id_line_edit
        self.api_key_line_edit = api_key_line_edit
        self.platform_line_edit = platform_line_edit

        self.selected_index = None
        self.save_vendor_changes_button = save_vendor_changes_button
        self.undo_vendor_changes_button = undo_vendor_changes_button
        self.remove_vendor_button = remove_vendor_button
        self.add_vendor_button = add_vendor_button

        self.save_vendor_changes_button.clicked.connect(self.save_vendor_changes)
        self.undo_vendor_changes_button.clicked.connect(self.populate_edit_vendor_view)
        self.remove_vendor_button.clicked.connect(self.remove_vendor)
        self.add_vendor_button.clicked.connect(self.open_add_vendor_dialog)

        self.vendors_list_view = vendors_list_view
        self.vendors_list_model = QStandardItemModel(self.vendors_list_view)
        self.vendors_list_view.setModel(self.vendors_list_model)
        self.vendors_list_view.clicked.connect(self.on_item_changed)

        self.vendors = list()
        vendors_json_string = DataStorage.read_json_file(VENDORS_FILE_DIR + VENDORS_FILE_NAME)
        vendor_dicts = json.loads(vendors_json_string)
        for json_dict in vendor_dicts:
            vendor = Vendor.from_json(json_dict)
            self.vendors.append(vendor)
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendors_list_model.appendRow(item)

    def on_item_changed(self, model_index: QModelIndex):
        index = model_index.row()
        self.selected_index = index
        self.populate_edit_vendor_view()
        self.edit_vendor_frame.setEnabled(True)

    def save_vendor_changes(self):
        if self.selected_index is not None:
            selected_vendor = self.vendors[self.selected_index]
            selected_vendor.name = self.name_line_edit.text()
            selected_vendor.customer_id = self.customer_id_line_edit.text()
            selected_vendor.base_url = self.base_url_line_edit.text()
            selected_vendor.requestor_id = self.requestor_id_line_edit.text()
            selected_vendor.api_key = self.api_key_line_edit.text()
            selected_vendor.platform = self.platform_line_edit.text()

            item = QStandardItem(selected_vendor.name)
            item.setEditable(False)
            self.vendors_list_model.setItem(self.selected_index, item)

            self.save_all_vendors_to_disk()

    def open_add_vendor_dialog(self):
        vendor_dialog = QDialog()
        vendor_dialog_ui = ui.AddVendorDialog.Ui_addVendorDialog()
        vendor_dialog_ui.setupUi(vendor_dialog)

        name_edit = vendor_dialog_ui.nameEdit
        customer_id_edit = vendor_dialog_ui.customerIdEdit
        base_url_edit = vendor_dialog_ui.baseUrlEdit
        requestor_id_edit = vendor_dialog_ui.requestorIdEdit
        api_key_edit = vendor_dialog_ui.apiKeyEdit
        platform_edit = vendor_dialog_ui.platformEdit

        def add_vendor():
            vendor = Vendor(name_edit.text(),
                            customer_id_edit.text(),
                            base_url_edit.text(),
                            requestor_id_edit.text(),
                            api_key_edit.text(),
                            platform_edit.text())

            self.vendors.append(vendor)
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendors_list_model.appendRow(item)

            self.vendors_changed_signal.emit()
            self.save_all_vendors_to_disk()

        button_box = vendor_dialog_ui.buttonBox
        button_box.accepted.connect(add_vendor)

        vendor_dialog.exec_()

    def populate_edit_vendor_view(self):
        if self.selected_index is not None:
            selected_vendor = self.vendors[self.selected_index]
            self.name_line_edit.setText(selected_vendor.name)
            self.customer_id_line_edit.setText(selected_vendor.customer_id)
            self.base_url_line_edit.setText(selected_vendor.base_url)
            self.requestor_id_line_edit.setText(selected_vendor.requestor_id)
            self.api_key_line_edit.setText(selected_vendor.api_key)
            self.platform_line_edit.setText(selected_vendor.platform)

    def remove_vendor(self):
        if self.selected_index is not None:
            self.vendors.pop(self.selected_index)
            self.vendors_list_model.removeRow(self.selected_index)
            self.selected_index = None
            self.save_all_vendors_to_disk()
            if len(self.vendors) > 0:
                self.selected_index = len(self.vendors) - 1
                self.populate_edit_vendor_view()

            self.vendors_changed_signal.emit()

    def save_all_vendors_to_disk(self):
        json_string = json.dumps(self.vendors, default=lambda o: o.__dict__)
        DataStorage.save_json_file(VENDORS_FILE_DIR, VENDORS_FILE_NAME, json_string)
