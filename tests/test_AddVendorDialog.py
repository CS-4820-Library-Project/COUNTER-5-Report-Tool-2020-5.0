import sys
import unittest
from PyQt5.QtWidgets import QApplication, QDialog


from ui import AddVendorDialog

app = QApplication(sys.argv)

vendor_dialog = QDialog()
vendor_dialog_ui = AddVendorDialog.Ui_addVendorDialog()
vendor_dialog_ui.setupUi(vendor_dialog)

class AddVendorDialogTests(unittest.TestCase):

    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(vendor_dialog_ui.nameEdit.text(), "")
        self.assertEqual(vendor_dialog_ui.customerIdEdit.text(), "")
        self.assertEqual(vendor_dialog_ui.baseUrlEdit.text(), "")
        self.assertEqual(vendor_dialog_ui.requestorIdEdit.text(), "")
        self.assertEqual(vendor_dialog_ui.apiKeyEdit.text(), "")
        self.assertEqual(vendor_dialog_ui.platformEdit.text(), "")
        self.assertEqual(vendor_dialog_ui.local_only_check_box.checkState(), False)
        self.assertEqual(vendor_dialog_ui.descriptionEdit.toPlainText(), "")

    def test_ok_button(self):
        okWidget = vendor_dialog_ui.buttonBox.Ok
        self.assertIsNotNone(okWidget)
        cancelWidget = vendor_dialog_ui.buttonBox.Cancel
        self.assertIsNotNone(cancelWidget)

if __name__ == "__main__":
        unittest.main()