# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SearchAndFrame.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_search_and_clause_parameter_frame(object):
    def setupUi(self, search_and_clause_parameter_frame):
        search_and_clause_parameter_frame.setObjectName("search_and_clause_parameter_frame")
        search_and_clause_parameter_frame.resize(338, 256)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(search_and_clause_parameter_frame.sizePolicy().hasHeightForWidth())
        search_and_clause_parameter_frame.setSizePolicy(sizePolicy)
        search_and_clause_parameter_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        search_and_clause_parameter_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.verticalLayout = QtWidgets.QVBoxLayout(search_and_clause_parameter_frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.search_and_label = QtWidgets.QLabel(search_and_clause_parameter_frame)
        self.search_and_label.setMaximumSize(QtCore.QSize(16777215, 22))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.search_and_label.setFont(font)
        self.search_and_label.setAlignment(QtCore.Qt.AlignCenter)
        self.search_and_label.setObjectName("search_and_label")
        self.verticalLayout.addWidget(self.search_and_label)
        self.search_and_clause_body_frame = QtWidgets.QFrame(search_and_clause_parameter_frame)
        self.search_and_clause_body_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.search_and_clause_body_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.search_and_clause_body_frame.setObjectName("search_and_clause_body_frame")
        self.gridLayout = QtWidgets.QGridLayout(self.search_and_clause_body_frame)
        self.gridLayout.setObjectName("gridLayout")
        self.search_add_or_clause_button = QtWidgets.QPushButton(self.search_and_clause_body_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_add_or_clause_button.sizePolicy().hasHeightForWidth())
        self.search_add_or_clause_button.setSizePolicy(sizePolicy)
        self.search_add_or_clause_button.setObjectName("search_add_or_clause_button")
        self.gridLayout.addWidget(self.search_add_or_clause_button, 0, 1, 1, 1)
        self.search_remove_and_clause_button = QtWidgets.QPushButton(self.search_and_clause_body_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_remove_and_clause_button.sizePolicy().hasHeightForWidth())
        self.search_remove_and_clause_button.setSizePolicy(sizePolicy)
        self.search_remove_and_clause_button.setObjectName("search_remove_and_clause_button")
        self.gridLayout.addWidget(self.search_remove_and_clause_button, 1, 1, 1, 1)
        self.search_or_clause_parameters_frame = QtWidgets.QFrame(self.search_and_clause_body_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_or_clause_parameters_frame.sizePolicy().hasHeightForWidth())
        self.search_or_clause_parameters_frame.setSizePolicy(sizePolicy)
        self.search_or_clause_parameters_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.search_or_clause_parameters_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.search_or_clause_parameters_frame.setObjectName("search_or_clause_parameters_frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.search_or_clause_parameters_frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout.addWidget(self.search_or_clause_parameters_frame, 0, 0, 2, 1)
        self.verticalLayout.addWidget(self.search_and_clause_body_frame)

        self.retranslateUi(search_and_clause_parameter_frame)
        QtCore.QMetaObject.connectSlotsByName(search_and_clause_parameter_frame)

    def retranslateUi(self, search_and_clause_parameter_frame):
        _translate = QtCore.QCoreApplication.translate
        search_and_clause_parameter_frame.setWindowTitle(_translate("search_and_clause_parameter_frame", "Frame"))
        self.search_and_label.setText(_translate("search_and_clause_parameter_frame", "AND"))
        self.search_add_or_clause_button.setText(_translate("search_and_clause_parameter_frame", "Add \"Or\""))
        self.search_remove_and_clause_button.setText(_translate("search_and_clause_parameter_frame", "Remove \"And\""))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    search_and_clause_parameter_frame = QtWidgets.QFrame()
    ui = Ui_search_and_clause_parameter_frame()
    ui.setupUi(search_and_clause_parameter_frame)
    search_and_clause_parameter_frame.show()
    sys.exit(app.exec_())

