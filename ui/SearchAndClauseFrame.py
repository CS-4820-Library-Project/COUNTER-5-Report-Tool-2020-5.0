# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SearchAndClauseFrame.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_search_and_clause_parameter_frame(object):
    def setupUi(self, search_and_clause_parameter_frame):
        search_and_clause_parameter_frame.setObjectName("search_and_clause_parameter_frame")
        search_and_clause_parameter_frame.resize(400, 164)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(search_and_clause_parameter_frame.sizePolicy().hasHeightForWidth())
        search_and_clause_parameter_frame.setSizePolicy(sizePolicy)
        search_and_clause_parameter_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        search_and_clause_parameter_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalLayout = QtWidgets.QVBoxLayout(search_and_clause_parameter_frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.search_or_clause_parameters_frame = QtWidgets.QFrame(search_and_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_or_clause_parameters_frame.sizePolicy().hasHeightForWidth())
        self.search_or_clause_parameters_frame.setSizePolicy(sizePolicy)
        self.search_or_clause_parameters_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.search_or_clause_parameters_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.search_or_clause_parameters_frame.setObjectName("search_or_clause_parameters_frame")
        self.verticalLayout_22 = QtWidgets.QVBoxLayout(self.search_or_clause_parameters_frame)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.verticalLayout.addWidget(self.search_or_clause_parameters_frame)
        self.search_add_or_clause_button = QtWidgets.QPushButton(search_and_clause_parameter_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_add_or_clause_button.sizePolicy().hasHeightForWidth())
        self.search_add_or_clause_button.setSizePolicy(sizePolicy)
        self.search_add_or_clause_button.setObjectName("search_add_or_clause_button")
        self.verticalLayout.addWidget(self.search_add_or_clause_button)

        self.retranslateUi(search_and_clause_parameter_frame)
        QtCore.QMetaObject.connectSlotsByName(search_and_clause_parameter_frame)

    def retranslateUi(self, search_and_clause_parameter_frame):
        _translate = QtCore.QCoreApplication.translate
        search_and_clause_parameter_frame.setWindowTitle(_translate("search_and_clause_parameter_frame", "Frame"))
        self.search_add_or_clause_button.setText(_translate("search_and_clause_parameter_frame", "Add \"Or\" Clause"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    search_and_clause_parameter_frame = QtWidgets.QFrame()
    ui = Ui_search_and_clause_parameter_frame()
    ui.setupUi(search_and_clause_parameter_frame)
    search_and_clause_parameter_frame.show()
    sys.exit(app.exec_())

