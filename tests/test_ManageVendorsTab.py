import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import ManageVendorsTab

app = QApplication(sys.argv)
manageVendorsTab_widget = QWidget()
manageVendorsTab_widget_ui = ManageVendorsTab.Ui_manage_vendors_tab()
manageVendorsTab_widget_ui.setupUi(manageVendorsTab_widget)

class ManageVendorsTabTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(manageVendorsTab_widget_ui.label_13.text(),"Select Vendor")
        self.assertEqual(manageVendorsTab_widget_ui.companiesText.text(),"External Companies")
        self.assertEqual(manageVendorsTab_widget_ui.label.text(),"Name")
        self.assertEqual(manageVendorsTab_widget_ui.label_2.text(),"Customer ID")
        self.assertEqual(manageVendorsTab_widget_ui.label_28.text(), "Description")
        self.assertEqual(manageVendorsTab_widget_ui.label_3.text(),"Base URL")
        self.assertEqual(manageVendorsTab_widget_ui.label_39.text(), "Local Only Vendor")
        self.assertEqual(manageVendorsTab_widget_ui.label_4.text(),"Requestor ID")
        self.assertEqual(manageVendorsTab_widget_ui.label_5.text(), "API Key")
        self.assertEqual(manageVendorsTab_widget_ui.label_6.text(), "Platform")
        self.assertEqual(manageVendorsTab_widget_ui.name_validation_label.text(),"Validation label")
        self.assertEqual(manageVendorsTab_widget_ui.url_validation_label.text(),"Validation label")

    def test_pushButton(self):
        '''Test the defaults'''
        self.assertEqual(manageVendorsTab_widget_ui.addVendorButton.text(),"Add New Vendor")
        self.assertEqual(manageVendorsTab_widget_ui.exportVendorsButton.text(),"Export Vendors")
        self.assertEqual(manageVendorsTab_widget_ui.importVendorsButton.text(),"Import Vendors")
        self.assertEqual(manageVendorsTab_widget_ui.removeVendorButton.text(), "Remove Vendor")
        self.assertEqual(manageVendorsTab_widget_ui.saveVendorChangesButton.text(), "Save Changes")
        self.assertEqual(manageVendorsTab_widget_ui.undoVendorChangesButton.text(), "Undo Changes")

    def test_lineEdit(self):
        '''Test the defaults'''
        self.assertEqual(manageVendorsTab_widget_ui.apiKeyEdit.text(),"")
        self.assertEqual(manageVendorsTab_widget_ui.baseUrlEdit.text(), "")
        self.assertEqual(manageVendorsTab_widget_ui.companiesEdit.toPlainText(), "")
        self.assertEqual(manageVendorsTab_widget_ui.customerIdEdit.text(), "")
        self.assertEqual(manageVendorsTab_widget_ui.descriptionEdit.toPlainText(), "")
        self.assertEqual(manageVendorsTab_widget_ui.nameEdit.text(), "")
        self.assertEqual(manageVendorsTab_widget_ui.platformEdit.text(), "")
        self.assertEqual(manageVendorsTab_widget_ui.requestorIdEdit.text(), "")

    def test_checkBox(self):
        '''Test the defaults'''
        self.assertEqual(manageVendorsTab_widget_ui.local_only_check_box.isChecked(),False)

if __name__ == '__main__':
    unittest.main()
