import sys
import unittest
import FetchData
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QDate


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
        testJson =  {"Code":"123456789","Message":"Test Test","Severity":"Test","Data":"2020-01"}
        test = FetchData.ExceptionModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.ExceptionModel))
        self.assertEqual(test.code, 123456789)
        self.assertEqual(test.message, "Test Test")
        self.assertEqual(test.severity, "Test")
        self.assertEqual(test.data, "2020-01")

    def test_exception_models_to_message(self):
        test = FetchData.exception_models_to_message("")
        self.assertEqual(test, "")

    def test_ReportHeaderModel(self):
        testJson = {"Report_Name": "test",
                    "Report_ID": "test",
                    "Release": "test",
                    "Institution_Name": "test",
                    "Created": "test",
                    "Created_By": "test",
                    "Institution_ID": "test",
                    "Report_Filters": "test",
                    "Report_Attributes": "test",
                    "Exceptions": "test"}
        test = FetchData.ReportHeaderModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.ReportHeaderModel))
        self.assertEqual(test.report_name, "test")
        self.assertEqual(test.report_id, "TEST")
        self.assertEqual(test.release,"test")
        self.assertEqual(test.institution_name, "test")
        self.assertEqual(test.created, "test")
        self.assertEqual(test.created_by, "test")
        self.assertEqual(test.institution_ids, [])
        self.assertEqual(test.report_filters, [])
        self.assertEqual(test.report_attributes, [])
        self.assertEqual(test.exceptions, [])

    def test_PlatformReportItemModel(self):
        testJson = {"Platform":"Test","Data_Type":"Test","Access_Method":"Test","Performance":"Test"}
        test = FetchData.PlatformReportItemModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.PlatformReportItemModel))
        self.assertEqual(test.platform, "Test")
        self.assertEqual(test.data_type, "Test")
        self.assertEqual(test.access_method, "Test")
        self.assertEqual(test.performances, [])

    def test_DatabaseReportItemModel(self):
        testJson = {"Database":"Test",
                    "Publisher":"Test",
                    "Platform":"Test",
                    "Data_Type":"Test",
                    "Access_Method":"Test",
                    "Item_ID":"Test",
                    "Publisher_ID":"Test",
                    "Performance":"Test"}
        test = FetchData.DatabaseReportItemModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.DatabaseReportItemModel))
        self.assertEqual(test.database, "Test")
        self.assertEqual(test.publisher, "Test")
        self.assertEqual(test.platform, "Test")
        self.assertEqual(test.data_type, "Test")
        self.assertEqual(test.access_method, "Test")
        self.assertEqual(test.item_ids, [])
        self.assertEqual(test.publisher_ids, [])
        self.assertEqual(test.performances, [])

    def test_TitleReportItemModel(self):
        testJson = {"Title": "Test",
                    "Platform": "Test",
                    "Publisher": "Test",
                    "Data_Type": "Test",
                    "Section_Type": "Test",
                    "YOP": "Test",
                    "Access_Type": "Test",
                    "Access_Method": "Test",
                    "Item_ID":"Test",
                    "Publisher_ID":"Test",
                    "Performance":"Test"}
        test = FetchData.TitleReportItemModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.TitleReportItemModel))
        self.assertEqual(test.title, "Test")
        self.assertEqual(test.publisher, "Test")
        self.assertEqual(test.platform, "Test")
        self.assertEqual(test.data_type, "Test")
        self.assertEqual(test.section_type, "Test")
        self.assertEqual(test.yop, "Test")
        self.assertEqual(test.access_type, "Test")
        self.assertEqual(test.access_method, "Test")
        self.assertEqual(test.item_ids, [])
        self.assertEqual(test.publisher_ids, [])
        self.assertEqual(test.performances, [])

    def test_ItemContributorModel(self):
        testJson = {"Type":"Test","Name":"Test","Identifier":"Test"}
        test = FetchData.ItemContributorModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.ItemContributorModel))
        self.assertEqual(test.item_type, "Test")
        self.assertEqual(test.name, "Test")
        self.assertEqual(test.identifier, "Test")

    def test_ItemParentModel(self):
        testJson = {"Item_Name": "Test",
                    "Data_Type": "Test",
                    "Item_Contributors": "Test",
                    "Item_ID": "Test",
                    "Item_Dates": "Test",
                    "Item_Attributes": "Test"}
        test = FetchData.ItemParentModel.from_json(testJson)
        self.assertTrue(isinstance(test,FetchData.ItemParentModel))
        self.assertEqual(test.item_name, "Test")
        self.assertEqual(test.data_type, "Test")
        self.assertEqual(test.item_contributors, [])
        self.assertEqual(test.item_ids, [])
        self.assertEqual(test.item_dates, [])
        self.assertEqual(test.item_attributes, [])

    def test_ItemComponentModel(self):
        testJson = {"Item_Name": "Test",
                    "Data_Type": "Test",
                    "Item_Contributors": "Test",
                    "Item_ID": "Test",
                    "Item_Dates": "Test",
                    "Item_Attributes": "Test",
                    "Performance": "Test"}
        test = FetchData.ItemComponentModel.from_json(testJson)
        self.assertTrue(isinstance(test, FetchData.ItemComponentModel))
        self.assertEqual(test.item_name, "Test")
        self.assertEqual(test.data_type, "Test")
        self.assertEqual(test.item_contributors, [])
        self.assertEqual(test.item_ids, [])
        self.assertEqual(test.item_dates, [])
        self.assertEqual(test.item_attributes, [])
        self.assertEqual(test.performances,[])

    def test_ItemReportItemModel(self):
        testJson = {"Item":"Test",
                    "Platform": "Test",
                    "Publisher": "Test",
                    "Data_Type": "Test",
                    "YOP": "Test",
                    "Access_Type": "Test",
                    "Access_Method": "Test",
                    "Item_Parent":"Test",
                    "Item_Contributors": "Test",
                    "Item_ID": "Test",
                    "Item_Dates": "Test",
                    "Item_Attributes": "Test",
                    "Performance": "Test",
                    "Publisher_ID:":"Test",
                    "Item_Component":"Test"}
        test = FetchData.ItemReportItemModel.from_json(testJson)
        self.assertTrue(isinstance(test, FetchData.ItemReportItemModel))
        self.assertEqual(test.item, "Test")
        self.assertEqual(test.publisher, "Test")
        self.assertEqual(test.platform, "Test")
        self.assertEqual(test.data_type, "Test")
        self.assertEqual(test.yop, "Test")
        self.assertEqual(test.access_type, "Test")
        self.assertEqual(test.access_method, "Test")
        self.assertTrue(isinstance(test.item_parent,FetchData.ItemParentModel))
        self.assertEqual(test.item_ids, [])
        self.assertEqual(test.publisher_ids, [])
        self.assertEqual(test.performances, [])
        self.assertEqual(test.item_dates, [])
        self.assertEqual(test.item_attributes, [])
        self.assertEqual(test.item_components, [])

    def test_get_models(self):
        test = FetchData.get_models("123",FetchData.TypeValueModel,"None")
        self.assertTrue(isinstance(test, list))
        self.assertEqual(len(test), 0)

    def test_get_month_years(self):
        begin = QDate(2020,1,1)
        end = QDate(2020,12,1)
        test = FetchData.get_month_years(begin,end)
        self.assertTrue(isinstance(test, list))
        self.assertEqual(len(test),12)

    def test_RequestData(self):
        now = QDate.currentDate()
        test = FetchData.RequestData(FetchData.Vendor, FetchData.REPORT_TYPES, now, now, "", FetchData.SettingsModel, FetchData.SpecialReportOptions)
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


if __name__ == "__main__":
        unittest.main()