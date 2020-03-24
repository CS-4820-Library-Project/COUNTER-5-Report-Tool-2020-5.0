import unittest
import sys
from PyQt5.QtWidgets import QApplication, QDialog

from ui import ReportTypeDialog

app = QApplication(sys.argv)
report_type_dialog = QDialog()
report_type_dialog_ui = ReportTypeDialog.Ui_report_type_dialog()
report_type_dialog_ui.setupUi(report_type_dialog)

class ReportTypeDialogTests(unittest.TestCase):
    def test_comboBox(self):
        '''Test the defaults'''
        self.assertEqual(report_type_dialog_ui.report_type_combobox.isEditable(),False)
        self.assertEqual(report_type_dialog_ui.report_type_combobox.currentText(),"")

    def test_buttonBox(self):
        '''Test the defaults'''
        okWidget = report_type_dialog_ui.buttonBox.Ok
        self.assertIsNotNone(okWidget)
        cancelWidget = report_type_dialog_ui.buttonBox.Cancel
        self.assertIsNotNone(cancelWidget)

if __name__ == '__main__':
    unittest.main()
