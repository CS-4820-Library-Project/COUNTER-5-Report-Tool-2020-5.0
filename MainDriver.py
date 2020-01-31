import sys

import ui.MainWindow
from ManageVendors import ManageVendorsController
from FetchData import FetchDataController, FetchSpecialDataController
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

    manageVendorsController = ManageVendorsController(main_window_ui)
    search_controller = SearchController(main_window_ui)

    fetchDataController = FetchDataController(manageVendorsController.vendors, search_controller, main_window_ui)
    fetchSpecialDataController = FetchSpecialDataController(manageVendorsController.vendors, search_controller, main_window_ui)
    manageVendorsController.vendors_changed_signal.connect(fetchDataController.on_vendors_size_changed)

    importFileController = ImportFileController(manageVendorsController.vendors, search_controller, main_window_ui)
    manageVendorsController.vendors_changed_signal.connect(importFileController.on_vendors_size_changed)

    main_window.show()
    sys.exit(app.exec_())
