# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VisualTab.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_visual_tab(object):
    def setupUi(self, visual_tab):
        visual_tab.setObjectName("visual_tab")
        visual_tab.resize(860, 550)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ui/resources/tab_icons/visual_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        visual_tab.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(visual_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.search_initial_parameters_frame_2 = QtWidgets.QFrame(visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_initial_parameters_frame_2.sizePolicy().hasHeightForWidth())
        self.search_initial_parameters_frame_2.setSizePolicy(sizePolicy)
        self.search_initial_parameters_frame_2.setObjectName("search_initial_parameters_frame_2")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.search_initial_parameters_frame_2)
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.report_combo_box = QtWidgets.QComboBox(self.search_initial_parameters_frame_2)
        self.report_combo_box.setObjectName("report_combo_box")
        self.gridLayout_6.addWidget(self.report_combo_box, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem, 0, 4, 1, 1)
        self.visual_vendor_parameter_label = QtWidgets.QLabel(self.search_initial_parameters_frame_2)
        self.visual_vendor_parameter_label.setMinimumSize(QtCore.QSize(200, 0))
        self.visual_vendor_parameter_label.setObjectName("visual_vendor_parameter_label")
        self.gridLayout_6.addWidget(self.visual_vendor_parameter_label, 0, 1, 1, 1)
        self.vendor_combo_box = QtWidgets.QComboBox(self.search_initial_parameters_frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vendor_combo_box.sizePolicy().hasHeightForWidth())
        self.vendor_combo_box.setSizePolicy(sizePolicy)
        self.vendor_combo_box.setObjectName("vendor_combo_box")
        self.gridLayout_6.addWidget(self.vendor_combo_box, 3, 1, 1, 1)
        self.search_end_year_parameter_label_2 = QtWidgets.QLabel(self.search_initial_parameters_frame_2)
        self.search_end_year_parameter_label_2.setMinimumSize(QtCore.QSize(200, 0))
        self.search_end_year_parameter_label_2.setObjectName("search_end_year_parameter_label_2")
        self.gridLayout_6.addWidget(self.search_end_year_parameter_label_2, 0, 3, 1, 1)
        self.search_report_parameter_label_2 = QtWidgets.QLabel(self.search_initial_parameters_frame_2)
        self.search_report_parameter_label_2.setMinimumSize(QtCore.QSize(200, 0))
        self.search_report_parameter_label_2.setObjectName("search_report_parameter_label_2")
        self.gridLayout_6.addWidget(self.search_report_parameter_label_2, 0, 0, 1, 1)
        self.search_start_year_parameter_label_2 = QtWidgets.QLabel(self.search_initial_parameters_frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_start_year_parameter_label_2.sizePolicy().hasHeightForWidth())
        self.search_start_year_parameter_label_2.setSizePolicy(sizePolicy)
        self.search_start_year_parameter_label_2.setMinimumSize(QtCore.QSize(200, 0))
        self.search_start_year_parameter_label_2.setObjectName("search_start_year_parameter_label_2")
        self.gridLayout_6.addWidget(self.search_start_year_parameter_label_2, 0, 2, 1, 1)
        self.start_year_date_edit = QtWidgets.QDateEdit(self.search_initial_parameters_frame_2)
        self.start_year_date_edit.setObjectName("start_year_date_edit")
        self.gridLayout_6.addWidget(self.start_year_date_edit, 3, 2, 1, 1)
        self.end_year_date_edit = QtWidgets.QDateEdit(self.search_initial_parameters_frame_2)
        self.end_year_date_edit.setCurrentSection(QtWidgets.QDateTimeEdit.YearSection)
        self.end_year_date_edit.setObjectName("end_year_date_edit")
        self.gridLayout_6.addWidget(self.end_year_date_edit, 3, 3, 1, 1)
        self.start_month_combo_box = QtWidgets.QComboBox(self.search_initial_parameters_frame_2)
        self.start_month_combo_box.setObjectName("start_month_combo_box")
        self.gridLayout_6.addWidget(self.start_month_combo_box, 4, 2, 1, 1)
        self.end_month_combo_box = QtWidgets.QComboBox(self.search_initial_parameters_frame_2)
        self.end_month_combo_box.setObjectName("end_month_combo_box")
        self.gridLayout_6.addWidget(self.end_month_combo_box, 4, 3, 1, 1)
        self.verticalLayout.addWidget(self.search_initial_parameters_frame_2)
        self.frame_15 = QtWidgets.QFrame(visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_15.sizePolicy().hasHeightForWidth())
        self.frame_15.setSizePolicy(sizePolicy)
        self.frame_15.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_15.setObjectName("frame_15")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_15)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame = QtWidgets.QFrame(self.frame_15)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_18 = QtWidgets.QFrame(self.frame)
        self.frame_18.setEnabled(True)
        self.frame_18.setMinimumSize(QtCore.QSize(200, 0))
        self.frame_18.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_18.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_18.setObjectName("frame_18")
        self.verticalLayout_28 = QtWidgets.QVBoxLayout(self.frame_18)
        self.verticalLayout_28.setObjectName("verticalLayout_28")
        self.label_45 = QtWidgets.QLabel(self.frame_18)
        self.label_45.setTextFormat(QtCore.Qt.AutoText)
        self.label_45.setObjectName("label_45")
        self.verticalLayout_28.addWidget(self.label_45)
        self.vertical_bar_radio_button = QtWidgets.QRadioButton(self.frame_18)
        self.vertical_bar_radio_button.setObjectName("vertical_bar_radio_button")
        self.verticalLayout_28.addWidget(self.vertical_bar_radio_button)
        self.horizontal_bar_radio_button = QtWidgets.QRadioButton(self.frame_18)
        self.horizontal_bar_radio_button.setObjectName("horizontal_bar_radio_button")
        self.verticalLayout_28.addWidget(self.horizontal_bar_radio_button)
        self.line_radio_button = QtWidgets.QRadioButton(self.frame_18)
        self.line_radio_button.setObjectName("line_radio_button")
        self.verticalLayout_28.addWidget(self.line_radio_button)
        spacerItem1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_28.addItem(spacerItem1)
        self.horizontalLayout.addWidget(self.frame_18)
        self.frame_options = QtWidgets.QFrame(self.frame)
        self.frame_options.setMinimumSize(QtCore.QSize(200, 0))
        self.frame_options.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_options.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_options.setObjectName("frame_options")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_options)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_46 = QtWidgets.QLabel(self.frame_options)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_46.sizePolicy().hasHeightForWidth())
        self.label_46.setSizePolicy(sizePolicy)
        self.label_46.setTextFormat(QtCore.Qt.AutoText)
        self.label_46.setObjectName("label_46")
        self.verticalLayout_3.addWidget(self.label_46)
        self.monthly_radio_button = QtWidgets.QRadioButton(self.frame_options)
        self.monthly_radio_button.setObjectName("monthly_radio_button")
        self.verticalLayout_3.addWidget(self.monthly_radio_button)
        self.yearly_radio_button = QtWidgets.QRadioButton(self.frame_options)
        self.yearly_radio_button.setObjectName("yearly_radio_button")
        self.verticalLayout_3.addWidget(self.yearly_radio_button)
        self.top_radio_button = QtWidgets.QRadioButton(self.frame_options)
        self.top_radio_button.setObjectName("top_radio_button")
        self.verticalLayout_3.addWidget(self.top_radio_button)
        self.cost_ratio_radio_button = QtWidgets.QRadioButton(self.frame_options)
        self.cost_ratio_radio_button.setObjectName("cost_ratio_radio_button")
        self.verticalLayout_3.addWidget(self.cost_ratio_radio_button)
        spacerItem2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.horizontalLayout.addWidget(self.frame_options)
        self.frame_16 = QtWidgets.QFrame(self.frame)
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
        self.vertical_axis_line_edit = QtWidgets.QLineEdit(self.frame_16)
        self.vertical_axis_line_edit.setObjectName("vertical_axis_line_edit")
        self.gridLayout_14.addWidget(self.vertical_axis_line_edit, 2, 2, 1, 1)
        self.label_43 = QtWidgets.QLabel(self.frame_16)
        self.label_43.setObjectName("label_43")
        self.gridLayout_14.addWidget(self.label_43, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_14.addItem(spacerItem3, 3, 0, 1, 1)
        self.label_44 = QtWidgets.QLabel(self.frame_16)
        self.label_44.setObjectName("label_44")
        self.gridLayout_14.addWidget(self.label_44, 2, 0, 1, 1)
        self.horizontal_axis_line_edit = QtWidgets.QLineEdit(self.frame_16)
        self.horizontal_axis_line_edit.setObjectName("horizontal_axis_line_edit")
        self.gridLayout_14.addWidget(self.horizontal_axis_line_edit, 1, 2, 1, 1)
        self.chart_title_line_edit = QtWidgets.QLineEdit(self.frame_16)
        self.chart_title_line_edit.setObjectName("chart_title_line_edit")
        self.gridLayout_14.addWidget(self.chart_title_line_edit, 0, 2, 1, 1)
        self.label_36 = QtWidgets.QLabel(self.frame_16)
        self.label_36.setObjectName("label_36")
        self.gridLayout_14.addWidget(self.label_36, 0, 0, 1, 1)
        self.horizontalLayout.addWidget(self.frame_16)
        self.verticalLayout_2.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.frame_15)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout.setObjectName("gridLayout")
        self.metric_type_label = QtWidgets.QLabel(self.frame_2)
        self.metric_type_label.setObjectName("metric_type_label")
        self.gridLayout.addWidget(self.metric_type_label, 0, 0, 1, 1)
        self.metric_type_combo_box = QtWidgets.QComboBox(self.frame_2)
        self.metric_type_combo_box.setMinimumSize(QtCore.QSize(200, 0))
        self.metric_type_combo_box.setObjectName("metric_type_combo_box")
        self.gridLayout.addWidget(self.metric_type_combo_box, 0, 1, 1, 1)
        self.top_label = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top_label.sizePolicy().hasHeightForWidth())
        self.top_label.setSizePolicy(sizePolicy)
        self.top_label.setTextFormat(QtCore.Qt.AutoText)
        self.top_label.setObjectName("top_label")
        self.gridLayout.addWidget(self.top_label, 2, 0, 1, 1)
        self.cost_ratio_combo_box = QtWidgets.QComboBox(self.frame_2)
        self.cost_ratio_combo_box.setMinimumSize(QtCore.QSize(200, 0))
        self.cost_ratio_combo_box.setObjectName("cost_ratio_combo_box")
        self.gridLayout.addWidget(self.cost_ratio_combo_box, 3, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 0, 2, 1, 1)
        self.cost_ratio_label = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cost_ratio_label.sizePolicy().hasHeightForWidth())
        self.cost_ratio_label.setSizePolicy(sizePolicy)
        self.cost_ratio_label.setTextFormat(QtCore.Qt.AutoText)
        self.cost_ratio_label.setObjectName("cost_ratio_label")
        self.gridLayout.addWidget(self.cost_ratio_label, 3, 0, 1, 1)
        self.name_label = QtWidgets.QLabel(self.frame_2)
        self.name_label.setEnabled(True)
        self.name_label.setObjectName("name_label")
        self.gridLayout.addWidget(self.name_label, 1, 0, 1, 1)
        self.name_combo_box = QtWidgets.QComboBox(self.frame_2)
        self.name_combo_box.setEnabled(True)
        self.name_combo_box.setMinimumSize(QtCore.QSize(200, 0))
        self.name_combo_box.setEditable(True)
        self.name_combo_box.setObjectName("name_combo_box")
        self.gridLayout.addWidget(self.name_combo_box, 1, 1, 1, 1)
        self.top_spin_box = QtWidgets.QSpinBox(self.frame_2)
        self.top_spin_box.setMinimumSize(QtCore.QSize(200, 0))
        self.top_spin_box.setMaximum(999)
        self.top_spin_box.setProperty("value", 1)
        self.top_spin_box.setObjectName("top_spin_box")
        self.gridLayout.addWidget(self.top_spin_box, 2, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.frame_2)
        self.verticalLayout.addWidget(self.frame_15)
        self.search_control_frame_2 = QtWidgets.QFrame(visual_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_control_frame_2.sizePolicy().hasHeightForWidth())
        self.search_control_frame_2.setSizePolicy(sizePolicy)
        self.search_control_frame_2.setObjectName("search_control_frame_2")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.search_control_frame_2)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.open_folder_checkBox = QtWidgets.QCheckBox(self.search_control_frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.open_folder_checkBox.sizePolicy().hasHeightForWidth())
        self.open_folder_checkBox.setSizePolicy(sizePolicy)
        self.open_folder_checkBox.setObjectName("open_folder_checkBox")
        self.gridLayout_12.addWidget(self.open_folder_checkBox, 2, 0, 1, 1)
        self.create_chart_button = QtWidgets.QPushButton(self.search_control_frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_chart_button.sizePolicy().hasHeightForWidth())
        self.create_chart_button.setSizePolicy(sizePolicy)
        self.create_chart_button.setObjectName("create_chart_button")
        self.gridLayout_12.addWidget(self.create_chart_button, 0, 1, 3, 2)
        self.open_file_checkBox = QtWidgets.QCheckBox(self.search_control_frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.open_file_checkBox.sizePolicy().hasHeightForWidth())
        self.open_file_checkBox.setSizePolicy(sizePolicy)
        self.open_file_checkBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.open_file_checkBox.setChecked(True)
        self.open_file_checkBox.setObjectName("open_file_checkBox")
        self.gridLayout_12.addWidget(self.open_file_checkBox, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.search_control_frame_2)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem5)

        self.retranslateUi(visual_tab)
        QtCore.QMetaObject.connectSlotsByName(visual_tab)

    def retranslateUi(self, visual_tab):
        _translate = QtCore.QCoreApplication.translate
        visual_tab.setWindowTitle(_translate("visual_tab", "Visual"))
        self.visual_vendor_parameter_label.setText(_translate("visual_tab", "Vendor"))
        self.search_end_year_parameter_label_2.setText(_translate("visual_tab", "End Date"))
        self.search_report_parameter_label_2.setText(_translate("visual_tab", "Report"))
        self.search_start_year_parameter_label_2.setText(_translate("visual_tab", "Start Date"))
        self.start_year_date_edit.setDisplayFormat(_translate("visual_tab", "yyyy"))
        self.end_year_date_edit.setDisplayFormat(_translate("visual_tab", "yyyy"))
        self.label_45.setText(_translate("visual_tab", "Select Chart Type"))
        self.vertical_bar_radio_button.setText(_translate("visual_tab", "Vertical Bar"))
        self.horizontal_bar_radio_button.setText(_translate("visual_tab", "Horizontal Bar"))
        self.line_radio_button.setText(_translate("visual_tab", "Line"))
        self.label_46.setText(_translate("visual_tab", "Calculation Type"))
        self.monthly_radio_button.setText(_translate("visual_tab", "Monthly"))
        self.yearly_radio_button.setText(_translate("visual_tab", "Yearly"))
        self.top_radio_button.setText(_translate("visual_tab", "Top #"))
        self.cost_ratio_radio_button.setText(_translate("visual_tab", "Cost Ratio"))
        self.label_43.setText(_translate("visual_tab", "Horizontal Axis Title"))
        self.label_44.setText(_translate("visual_tab", "Vertical Axis Title"))
        self.label_36.setText(_translate("visual_tab", "Chart Title"))
        self.metric_type_label.setText(_translate("visual_tab", "Metric Type "))
        self.top_label.setText(_translate("visual_tab", " Top # "))
        self.cost_ratio_label.setText(_translate("visual_tab", "Cost Ratio Option"))
        self.name_label.setText(_translate("visual_tab", "Name"))
        self.open_folder_checkBox.setText(_translate("visual_tab", "Open Folder"))
        self.create_chart_button.setText(_translate("visual_tab", "Create Chart"))
        self.open_file_checkBox.setText(_translate("visual_tab", "Open File"))

import Resources_rc
