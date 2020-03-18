import csv
import json
import validators
from PyQt5.QtWidgets import QDialog, QLabel, QDialogButtonBox, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QObject, QModelIndex, pyqtSignal
from ui import ManageVendorsTab, AddVendorDialog, MessageDialog, RemoveVendorDialog
import DataStorage, ManageDB
import webbrowser
from JsonUtils import JsonModel

VENDORS_FILE_DIR = "./all_data/vendor_manager/"
VENDORS_FILE_NAME = "vendors.dat"
VENDORS_FILE_PATH = VENDORS_FILE_DIR + VENDORS_FILE_NAME

EXPORT_VENDORS_FILE_NAME = "exported_vendor_data.tsv"
help_site = "https://github.com/CS-4820-Library-Project/Libly/wiki"


class Vendor(JsonModel):
    def __init__(self, name: str, customer_id: str, base_url: str, requestor_id: str, api_key: str, platform: str,
                 is_local: bool, description: str, companies: str):
        self.name = name
        self.customer_id = customer_id
        self.base_url = base_url
        self.requestor_id = requestor_id
        self.api_key = api_key
        self.platform = platform
        self.is_local = is_local
        self.description = description
        self.companies = companies

    @classmethod
    def from_json(cls, json_dict: dict):
        name = json_dict["name"] if "name" in json_dict else ""
        customer_id = json_dict["customer_id"] if "customer_id" in json_dict else ""
        base_url = json_dict["base_url"] if "base_url" in json_dict else ""
        requestor_id = json_dict["requestor_id"] if "requestor_id" in json_dict else ""
        api_key = json_dict["api_key"] if "api_key" in json_dict else ""
        platform = json_dict["platform"] if "platform" in json_dict else ""
        is_local = json_dict["is_local"] if "is_local" in json_dict else False
        description = json_dict["description"] if "description" in json_dict else ""
        companies = json_dict["companies"] if "companies" in json_dict else ""

        return cls(name, customer_id, base_url, requestor_id, api_key, platform, is_local, description, companies)


class ManageVendorsController(QObject):
    vendors_changed_signal = pyqtSignal(list)

    def __init__(self, manage_vendors_ui: ManageVendorsTab.Ui_manage_vendors_tab):
        super().__init__()
        self.selected_index = -1

        self.edit_vendor_details_frame = manage_vendors_ui.edit_vendor_details_frame
        self.edit_vendor_options_frame = manage_vendors_ui.edit_vendor_options_frame

        self.name_line_edit = manage_vendors_ui.nameEdit
        self.customer_id_line_edit = manage_vendors_ui.customerIdEdit
        self.base_url_line_edit = manage_vendors_ui.baseUrlEdit
        self.requestor_id_line_edit = manage_vendors_ui.requestorIdEdit
        self.api_key_line_edit = manage_vendors_ui.apiKeyEdit
        self.platform_line_edit = manage_vendors_ui.platformEdit
        self.local_only_check_box = manage_vendors_ui.local_only_check_box
        self.description_text_edit = manage_vendors_ui.descriptionEdit
        self.companies_text_edit = manage_vendors_ui.companiesEdit

        self.name_validation_label = manage_vendors_ui.name_validation_label
        self.name_validation_label.hide()
        self.url_validation_label = manage_vendors_ui.url_validation_label
        self.url_validation_label.hide()

        self.save_vendor_changes_button = manage_vendors_ui.saveVendorChangesButton
        self.undo_vendor_changes_button = manage_vendors_ui.undoVendorChangesButton
        self.remove_vendor_button = manage_vendors_ui.removeVendorButton
        self.add_vendor_button = manage_vendors_ui.addVendorButton
        self.export_vendors_button = manage_vendors_ui.exportVendorsButton
        self.import_vendors_button = manage_vendors_ui.importVendorsButton

        self.save_vendor_changes_button.clicked.connect(self.modify_vendor)
        self.undo_vendor_changes_button.clicked.connect(self.populate_edit_vendor_view)
        self.remove_vendor_button.clicked.connect(self.open_remove_vendor_dialog)
        self.add_vendor_button.clicked.connect(self.open_add_vendor_dialog)
        self.export_vendors_button.clicked.connect(self.open_custom_folder_select_dialog)
        self.import_vendors_button.clicked.connect(self.open_file_select_dialog)

        self.vendor_list_view = manage_vendors_ui.vendorsListView
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        self.vendor_list_view.clicked.connect(self.on_vendor_selected)

        self.vendors = []
        self.vendor_names = set()  # Hash set for faster operations
        vendors_json_string = DataStorage.read_json_file(VENDORS_FILE_PATH)
        vendor_dicts = json.loads(vendors_json_string)
        for json_dict in vendor_dicts:
            vendor = Vendor.from_json(json_dict)
            self.vendors.append(vendor)
            self.vendor_names.add(vendor.name.lower())

        self.update_vendors_ui()

    def on_vendor_selected(self, model_index: QModelIndex):
        self.selected_index = model_index.row()
        self.populate_edit_vendor_view()

    def on_name_text_changed(self, new_name: str, original_name: str, validation_label: QLabel, validate: bool = True):
        if not validate:
            validation_label.hide()
            return

        is_valid, message = self.validate_new_name(new_name, original_name)
        if is_valid:
            validation_label.hide()
        else:
            validation_label.show()
            validation_label.setText(message)

    def on_url_text_changed(self, url: str, validation_label: QLabel, validate: bool = True):
        if not validate:
            validation_label.hide()
            return

        is_valid, message = self.validate_url(url)
        if is_valid:
            validation_label.hide()
        else:
            validation_label.show()
            validation_label.setText(message)

    def validate_new_name(self, new_name: str, original_name: str = "") -> (bool, str):
        if not new_name:
            return False, "Vendor name can't be empty"
        elif new_name.lower() in self.vendor_names:
            if original_name and original_name.lower() == new_name.lower():
                return True, ""
            else:
                return False, "Duplicate vendor name"
        else:
            return True, ""

    def validate_url(self, url: str) -> (bool, str):
        if not validators.url(url):
            return False, "Invalid Url"
        elif not url.endswith("/reports"):
            return False, "URL must end with '/reports'"
        else:
            return True, ""

    def update_vendors_ui(self):
        self.vendor_list_model.clear()
        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

        self.populate_edit_vendor_view()

    def update_vendor_names(self):
        self.vendor_names.clear()
        for vendor in self.vendors:
            self.vendor_names.add(vendor.name.lower())

    def add_vendor(self, new_vendor: Vendor) -> (bool, str):
        # Check if vendor is valid
        is_valid, message = self.validate_new_name(new_vendor.name)
        if not is_valid:
            return is_valid, message

        if not new_vendor.is_local:
            is_valid, message = self.validate_url(new_vendor.base_url)
            if not is_valid:
                return is_valid, message

        self.vendors.append(new_vendor)
        self.vendor_names.add(new_vendor.name.lower())

        return True, ""

    def modify_vendor(self):
        if self.selected_index < 0:
            print("No vendor selected")
            return

        selected_vendor = self.vendors[self.selected_index]

        # Check if entries are valid
        new_name = self.name_line_edit.text()
        original_name = selected_vendor.name
        is_valid, message = self.validate_new_name(new_name, original_name)
        if not is_valid:
            self.show_message(message)
            return

        if not self.local_only_check_box.isChecked():
            url = self.base_url_line_edit.text()
            is_valid, message = self.validate_url(url)
            if not is_valid:
                self.show_message(message)
                return

        # Apply Changes
        selected_vendor.name = self.name_line_edit.text()
        selected_vendor.base_url = self.base_url_line_edit.text()
        selected_vendor.customer_id = self.customer_id_line_edit.text()
        selected_vendor.requestor_id = self.requestor_id_line_edit.text()
        selected_vendor.api_key = self.api_key_line_edit.text()
        selected_vendor.platform = self.platform_line_edit.text()
        selected_vendor.is_local = self.local_only_check_box.checkState() == Qt.Checked
        selected_vendor.description = self.description_text_edit.toPlainText()
        selected_vendor.companies = self.companies_text_edit.toPlainText()

        self.update_vendors_ui()
        self.update_vendor_names()
        self.vendors_changed_signal.emit(self.vendors)
        self.save_all_vendors_to_disk()

        if original_name != new_name:
            ManageDB.update_vendor_in_all_tables(original_name, new_name)
            for report_type in ManageDB.REPORT_TYPE_SWITCHER.keys():
                ManageDB.backup_costs_data(report_type)

        self.show_message("Changes Saved!")

    def open_add_vendor_dialog(self):
        vendor_dialog = QDialog()
        vendor_dialog_ui = AddVendorDialog.Ui_addVendorDialog()
        vendor_dialog_ui.setupUi(vendor_dialog)

        name_edit = vendor_dialog_ui.nameEdit
        base_url_edit = vendor_dialog_ui.baseUrlEdit
        customer_id_edit = vendor_dialog_ui.customerIdEdit
        requestor_id_edit = vendor_dialog_ui.requestorIdEdit
        api_key_edit = vendor_dialog_ui.apiKeyEdit
        platform_edit = vendor_dialog_ui.platformEdit
        local_only_check_box = vendor_dialog_ui.local_only_check_box
        description_edit = vendor_dialog_ui.descriptionEdit
        companies_edit = vendor_dialog_ui.companiesEdit

        name_validation_label = vendor_dialog_ui.name_validation_label
        name_validation_label.hide()
        url_validation_label = vendor_dialog_ui.url_validation_label
        url_validation_label.hide()

        name_edit.textChanged.connect(
            lambda new_name: self.on_name_text_changed(new_name, "", name_validation_label))
        base_url_edit.textChanged.connect(
            lambda url: self.on_url_text_changed(url, url_validation_label))

        def attempt_add_vendor():
            vendor = Vendor(name_edit.text(),
                            customer_id_edit.text(),
                            base_url_edit.text(),
                            requestor_id_edit.text(),
                            api_key_edit.text(),
                            platform_edit.text(),
                            local_only_check_box.checkState() == Qt.Checked,
                            description_edit.toPlainText(),
                            companies_edit.toPlainText())

            is_valid, message = self.add_vendor(vendor)
            if is_valid:
                self.sort_vendors()
                self.selected_index = -1
                self.update_vendors_ui()
                self.populate_edit_vendor_view()
                self.vendors_changed_signal.emit(self.vendors)
                self.save_all_vendors_to_disk()
                vendor_dialog.close()
            else:
                self.show_message(message)

        button_box = vendor_dialog_ui.buttonBox
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.clicked.connect(attempt_add_vendor)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(lambda: vendor_dialog.close())

        vendor_dialog.exec_()

    def open_file_select_dialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("All TSV files (*.tsv)")
        if dialog.exec_():
            selected_file_path = dialog.selectedFiles()[0]
            self.import_vendors_tsv(selected_file_path)
            self.show_message(f"Import successful!")

    def open_custom_folder_select_dialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            directory = dialog.selectedFiles()[0] + "/"
            self.export_vendors_tsv(directory)
            self.show_message(f"Exported as {EXPORT_VENDORS_FILE_NAME}")

    def populate_edit_vendor_view(self):
        if self.selected_index >= 0:
            selected_vendor = self.vendors[self.selected_index]

            self.name_line_edit.textChanged.connect(
                lambda new_name: self.on_name_text_changed(new_name, selected_vendor.name, self.name_validation_label))
            self.name_line_edit.setText(selected_vendor.name)

            self.base_url_line_edit.textChanged.connect(
                lambda url: self.on_url_text_changed(url, self.url_validation_label))
            self.base_url_line_edit.setText(selected_vendor.base_url)

            self.customer_id_line_edit.setText(selected_vendor.customer_id)
            self.requestor_id_line_edit.setText(selected_vendor.requestor_id)
            self.api_key_line_edit.setText(selected_vendor.api_key)
            self.platform_line_edit.setText(selected_vendor.platform)
            self.local_only_check_box.setChecked(selected_vendor.is_local)
            self.description_text_edit.setPlainText(selected_vendor.description)
            self.companies_text_edit.setPlainText(selected_vendor.companies)

            self.set_edit_vendor_view_state(True)
        else:
            self.name_line_edit.textChanged.connect(
                lambda new_name: self.on_name_text_changed(new_name, "", self.name_validation_label, False))
            self.name_line_edit.setText("")
            self.name_line_edit.textChanged.emit("")  # Hide validation_label if showing

            self.base_url_line_edit.textChanged.connect(
                lambda url: self.on_url_text_changed(url, self.url_validation_label, False))
            self.base_url_line_edit.setText("")
            self.base_url_line_edit.textChanged.emit("")

            self.customer_id_line_edit.setText("")
            self.base_url_line_edit.setText("")
            self.requestor_id_line_edit.setText("")
            self.api_key_line_edit.setText("")
            self.platform_line_edit.setText("")
            self.local_only_check_box.setChecked(False)
            self.description_text_edit.setPlainText("")
            self.companies_text_edit.setPlainText("")

            self.set_edit_vendor_view_state(False)

    def set_edit_vendor_view_state(self, is_enabled):
        if is_enabled:
            self.edit_vendor_details_frame.setEnabled(True)
            self.edit_vendor_options_frame.setEnabled(True)
        else:
            self.edit_vendor_details_frame.setEnabled(False)
            self.edit_vendor_options_frame.setEnabled(False)

    def open_remove_vendor_dialog(self):
        dialog_remove = QDialog()
        dialog_remove_ui = RemoveVendorDialog.Ui_dialog_remove()
        dialog_remove_ui.setupUi(dialog_remove)

        def remove_vendor():
            if self.selected_index >= 0:
                self.vendors.pop(self.selected_index)
                self.selected_index = -1

                self.update_vendors_ui()
                self.update_vendor_names()
                self.populate_edit_vendor_view()
                self.vendors_changed_signal.emit(self.vendors)
                self.save_all_vendors_to_disk()

        button_box = dialog_remove_ui.buttonBox
        button_box.accepted.connect(remove_vendor)
        dialog_remove.exec_()

    def save_all_vendors_to_disk(self):
        json_string = json.dumps(self.vendors, default=lambda o: o.__dict__, indent=4)
        DataStorage.save_json_file(VENDORS_FILE_DIR, VENDORS_FILE_NAME, json_string)

    def show_message(self, message: str):
        message_dialog = QDialog(flags=Qt.WindowCloseButtonHint)
        message_dialog_ui = MessageDialog.Ui_message_dialog()
        message_dialog_ui.setupUi(message_dialog)

        message_label = message_dialog_ui.message_label
        message_label.setText(message)

        message_dialog.exec_()

    def sort_vendors(self):
        self.vendors = sorted(self.vendors, key=lambda vendor: vendor.name.lower())

    def import_vendors_tsv(self, file_path):
        try:
            tsv_file = open(file_path, 'r', encoding="utf-8", newline='')
            reader = csv.DictReader(tsv_file, delimiter='\t')
            for row in reader:
                if 'is_local' in row:
                    is_local = row['is_local'].lower() == "true"
                else:
                    is_local = False
                vendor = Vendor(row['name'] if 'name' in row else "",
                                row['customer_id'] if 'customer_id' in row else "",
                                row['base_url'] if 'base_url' in row else "",
                                row['requestor_id'] if 'requestor_id' in row else "",
                                row['api_key'] if 'api_key' in row else "",
                                row['platform'] if 'platform' in row else "",
                                is_local,
                                row['description'] if 'description' in row else "",
                                row['companies'] if 'companies' in row else "")

                is_valid, message = self.add_vendor(vendor)
                if not is_valid:
                    print(message)

            tsv_file.close()

            self.sort_vendors()
            self.selected_index = -1
            self.update_vendors_ui()
            self.update_vendor_names()
            self.populate_edit_vendor_view()
            self.vendors_changed_signal.emit(self.vendors)
            self.save_all_vendors_to_disk()
        except Exception as e:
            print(f"File import failed: {e}")

    def export_vendors_tsv(self, dir_path):
        file_path = f"{dir_path}{EXPORT_VENDORS_FILE_NAME}"
        column_names = ["name",
                        "customer_id",
                        "base_url",
                        "requestor_id",
                        "api_key",
                        "platform",
                        "is_local",
                        "description",
                        "companies"]
        try:
            tsv_file = open(file_path, 'w', encoding="utf-8", newline='')
            tsv_dict_writer = csv.DictWriter(tsv_file, column_names, delimiter='\t')
            tsv_dict_writer.writeheader()

            for vendor in self.vendors:
                tsv_dict_writer.writerow(vendor.__dict__)

            tsv_file.close()

        except Exception as e:
            print(f"File export failed: {e}")

