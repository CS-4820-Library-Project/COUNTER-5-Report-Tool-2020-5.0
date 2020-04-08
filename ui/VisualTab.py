# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VisualTab.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_visual_tab(object):
    def setupUi(self, visual_tab):
        visual_tab.setObjectName("visual_tab")
        visual_tab.resize(977, 648)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ui/resources/tab_icons/visual_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        visual_tab.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(visual_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.search_parameters_frame_2 = QtWidgets.QFrame(visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_parameters_frame_2.sizePolicy().hasHeightForWidth())
        self.search_parameters_frame_2.setSizePolicy(sizePolicy)
        self.search_parameters_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.search_parameters_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.search_parameters_frame_2.setObjectName("search_parameters_frame_2")
        self.verticalLayout_22 = QtWidgets.QVBoxLayout(self.search_parameters_frame_2)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.search_initial_parameters_frame_2 = QtWidgets.QFrame(self.search_parameters_frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_initial_parameters_frame_2.sizePolicy().hasHeightForWidth())
        self.search_initial_parameters_frame_2.setSizePolicy(sizePolicy)
        self.search_initial_parameters_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.search_initial_parameters_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.search_initial_parameters_frame_2.setObjectName("search_initial_parameters_frame_2")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.search_initial_parameters_frame_2)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.search_start_year_parameter_label_2 = QtWidgets.QLabel(self.search_initial_parameters_frame_2)
        self.search_start_year_parameter_label_2.setObjectName("search_start_year_parameter_label_2")
        self.gridLayout_6.addWidget(self.search_start_year_parameter_label_2, 0, 1, 1, 1)
        self.search_report_parameter_label_2 = QtWidgets.QLabel(self.search_initial_parameters_frame_2)
        self.search_report_parameter_label_2.setObjectName("search_report_parameter_label_2")
        self.gridLayout_6.addWidget(self.search_report_parameter_label_2, 0, 0, 1, 1)
        self.search_end_year_parameter_label_2 = QtWidgets.QLabel(self.search_initial_parameters_frame_2)
        self.search_end_year_parameter_label_2.setObjectName("search_end_year_parameter_label_2")
        self.gridLayout_6.addWidget(self.search_end_year_parameter_label_2, 0, 2, 1, 1)
        self.search_report_parameter_combobox_2 = QtWidgets.QComboBox(self.search_initial_parameters_frame_2)
        self.search_report_parameter_combobox_2.setObjectName("search_report_parameter_combobox_2")
        self.gridLayout_6.addWidget(self.search_report_parameter_combobox_2, 1, 0, 2, 1)
        self.search_start_year_parameter_dateedit_2 = QtWidgets.QDateEdit(self.search_initial_parameters_frame_2)
        self.search_start_year_parameter_dateedit_2.setObjectName("search_start_year_parameter_dateedit_2")
        self.gridLayout_6.addWidget(self.search_start_year_parameter_dateedit_2, 1, 1, 2, 1)
        self.search_end_year_parameter_dateedit_2 = QtWidgets.QDateEdit(self.search_initial_parameters_frame_2)
        self.search_end_year_parameter_dateedit_2.setCurrentSection(QtWidgets.QDateTimeEdit.YearSection)
        self.search_end_year_parameter_dateedit_2.setObjectName("search_end_year_parameter_dateedit_2")
        self.gridLayout_6.addWidget(self.search_end_year_parameter_dateedit_2, 1, 2, 2, 1)
        self.verticalLayout_22.addWidget(self.search_initial_parameters_frame_2)
        self.verticalLayout.addWidget(self.search_parameters_frame_2)
        self.frame_14 = QtWidgets.QFrame(visual_tab)
        self.frame_14.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_14.setObjectName("frame_14")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.frame_14)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.frame_15 = QtWidgets.QFrame(self.frame_14)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_15.sizePolicy().hasHeightForWidth())
        self.frame_15.setSizePolicy(sizePolicy)
        self.frame_15.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_15.setObjectName("frame_15")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.frame_15)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.frame_2 = QtWidgets.QFrame(self.frame_15)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.visual_name_label = QtWidgets.QLabel(self.frame_2)
        self.visual_name_label.setEnabled(True)
        self.visual_name_label.setGeometry(QtCore.QRect(10, 110, 97, 21))
        self.visual_name_label.setObjectName("visual_name_label")
        self.visual_metric_parameter_label = QtWidgets.QLabel(self.frame_2)
        self.visual_metric_parameter_label.setGeometry(QtCore.QRect(10, 150, 213, 20))
        self.visual_metric_parameter_label.setObjectName("visual_metric_parameter_label")
        self.metric_Type_comboBox = QtWidgets.QComboBox(self.frame_2)
        self.metric_Type_comboBox.setGeometry(QtCore.QRect(90, 150, 331, 26))
        self.metric_Type_comboBox.setObjectName("metric_Type_comboBox")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(170, 0, 212, 35))
        self.label.setObjectName("label")
        self.visual_vendor_parameter_label = QtWidgets.QLabel(self.frame_2)
        self.visual_vendor_parameter_label.setGeometry(QtCore.QRect(10, 70, 44, 20))
        self.visual_vendor_parameter_label.setObjectName("visual_vendor_parameter_label")
        self.visual_vendor_parameter_combobox = QtWidgets.QComboBox(self.frame_2)
        self.visual_vendor_parameter_combobox.setGeometry(QtCore.QRect(90, 70, 331, 26))
        self.visual_vendor_parameter_combobox.setObjectName("visual_vendor_parameter_combobox")
        self.visual_name_parameter_combobox = QtWidgets.QComboBox(self.frame_2)
        self.visual_name_parameter_combobox.setEnabled(True)
        self.visual_name_parameter_combobox.setGeometry(QtCore.QRect(90, 110, 331, 28))
        self.visual_name_parameter_combobox.setEditable(True)
        self.visual_name_parameter_combobox.setObjectName("visual_name_parameter_combobox")
        self.gridLayout_13.addWidget(self.frame_2, 1, 0, 1, 3)
        self.option_frame = QtWidgets.QFrame(self.frame_15)
        self.option_frame.setEnabled(True)
        self.option_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.option_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.option_frame.setObjectName("option_frame")
        self.edit_cost_ratio_frame = QtWidgets.QFrame(self.option_frame)
        self.edit_cost_ratio_frame.setGeometry(QtCore.QRect(10, 10, 141, 81))
        self.edit_cost_ratio_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.edit_cost_ratio_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.edit_cost_ratio_frame.setObjectName("edit_cost_ratio_frame")
        self.label_47 = QtWidgets.QLabel(self.edit_cost_ratio_frame)
        self.label_47.setGeometry(QtCore.QRect(10, 10, 183, 15))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_47.sizePolicy().hasHeightForWidth())
        self.label_47.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.label_47.setFont(font)
        self.label_47.setTextFormat(QtCore.Qt.AutoText)
        self.label_47.setObjectName("label_47")
        self.cost_ratio_option_combobox = QtWidgets.QComboBox(self.edit_cost_ratio_frame)
        self.cost_ratio_option_combobox.setGeometry(QtCore.QRect(0, 30, 121, 26))
        self.cost_ratio_option_combobox.setObjectName("cost_ratio_option_combobox")
        self.edit_top_num_frame = QtWidgets.QFrame(self.option_frame)
        self.edit_top_num_frame.setGeometry(QtCore.QRect(10, 100, 141, 81))
        self.edit_top_num_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.edit_top_num_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.edit_top_num_frame.setObjectName("edit_top_num_frame")
        self.label_48 = QtWidgets.QLabel(self.edit_top_num_frame)
        self.label_48.setGeometry(QtCore.QRect(10, 10, 183, 15))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_48.sizePolicy().hasHeightForWidth())
        self.label_48.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.label_48.setFont(font)
        self.label_48.setTextFormat(QtCore.Qt.AutoText)
        self.label_48.setObjectName("label_48")
        self.top_num_spinbox = QtWidgets.QSpinBox(self.edit_top_num_frame)
        self.top_num_spinbox.setGeometry(QtCore.QRect(10, 30, 101, 24))
        self.top_num_spinbox.setObjectName("top_num_spinbox")
        self.gridLayout_13.addWidget(self.option_frame, 4, 2, 1, 1)
        self.frame_options = QtWidgets.QFrame(self.frame_15)
        self.frame_options.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_options.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_options.setObjectName("frame_options")
        self.label_46 = QtWidgets.QLabel(self.frame_options)
        self.label_46.setGeometry(QtCore.QRect(20, 30, 183, 15))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_46.sizePolicy().hasHeightForWidth())
        self.label_46.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.label_46.setFont(font)
        self.label_46.setTextFormat(QtCore.Qt.AutoText)
        self.label_46.setObjectName("label_46")
        self.monthly_radioButton = QtWidgets.QRadioButton(self.frame_options)
        self.monthly_radioButton.setGeometry(QtCore.QRect(10, 60, 112, 20))
        self.monthly_radioButton.setObjectName("monthly_radioButton")
        self.yearly_radioButton = QtWidgets.QRadioButton(self.frame_options)
        self.yearly_radioButton.setGeometry(QtCore.QRect(10, 90, 112, 20))
        self.yearly_radioButton.setObjectName("yearly_radioButton")
        self.topnum_radioButton = QtWidgets.QRadioButton(self.frame_options)
        self.topnum_radioButton.setGeometry(QtCore.QRect(10, 120, 112, 20))
        self.topnum_radioButton.setObjectName("topnum_radioButton")
        self.costratio_radioButton = QtWidgets.QRadioButton(self.frame_options)
        self.costratio_radioButton.setGeometry(QtCore.QRect(10, 150, 112, 20))
        self.costratio_radioButton.setObjectName("costratio_radioButton")
        self.gridLayout_13.addWidget(self.frame_options, 4, 1, 1, 1)
        self.frame_18 = QtWidgets.QFrame(self.frame_15)
        self.frame_18.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_18.sizePolicy().hasHeightForWidth())
        self.frame_18.setSizePolicy(sizePolicy)
        self.frame_18.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_18.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_18.setObjectName("frame_18")
        self.verticalLayout_28 = QtWidgets.QVBoxLayout(self.frame_18)
        self.verticalLayout_28.setObjectName("verticalLayout_28")
        self.label_45 = QtWidgets.QLabel(self.frame_18)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_45.sizePolicy().hasHeightForWidth())
        self.label_45.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.label_45.setFont(font)
        self.label_45.setTextFormat(QtCore.Qt.AutoText)
        self.label_45.setObjectName("label_45")
        self.verticalLayout_28.addWidget(self.label_45)
        self.radioButton_3 = QtWidgets.QRadioButton(self.frame_18)
        self.radioButton_3.setObjectName("radioButton_3")
        self.verticalLayout_28.addWidget(self.radioButton_3)
        self.radioButton = QtWidgets.QRadioButton(self.frame_18)
        self.radioButton.setObjectName("radioButton")
        self.verticalLayout_28.addWidget(self.radioButton)
        self.radioButton_4 = QtWidgets.QRadioButton(self.frame_18)
        self.radioButton_4.setObjectName("radioButton_4")
        self.verticalLayout_28.addWidget(self.radioButton_4)
        self.gridLayout_13.addWidget(self.frame_18, 4, 0, 1, 1)
        self.horizontalLayout_14.addWidget(self.frame_15)
        self.frame_16 = QtWidgets.QFrame(self.frame_14)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_16.sizePolicy().hasHeightForWidth())
        self.frame_16.setSizePolicy(sizePolicy)
        self.frame_16.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_16.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_16.setObjectName("frame_16")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.frame_16)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.label_36 = QtWidgets.QLabel(self.frame_16)
        self.label_36.setObjectName("label_36")
        self.gridLayout_14.addWidget(self.label_36, 4, 0, 1, 1)
        self.label_44 = QtWidgets.QLabel(self.frame_16)
        self.label_44.setObjectName("label_44")
        self.gridLayout_14.addWidget(self.label_44, 6, 0, 1, 1)
        self.label_43 = QtWidgets.QLabel(self.frame_16)
        self.label_43.setObjectName("label_43")
        self.gridLayout_14.addWidget(self.label_43, 5, 0, 1, 1)
        self.label_42 = QtWidgets.QLabel(self.frame_16)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_42.sizePolicy().hasHeightForWidth())
        self.label_42.setSizePolicy(sizePolicy)
        self.label_42.setAlignment(QtCore.Qt.AlignCenter)
        self.label_42.setObjectName("label_42")
        self.gridLayout_14.addWidget(self.label_42, 1, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.frame_16)
        self.label_16.setObjectName("label_16")
        self.gridLayout_14.addWidget(self.label_16, 3, 0, 1, 1)
        self.file_name_lineEdit = QtWidgets.QLineEdit(self.frame_16)
        self.file_name_lineEdit.setEnabled(True)
        self.file_name_lineEdit.setObjectName("file_name_lineEdit")
        self.gridLayout_14.addWidget(self.file_name_lineEdit, 3, 1, 1, 3)
        self.chart_title_lineEdit = QtWidgets.QLineEdit(self.frame_16)
        self.chart_title_lineEdit.setObjectName("chart_title_lineEdit")
        self.gridLayout_14.addWidget(self.chart_title_lineEdit, 4, 1, 1, 3)
        self.horizontal_axis_lineEdit = QtWidgets.QLineEdit(self.frame_16)
        self.horizontal_axis_lineEdit.setObjectName("horizontal_axis_lineEdit")
        self.gridLayout_14.addWidget(self.horizontal_axis_lineEdit, 5, 1, 1, 3)
        self.vertical_axis_lineEdit = QtWidgets.QLineEdit(self.frame_16)
        self.vertical_axis_lineEdit.setObjectName("vertical_axis_lineEdit")
        self.gridLayout_14.addWidget(self.vertical_axis_lineEdit, 6, 1, 1, 3)
        self.horizontalLayout_14.addWidget(self.frame_16)
        self.verticalLayout.addWidget(self.frame_14)
        self.search_control_frame_2 = QtWidgets.QFrame(visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_control_frame_2.sizePolicy().hasHeightForWidth())
        self.search_control_frame_2.setSizePolicy(sizePolicy)
        self.search_control_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.search_control_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.search_control_frame_2.setObjectName("search_control_frame_2")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.search_control_frame_2)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.create_chart_button = QtWidgets.QPushButton(self.search_control_frame_2)
        self.create_chart_button.setObjectName("create_chart_button")
        self.gridLayout_12.addWidget(self.create_chart_button, 2, 1, 1, 2)
        self.verticalLayout.addWidget(self.search_control_frame_2)

        self.retranslateUi(visual_tab)
        QtCore.QMetaObject.connectSlotsByName(visual_tab)

    def retranslateUi(self, visual_tab):
        _translate = QtCore.QCoreApplication.translate
        visual_tab.setWindowTitle(_translate("visual_tab", "Visual"))
        self.search_start_year_parameter_label_2.setText(_translate("visual_tab", "Start Year"))
        self.search_report_parameter_label_2.setText(_translate("visual_tab", "Report"))
        self.search_end_year_parameter_label_2.setText(_translate("visual_tab", "End year"))
        self.search_start_year_parameter_dateedit_2.setDisplayFormat(_translate("visual_tab", "yyyy"))
        self.search_end_year_parameter_dateedit_2.setDisplayFormat(_translate("visual_tab", "yyyy"))
        self.visual_name_label.setText(_translate("visual_tab", "Database"))
        self.visual_metric_parameter_label.setText(_translate("visual_tab", "Metric Type "))
        self.label.setText(_translate("visual_tab", "Create Chart"))
        self.visual_vendor_parameter_label.setText(_translate("visual_tab", "Vendor"))
        self.label_47.setText(_translate("visual_tab", "Cost Ratio Option"))
        self.label_48.setText(_translate("visual_tab", " Top # "))
        self.label_46.setText(_translate("visual_tab", "Calculation Type"))
        self.monthly_radioButton.setText(_translate("visual_tab", "Monthly"))
        self.yearly_radioButton.setText(_translate("visual_tab", "Yearly"))
        self.topnum_radioButton.setText(_translate("visual_tab", "Top #"))
        self.costratio_radioButton.setText(_translate("visual_tab", "Cost Ratio"))
        self.label_45.setText(_translate("visual_tab", "Select Chart Type"))
        self.radioButton_3.setText(_translate("visual_tab", "Vertical Bar"))
        self.radioButton.setText(_translate("visual_tab", "Horizontal Bar"))
        self.radioButton_4.setText(_translate("visual_tab", "Line"))
        self.label_36.setText(_translate("visual_tab", "Chart Title"))
        self.label_44.setText(_translate("visual_tab", "Vertical Axis Title"))
        self.label_43.setText(_translate("visual_tab", "Horizontal Axis Title"))
        self.label_42.setText(_translate("visual_tab", "Customize Chart"))
        self.label_16.setText(_translate("visual_tab", "File Name"))
        self.create_chart_button.setText(_translate("visual_tab", "Create Chart"))
import Resources_rc
