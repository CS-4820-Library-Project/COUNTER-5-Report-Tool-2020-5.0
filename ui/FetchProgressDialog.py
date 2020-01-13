# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FetchProgressDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FetchProgressDialog(object):
    def setupUi(self, FetchProgressDialog):
        FetchProgressDialog.setObjectName("FetchProgressDialog")
        FetchProgressDialog.resize(680, 353)
        FetchProgressDialog.setMinimumSize(QtCore.QSize(680, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        FetchProgressDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(FetchProgressDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.fetching_frame = QtWidgets.QFrame(FetchProgressDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fetching_frame.sizePolicy().hasHeightForWidth())
        self.fetching_frame.setSizePolicy(sizePolicy)
        self.fetching_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.fetching_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.fetching_frame.setObjectName("fetching_frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.fetching_frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.status_label = QtWidgets.QLabel(self.fetching_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status_label.sizePolicy().hasHeightForWidth())
        self.status_label.setSizePolicy(sizePolicy)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setObjectName("status_label")
        self.verticalLayout_2.addWidget(self.status_label)
        self.progress_bar = QtWidgets.QProgressBar(self.fetching_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress_bar.sizePolicy().hasHeightForWidth())
        self.progress_bar.setSizePolicy(sizePolicy)
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout_2.addWidget(self.progress_bar)
        self.verticalLayout.addWidget(self.fetching_frame)
        self.results_scroll_area = QtWidgets.QScrollArea(FetchProgressDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.results_scroll_area.sizePolicy().hasHeightForWidth())
        self.results_scroll_area.setSizePolicy(sizePolicy)
        self.results_scroll_area.setWidgetResizable(True)
        self.results_scroll_area.setObjectName("results_scroll_area")
        self.scroll_area_widget_contents = QtWidgets.QWidget()
        self.scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 660, 236))
        self.scroll_area_widget_contents.setObjectName("scroll_area_widget_contents")
        self.scroll_area_vertical_layout = QtWidgets.QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area_vertical_layout.setObjectName("scroll_area_vertical_layout")
        self.results_scroll_area.setWidget(self.scroll_area_widget_contents)
        self.verticalLayout.addWidget(self.results_scroll_area)
        self.buttonBox = QtWidgets.QDialogButtonBox(FetchProgressDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Retry)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(FetchProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(FetchProgressDialog)

    def retranslateUi(self, FetchProgressDialog):
        _translate = QtCore.QCoreApplication.translate
        FetchProgressDialog.setWindowTitle(_translate("FetchProgressDialog", "Fetch Progress"))
        self.status_label.setText(_translate("FetchProgressDialog", "Fetching..."))

