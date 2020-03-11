import sys
import webbrowser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout, QPushButton
from ui import MainWindow, ManageVendorsTab
from ManageVendors import ManageVendorsController
from FetchData import FetchReportsController, FetchSpecialReportsController
from ImportFile import ImportFileController
from Search import SearchController
from Settings import SettingsController
from Visual import VisualController

HELP_SITE = "https://github.com/CS-4820-Library-Project/Libly/wiki"


def open_help():
    webbrowser.open_new_tab(HELP_SITE)


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
    main_window_ui = MainWindow.Ui_mainWindow()
    main_window_ui.setupUi(main_window)

    # # region Setup Tab Controllers
    manage_vendors_tab = QWidget(main_window)
    manage_vendors_ui = ManageVendorsTab.Ui_manage_vendors_tab()
    manage_vendors_ui.setupUi(manage_vendors_tab)
    manage_vendors_controller = ManageVendorsController(manage_vendors_ui)

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

    main_window_ui.tab_widget.addTab(manage_vendors_tab, "Manage Vendors")

    # Status Bar
    status_bar = main_window_ui.statusbar

    help_frame = QFrame(status_bar)
    help_frame_layout = QHBoxLayout(help_frame)
    help_frame_layout.setContentsMargins(-1, 2, -1, 5)
    help_frame.setLayout(help_frame_layout)
    help_button = QPushButton("Help", help_frame)
    font = help_button.font()
    font.setPointSize(11)
    help_button.setFont(font)
    help_button.clicked.connect(open_help)
    help_frame_layout.addWidget(help_button)

    status_bar.addWidget(help_frame)

    main_window.show()
    sys.exit(app.exec_())
