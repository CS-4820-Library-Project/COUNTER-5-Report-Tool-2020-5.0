# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RestoreDatabaseProgressDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_restore_database_dialog(object):
    def setupUi(self, restore_database_dialog):
        restore_database_dialog.setObjectName("restore_database_dialog")
        restore_database_dialog.resize(433, 348)
        self.verticalLayout = QtWidgets.QVBoxLayout(restore_database_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.status_label = QtWidgets.QLabel(restore_database_dialog)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setObjectName("status_label")
        self.verticalLayout.addWidget(self.status_label)
        self.progressbar = QtWidgets.QProgressBar(restore_database_dialog)
        self.progressbar.setMaximum(1)
        self.progressbar.setProperty("value", 0)
        self.progressbar.setObjectName("progressbar")
        self.verticalLayout.addWidget(self.progressbar)
        self.scrollarea = QtWidgets.QScrollArea(restore_database_dialog)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setObjectName("scrollarea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 387, 126))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollarea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollarea)
        self.buttonBox = QtWidgets.QDialogButtonBox(restore_database_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(restore_database_dialog)
        self.buttonBox.accepted.connect(restore_database_dialog.accept)
        self.buttonBox.rejected.connect(restore_database_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(restore_database_dialog)

    def retranslateUi(self, restore_database_dialog):
        _translate = QtCore.QCoreApplication.translate
        restore_database_dialog.setWindowTitle(_translate("restore_database_dialog", "Restore Database"))
        self.status_label.setText(_translate("restore_database_dialog", "Status"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    restore_database_dialog = QtWidgets.QDialog()
    ui = Ui_restore_database_dialog()
    ui.setupUi(restore_database_dialog)
    restore_database_dialog.show()
    sys.exit(app.exec_())

