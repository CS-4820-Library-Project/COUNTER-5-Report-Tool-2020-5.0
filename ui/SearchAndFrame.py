# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SearchAndFrame.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_search_and_clause_parameter_frame(object):
    def setupUi(self, search_and_clause_parameter_frame):
        search_and_clause_parameter_frame.setObjectName("search_and_clause_parameter_frame")
        search_and_clause_parameter_frame.resize(296, 175)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(search_and_clause_parameter_frame.sizePolicy().hasHeightForWidth())
        search_and_clause_parameter_frame.setSizePolicy(sizePolicy)
        search_and_clause_parameter_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        search_and_clause_parameter_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.gridLayout = QtWidgets.QGridLayout(search_and_clause_parameter_frame)
        self.gridLayout.setObjectName("gridLayout")
        self.search_remove_and_clause_button = QtWidgets.QPushButton(search_and_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_remove_and_clause_button.sizePolicy().hasHeightForWidth())
        self.search_remove_and_clause_button.setSizePolicy(sizePolicy)
        self.search_remove_and_clause_button.setObjectName("search_remove_and_clause_button")
        self.gridLayout.addWidget(self.search_remove_and_clause_button, 2, 1, 1, 1)
        self.search_add_or_clause_button = QtWidgets.QPushButton(search_and_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_add_or_clause_button.sizePolicy().hasHeightForWidth())
        self.search_add_or_clause_button.setSizePolicy(sizePolicy)
        self.search_add_or_clause_button.setObjectName("search_add_or_clause_button")
        self.gridLayout.addWidget(self.search_add_or_clause_button, 1, 1, 1, 1)
        self.search_or_clause_parameters_frame = QtWidgets.QFrame(search_and_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_or_clause_parameters_frame.sizePolicy().hasHeightForWidth())
        self.search_or_clause_parameters_frame.setSizePolicy(sizePolicy)
        self.search_or_clause_parameters_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.search_or_clause_parameters_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.search_or_clause_parameters_frame.setObjectName("search_or_clause_parameters_frame")
        self.verticalLayout_22 = QtWidgets.QVBoxLayout(self.search_or_clause_parameters_frame)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.gridLayout.addWidget(self.search_or_clause_parameters_frame, 1, 0, 2, 1)
        self.AND_label = QtWidgets.QLabel(search_and_clause_parameter_frame)
        self.AND_label.setMaximumSize(QtCore.QSize(16777215, 22))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.AND_label.setFont(font)
        self.AND_label.setAlignment(QtCore.Qt.AlignCenter)
        self.AND_label.setObjectName("AND_label")
        self.gridLayout.addWidget(self.AND_label, 0, 0, 1, 2)

        self.retranslateUi(search_and_clause_parameter_frame)
        QtCore.QMetaObject.connectSlotsByName(search_and_clause_parameter_frame)

    def retranslateUi(self, search_and_clause_parameter_frame):
        _translate = QtCore.QCoreApplication.translate
        search_and_clause_parameter_frame.setWindowTitle(_translate("search_and_clause_parameter_frame", "Frame"))
        self.search_remove_and_clause_button.setText(_translate("search_and_clause_parameter_frame", "Remove \"And\""))
        self.search_add_or_clause_button.setText(_translate("search_and_clause_parameter_frame", "Add \"Or\""))
        self.AND_label.setText(_translate("search_and_clause_parameter_frame", "AND"))
