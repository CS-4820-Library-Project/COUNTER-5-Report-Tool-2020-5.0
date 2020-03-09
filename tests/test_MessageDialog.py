import unittest
import sys
from PyQt5.QtWidgets import QApplication, QDialog

from ui import MessageDialog

app = QApplication(sys.argv)
message_dialog = QDialog()
message_dialog_ui = MessageDialog.Ui_message_dialog()
message_dialog_ui.setupUi(message_dialog)

class MessageDialogTest(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(message_dialog_ui.message_label.text(),"Message!")

    def test_button(self):
        okWidget = message_dialog_ui.buttonBox.Ok
        self.assertIsNotNone(okWidget)

if __name__ == '__main__':
    unittest.main()
