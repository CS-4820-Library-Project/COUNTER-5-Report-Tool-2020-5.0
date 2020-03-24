import unittest
import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui import VisualTab

app = QApplication(sys.argv)
visualTab_widget = QWidget()
visualTab_widget_ui = VisualTab.Ui_visual_tab()
visualTab_widget_ui.setupUi(visualTab_widget)

class VisualTabTests(unittest.TestCase):
    def test_defaults(self):
        '''Test the defaults'''
        self.assertEqual(visualTab_widget_ui.label_46.text(), "IMPORTANT")
        self.assertEqual(visualTab_widget_ui.label_47.text(), "Name must correspond to Report:")
        self.assertEqual(visualTab_widget_ui.label_48.text(), "Examples :   Report is PR, Name must be a Platform")
        self.assertEqual(visualTab_widget_ui.label_49.text(), "Report is DR, Name must be a Database")
        self.assertEqual(visualTab_widget_ui.label_50.text(), "Report is TR, Name must be a Title")
        self.assertEqual(visualTab_widget_ui.label_45.text(), "Select Chart Type")
        self.assertEqual(visualTab_widget_ui.label.text(), "Create Chart")
        self.assertEqual(visualTab_widget_ui.label_14.text(), "Metric Type *   :")
        self.assertEqual(visualTab_widget_ui.label_15.text(), "Required fields*")
        self.assertEqual(visualTab_widget_ui.label_8.text(), "Name *   :")
        self.assertEqual(visualTab_widget_ui.label_16.text(), "File Name")
        self.assertEqual(visualTab_widget_ui.label_36.text(), "Chart Title")
        self.assertEqual(visualTab_widget_ui.label_42.text(), "Customize Chart")
        self.assertEqual(visualTab_widget_ui.label_43.text(), "Horizontal Axis Title")
        self.assertEqual(visualTab_widget_ui.label_44.text(), "Vertical Axis Title")
        self.assertEqual(visualTab_widget_ui.search_end_year_parameter_label_2.text(), "End year")
        self.assertEqual(visualTab_widget_ui.search_report_parameter_label_2.text(), "Report")
        self.assertEqual(visualTab_widget_ui.search_start_year_parameter_label_2.text(),"Start Year")

    def test_combobox(self):
        '''Test the defaults'''
        self.assertEqual(visualTab_widget_ui.metric_Type_comboBox.isEditable(),False)
        self.assertEqual(visualTab_widget_ui.metric_Type_comboBox.currentText(),"")
        self.assertEqual(visualTab_widget_ui.search_report_parameter_combobox_2.isEditable(), False)
        self.assertEqual(visualTab_widget_ui.search_report_parameter_combobox_2.currentText(), "")

    def test_radioButrton(self):
        '''Test the defaults'''
        self.assertEqual(visualTab_widget_ui.radioButton.text(),"Horizontal Bar")
        self.assertEqual(visualTab_widget_ui.radioButton_3.text(), "Vertical Bar")
        self.assertEqual(visualTab_widget_ui.radioButton_4.text(), "Line")

    def test_lineEdit(self):
        '''Test the defaults'''
        self.assertEqual(visualTab_widget_ui.name_lineEdit.text(),"")
        self.assertEqual(visualTab_widget_ui.chart_title_lineEdit.text(), "")
        self.assertEqual(visualTab_widget_ui.file_name_lineEdit.text(), "")
        self.assertEqual(visualTab_widget_ui.horizontal_axis_lineEdit.text(), "")
        self.assertEqual(visualTab_widget_ui.vertical_axis_lineEdit.text(), "")

    def test_pushButton(self):
        '''Test the defaults'''
        self.assertEqual(visualTab_widget_ui.create_chart_button.text(),"Create Chart")

    def test_dateEdit(self):
        '''Test the defaults'''
        self.assertEqual(visualTab_widget_ui.search_end_year_parameter_dateedit_2.text(),"2000")
        self.assertEqual(visualTab_widget_ui.search_start_year_parameter_dateedit_2.text(),"2000")

if __name__ == '__main__':
    unittest.main()
