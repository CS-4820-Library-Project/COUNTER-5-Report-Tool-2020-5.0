# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RemoveVendorDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dialog_remove(object):
    def setupUi(self, dialog_remove):
        dialog_remove.setObjectName("dialog_remove")
        dialog_remove.resize(399, 100)
        self.label = QtWidgets.QLabel(dialog_remove)
        self.label.setGeometry(QtCore.QRect(10, 10, 371, 41))
        self.label.setObjectName("label")
        self.buttonBox = QtWidgets.QDialogButtonBox(dialog_remove)
        self.buttonBox.setGeometry(QtCore.QRect(210, 60, 164, 32))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(dialog_remove)
        self.buttonBox.accepted.connect(dialog_remove.accept)
        self.buttonBox.rejected.connect(dialog_remove.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog_remove)

    def retranslateUi(self, dialog_remove):
        _translate = QtCore.QCoreApplication.translate
        dialog_remove.setWindowTitle(_translate("dialog_remove", "Remove Vendor"))
        self.label.setText(_translate("dialog_remove", "Are you sure you want to remove this vendor?"))
