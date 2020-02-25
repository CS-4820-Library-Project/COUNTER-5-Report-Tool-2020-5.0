# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SearchOrClauseFrame.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_search_or_clause_parameter_frame(object):
    def setupUi(self, search_or_clause_parameter_frame):
        search_or_clause_parameter_frame.setObjectName("search_or_clause_parameter_frame")
        search_or_clause_parameter_frame.resize(755, 103)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(search_or_clause_parameter_frame.sizePolicy().hasHeightForWidth())
        search_or_clause_parameter_frame.setSizePolicy(sizePolicy)
        search_or_clause_parameter_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        search_or_clause_parameter_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(search_or_clause_parameter_frame)
        self.gridLayout.setObjectName("gridLayout")
        self.search_value_parameter_lineedit = QtWidgets.QLineEdit(search_or_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_value_parameter_lineedit.sizePolicy().hasHeightForWidth())
        self.search_value_parameter_lineedit.setSizePolicy(sizePolicy)
        self.search_value_parameter_lineedit.setObjectName("search_value_parameter_lineedit")
        self.gridLayout.addWidget(self.search_value_parameter_lineedit, 0, 2, 1, 1)
        self.search_comparison_parameter_combobox = QtWidgets.QComboBox(search_or_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_comparison_parameter_combobox.sizePolicy().hasHeightForWidth())
        self.search_comparison_parameter_combobox.setSizePolicy(sizePolicy)
        self.search_comparison_parameter_combobox.setObjectName("search_comparison_parameter_combobox")
        self.gridLayout.addWidget(self.search_comparison_parameter_combobox, 0, 1, 1, 1)
        self.search_field_parameter_combobox = QtWidgets.QComboBox(search_or_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_field_parameter_combobox.sizePolicy().hasHeightForWidth())
        self.search_field_parameter_combobox.setSizePolicy(sizePolicy)
        self.search_field_parameter_combobox.setObjectName("search_field_parameter_combobox")
        self.gridLayout.addWidget(self.search_field_parameter_combobox, 0, 0, 1, 1)
        self.search_remove_or_clause_button = QtWidgets.QPushButton(search_or_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_remove_or_clause_button.sizePolicy().hasHeightForWidth())
        self.search_remove_or_clause_button.setSizePolicy(sizePolicy)
        self.search_remove_or_clause_button.setObjectName("search_remove_or_clause_button")
        self.gridLayout.addWidget(self.search_remove_or_clause_button, 0, 3, 1, 1)

        self.retranslateUi(search_or_clause_parameter_frame)
        QtCore.QMetaObject.connectSlotsByName(search_or_clause_parameter_frame)

    def retranslateUi(self, search_or_clause_parameter_frame):
        _translate = QtCore.QCoreApplication.translate
        search_or_clause_parameter_frame.setWindowTitle(_translate("search_or_clause_parameter_frame", "Frame"))
        self.search_remove_or_clause_button.setText(_translate("search_or_clause_parameter_frame", "Remove \"Or\" Clause"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    search_or_clause_parameter_frame = QtWidgets.QFrame()
    ui = Ui_search_or_clause_parameter_frame()
    ui.setupUi(search_or_clause_parameter_frame)
    search_or_clause_parameter_frame.show()
    sys.exit(app.exec_())

