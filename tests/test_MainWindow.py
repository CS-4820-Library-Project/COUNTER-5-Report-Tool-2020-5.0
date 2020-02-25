import sys
import unittest
from PyQt5.QtWidgets import QApplication, QMainWindow

from ui import MainWindow
app = QApplication(sys.argv)

main_window = QMainWindow()
main_window_ui = MainWindow.Ui_mainWindow()
main_window_ui.setupUi(main_window)

class MyTestCase(unittest.TestCase):

    def test_addVendorButton(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.addVendorButton.text(), "Add New Vendor")

    def test_edit_vendor_options_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.removeVendorButton.text(), "Remove Vendor")
        self.assertEqual(main_window_ui.saveVendorChangesButton.text(), "Save Changes")
        self.assertEqual(main_window_ui.undoVendorChangesButton.text(), "Undo Changes")

    def test_select_vendor_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.deselect_vendors_button_fetch.text(), "Deselect All")
        self.assertEqual(main_window_ui.select_vendors_button_fetch.text(), "Select All")
        self.assertEqual(main_window_ui.deselect_vendors_button_special.text(), "Deselect All")
        self.assertEqual(main_window_ui.select_vendors_button_special.text(), "Select All")

    def test_select_report_types_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.deselect_report_types_button_fetch.text(), "Deselect All")
        self.assertEqual(main_window_ui.select_report_types_button_fetch.text(), "Select All")
        self.assertEqual(main_window_ui.toolButton.text(), "?")

    def test_fetch_advanced_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.fetch_advanced_button.text(), "Fetch Selected Reports")

    def test_fetch_all_data_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.fetch_all_data_button.text(), "Fetch All Reports")

    def test_fetch_speical_data_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.fetch_special_data_button.text(), "Fetch Special Report")

    def test_select_file_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.select_file_button.text(), "Select File")
        self.assertEqual(main_window_ui.import_file_button.text(), "Import Selected File")

    def test_search_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.search_button.text(), "Search")

    def test_setting_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.concurrent_reports_help_button.text(), "?")
        self.assertEqual(main_window_ui.concurrent_vendors_help_button.text(), "?")
        self.assertEqual(main_window_ui.empty_cell_help_button.text(), "?")
        self.assertEqual(main_window_ui.general_json_directory_button.text(), "Choose Folder...")
        self.assertEqual(main_window_ui.general_json_directory_help_button.text(), "?")
        self.assertEqual(main_window_ui.general_tsv_directory_help_button.text(), "?")
        self.assertEqual(main_window_ui.general_tsv_directory_button.text(), "Choose Folder...")
        self.assertEqual(main_window_ui.request_interval_help_button.text(), "?")
        self.assertEqual(main_window_ui.special_json_directory_button.text(), "Choose Folder...")
        self.assertEqual(main_window_ui.special_json_directory_help_button.text(), "?")
        self.assertEqual(main_window_ui.special_tsv_directory_button.text(), "Choose Folder...")
        self.assertEqual(main_window_ui.special_tsv_directory_help_button.text(), "?")



    def test_date_edit(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.begin_date_edit_fetch.text(), "2020-01")
        self.assertEqual(main_window_ui.end_date_edit_fetch.text(), "2020-01")
        self.assertEqual(main_window_ui.All_reports_edit_fetch.text(), "2020")
        self.assertEqual(main_window_ui.begin_date_edit_special.text(), "2000-01")
        self.assertEqual(main_window_ui.end_date_edit_special.text(), "2000-01")
        self.assertEqual(main_window_ui.report_year_date_edit.text(), "2000")

    def test_radio_button(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.dr_radio_button.isChecked(), False)
        self.assertEqual(main_window_ui.ir_radio_button.isChecked(), False)
        self.assertEqual(main_window_ui.tr_radio_button.isChecked(), False)
        self.assertEqual(main_window_ui.pr_radio_button.isChecked(), True)

    def test_label(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.label.text(), "Name")
        self.assertEqual(main_window_ui.label_2.text(), "Customer ID")
        self.assertEqual(main_window_ui.label_3.text(), "Base URL")
        self.assertEqual(main_window_ui.label_4.text(), "Requestor ID")
        self.assertEqual(main_window_ui.label_5.text(), "API Key")
        self.assertEqual(main_window_ui.label_6.text(), "Platform")
        self.assertEqual(main_window_ui.label_7.text(), "Edit Vendor")
        self.assertEqual(main_window_ui.label_8.text(), "PAGE IS IN DEVELOPMENT")
        self.assertEqual(main_window_ui.label_9.text(), "Begin Date")
        self.assertEqual(main_window_ui.label_10.text(), "End Date")
        self.assertEqual(main_window_ui.label_11.text(), "Select Vendors")
        self.assertEqual(main_window_ui.label_12.text(), "Select Report Types")
        self.assertEqual(main_window_ui.label_13.text(), "Select Vendor")
        self.assertEqual(main_window_ui.label_14.text(), "Search Keyword(s)")
        self.assertEqual(main_window_ui.label_15.text(), "Search Results")
        self.assertEqual(main_window_ui.label_16.text(), "Search by:")
        self.assertEqual(main_window_ui.label_17.text(), "Select Report Type")
        self.assertEqual(main_window_ui.label_18.text(), "Select Vendor")
        self.assertEqual(main_window_ui.label_19.text(), "Report Year")
        self.assertEqual(main_window_ui.label_20.text(), "Select Report Type")
        self.assertEqual(main_window_ui.label_21.text(), "Select Vendors")
        self.assertEqual(main_window_ui.label_22.text(), "Begin Date")
        self.assertEqual(main_window_ui.label_23.text(), "End Date")
        self.assertEqual(main_window_ui.label_24.text(), "Reports")
        self.assertEqual(main_window_ui.label_25.text(), "General Reports Directory")
        self.assertEqual(main_window_ui.label_26.text(), "Search")
        self.assertEqual(main_window_ui.label_27.text(), "[In Development]")
        self.assertEqual(main_window_ui.label_28.text(), "Description")
        self.assertEqual(main_window_ui.label_29.text(), "Special Reports Directory")
        self.assertEqual(main_window_ui.label_30.text(), "Report Request Interval")
        self.assertEqual(main_window_ui.label_31.text(), "Concurrent Vendor Processes")
        self.assertEqual(main_window_ui.label_32.text(), "Concurrent Report Processes")
        self.assertEqual(main_window_ui.label_33.text(), "Empty Cell")
        self.assertEqual(main_window_ui.label_34.text(), "Year")
        self.assertEqual(main_window_ui.label_35.text(), "Fetch All Reports")
        self.assertEqual(main_window_ui.label_36.text(), "PAGE IS IN DEVELOPMENT")
        self.assertEqual(main_window_ui.label_37.text(), "General JSON Directory")
        self.assertEqual(main_window_ui.label_38.text(), "Special JSON Directory")
        self.assertEqual(main_window_ui.label_39.text(), "Local Only Vendor")
        self.assertEqual(main_window_ui.Adv_Fetch_text.text(), "Advanced Fetch Reports")
        self.assertEqual(main_window_ui.selected_file_label.text(), "None")

    def test_check_box(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.local_only_check_box.checkState(), False)
        self.assertEqual(main_window_ui.isbn_checkbox.checkState(), False)
        self.assertEqual(main_window_ui.issn_checkbox.checkState(), False)
        self.assertEqual(main_window_ui.title_checkbox.checkState(), False)

    def test_line_edit(self):
        '''Test the defaults'''
        self.assertEqual(main_window_ui.apiKeyEdit.text(),"")
        self.assertEqual(main_window_ui.baseUrlEdit.text(), "")
        self.assertEqual(main_window_ui.customerIdEdit.text(), "")
        self.assertEqual(main_window_ui.descriptionEdit.toPlainText(), "")
        self.assertEqual(main_window_ui.nameEdit.text(), "")
        self.assertEqual(main_window_ui.platformEdit.text(), "")
        self.assertEqual(main_window_ui.requestorIdEdit.text(), "")
        self.assertEqual(main_window_ui.search_term_edit.text(), "")
        self.assertEqual(main_window_ui.concurrent_reports_edit.text(), "")
        self.assertEqual(main_window_ui.concurrent_vendors_edit.text(), "")
        self.assertEqual(main_window_ui.empty_cell_edit.text(), "")
        self.assertEqual(main_window_ui.general_json_directory_edit.text(), "")
        self.assertEqual(main_window_ui.general_tsv_directory_edit.text(), "")
        self.assertEqual(main_window_ui.request_interval_edit.text(), "")
        self.assertEqual(main_window_ui.special_json_directory_edit.text(), "")
        self.assertEqual(main_window_ui.special_tsv_directory_edit.text(), "")
        self.assertEqual(main_window_ui.save_location_edit_fetch_2.text(), "[In Development]")

if __name__ == '__main__':
    unittest.main()
