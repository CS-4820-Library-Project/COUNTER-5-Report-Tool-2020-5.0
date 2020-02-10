import sys
import unittest
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QLabel, QDialog

from ui import AddVendorDialog

app = QApplication(sys.argv)

class AddVendorDialogTests(unittest.TestCase):

    def test_defaults(self):
        '''Test the defaults'''
        vendor_dialog = QDialog()
        vendor_dialog_ui = AddVendorDialog.Ui_addVendorDialog()
        vendor_dialog_ui.setupUi(vendor_dialog)

        self.assertEqual(vendor_dialog_ui.nameEdit.text(), "")


if __name__ == "__main__":
        unittest.main()