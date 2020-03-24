import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import FetchSpecialReportsTab

app = QApplication(sys.argv)
fetchSpecialReportsTab_widget = QWidget()
fetchSpecialReportsTab_widget_ui = FetchSpecialReportsTab.Ui_fetch_special_reports_tab()
fetchSpecialReportsTab_widget_ui.setupUi(fetchSpecialReportsTab_widget)

class FetchSpecialReportsTabTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(fetchSpecialReportsTab_widget_ui.label_20.text(),"Select Report Type")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.label_21.text(), "Select Vendors")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.label_14.text(),"Options")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.label_25.text(),"End Date")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.label_24.text(),"Begin Date")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.label_15.text(),"Date Range")

    def test_radioButrton(self):
        '''Test the defaults'''
        self.assertEqual(fetchSpecialReportsTab_widget_ui.dr_radio_button.text(),"DR")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.pr_radio_button.text(), "PR")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.tr_radio_button.text(), "TR")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.ir_radio_button.text(), "IR")

    def test_pushButton(self):
        '''Test the defaults'''
        self.assertEqual(fetchSpecialReportsTab_widget_ui.deselect_vendors_button_special.text(),"Deselect All")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.select_vendors_button_special.text(),"Select All")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.fetch_special_data_button.text(),"Fetch Special Report")

    def test_dateEdit(self):
        '''Test the defaults'''
        self.assertEqual(fetchSpecialReportsTab_widget_ui.begin_date_edit_special_month.text(),"01")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.begin_date_edit_special_year.text(),"2020")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.end_date_edit_special_month.text(),"01")
        self.assertEqual(fetchSpecialReportsTab_widget_ui.end_date_edit_special_year.text(),"2020")

if __name__ == '__main__':
    unittest.main()
