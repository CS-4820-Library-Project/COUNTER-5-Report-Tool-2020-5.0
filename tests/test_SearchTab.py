import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import SearchTab

app = QApplication(sys.argv)
searchTab_widget = QWidget()
searchTab_widget_ui = SearchTab.Ui_search_tab()
searchTab_widget_ui.setupUi(searchTab_widget)

class SearchTabTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(searchTab_widget_ui.search_end_year_parameter_label.text(),"End year")

    def test_radioButton(self):
        '''Test the defaults'''
        self.assertEqual(searchTab_widget_ui.dont_open_radioButton.text(),"Don't Open")
        self.assertEqual(searchTab_widget_ui.open_both_radioButton.text(), "Open Both")
        self.assertEqual(searchTab_widget_ui.open_file_radioButton.text(), "Open File")
        self.assertEqual(searchTab_widget_ui.open_folder_radioButton.text(), "Open Folder")
        self.assertEqual(searchTab_widget_ui.search_report_parameter_label.text(),"Report")
        self.assertEqual(searchTab_widget_ui.search_start_year_parameter_label.text(),"Start Year")

    def test_pushButton(self):
        '''Test the defaults'''
        self.assertEqual(searchTab_widget_ui.search_button.text(),"Search")
        self.assertEqual(searchTab_widget_ui.search_export_button.text(),"Export Search")
        self.assertEqual(searchTab_widget_ui.search_import_button.text(),"Import Search")
        self.assertEqual(searchTab_widget_ui.search_add_and_button.text(),"Add \"And\" Clause")

    def test_dateEdit(self):
        '''Test the defaults'''
        self.assertEqual(searchTab_widget_ui.search_end_year_parameter_dateedit.text(),"2000")
        self.assertEqual(searchTab_widget_ui.search_start_year_parameter_dateedit.text(),"2000")

    def test_comboBox(self):
        '''Test the defaults'''
        self.assertEqual(searchTab_widget_ui.search_report_parameter_combobox.isEditable(), False)
        self.assertEqual(searchTab_widget_ui.search_report_parameter_combobox.currentText(), "")

if __name__ == '__main__':
    unittest.main()
