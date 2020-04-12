# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UpdateDatabaseProgressDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_update_database_dialog(object):
    def setupUi(self, update_database_dialog):
        update_database_dialog.setObjectName("update_database_dialog")
        update_database_dialog.resize(433, 396)
        self.verticalLayout = QtWidgets.QVBoxLayout(update_database_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.status_label = QtWidgets.QLabel(update_database_dialog)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setObjectName("status_label")
        self.verticalLayout.addWidget(self.status_label)
        self.progressbar = QtWidgets.QProgressBar(update_database_dialog)
        self.progressbar.setMaximum(1)
        self.progressbar.setProperty("value", 0)
        self.progressbar.setObjectName("progressbar")
        self.verticalLayout.addWidget(self.progressbar)
        self.scrollarea = QtWidgets.QScrollArea(update_database_dialog)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setObjectName("scrollarea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 387, 174))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollarea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollarea)
        self.buttonBox = QtWidgets.QDialogButtonBox(update_database_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(update_database_dialog)
        self.buttonBox.accepted.connect(update_database_dialog.accept)
        self.buttonBox.rejected.connect(update_database_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(update_database_dialog)

    def retranslateUi(self, update_database_dialog):
        _translate = QtCore.QCoreApplication.translate
        update_database_dialog.setWindowTitle(_translate("update_database_dialog", "Update Database"))
        self.status_label.setText(_translate("update_database_dialog", "Status"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    update_database_dialog = QtWidgets.QDialog()
    ui = Ui_update_database_dialog()
    ui.setupUi(update_database_dialog)
    update_database_dialog.show()
    sys.exit(app.exec_())

