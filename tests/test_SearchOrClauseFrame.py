import unittest
import sys
from PyQt5.QtWidgets import QApplication, QFrame

from ui import SearchOrClauseFrame

app = QApplication(sys.argv)

search_or_clause_frame = QFrame()
search_or_clause_frame_ui = SearchOrClauseFrame.Ui_search_or_clause_parameter_frame()
search_or_clause_frame_ui.setupUi(search_or_clause_frame)

class SearchOrClauseFrameTests(unittest.TestCase):
    def test_button(self):
        self.assertEqual(search_or_clause_frame_ui.search_remove_or_clause_button.text(),"Remove \"Or\" Clause")

    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(search_or_clause_frame_ui.search_value_parameter_lineedit.text(), "")

    def test_combo_box(self):
        self.assertEqual(search_or_clause_frame_ui.search_comparison_parameter_combobox.currentText(),"")
        self.assertEqual(search_or_clause_frame_ui.search_field_parameter_combobox.currentText(),"")

if __name__ == '__main__':
    unittest.main()
