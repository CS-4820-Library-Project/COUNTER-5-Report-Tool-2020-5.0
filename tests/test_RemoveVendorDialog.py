import unittest
import sys
from PyQt5.QtWidgets import QApplication, QDialog

from ui import RemoveVendorDialog

app = QApplication(sys.argv)
remove_vendor_dialog = QDialog()
remove_vendor_dialog_ui = RemoveVendorDialog.Ui_dialog_remove()
remove_vendor_dialog_ui.setupUi(remove_vendor_dialog)

class RemoveVendorDialogTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(remove_vendor_dialog_ui.label.text(),
                         "Are you sure you want to remove this vendor?")

    def test_button(self):
        okWidget = remove_vendor_dialog_ui.buttonBox.Ok
        self.assertIsNotNone(okWidget)

if __name__ == '__main__':
    unittest.main()
