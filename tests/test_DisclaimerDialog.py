import unittest
import sys
from PyQt5.QtWidgets import QApplication, QDialog

from ui import DisclaimerDialog

app = QApplication(sys.argv)
disclaimer_dialog = QDialog()
disclaimer_dialog_ui = DisclaimerDialog.Ui_dialog()
disclaimer_dialog_ui.setupUi(disclaimer_dialog)

class DisclaimerDialogTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(disclaimer_dialog_ui.label.text(),"Only reports supported by selected vendor will be retrieved!")

    def test_button(self):
        okWidget = disclaimer_dialog_ui.buttonBox.Ok
        self.assertIsNotNone(okWidget)

if __name__ == '__main__':
    unittest.main()
