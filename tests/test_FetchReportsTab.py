import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import FetchReportsTab

app = QApplication(sys.argv)
fetchReportsTab_widget = QWidget()
fetchReportsTab_widget_ui = FetchReportsTab.Ui_fetch_reports_tab()
fetchReportsTab_widget_ui.setupUi(fetchReportsTab_widget)

class FetchReportsTabTest(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(fetchReportsTab_widget_ui.Adv_Fetch_text.text(),"Advanced Fetch Reports")
        self.assertEqual(fetchReportsTab_widget_ui.label_11.text(),"Select Vendors")
        self.assertEqual(fetchReportsTab_widget_ui.label_12.text(), "Select Report Types")
        self.assertEqual(fetchReportsTab_widget_ui.label_38.text(), "Not a yearly date range")
        self.assertEqual(fetchReportsTab_widget_ui.label_41.text(), "Report(s) will be saved to:")
        self.assertEqual(fetchReportsTab_widget_ui.label_10.text(), "End Date")
        self.assertEqual(fetchReportsTab_widget_ui.label_9.text(), "Begin Date")
        self.assertEqual(fetchReportsTab_widget_ui.label_8.text(), "Date Range")
        self.assertEqual(fetchReportsTab_widget_ui.label_34.text(), "Year")
        self.assertEqual(fetchReportsTab_widget_ui.label_35.text(), "Fetch All Reports")

    def test_dateEdit(self):
        '''Test the defaults'''
        self.assertEqual(fetchReportsTab_widget_ui.begin_date_edit_fetch_month.text(),"01")
        self.assertEqual(fetchReportsTab_widget_ui.begin_date_edit_fetch_year.text(),"2020")
        self.assertEqual(fetchReportsTab_widget_ui.end_date_edit_fetch_month.text(),"01")
        self.assertEqual(fetchReportsTab_widget_ui.end_date_edit_fetch_year.text(),"2020")
        self.assertEqual(fetchReportsTab_widget_ui.All_reports_edit_fetch.text(),"2020")

    def test_pushButton(self):
        '''Test the defaults'''
        self.assertEqual(fetchReportsTab_widget_ui.deselect_vendors_button_fetch.text(),"Deselect All")
        self.assertEqual(fetchReportsTab_widget_ui.select_vendors_button_fetch.text(),"Select All")
        self.assertEqual(fetchReportsTab_widget_ui.deselect_report_types_button_fetch.text(), "Deselect All")
        self.assertEqual(fetchReportsTab_widget_ui.select_report_types_button_fetch.text(), "Select All")
        self.assertEqual(fetchReportsTab_widget_ui.report_types_help_button.text(),"?")
        self.assertEqual(fetchReportsTab_widget_ui.fetch_advanced_button.text(),"Fetch Selected Reports")
        self.assertEqual(fetchReportsTab_widget_ui.custom_dir_button.text(),"Change")
        self.assertEqual(fetchReportsTab_widget_ui.fetch_all_data_button.text(),"Fetch All Reports")

    def test_lineEdit(self):
        '''Test the defaults'''
        self.assertEqual(fetchReportsTab_widget_ui.custom_dir_edit.text(),"")

if __name__ == '__main__':
    unittest.main()
