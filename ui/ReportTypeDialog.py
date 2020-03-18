# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportTypeDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_report_type_dialog(object):
    def setupUi(self, report_type_dialog):
        report_type_dialog.setObjectName("report_type_dialog")
        report_type_dialog.resize(433, 155)
        self.verticalLayout = QtWidgets.QVBoxLayout(report_type_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.report_type_combobox = QtWidgets.QComboBox(report_type_dialog)
        self.report_type_combobox.setObjectName("report_type_combobox")
        self.verticalLayout.addWidget(self.report_type_combobox)
        self.buttonBox = QtWidgets.QDialogButtonBox(report_type_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(report_type_dialog)
        self.buttonBox.accepted.connect(report_type_dialog.accept)
        self.buttonBox.rejected.connect(report_type_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(report_type_dialog)

    def retranslateUi(self, report_type_dialog):
        _translate = QtCore.QCoreApplication.translate
        report_type_dialog.setWindowTitle(_translate("report_type_dialog", "Report Type"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    report_type_dialog = QtWidgets.QDialog()
    ui = Ui_report_type_dialog()
    ui.setupUi(report_type_dialog)
    report_type_dialog.show()
    sys.exit(app.exec_())

