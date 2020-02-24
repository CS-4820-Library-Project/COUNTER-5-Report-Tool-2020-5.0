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
        search_or_clause_parameter_frame.resize(483, 133)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(search_or_clause_parameter_frame.sizePolicy().hasHeightForWidth())
        search_or_clause_parameter_frame.setSizePolicy(sizePolicy)
        search_or_clause_parameter_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        search_or_clause_parameter_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(search_or_clause_parameter_frame)
        self.gridLayout.setObjectName("gridLayout")
        self.search_value_parameter_lineedit = QtWidgets.QLineEdit(search_or_clause_parameter_frame)
        self.search_value_parameter_lineedit.setObjectName("search_value_parameter_lineedit")
        self.gridLayout.addWidget(self.search_value_parameter_lineedit, 1, 2, 1, 1)
        self.search_value_parameter_label = QtWidgets.QLabel(search_or_clause_parameter_frame)
        self.search_value_parameter_label.setObjectName("search_value_parameter_label")
        self.gridLayout.addWidget(self.search_value_parameter_label, 0, 2, 1, 1)
        self.search_field_parameter_combobox = QtWidgets.QComboBox(search_or_clause_parameter_frame)
        self.search_field_parameter_combobox.setObjectName("search_field_parameter_combobox")
        self.gridLayout.addWidget(self.search_field_parameter_combobox, 1, 0, 1, 1)
        self.search_field_parameter_label = QtWidgets.QLabel(search_or_clause_parameter_frame)
        self.search_field_parameter_label.setObjectName("search_field_parameter_label")
        self.gridLayout.addWidget(self.search_field_parameter_label, 0, 0, 1, 1)
        self.search_comparison_parameter_label = QtWidgets.QLabel(search_or_clause_parameter_frame)
        self.search_comparison_parameter_label.setObjectName("search_comparison_parameter_label")
        self.gridLayout.addWidget(self.search_comparison_parameter_label, 0, 1, 1, 1)
        self.search_comparison_parameter_combobox = QtWidgets.QComboBox(search_or_clause_parameter_frame)
        self.search_comparison_parameter_combobox.setObjectName("search_comparison_parameter_combobox")
        self.gridLayout.addWidget(self.search_comparison_parameter_combobox, 1, 1, 1, 1)

        self.retranslateUi(search_or_clause_parameter_frame)
        QtCore.QMetaObject.connectSlotsByName(search_or_clause_parameter_frame)

    def retranslateUi(self, search_or_clause_parameter_frame):
        _translate = QtCore.QCoreApplication.translate
        search_or_clause_parameter_frame.setWindowTitle(_translate("search_or_clause_parameter_frame", "Frame"))
        self.search_value_parameter_label.setText(_translate("search_or_clause_parameter_frame", "Value"))
        self.search_field_parameter_label.setText(_translate("search_or_clause_parameter_frame", "Field"))
        self.search_comparison_parameter_label.setText(_translate("search_or_clause_parameter_frame", "Comparison"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    search_or_clause_parameter_frame = QtWidgets.QFrame()
    ui = Ui_search_or_clause_parameter_frame()
    ui.setupUi(search_or_clause_parameter_frame)
    search_or_clause_parameter_frame.show()
    sys.exit(app.exec_())

