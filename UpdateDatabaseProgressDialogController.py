import os
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel

import ManageDB
from ui import UpdateDatabaseProgressDialog


class UpdateDatabaseProgressDialogController:

    def __init__(self, parent_widget: QObject = None):
        self.parent_widget = parent_widget
        self.update_database_progress_dialog = None

        self.update_database_thread = None

        self.database_worker = None

        self.update_status_label = None
        self.update_progress_bar = None
        self.update_task_finished_widget = None
        self.update_task_finished_scrollarea = None

        self.is_updating_database = False

    def update_database(self, files, recreate_tables):
        self.update_database_progress_dialog = QDialog(self.parent_widget)

        dialog_ui = UpdateDatabaseProgressDialog.Ui_restore_database_dialog()
        dialog_ui.setupUi(self.update_database_progress_dialog)

        self.update_status_label = dialog_ui.status_label
        self.update_progress_bar = dialog_ui.progressbar
        self.update_task_finished_scrollarea = dialog_ui.scrollarea

        self.update_task_finished_widget = QWidget()
        self.update_task_finished_widget.setLayout(QVBoxLayout())
        self.update_task_finished_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.update_task_finished_scrollarea.setWidget(self.update_task_finished_widget)

        self.update_progress_bar.setMaximum(len(files))

        self.update_database_progress_dialog.show()

        self.update_database_thread = QThread()

        self.database_worker = UpdateDatabaseWorker(files, recreate_tables)

        self.database_worker.status_changed_signal.connect(lambda status: self.on_status_changed(status))
        self.database_worker.progress_changed_signal.connect(lambda progress: self.on_progress_changed(progress))
        self.database_worker.task_finished_signal.connect(lambda task: self.on_task_finished(task))
        self.database_worker.worker_finished_signal.connect(lambda code: self.on_thread_finish(code))

        self.database_worker.moveToThread(self.update_database_thread)

        self.update_database_thread.started.connect(self.database_worker.work)

        self.update_database_thread.start()

    def on_status_changed(self, status: str):
        self.update_status_label.setText(status)

    def on_progress_changed(self, progress: int):
        self.update_progress_bar.setValue(progress)

    def on_task_finished(self, task: str):
        label = QLabel(task)
        self.update_task_finished_widget.layout().addWidget(label)

    def on_thread_finish(self, code):
        print(code)  # testing
        # exit thread
        self.update_database_thread.quit()
        self.update_database_thread.wait()


class UpdateDatabaseWorker(QObject):
    worker_finished_signal = pyqtSignal(int)
    status_changed_signal = pyqtSignal(str)
    progress_changed_signal = pyqtSignal(int)
    task_finished_signal = pyqtSignal(str)

    def __init__(self, files, recreate_tables):
        super().__init__()
        self.recreate_tables = recreate_tables
        self.files = files

    def work(self):
        current = 0
        if self.recreate_tables:
            self.status_changed_signal.emit('Recreating tables...')
            ManageDB.setup_database(True)
            current += 1
            self.progress_changed_signal.emit(current)
            self.task_finished_signal.emit('Recreated tables')
        else:
            self.progress_changed_signal.emit(len(self.files))
        self.status_changed_signal.emit('Filling tables...')
        for file in self.files:
            filename = os.path.basename(file['file'])
            print('READ ' + filename)
            if not filename[:-4].endswith(ManageDB.COST_TABLE_SUFFIX):
                ManageDB.insert_single_file(file['file'], file['vendor'], file['year'])
            else:
                ManageDB.insert_single_cost_file(file['file'])
            self.task_finished_signal.emit(filename)
            current += 1
            self.progress_changed_signal.emit(current)
        self.status_changed_signal.emit('Done')
        self.worker_finished_signal.emit(0)