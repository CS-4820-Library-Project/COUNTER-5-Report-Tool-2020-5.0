import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import VendorResultsWidget

app = QApplication(sys.argv)
vendor_results_widget = QWidget()
vendor_results_ui = VendorResultsWidget.Ui_VendorResultsWidget()
vendor_results_ui.setupUi(vendor_results_widget)

class VendorResultsWidgetTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(vendor_results_ui.status_label.text(),"Success")
        self.assertEqual(vendor_results_ui.vendor_label.text(),"Bioone")


    def test_button(self):
        self.assertEqual(vendor_results_ui.collapse_button.text(), "Collapse")
        self.assertEqual(vendor_results_ui.expand_button.text(), "Expand")

if __name__ == '__main__':
    unittest.main()
