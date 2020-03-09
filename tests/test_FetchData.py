import sys
import unittest
import FetchData
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt

from ui import MessageDialog

app = QApplication(sys.argv)

message_dialog = QDialog()
message_dialog_ui = MessageDialog.Ui_message_dialog()
message_dialog_ui.setupUi(message_dialog)

class FetchDataTest(unittest.TestCase):

    def test_get_major_report_type(self):
        '''Test the report_type: PR'''
        result = FetchData.get_major_report_type("PR")
        self.assertEqual(result, FetchData.MajorReportType.PLATFORM)
        result = FetchData.get_major_report_type("PR_P1")
        self.assertEqual(result, FetchData.MajorReportType.PLATFORM)

        '''Test the report_type: DR'''
        result = FetchData.get_major_report_type("DR")
        self.assertEqual(result, FetchData.MajorReportType.DATABASE)
        result = FetchData.get_major_report_type("DR_D1")
        self.assertEqual(result, FetchData.MajorReportType.DATABASE)
        result = FetchData.get_major_report_type("DR_D2")
        self.assertEqual(result, FetchData.MajorReportType.DATABASE)

        '''Test the report_type: TR'''
        result = FetchData.get_major_report_type("TR")
        self.assertEqual(result, FetchData.MajorReportType.TITLE)
        result = FetchData.get_major_report_type("TR_B1")
        self.assertEqual(result, FetchData.MajorReportType.TITLE)
        result = FetchData.get_major_report_type("TR_B2")
        self.assertEqual(result, FetchData.MajorReportType.TITLE)
        result = FetchData.get_major_report_type("TR_B3")
        self.assertEqual(result, FetchData.MajorReportType.TITLE)
        result = FetchData.get_major_report_type("TR_J1")
        self.assertEqual(result, FetchData.MajorReportType.TITLE)
        result = FetchData.get_major_report_type("TR_J2")
        self.assertEqual(result, FetchData.MajorReportType.TITLE)
        result = FetchData.get_major_report_type("TR_J3")
        self.assertEqual(result, FetchData.MajorReportType.TITLE)
        result = FetchData.get_major_report_type("TR_J4")
        self.assertEqual(result, FetchData.MajorReportType.TITLE)

        '''Test the report_type: IR'''
        result = FetchData.get_major_report_type("IR")
        self.assertEqual(result, FetchData.MajorReportType.ITEM)
        result = FetchData.get_major_report_type("IR_A1")
        self.assertEqual(result, FetchData.MajorReportType.ITEM)
        result = FetchData.get_major_report_type("IR_M1")
        self.assertEqual(result, FetchData.MajorReportType.ITEM)

        '''Test the defaults'''
        result = FetchData.get_major_report_type("")
        self.assertEqual(result, None)

        '''Test the random str'''
        result = FetchData.get_major_report_type("123abc")
        self.assertEqual(result, None)

    def test_show_message(self):
        print("Test string: abc")
        self.assertEqual(FetchData.show_message("abc"), None)
        print("Test string: 123")
        self.assertEqual(FetchData.show_message("123"), None)

    def test_SupportedReportModel(self):
        testJson = {"Report_Name": "Platform Master Report", "Report_ID": "PR", "Release": "5","Report Description": "A customizable report that summarizes activity across a provider�s platforms and allows the user to apply filters and select other configuration options."}
        test = FetchData.SupportedReportModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.SupportedReportModel))
        self.assertEqual(test.report_id,"PR")

    def test_PeriodModel(self):
        testJson =  {"Begin_Date": "2019-01-01", "End_Date": "2020-02-29"}
        test = FetchData.PeriodModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.PeriodModel))
        self.assertEqual(test.begin_date, "2019-01-01")
        self.assertEqual(test.end_date, "2020-02-29")

    def test_InstanceModel(self):
        testJson = {"Metric_Type":"Searches_Platform", "Count":142}
        test = FetchData.InstanceModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.InstanceModel))
        self.assertEqual(test.metric_type, "Searches_Platform")
        self.assertEqual(test.count, 142)

    def test_PerformanceModel(self):
        testJson = {"Period":{"Begin_Date":"2019-01-01","End_Date":"2019-01-31"},"Instance":[{"Metric_Type":"Searches_Platform","Count":142}]}
        test = FetchData.PerformanceModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.PerformanceModel))
        print(test.instances)
        print(test.period)

    def test_TypeValueModel(self):
        testJson = {"Type":"Proprietary","Value":"achs:2298202"}
        test = FetchData.TypeValueModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.TypeValueModel))
        self.assertEqual(test.item_type, "Proprietary")
        self.assertEqual(test.value, "achs:2298202")

    def test_NameValueModel(self):
        testJson = {"Name":"End_Date","Value":"2020-02-29"}
        test = FetchData.NameValueModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.NameValueModel))
        self.assertEqual(test.name,"End_Date")
        self.assertEqual(test.value, "2020-02-29")

    def test_ExceptionModel(self):
        test = FetchData.ExceptionModel.from_json("")
        self.assertTrue(isinstance(test,FetchData.ExceptionModel))


    def test_ReportHeaderModel(self):
        test = FetchData.ReportHeaderModel.from_json("")
        self.assertTrue(isinstance(test,FetchData.ReportHeaderModel))


    def test_PlatformReportItemModel(self):
        test = FetchData.PlatformReportItemModel.from_json("")
        self.assertTrue(isinstance(test,FetchData.PlatformReportItemModel))

    def test_DatabaseReportItemModel(self):
        test = FetchData.DatabaseReportItemModel.from_json("")
        self.assertTrue(isinstance(test,FetchData.DatabaseReportItemModel))

    def test_TitleReportItemModel(self):
        test = FetchData.TitleReportItemModel.from_json("")
        self.assertTrue(isinstance(test,FetchData.TitleReportItemModel))

    def test_ItemContributorModel(self):
        test = FetchData.ItemContributorModel.from_json("")
        self.assertTrue(isinstance(test,FetchData.ItemContributorModel))

    def test_ItemParentModel(self):
        test = FetchData.ItemParentModel.from_json("")
        self.assertTrue(isinstance(test,FetchData.ItemParentModel))

    def test_ItemComponentModel(self):
        test = FetchData.ItemComponentModel.from_json("")
        self.assertTrue(isinstance(test, FetchData.ItemComponentModel))

    def test_ItemReportItemModel(self):
        test = FetchData.ItemReportItemModel.from_json("")
        self.assertTrue(isinstance(test, FetchData.ItemReportItemModel))

    def test_get_models(self):
        test = FetchData.get_models("123",FetchData.TypeValueModel,"None")
        self.assertTrue(isinstance(test, list))

    def test_get_month_years(self):
        now = QDate.currentDate()
        test = FetchData.get_month_years(now,now)
        self.assertTrue(isinstance(test, list))

    def test_Attributes(self):
        test = FetchData.Attributes()
        self.assertTrue(isinstance(test, FetchData.Attributes))

    def test_RequestData(self):
        now = QDate.currentDate()
        test = FetchData.RequestData(FetchData.Vendor, FetchData.REPORT_TYPES, now, now, FetchData.FetchType, FetchData.SettingsModel, FetchData.Attributes)
        self.assertTrue(isinstance(test, FetchData.RequestData))

    def test_ProcessResult(self):
        test = FetchData.ProcessResult(FetchData.Vendor, "123")
        self.assertTrue(isinstance(test, FetchData.ProcessResult))

    def test_RetryLaterException(self):
        test = FetchData.RetryLaterException(Exception)
        self.assertTrue(isinstance(test, Exception))

    def test_ReportHeaderMissingException(self):
        test = FetchData.ReportHeaderMissingException(Exception)
        self.assertTrue(isinstance(test, Exception))

    def test_UnacceptableCodeException(self):
        test = FetchData.UnacceptableCodeException(Exception)
        self.assertTrue(isinstance(test, Exception))

    #def test_FetchReportsAbstract_init_(self):
        #test = FetchData.FetchReportsAbstract.__init__(self, ["test1","test2"], FetchData.SearchController, FetchData.SettingsModel)
        #self.assertEqual(test, None)

    #def test_fetch_vendor_data(self):
        #now = QDate.currentDate()
        #data = FetchData.RequestData(self, FetchData.Vendor, FetchData.REPORT_TYPES, now, now, FetchData.FetchType, FetchData.SettingsModel)
        #test = FetchData.FetchReportsAbstract.fetch_vendor_data(self,data)


if __name__ == "__main__":
        unittest.main()