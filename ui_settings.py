# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui_settings.ui'
#
# Created: Wed Nov  6 22:44:20 2013
#      by: PyQt5 UI code generator 5.1.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(415, 328)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(SettingsDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(SettingsDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.pushButton = QtWidgets.QPushButton(SettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/newPrefix/images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(SettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/newPrefix/images/remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.listWidget = QtWidgets.QListWidget(SettingsDialog)
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        self.verticalLayout.addWidget(self.listWidget)
        self.label_2 = QtWidgets.QLabel(SettingsDialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.textAppSettings = QtWidgets.QLineEdit(SettingsDialog)
        self.textAppSettings.setEnabled(False)
        self.textAppSettings.setObjectName("textAppSettings")
        self.horizontalLayout_4.addWidget(self.textAppSettings)
        self.pushSelectAppSettingsDir = QtWidgets.QPushButton(SettingsDialog)
        self.pushSelectAppSettingsDir.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/newPrefix/images/open_folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushSelectAppSettingsDir.setIcon(icon2)
        self.pushSelectAppSettingsDir.setObjectName("pushSelectAppSettingsDir")
        self.horizontalLayout_4.addWidget(self.pushSelectAppSettingsDir)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.label_3 = QtWidgets.QLabel(SettingsDialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.textMangaSettings = QtWidgets.QLineEdit(SettingsDialog)
        self.textMangaSettings.setEnabled(False)
        self.textMangaSettings.setObjectName("textMangaSettings")
        self.horizontalLayout_2.addWidget(self.textMangaSettings)
        self.pushSelectMangaSettingsDir = QtWidgets.QPushButton(SettingsDialog)
        self.pushSelectMangaSettingsDir.setText("")
        self.pushSelectMangaSettingsDir.setIcon(icon2)
        self.pushSelectMangaSettingsDir.setObjectName("pushSelectMangaSettingsDir")
        self.horizontalLayout_2.addWidget(self.pushSelectMangaSettingsDir)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.label_4 = QtWidgets.QLabel(SettingsDialog)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.textUnrarExe = QtWidgets.QLineEdit(SettingsDialog)
        self.textUnrarExe.setEnabled(False)
        self.textUnrarExe.setObjectName("textUnrarExe")
        self.horizontalLayout_3.addWidget(self.textUnrarExe)
        self.pushSelectUnrarExecutable = QtWidgets.QPushButton(SettingsDialog)
        self.pushSelectUnrarExecutable.setText("")
        self.pushSelectUnrarExecutable.setIcon(icon2)
        self.pushSelectUnrarExecutable.setObjectName("pushSelectUnrarExecutable")
        self.horizontalLayout_3.addWidget(self.pushSelectUnrarExecutable)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(SettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "PyMangaReader Settings"))
        self.label.setText(_translate("SettingsDialog", "Manga Directories"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("SettingsDialog", "1"))
        item = self.listWidget.item(1)
        item.setText(_translate("SettingsDialog", "2"))
        item = self.listWidget.item(2)
        item.setText(_translate("SettingsDialog", "3"))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.label_2.setText(_translate("SettingsDialog", "Application Settings"))
        self.label_3.setText(_translate("SettingsDialog", "Manga settings (last viewed page)"))
        self.label_4.setText(_translate("SettingsDialog", "Unrar executable (if not in PATH)"))

import images_res_rc