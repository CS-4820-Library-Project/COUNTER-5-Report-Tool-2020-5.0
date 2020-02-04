from PyQt5.QtWidgets import QDialog, QListView, QPushButton, QLineEdit, QFrame
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QObject, QModelIndex, pyqtSignal
from ui import MainWindow, AddVendorDialog, MessageDialog
import json
import DataStorage
from JsonUtils import JsonModel

VENDORS_FILE_DIR = "./all_data/vendor_manager/"
VENDORS_FILE_NAME = "vendors.dat"

# TODO validate data entry


class Vendor(JsonModel):
    def __init__(self, name="", customer_id="", base_url="", requestor_id="", api_key="", platform="", description=""):
        self.name = name
        self.customer_id = customer_id
        self.base_url = base_url
        self.requestor_id = requestor_id
        self.api_key = api_key
        self.platform = platform
        self.description = description

    @classmethod
    def from_json(cls, json_dict: dict):

        return cls(json_dict["name"],
                   json_dict["customer_id"],
                   json_dict["base_url"],
                   json_dict["requestor_id"],
                   json_dict["api_key"],
                   json_dict["platform"],
                   json_dict["description"])


class ManageVendorsController(QObject):
    vendors_changed_signal = pyqtSignal()

    def __init__(self, main_window_ui: MainWindow.Ui_mainWindow):
        super().__init__()
        self.edit_vendor_details_frame = main_window_ui.edit_vendor_details_frame
        self.edit_vendor_options_frame = main_window_ui.edit_vendor_options_frame

        self.name_line_edit = main_window_ui.nameEdit
        self.customer_id_line_edit = main_window_ui.customerIdEdit
        self.base_url_line_edit = main_window_ui.baseUrlEdit
        self.requestor_id_line_edit = main_window_ui.requestorIdEdit
        self.api_key_line_edit = main_window_ui.apiKeyEdit
        self.platform_line_edit = main_window_ui.platformEdit
        self.description_text_edit = main_window_ui.descriptionEdit

        self.selected_index = -1
        self.save_vendor_changes_button = main_window_ui.saveVendorChangesButton
        self.undo_vendor_changes_button = main_window_ui.undoVendorChangesButton
        self.remove_vendor_button = main_window_ui.removeVendorButton
        self.add_vendor_button = main_window_ui.addVendorButton

        self.save_vendor_changes_button.clicked.connect(self.modify_vendor)
        self.undo_vendor_changes_button.clicked.connect(self.populate_edit_vendor_view)
        self.remove_vendor_button.clicked.connect(self.remove_vendor)
        self.add_vendor_button.clicked.connect(self.open_add_vendor_dialog)

        self.vendors_list_view = main_window_ui.vendorsListView
        self.vendors_list_model = QStandardItemModel(self.vendors_list_view)
        self.vendors_list_view.setModel(self.vendors_list_model)
        self.vendors_list_view.clicked.connect(self.on_vendor_selected)

        self.vendors = list()
        vendors_json_string = DataStorage.read_json_file(VENDORS_FILE_DIR + VENDORS_FILE_NAME)
        vendor_dicts = json.loads(vendors_json_string)
        for json_dict in vendor_dicts:
            vendor = Vendor.from_json(json_dict)
            self.vendors.append(vendor)
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendors_list_model.appendRow(item)

    def on_vendor_selected(self, model_index: QModelIndex):
        self.selected_index = model_index.row()
        self.set_edit_vendor_view_state(True)
        self.populate_edit_vendor_view()

    def modify_vendor(self):
        if self.selected_index >= 0:
            selected_vendor = self.vendors[self.selected_index]
            selected_vendor.name = self.name_line_edit.text()
            selected_vendor.customer_id = self.customer_id_line_edit.text()
            selected_vendor.base_url = self.base_url_line_edit.text()
            selected_vendor.requestor_id = self.requestor_id_line_edit.text()
            selected_vendor.api_key = self.api_key_line_edit.text()
            selected_vendor.platform = self.platform_line_edit.text()
            selected_vendor.description = self.description_text_edit.toPlainText()

            item = QStandardItem(selected_vendor.name)
            item.setEditable(False)
            self.vendors_list_model.setItem(self.selected_index, item)

            self.vendors_changed_signal.emit()
            self.save_all_vendors_to_disk()
            self.show_message("Changes Saved!")

    def open_add_vendor_dialog(self):
        vendor_dialog = QDialog()
        vendor_dialog_ui = AddVendorDialog.Ui_addVendorDialog()
        vendor_dialog_ui.setupUi(vendor_dialog)

        name_edit = vendor_dialog_ui.nameEdit
        customer_id_edit = vendor_dialog_ui.customerIdEdit
        base_url_edit = vendor_dialog_ui.baseUrlEdit
        requestor_id_edit = vendor_dialog_ui.requestorIdEdit
        api_key_edit = vendor_dialog_ui.apiKeyEdit
        platform_edit = vendor_dialog_ui.platformEdit
        description_edit = vendor_dialog_ui.descriptionEdit

        def add_vendor():
            vendor = Vendor(name_edit.text(),
                            customer_id_edit.text(),
                            base_url_edit.text(),
                            requestor_id_edit.text(),
                            api_key_edit.text(),
                            platform_edit.text(),
                            description_edit.toPlainText())

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
        if self.selected_index >= 0:
            selected_vendor = self.vendors[self.selected_index]
            self.name_line_edit.setText(selected_vendor.name)
            self.customer_id_line_edit.setText(selected_vendor.customer_id)
            self.base_url_line_edit.setText(selected_vendor.base_url)
            self.requestor_id_line_edit.setText(selected_vendor.requestor_id)
            self.api_key_line_edit.setText(selected_vendor.api_key)
            self.platform_line_edit.setText(selected_vendor.platform)
            self.description_text_edit.setPlainText(selected_vendor.description)

    def set_edit_vendor_view_state(self, is_enabled):
        if is_enabled:
            self.edit_vendor_details_frame.setEnabled(True)
            self.edit_vendor_options_frame.setEnabled(True)
        else:
            self.edit_vendor_details_frame.setEnabled(False)
            self.edit_vendor_options_frame.setEnabled(False)

    def remove_vendor(self):
        if self.selected_index >= 0:
            self.vendors.pop(self.selected_index)
            self.vendors_list_model.removeRow(self.selected_index)
            self.selected_index = -1
            self.set_edit_vendor_view_state(False)

            self.vendors_changed_signal.emit()
            self.save_all_vendors_to_disk()

    def save_all_vendors_to_disk(self):
        json_string = json.dumps(self.vendors, default=lambda o: o.__dict__)
        DataStorage.save_json_file(VENDORS_FILE_DIR, VENDORS_FILE_NAME, json_string)

    def show_message(self, message: str):
        message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        message_dialog_ui = MessageDialog.Ui_message_dialog()
        message_dialog_ui.setupUi(message_dialog)

        message_label = message_dialog_ui.message_label
        message_label.setText(message)

        message_dialog.exec_()


