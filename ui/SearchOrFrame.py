# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SearchOrFrame.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_search_or_clause_parameter_frame(object):
    def setupUi(self, search_or_clause_parameter_frame):
        search_or_clause_parameter_frame.setObjectName("search_or_clause_parameter_frame")
        search_or_clause_parameter_frame.resize(842, 101)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(search_or_clause_parameter_frame.sizePolicy().hasHeightForWidth())
        search_or_clause_parameter_frame.setSizePolicy(sizePolicy)
        search_or_clause_parameter_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        search_or_clause_parameter_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.horizontalLayout = QtWidgets.QHBoxLayout(search_or_clause_parameter_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.search_or_label = QtWidgets.QLabel(search_or_clause_parameter_frame)
        self.search_or_label.setMaximumSize(QtCore.QSize(16777215, 22))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.search_or_label.setFont(font)
        self.search_or_label.setAutoFillBackground(False)
        self.search_or_label.setAlignment(QtCore.Qt.AlignCenter)
        self.search_or_label.setObjectName("search_or_label")
        self.horizontalLayout.addWidget(self.search_or_label)
        self.search_field_parameter_combobox = QtWidgets.QComboBox(search_or_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_field_parameter_combobox.sizePolicy().hasHeightForWidth())
        self.search_field_parameter_combobox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.search_field_parameter_combobox.setFont(font)
        self.search_field_parameter_combobox.setObjectName("search_field_parameter_combobox")
        self.horizontalLayout.addWidget(self.search_field_parameter_combobox)
        self.search_comparison_parameter_combobox = QtWidgets.QComboBox(search_or_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_comparison_parameter_combobox.sizePolicy().hasHeightForWidth())
        self.search_comparison_parameter_combobox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.search_comparison_parameter_combobox.setFont(font)
        self.search_comparison_parameter_combobox.setObjectName("search_comparison_parameter_combobox")
        self.horizontalLayout.addWidget(self.search_comparison_parameter_combobox)
        self.search_type_label = QtWidgets.QLabel(search_or_clause_parameter_frame)
        self.search_type_label.setObjectName("search_type_label")
        self.horizontalLayout.addWidget(self.search_type_label)
        self.search_value_parameter_lineedit = QtWidgets.QLineEdit(search_or_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_value_parameter_lineedit.sizePolicy().hasHeightForWidth())
        self.search_value_parameter_lineedit.setSizePolicy(sizePolicy)
        self.search_value_parameter_lineedit.setObjectName("search_value_parameter_lineedit")
        self.horizontalLayout.addWidget(self.search_value_parameter_lineedit)
        self.search_remove_or_clause_button = QtWidgets.QPushButton(search_or_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_remove_or_clause_button.sizePolicy().hasHeightForWidth())
        self.search_remove_or_clause_button.setSizePolicy(sizePolicy)
        self.search_remove_or_clause_button.setObjectName("search_remove_or_clause_button")
        self.horizontalLayout.addWidget(self.search_remove_or_clause_button)

        self.retranslateUi(search_or_clause_parameter_frame)
        QtCore.QMetaObject.connectSlotsByName(search_or_clause_parameter_frame)

    def retranslateUi(self, search_or_clause_parameter_frame):
        _translate = QtCore.QCoreApplication.translate
        search_or_clause_parameter_frame.setWindowTitle(_translate("search_or_clause_parameter_frame", "Frame"))
        self.search_or_label.setText(_translate("search_or_clause_parameter_frame", "OR"))
        self.search_type_label.setText(_translate("search_or_clause_parameter_frame", "Type"))
        self.search_remove_or_clause_button.setText(_translate("search_or_clause_parameter_frame", "Remove \"Or\""))
