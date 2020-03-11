import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
import ui.MainWindow
from ManageVendors import ManageVendorsController
from FetchData import FetchReportsController, FetchSpecialReportsController
from ImportFile import ImportFileController
from Search import SearchController
from Settings import SettingsController
from Visual import VisualController


# region debug_stuff

def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug

# endregion

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window_ui = ui.MainWindow.Ui_mainWindow()
    main_window_ui.setupUi(main_window)

    # # region Setup Tab Controllers
    # manage_vendors_controller = ManageVendorsController(main_window_ui)
    # settings_controller = SettingsController(main_window_ui)
    # fetch_reports_controller = FetchReportsController(manage_vendors_controller.vendors, settings_controller.settings,
    #                                                   main_window_ui)
    # fetch_special_reports_controller = FetchSpecialReportsController(manage_vendors_controller.vendors,
    #                                                                  settings_controller.settings, main_window_ui)
    # search_controller = SearchController(main_window_ui)
    # import_file_controller = ImportFileController(manage_vendors_controller.vendors, settings_controller.settings,
    #                                               main_window_ui)
    # visual_controller = VisualController(main_window_ui)
    # # endregion
    #
    # # region Connect Signals
    # manage_vendors_controller.vendors_changed_signal.connect(fetch_reports_controller.on_vendors_changed)
    # manage_vendors_controller.vendors_changed_signal.connect(fetch_special_reports_controller.on_vendors_changed)
    # manage_vendors_controller.vendors_changed_signal.connect(import_file_controller.on_vendors_changed)
    # # endregion

    main_window.show()
    sys.exit(app.exec_())
