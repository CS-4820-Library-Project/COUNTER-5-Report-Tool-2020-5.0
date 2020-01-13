# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddVendorDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_addVendorDialog(object):
    def setupUi(self, addVendorDialog):
        addVendorDialog.setObjectName("addVendorDialog")
        addVendorDialog.resize(584, 300)
        self.gridLayout = QtWidgets.QGridLayout(addVendorDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(addVendorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.frame = QtWidgets.QFrame(addVendorDialog)
        self.frame.setObjectName("frame")
        self.formLayout = QtWidgets.QFormLayout(self.frame)
        self.formLayout.setSpacing(20)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.nameEdit = QtWidgets.QLineEdit(self.frame)
        self.nameEdit.setObjectName("nameEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameEdit)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.label_6 = QtWidgets.QLabel(self.frame)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.customerIdEdit = QtWidgets.QLineEdit(self.frame)
        self.customerIdEdit.setObjectName("customerIdEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.customerIdEdit)
        self.baseUrlEdit = QtWidgets.QLineEdit(self.frame)
        self.baseUrlEdit.setObjectName("baseUrlEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.baseUrlEdit)
        self.requestorIdEdit = QtWidgets.QLineEdit(self.frame)
        self.requestorIdEdit.setObjectName("requestorIdEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.requestorIdEdit)
        self.apiKeyEdit = QtWidgets.QLineEdit(self.frame)
        self.apiKeyEdit.setObjectName("apiKeyEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.apiKeyEdit)
        self.platformEdit = QtWidgets.QLineEdit(self.frame)
        self.platformEdit.setObjectName("platformEdit")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.platformEdit)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(addVendorDialog)
        self.buttonBox.accepted.connect(addVendorDialog.accept)
        self.buttonBox.rejected.connect(addVendorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(addVendorDialog)

    def retranslateUi(self, addVendorDialog):
        _translate = QtCore.QCoreApplication.translate
        addVendorDialog.setWindowTitle(_translate("addVendorDialog", "Add Vendor"))
        self.label.setText(_translate("addVendorDialog", "Name"))
        self.label_2.setText(_translate("addVendorDialog", "Customer ID"))
        self.label_3.setText(_translate("addVendorDialog", "Base URL"))
        self.label_4.setText(_translate("addVendorDialog", "Requestor ID (oprtional)"))
        self.label_5.setText(_translate("addVendorDialog", "API Key (optional)"))
        self.label_6.setText(_translate("addVendorDialog", "Platform (optional)"))

