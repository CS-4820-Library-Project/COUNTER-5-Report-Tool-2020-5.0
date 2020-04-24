import unittest
import sys
from PyQt5.QtWidgets import QApplication, QFrame

from ui import SearchAndFrame

app = QApplication(sys.argv)

search_and_clause_frame = QFrame()
search_and_clause_frame_ui = SearchAndFrame.Ui_search_and_clause_parameter_frame()
search_and_clause_frame_ui.setupUi(search_and_clause_frame)

class SearchAndClauseFrameTests(unittest.TestCase):
    def test_button(self):
        self.assertEqual(search_and_clause_frame_ui.search_add_or_clause_button.text(),"Add \"Or\" Clause")
        self.assertEqual(search_and_clause_frame_ui.search_remove_and_clause_button.text(),"Remove \"And\" Clause")

if __name__ == '__main__':
    unittest.main()
