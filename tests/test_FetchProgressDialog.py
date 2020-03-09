import unittest
import sys
from PyQt5.QtWidgets import QApplication, QDialog

from ui import FetchProgressDialog

app = QApplication(sys.argv)
fetch_progress_dialog = QDialog()
fetch_progress_dialog_ui = FetchProgressDialog.Ui_FetchProgressDialog()
fetch_progress_dialog_ui.setupUi(fetch_progress_dialog)


class FetchProgressDialogTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(fetch_progress_dialog_ui.status_label.text(), "Fetching...")
        self.assertEqual(fetch_progress_dialog_ui.progress_bar.text(), "24%")

    def test_button(self):
        okWidget = fetch_progress_dialog_ui.buttonBox.Ok
        self.assertIsNotNone(okWidget)
        retryWidget = fetch_progress_dialog_ui.buttonBox.Retry
        self.assertIsNotNone(retryWidget)
        cancelWidget = fetch_progress_dialog_ui.buttonBox.Cancel
        self.assertIsNotNone(cancelWidget)

if __name__ == '__main__':
    unittest.main()
