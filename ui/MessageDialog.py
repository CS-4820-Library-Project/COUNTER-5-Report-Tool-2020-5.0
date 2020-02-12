# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MessageDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_message_dialog(object):
    def setupUi(self, message_dialog):
        message_dialog.setObjectName("message_dialog")
        message_dialog.resize(400, 60)
        self.verticalLayout = QtWidgets.QVBoxLayout(message_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.message_label = QtWidgets.QLabel(message_dialog)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.message_label.setFont(font)
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setObjectName("message_label")
        self.verticalLayout.addWidget(self.message_label)

        self.retranslateUi(message_dialog)
        QtCore.QMetaObject.connectSlotsByName(message_dialog)

    def retranslateUi(self, message_dialog):
        _translate = QtCore.QCoreApplication.translate
        message_dialog.setWindowTitle(_translate("message_dialog", "Message"))
        self.message_label.setText(_translate("message_dialog", "Message!"))

