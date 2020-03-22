"""This module handles all operations involving managing vendors."""

import csv
import json
import validators
from PyQt5.QtWidgets import QDialog, QLabel, QDialogButtonBox, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QObject, QModelIndex, pyqtSignal
from ui import ManageVendorsTab, AddVendorDialog, RemoveVendorDialog
import ManageDB
import GeneralUtils
from GeneralUtils import JsonModel
from VariableConstants import *

VENDORS_FILE_DIR = "./all_data/vendor_manager/"
VENDORS_FILE_NAME = "vendors.dat"
VENDORS_FILE_PATH = VENDORS_FILE_DIR + VENDORS_FILE_NAME

EXPORT_VENDORS_FILE_NAME = "exported_vendor_data.tsv"


class Vendor(JsonModel):
    """This holds a vendor's information

    :param name: The vendor's unique name (Mandatory)
    :param base_url: The base URL for making sushi report calls (must end with '/reports', mandatory)
    :param customer_id: The customer id used in sushi report calls
    :param requestor_id: The requestor id id used in sushi report calls
    :param api_key: The api key id used in sushi report calls
    :param platform: The platform id used in sushi report calls
    :param is_local: This indicates if this vendor is sushi compatible
    :param description: A description of this vendor
    :param companies: More information about the vendor
    """
    def __init__(self, name: str, base_url: str, customer_id: str, requestor_id: str, api_key: str, platform: str,
                 is_local: bool, description: str, companies: str):
        self.name = name
        self.base_url = base_url
        self.customer_id = customer_id
        self.requestor_id = requestor_id
        self.api_key = api_key
        self.platform = platform
        self.is_local = is_local
        self.description = description
        self.companies = companies

    @classmethod
    def from_json(cls, json_dict: dict):
        """This returns a vendor object using the parameters in a json dict

        :param json_dict: A dict containing a vendor's details
        :return: Vendor
        """
        name = json_dict["name"] if "name" in json_dict else ""
        customer_id = json_dict["customer_id"] if "customer_id" in json_dict else ""
        base_url = json_dict["base_url"] if "base_url" in json_dict else ""
        requestor_id = json_dict["requestor_id"] if "requestor_id" in json_dict else ""
        api_key = json_dict["api_key"] if "api_key" in json_dict else ""
        platform = json_dict["platform"] if "platform" in json_dict else ""
        is_local = json_dict["is_local"] if "is_local" in json_dict else False
        description = json_dict["description"] if "description" in json_dict else ""
        companies = json_dict["companies"] if "companies" in json_dict else ""

        return cls(name, base_url, customer_id, requestor_id, api_key, platform, is_local, description, companies)


class ManageVendorsController(QObject):
    """Controls the Manage Vendors tab

    :param manage_vendors_widget: The manage vendors widget.
    :param manage_vendors_ui: The UI for the manage_vendors_widget.
    """
    vendors_changed_signal = pyqtSignal(list)

    def __init__(self, manage_vendors_widget: QWidget, manage_vendors_ui: ManageVendorsTab.Ui_manage_vendors_tab):
        super().__init__()
        self.manage_vendors_widget = manage_vendors_widget
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
        self.remove_vendor_button.clicked.connect(self.on_remove_vendor_clicked)
        self.add_vendor_button.clicked.connect(self.on_add_vendor_clicked)
        self.export_vendors_button.clicked.connect(self.on_export_vendors_clicked)
        self.import_vendors_button.clicked.connect(self.on_import_vendors_clicked)

        self.vendor_list_view = manage_vendors_ui.vendorsListView
        self.vendor_list_model = QStandardItemModel(self.vendor_list_view)
        self.vendor_list_view.setModel(self.vendor_list_model)
        self.vendor_list_view.clicked.connect(self.on_vendor_selected)

        self.vendors = []
        self.vendor_names = set()  # Hash set for faster operations
        vendors_json_string = GeneralUtils.read_json_file(VENDORS_FILE_PATH)
        vendor_dicts = json.loads(vendors_json_string)
        for json_dict in vendor_dicts:
            vendor = Vendor.from_json(json_dict)
            self.vendors.append(vendor)
            self.vendor_names.add(vendor.name.lower())

        self.update_vendors_ui()

    def on_vendor_selected(self, model_index: QModelIndex):
        """Handles the signal emitted when a vendor is selected

        :param model_index: An object containing the location of the vendor on the vendor list
        """
        self.selected_index = model_index.row()
        self.populate_edit_vendor_view()

    def on_name_text_changed(self, new_name: str, original_name: str, validation_label: QLabel, validate: bool = True):
        """Handles the signal emitted when a vendor's name is changed

        :param new_name: The new name entered in the text field
        :param original_name: The vendor's original name
        :param validation_label: The label to show validation messages
        :param validate: This indicates whether the new_name should be validated
        """
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
        """Handles the signal emitted when a vendor's URL is changed

        :param url: The URL entered in the text field
        :param validation_label: The label to show validation messages
        :param validate: This indicates whether the url should be validated
        """
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
        """Validates a new vendor name

        :param new_name: The new name to be validated
        :param original_name: The original name
        :returns: (is_successful, message) A Tuple with the completion status and a message
        """
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
        """Validates a new url

        :param url: The URL to be validated
        :returns: (is_successful, message) A Tuple with the completion status and a message
        """
        if not validators.url(url):
            return False, "Invalid Url"
        elif not url.endswith("/reports"):
            return False, "URL must end with '/reports'"
        else:
            return True, ""

    def update_vendors_ui(self):
        """Updates the UI to show all vendors"""
        self.vendor_list_model.clear()
        for vendor in self.vendors:
            item = QStandardItem(vendor.name)
            item.setEditable(False)
            self.vendor_list_model.appendRow(item)

        self.populate_edit_vendor_view()

    def update_vendor_names(self):
        """Updates the local set of vendor names used for validation"""
        self.vendor_names.clear()
        for vendor in self.vendors:
            self.vendor_names.add(vendor.name.lower())

    def add_vendor(self, new_vendor: Vendor) -> (bool, str):
        """Adds a new vendor to the system if the vendor is valid

        :param new_vendor: The new vendor to be added
        :returns: (is_successful, message) A Tuple with the completion status and a message
        """
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
        """Updates a vendor's information in the system if the vendor is valid"""
        if self.selected_index < 0:
            print("No vendor selected")
            return

        selected_vendor = self.vendors[self.selected_index]

        # Check if entries are valid
        new_name = self.name_line_edit.text()
        original_name = selected_vendor.name
        is_valid, message = self.validate_new_name(new_name, original_name)
        if not is_valid:
            GeneralUtils.show_message(message)
            return

        if not self.local_only_check_box.isChecked():
            url = self.base_url_line_edit.text()
            is_valid, message = self.validate_url(url)
            if not is_valid:
                GeneralUtils.show_message(message)
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
            for report_type in REPORT_TYPE_SWITCHER.keys():
                ManageDB.backup_costs_data(report_type)

        GeneralUtils.show_message("Changes Saved!")

    def on_add_vendor_clicked(self):
        """Handles the signal emitted when the add vendor button is clicked

        A dialog is show to allow the user to enter a new vendor's information. If the information entered is valid,
        the vendor is added to the system
        """
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
            vendor = Vendor(name_edit.text(), base_url_edit.text(), customer_id_edit.text(), requestor_id_edit.text(),
                            api_key_edit.text(), platform_edit.text(), local_only_check_box.checkState() == Qt.Checked,
                            description_edit.toPlainText(), companies_edit.toPlainText())

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
                GeneralUtils.show_message(message)

        button_box = vendor_dialog_ui.buttonBox
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.clicked.connect(attempt_add_vendor)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(lambda: vendor_dialog.close())

        vendor_dialog.exec_()

    def on_import_vendors_clicked(self):
        """Handles the signal emitted when the import vendors button is clicked.

        A file select dialog is shown to allow the user to select the vendors TSV file to import. The selected file is
        then imported.
        """
        file_path = GeneralUtils.choose_file(TSV_FILTER)
        if file_path:
            self.import_vendors_tsv(file_path)
            GeneralUtils.show_message(f"Import successful!")

    def on_export_vendors_clicked(self):
        """Handles the signal emitted when the export vendors button is clicked.

        A folder select dialog is shown to allow the user to select the target directory to export the vendors file to.
        A vendors TSV file containing all the vendors in the system is then exported
        """
        dir_path = GeneralUtils.choose_directory()
        if dir_path:
            self.export_vendors_tsv(dir_path)
            GeneralUtils.show_message(f"Exported as {EXPORT_VENDORS_FILE_NAME}")

    def populate_edit_vendor_view(self):
        """Populates the edit vendor view with the selected vendors's information"""
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
        """Enables or disables the elements in the edit vendor view

        :param is_enabled: This indicates whether the edit vendor view should be enabled
        """
        if is_enabled:
            self.edit_vendor_details_frame.setEnabled(True)
            self.edit_vendor_options_frame.setEnabled(True)
        else:
            self.edit_vendor_details_frame.setEnabled(False)
            self.edit_vendor_options_frame.setEnabled(False)

    def on_remove_vendor_clicked(self):
        """Handles the signal emitted when the remove vendor button is clicked.

        A confirmation dialog is shown to confirm the removal of the vendor. The vendor is removed from the system if
        confirmed
        """
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
        """Saves all the vendors in the system to disk"""
        json_string = json.dumps(self.vendors, default=lambda o: o.__dict__, indent=4)
        GeneralUtils.save_json_file(VENDORS_FILE_DIR, VENDORS_FILE_NAME, json_string)

    def sort_vendors(self):
        """Sorts the vendors alphabetically based their names"""
        self.vendors = sorted(self.vendors, key=lambda vendor: vendor.name.lower())

    def import_vendors_tsv(self, file_path):
        """Imports the vendors in a TSV file path to the system

        :param file_path: The file path of the vendors TSV file
        """
        try:
            tsv_file = open(file_path, 'r', encoding="utf-8", newline='')
            reader = csv.DictReader(tsv_file, delimiter='\t')
            for row in reader:
                if 'is_local' in row:
                    is_local = row['is_local'].lower() == "true"
                else:
                    is_local = False
                vendor = Vendor(row['name'] if 'name' in row else "",
                                row['base_url'] if 'base_url' in row else "",
                                row['customer_id'] if 'customer_id' in row else "",
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
        """Exports all vendor information as a TSV file to a directory

        :param dir_path: The directory path to export the vendors TSV file to
        """
        file_path = f"{dir_path}{EXPORT_VENDORS_FILE_NAME}"
        column_names = ["name",
                        "base_url",
                        "customer_id",
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

