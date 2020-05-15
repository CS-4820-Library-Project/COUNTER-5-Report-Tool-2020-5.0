# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CostsTab.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_costs_tab(object):
    def setupUi(self, costs_tab):
        costs_tab.setObjectName("costs_tab")
        costs_tab.resize(902, 552)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ui/resources/tab_icons/costs_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        costs_tab.setWindowIcon(icon)
        self.horizontalLayout = QtWidgets.QHBoxLayout(costs_tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(120, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.frame = QtWidgets.QFrame(costs_tab)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.costs_parameters_frame = QtWidgets.QFrame(self.frame)
        self.costs_parameters_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.costs_parameters_frame.setObjectName("costs_parameters_frame")
        self.formLayout_3 = QtWidgets.QFormLayout(self.costs_parameters_frame)
        self.formLayout_3.setObjectName("formLayout_3")
        self.costs_report_parameter_label = QtWidgets.QLabel(self.costs_parameters_frame)
        self.costs_report_parameter_label.setObjectName("costs_report_parameter_label")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.costs_report_parameter_label)
        self.costs_report_parameter_combobox = QtWidgets.QComboBox(self.costs_parameters_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.costs_report_parameter_combobox.sizePolicy().hasHeightForWidth())
        self.costs_report_parameter_combobox.setSizePolicy(sizePolicy)
        self.costs_report_parameter_combobox.setMinimumSize(QtCore.QSize(300, 0))
        self.costs_report_parameter_combobox.setObjectName("costs_report_parameter_combobox")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.costs_report_parameter_combobox)
        self.costs_vendor_parameter_label = QtWidgets.QLabel(self.costs_parameters_frame)
        self.costs_vendor_parameter_label.setObjectName("costs_vendor_parameter_label")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.costs_vendor_parameter_label)
        self.costs_vendor_parameter_combobox = QtWidgets.QComboBox(self.costs_parameters_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.costs_vendor_parameter_combobox.sizePolicy().hasHeightForWidth())
        self.costs_vendor_parameter_combobox.setSizePolicy(sizePolicy)
        self.costs_vendor_parameter_combobox.setMinimumSize(QtCore.QSize(300, 0))
        self.costs_vendor_parameter_combobox.setEditable(False)
        self.costs_vendor_parameter_combobox.setObjectName("costs_vendor_parameter_combobox")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.costs_vendor_parameter_combobox)
        self.costs_name_parameter_label = QtWidgets.QLabel(self.costs_parameters_frame)
        self.costs_name_parameter_label.setObjectName("costs_name_parameter_label")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.costs_name_parameter_label)
        self.costs_name_parameter_combobox = QtWidgets.QComboBox(self.costs_parameters_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.costs_name_parameter_combobox.sizePolicy().hasHeightForWidth())
        self.costs_name_parameter_combobox.setSizePolicy(sizePolicy)
        self.costs_name_parameter_combobox.setMinimumSize(QtCore.QSize(300, 0))
        self.costs_name_parameter_combobox.setEditable(True)
        self.costs_name_parameter_combobox.setObjectName("costs_name_parameter_combobox")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.costs_name_parameter_combobox)
        self.verticalLayout_2.addWidget(self.costs_parameters_frame)
        self.frame_3 = QtWidgets.QFrame(self.frame)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.costs_values_frame = QtWidgets.QFrame(self.frame_3)
        self.costs_values_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.costs_values_frame.setObjectName("costs_values_frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.costs_values_frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.costs_values_frame)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.end_year_date_edit = QtWidgets.QDateEdit(self.costs_values_frame)
        self.end_year_date_edit.setObjectName("end_year_date_edit")
        self.gridLayout_2.addWidget(self.end_year_date_edit, 1, 1, 1, 1)
        self.costs_cost_in_original_currency_label = QtWidgets.QLabel(self.costs_values_frame)
        self.costs_cost_in_original_currency_label.setObjectName("costs_cost_in_original_currency_label")
        self.gridLayout_2.addWidget(self.costs_cost_in_original_currency_label, 3, 0, 1, 1)
        self.start_year_date_edit = QtWidgets.QDateEdit(self.costs_values_frame)
        self.start_year_date_edit.setObjectName("start_year_date_edit")
        self.gridLayout_2.addWidget(self.start_year_date_edit, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.costs_values_frame)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.costs_cost_in_local_currency_with_tax_label = QtWidgets.QLabel(self.costs_values_frame)
        self.costs_cost_in_local_currency_with_tax_label.setObjectName("costs_cost_in_local_currency_with_tax_label")
        self.gridLayout_2.addWidget(self.costs_cost_in_local_currency_with_tax_label, 6, 0, 1, 1)
        self.costs_cost_in_local_currency_label = QtWidgets.QLabel(self.costs_values_frame)
        self.costs_cost_in_local_currency_label.setObjectName("costs_cost_in_local_currency_label")
        self.gridLayout_2.addWidget(self.costs_cost_in_local_currency_label, 5, 0, 1, 1)
        self.costs_cost_in_local_currency_with_tax_doublespinbox = QtWidgets.QDoubleSpinBox(self.costs_values_frame)
        self.costs_cost_in_local_currency_with_tax_doublespinbox.setEnabled(False)
        self.costs_cost_in_local_currency_with_tax_doublespinbox.setMaximum(999999999.99)
        self.costs_cost_in_local_currency_with_tax_doublespinbox.setObjectName("costs_cost_in_local_currency_with_tax_doublespinbox")
        self.gridLayout_2.addWidget(self.costs_cost_in_local_currency_with_tax_doublespinbox, 6, 1, 1, 1)
        self.costs_original_currency_value_combobox = QtWidgets.QComboBox(self.costs_values_frame)
        self.costs_original_currency_value_combobox.setEnabled(False)
        self.costs_original_currency_value_combobox.setEditable(True)
        self.costs_original_currency_value_combobox.setObjectName("costs_original_currency_value_combobox")
        self.gridLayout_2.addWidget(self.costs_original_currency_value_combobox, 4, 1, 1, 1)
        self.costs_cost_in_original_currency_doublespinbox = QtWidgets.QDoubleSpinBox(self.costs_values_frame)
        self.costs_cost_in_original_currency_doublespinbox.setEnabled(False)
        self.costs_cost_in_original_currency_doublespinbox.setMaximum(999999999.99)
        self.costs_cost_in_original_currency_doublespinbox.setObjectName("costs_cost_in_original_currency_doublespinbox")
        self.gridLayout_2.addWidget(self.costs_cost_in_original_currency_doublespinbox, 3, 1, 1, 1)
        self.costs_cost_in_local_currency_doublespinbox = QtWidgets.QDoubleSpinBox(self.costs_values_frame)
        self.costs_cost_in_local_currency_doublespinbox.setEnabled(False)
        self.costs_cost_in_local_currency_doublespinbox.setMaximum(999999999.99)
        self.costs_cost_in_local_currency_doublespinbox.setObjectName("costs_cost_in_local_currency_doublespinbox")
        self.gridLayout_2.addWidget(self.costs_cost_in_local_currency_doublespinbox, 5, 1, 1, 1)
        self.costs_original_currency_label = QtWidgets.QLabel(self.costs_values_frame)
        self.costs_original_currency_label.setObjectName("costs_original_currency_label")
        self.gridLayout_2.addWidget(self.costs_original_currency_label, 4, 0, 1, 1)
        self.end_month_combo_box = QtWidgets.QComboBox(self.costs_values_frame)
        self.end_month_combo_box.setObjectName("end_month_combo_box")
        self.gridLayout_2.addWidget(self.end_month_combo_box, 1, 2, 1, 1)
        self.start_month_combo_box = QtWidgets.QComboBox(self.costs_values_frame)
        self.start_month_combo_box.setObjectName("start_month_combo_box")
        self.gridLayout_2.addWidget(self.start_month_combo_box, 0, 2, 1, 1)
        self.verticalLayout.addWidget(self.costs_values_frame)
        self.update_cost_frame = QtWidgets.QFrame(self.frame_3)
        self.update_cost_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.update_cost_frame.setObjectName("update_cost_frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.update_cost_frame)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.costs_save_button = QtWidgets.QPushButton(self.update_cost_frame)
        self.costs_save_button.setObjectName("costs_save_button")
        self.horizontalLayout_3.addWidget(self.costs_save_button)
        self.costs_load_button = QtWidgets.QPushButton(self.update_cost_frame)
        self.costs_load_button.setObjectName("costs_load_button")
        self.horizontalLayout_3.addWidget(self.costs_load_button)
        self.costs_clear_button = QtWidgets.QPushButton(self.update_cost_frame)
        self.costs_clear_button.setObjectName("costs_clear_button")
        self.horizontalLayout_3.addWidget(self.costs_clear_button)
        self.verticalLayout.addWidget(self.update_cost_frame)
        spacerItem2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addWidget(self.frame_3)
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.list_view = QtWidgets.QListView(self.frame_2)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setObjectName("list_view")
        self.verticalLayout_3.addWidget(self.list_view)
        self.verticalLayout_2.addWidget(self.frame_2)
        self.frame_6 = QtWidgets.QFrame(self.frame)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.costs_import_costs_button = QtWidgets.QPushButton(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.costs_import_costs_button.sizePolicy().hasHeightForWidth())
        self.costs_import_costs_button.setSizePolicy(sizePolicy)
        self.costs_import_costs_button.setObjectName("costs_import_costs_button")
        self.horizontalLayout_4.addWidget(self.costs_import_costs_button, 0, QtCore.Qt.AlignLeft)
        self.verticalLayout_2.addWidget(self.frame_6)
        self.horizontalLayout.addWidget(self.frame)
        spacerItem3 = QtWidgets.QSpacerItem(120, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)

        self.retranslateUi(costs_tab)
        QtCore.QMetaObject.connectSlotsByName(costs_tab)

    def retranslateUi(self, costs_tab):
        _translate = QtCore.QCoreApplication.translate
        costs_tab.setWindowTitle(_translate("costs_tab", "Costs"))
        self.costs_report_parameter_label.setText(_translate("costs_tab", "Report"))
        self.costs_vendor_parameter_label.setText(_translate("costs_tab", "Vendor"))
        self.costs_name_parameter_label.setText(_translate("costs_tab", "Name"))
        self.label.setText(_translate("costs_tab", "End Date"))
        self.end_year_date_edit.setDisplayFormat(_translate("costs_tab", "yyyy"))
        self.costs_cost_in_original_currency_label.setText(_translate("costs_tab", "Cost in Original Currency"))
        self.start_year_date_edit.setDisplayFormat(_translate("costs_tab", "yyyy"))
        self.label_2.setText(_translate("costs_tab", "Start Date"))
        self.costs_cost_in_local_currency_with_tax_label.setText(_translate("costs_tab", "Cost in Local Currency with Tax"))
        self.costs_cost_in_local_currency_label.setText(_translate("costs_tab", "Cost in Local Currency"))
        self.costs_original_currency_label.setText(_translate("costs_tab", "Original Currency"))
        self.costs_save_button.setText(_translate("costs_tab", "Update Costs"))
        self.costs_load_button.setText(_translate("costs_tab", "Refresh"))
        self.costs_clear_button.setText(_translate("costs_tab", "Clear Fields"))
        self.label_3.setText(_translate("costs_tab", "Available Costs"))
        self.costs_import_costs_button.setText(_translate("costs_tab", "Import Costs File"))
import Resources_rc
