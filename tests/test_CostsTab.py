import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import CostsTab

app = QApplication(sys.argv)
costTab_widget = QWidget()
costTab_widget_ui = CostsTab.Ui_costs_tab()
costTab_widget_ui.setupUi(costTab_widget)

class CostsTabTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(costTab_widget_ui.costs_name_parameter_label.text(),"Name")
        self.assertEqual(costTab_widget_ui.costs_report_parameter_label.text(), "Report")
        self.assertEqual(costTab_widget_ui.costs_vendor_parameter_label.text(),"Vendor")
        self.assertEqual(costTab_widget_ui.costs_year_parameter_label.text(),"Year")
        self.assertEqual(costTab_widget_ui.costs_cost_in_local_currency_label.text(),"Cost in Local Currency")
        self.assertEqual(costTab_widget_ui.costs_cost_in_local_currency_with_tax_label.text(),"Cost in Local Currency with Tax")
        self.assertEqual(costTab_widget_ui.costs_cost_in_original_currency_label.text(),"Cost in Original Currency")
        self.assertEqual(costTab_widget_ui.costs_original_currency_label.text(),"Original Currency")

    def test_doublesPinBox(self):
        '''Test the defaults'''
        self.assertEqual(costTab_widget_ui.costs_cost_in_local_currency_doublespinbox.text(),"")
        self.assertEqual(costTab_widget_ui.costs_cost_in_local_currency_with_tax_doublespinbox.text(),"")
        self.assertEqual(costTab_widget_ui.costs_cost_in_original_currency_doublespinbox.text(),"")

    def test_combobox(self):
        '''Test the defaults'''
        self.assertEqual(costTab_widget_ui.costs_name_parameter_combobox.isEditable(),True)
        self.assertEqual(costTab_widget_ui.costs_report_parameter_combobox.isEditable(),False)
        self.assertEqual(costTab_widget_ui.costs_vendor_parameter_combobox.isEditable(),False)
        self.assertEqual(costTab_widget_ui.costs_original_currency_value_combobox.isEditable(),True)
        self.assertEqual(costTab_widget_ui.costs_name_parameter_combobox.currentText(), "")
        self.assertEqual(costTab_widget_ui.costs_report_parameter_combobox.currentText(), "")
        self.assertEqual(costTab_widget_ui.costs_vendor_parameter_combobox.currentText(), "")
        self.assertEqual(costTab_widget_ui.costs_original_currency_value_combobox.currentText(), "")

    def test_dateEdit(self):
        '''Test the defaults'''
        self.assertEqual(costTab_widget_ui.costs_year_parameter_dateedit.text(),"2000")

    def test_button(self):
        '''Test the defaults'''
        self.assertEqual(costTab_widget_ui.costs_clear_button.text(), "Clear")
        self.assertEqual(costTab_widget_ui.costs_insert_button.text(), "Insert")
        self.assertEqual(costTab_widget_ui.costs_load_button.text(), "Load")
        self.assertEqual(costTab_widget_ui.costs_load_from_disk_button.text(), "Load From Disk")

if __name__ == '__main__':
    unittest.main()
