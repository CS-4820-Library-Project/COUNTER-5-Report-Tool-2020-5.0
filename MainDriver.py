import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import ui.MainWindow
from ManageVendors import ManageVendorsController
from FetchData import FetchReportsController, FetchSpecialReportsController
from ImportFile import ImportFileController
from Search import SearchController
from Settings import SettingsController


# region debug_stuff

def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug

# endregion

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window_ui = ui.MainWindow.Ui_mainWindow()
    main_window_ui.setupUi(main_window)

    # region Setup Tab Controllers
    manage_vendors_controller = ManageVendorsController(main_window_ui)
    search_controller = SearchController(main_window_ui)
    settings_controller = SettingsController(main_window_ui)
    fetch_reports_controller = FetchReportsController(manage_vendors_controller.vendors, search_controller,
                                                      settings_controller.settings_model, main_window_ui)
    fetch_special_reports_controller = FetchSpecialReportsController(manage_vendors_controller.vendors,
                                                                     search_controller, main_window_ui)
    import_file_controller = ImportFileController(manage_vendors_controller.vendors, search_controller, main_window_ui)
    # endregion

    # region Connect Signals
    manage_vendors_controller.vendors_changed_signal.connect(fetch_reports_controller.on_vendors_size_changed)
    manage_vendors_controller.vendors_changed_signal.connect(fetch_special_reports_controller.on_vendors_size_changed)
    manage_vendors_controller.vendors_changed_signal.connect(import_file_controller.on_vendors_size_changed)
    settings_controller.settings_changed_signal.connect(fetch_reports_controller.on_settings_changed)
    # endregion

    main_window.show()
    sys.exit(app.exec_())
