import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import ReportResultWidget

app = QApplication(sys.argv)
report_result_widget = QWidget()
report_result_ui = ReportResultWidget.Ui_ReportResultWidget()
report_result_ui.setupUi(report_result_widget)

class ReportResultWidgetTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(report_result_ui.file_label.text(),"Saved as: Bleh.tsv")
        self.assertEqual(report_result_ui.message_label.text(),"No exception messages")
        self.assertEqual(report_result_ui.label_6.text(),"Retry")
        self.assertEqual(report_result_ui.success_label.text(),"Failed!")
        self.assertEqual(report_result_ui.report_type_label.text(),"TR_J1")

    def test_button(self):
        self.assertEqual(report_result_ui.folder_button.text(),"")

    def test_checkBox(self):
        self.assertEqual(report_result_ui.retry_check_box.checkState(),False)

if __name__ == '__main__':
    unittest.main()
