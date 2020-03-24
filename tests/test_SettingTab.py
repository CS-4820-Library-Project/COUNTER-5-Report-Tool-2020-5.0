import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import SettingsTab

app = QApplication(sys.argv)
settingsTab_widget = QWidget()
settingsTab_widget_ui = SettingsTab.Ui_settings_tab()
settingsTab_widget_ui.setupUi(settingsTab_widget)

class SettingsTabTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(settingsTab_widget_ui.label_25.text(), "Yearly Reports Directory")
        self.assertEqual(settingsTab_widget_ui.label_29.text(),"Other Reports Directory")
        self.assertEqual(settingsTab_widget_ui.label_30.text(), "Report Request Interval")
        self.assertEqual(settingsTab_widget_ui.label_31.text(), "Concurrent Vendors")
        self.assertEqual(settingsTab_widget_ui.label_32.text(), "Concurrent Reports")
        self.assertEqual(settingsTab_widget_ui.label_33.text(), "Empty Cell")
        self.assertEqual(settingsTab_widget_ui.label_37.text(), "Request Timeout")
        self.assertEqual(settingsTab_widget_ui.label_73.text(), "User Agent")
        self.assertEqual(settingsTab_widget_ui.label_24.text(),"Reports")
        self.assertEqual(settingsTab_widget_ui.label_26.text(),"Search")

    def test_pushButton(self):
        '''Test the defaults'''
        self.assertEqual(settingsTab_widget_ui.save_button.text(),"Save Changes")
        self.assertEqual(settingsTab_widget_ui.concurrent_reports_help_button.text(),"?")
        self.assertEqual(settingsTab_widget_ui.concurrent_vendors_help_button.text(), "?")
        self.assertEqual(settingsTab_widget_ui.empty_cell_help_button.text(), "?")
        self.assertEqual(settingsTab_widget_ui.other_directory_help_button.text(), "?")
        self.assertEqual(settingsTab_widget_ui.request_interval_help_button.text(), "?")
        self.assertEqual(settingsTab_widget_ui.request_timeout_help_button.text(), "?")
        self.assertEqual(settingsTab_widget_ui.other_directory_button.text(),"Choose")
        self.assertEqual(settingsTab_widget_ui.yearly_directory_button.text(), "Choose")
        self.assertEqual(settingsTab_widget_ui.user_agent_help_button.text(), "?")
        self.assertEqual(settingsTab_widget_ui.yearly_directory_help_button.text(), "?")
        self.assertEqual(settingsTab_widget_ui.settings_restore_database_button.text(),"Restore Database")

    def test_spinBox(self):
        '''Test the defaults'''
        self.assertEqual(settingsTab_widget_ui.concurrent_reports_spin_box.value(),0)
        self.assertEqual(settingsTab_widget_ui.concurrent_vendors_spin_box.value(), 0)
        self.assertEqual(settingsTab_widget_ui.request_interval_spin_box.value(), 0)
        self.assertEqual(settingsTab_widget_ui.request_timeout_spin_box.value(), 0)

    def test_lineEdit(self):
        '''Test the defaults'''
        self.assertEqual(settingsTab_widget_ui.empty_cell_edit.text(),"")
        self.assertEqual(settingsTab_widget_ui.other_directory_edit.text(),"")
        self.assertEqual(settingsTab_widget_ui.user_agent_edit.text(),"")
        self.assertEqual(settingsTab_widget_ui.yearly_directory_edit.text(),"")

if __name__ == '__main__':
    unittest.main()
