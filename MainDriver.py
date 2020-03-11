import sys
import webbrowser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout, QPushButton
from ui import MainWindow, ManageVendorsTab, SettingsTab, FetchReportsTab, FetchSpecialReportsTab, ImportReportTab,\
    SearchTab, VisualTab
from ManageVendors import ManageVendorsController
from FetchData import FetchReportsController, FetchSpecialReportsController
from ImportFile import ImportReportController
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

    settings_tab = QWidget(main_window)
    settings_ui = SettingsTab.Ui_settings_tab()
    settings_ui.setupUi(settings_tab)
    settings_controller = SettingsController(settings_ui)

    fetch_reports_tab = QWidget(main_window)
    fetch_reports_ui = FetchReportsTab.Ui_fetch_reports_tab()
    fetch_reports_ui.setupUi(fetch_reports_tab)
    fetch_reports_controller = FetchReportsController(manage_vendors_controller.vendors, settings_controller.settings,
                                                      fetch_reports_ui)

    fetch_special_reports_tab = QWidget(main_window)
    fetch_special_reports_ui = FetchSpecialReportsTab.Ui_fetch_special_reports_tab()
    fetch_special_reports_ui.setupUi(fetch_special_reports_tab)
    fetch_special_reports_controller = FetchSpecialReportsController(manage_vendors_controller.vendors,
                                                                     settings_controller.settings,
                                                                     fetch_special_reports_ui)

    import_report_tab = QWidget(main_window)
    import_report_ui = ImportReportTab.Ui_import_report_tab()
    import_report_ui.setupUi(import_report_tab)
    import_report_controller = ImportReportController(manage_vendors_controller.vendors, settings_controller.settings,
                                                      import_report_ui)

    search_tab = QWidget(main_window)
    search_ui = SearchTab.Ui_search_tab()
    search_ui.setupUi(search_tab)
    search_controller = SearchController(search_ui)

    visual_tab = QWidget(main_window)
    visual_ui = VisualTab.Ui_visual_tab()
    visual_ui.setupUi(visual_tab)
    visual_controller = VisualController(visual_ui)
    # # endregion

    # region Connect Signals
    manage_vendors_controller.vendors_changed_signal.connect(fetch_reports_controller.on_vendors_changed)
    manage_vendors_controller.vendors_changed_signal.connect(fetch_special_reports_controller.on_vendors_changed)
    manage_vendors_controller.vendors_changed_signal.connect(import_report_controller.on_vendors_changed)
    # endregion

    # Add tabs to main window
    main_window_ui.tab_widget.addTab(manage_vendors_tab, "Manage Vendors")
    main_window_ui.tab_widget.addTab(fetch_reports_tab, "Fetch Reports")
    main_window_ui.tab_widget.addTab(fetch_special_reports_tab, "Fetch Special Reports")
    main_window_ui.tab_widget.addTab(import_report_tab, "Import Report")
    main_window_ui.tab_widget.addTab(search_tab, "Search")
    main_window_ui.tab_widget.addTab(visual_tab, "Visual")
    main_window_ui.tab_widget.addTab(settings_tab, "Settings")

    main_window_ui.tab_widget.setCurrentIndex(1)

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
