import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import ImportReportTab

app = QApplication(sys.argv)
importReportTab_widget = QWidget()
importReportTab_widget_ui = ImportReportTab.Ui_import_report_tab()
importReportTab_widget_ui.setupUi(importReportTab_widget)

class ImportReportTabTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(importReportTab_widget_ui.label_17.text(),"Select Report Type")
        self.assertEqual(importReportTab_widget_ui.label_18.text(),"Select Vendor")
        self.assertEqual(importReportTab_widget_ui.label_19.text(),"Report Year")
        self.assertEqual(importReportTab_widget_ui.label_16.text(), "Date")
        self.assertEqual(importReportTab_widget_ui.label_36.text(),"Target Report File")

    def test_dateEdit(self):
        '''Test the defaults'''
        self.assertEqual(importReportTab_widget_ui.report_year_date_edit.text(),"2000")

    def test_pushButton(self):
        '''Test the defaults'''
        self.assertEqual(importReportTab_widget_ui.select_file_button.text(),"Select File")
        self.assertEqual(importReportTab_widget_ui.import_report_button.text(),"Import Selected Report")

    def test_lineEdit(self):
        '''Test the defaults'''
        self.assertEqual(importReportTab_widget_ui.selected_file_edit.text(),"")

if __name__ == '__main__':
    unittest.main()
