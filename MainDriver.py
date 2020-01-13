import sys
import ui.MainWindow
from ManageVendors import ManageVendorsController
from FetchData import FetchDataController
from ImportFile import ImportFileController
from Search import SearchController
from PyQt5.QtWidgets import QApplication, QMainWindow


# region debug_stuff

def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug

# endregion

PREF_VIEW_WIDTH = 1000.0
PREF_VIEW_HEIGHT = 600.0

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window_ui = ui.MainWindow.Ui_mainWindow()
    main_window_ui.setupUi(main_window)

    manageVendorsController = ManageVendorsController(main_window_ui.vendorsListView,
                                                      main_window_ui.modifyVendorFrame,
                                                      main_window_ui.nameEdit,
                                                      main_window_ui.customerIdEdit,
                                                      main_window_ui.baseUrlEdit,
                                                      main_window_ui.requestorIdEdit,
                                                      main_window_ui.apiKeyEdit,
                                                      main_window_ui.platformEdit,
                                                      main_window_ui.saveVendorChangesButton,
                                                      main_window_ui.undoVendorChangesButton,
                                                      main_window_ui.removeVendorButton,
                                                      main_window_ui.addVendorButton)

    search_controller = SearchController(main_window_ui.search_term_edit,
                                         main_window_ui.title_checkbox,
                                         main_window_ui.issn_checkbox,
                                         main_window_ui.isbn_checkbox,
                                         main_window_ui.search_button,
                                         main_window_ui.search_results_table_view)

    fetchDataController = FetchDataController(manageVendorsController.vendors,
                                              search_controller,
                                              main_window_ui.fetch_all_data_button,
                                              main_window_ui.fetch_advanced_button,
                                              main_window_ui.vendors_list_view_fetch,
                                              main_window_ui.select_vendors_button_fetch,
                                              main_window_ui.deselect_vendors_button_fetch,
                                              main_window_ui.report_types_list_view,
                                              main_window_ui.select_report_types_button_fetch,
                                              main_window_ui.deselect_report_types_button_fetch,
                                              main_window_ui.begin_date_edit,
                                              main_window_ui.end_date_edit)
    manageVendorsController.vendors_changed_signal.connect(fetchDataController.on_vendors_size_changed)

    importFileController = ImportFileController(manageVendorsController.vendors,
                                                search_controller,
                                                main_window_ui.vendors_list_view_import,
                                                main_window_ui.report_types_list_view_import,
                                                main_window_ui.report_year_date_edit,
                                                main_window_ui.select_file_button,
                                                main_window_ui.selected_file_label,
                                                main_window_ui.import_file_button)
    manageVendorsController.vendors_changed_signal.connect(importFileController.on_vendors_size_changed)

    main_window.show()

    sys.exit(app.exec_())
