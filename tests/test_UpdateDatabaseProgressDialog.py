import unittest
import sys
from PyQt5.QtWidgets import QApplication, QDialog

from ui import UpdateDatabaseProgressDialog

app = QApplication(sys.argv)
update_database_progress_dialog = QDialog()
update_database_progress_dialog_ui = UpdateDatabaseProgressDialog.Ui_restore_database_dialog()
update_database_progress_dialog_ui.setupUi(update_database_progress_dialog)

class UpdateDatabaseProgressDialogTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(update_database_progress_dialog_ui.status_label.text(),"Status")

    def test_buttonBox(self):
        '''Test the defaults'''
        okWidget = update_database_progress_dialog_ui.buttonBox.Ok
        self.assertIsNotNone(okWidget)
        cancelWidget = update_database_progress_dialog_ui.buttonBox.Cancel
        self.assertIsNotNone(cancelWidget)

    def test_progressBar(self):
        '''Test the defaults'''
        self.assertEqual(update_database_progress_dialog_ui.progressbar.text(),"0%")
        self.assertEqual(update_database_progress_dialog_ui.progressbar.value(), 0)

if __name__ == '__main__':
    unittest.main()
