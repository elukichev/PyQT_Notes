# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'welcome_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Welcome_window(object):
    def setupUi(self, Welcome_window):
        Welcome_window.setObjectName("Welcome_window")
        Welcome_window.resize(661, 242)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Welcome_window)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.welocom_message = QtWidgets.QLabel(Welcome_window)
        self.welocom_message.setObjectName("welocom_message")
        self.horizontalLayout.addWidget(self.welocom_message)
        self.usernames_box = QtWidgets.QComboBox(Welcome_window)
        self.usernames_box.setObjectName("usernames_box")
        self.horizontalLayout.addWidget(self.usernames_box)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.start_button = QtWidgets.QPushButton(Welcome_window)
        self.start_button.setObjectName("start_button")
        self.horizontalLayout_2.addWidget(self.start_button)
        self.delete_user_button = QtWidgets.QPushButton(Welcome_window)
        self.delete_user_button.setObjectName("delete_user_button")
        self.horizontalLayout_2.addWidget(self.delete_user_button)
        self.new_user_button = QtWidgets.QPushButton(Welcome_window)
        self.new_user_button.setObjectName("new_user_button")
        self.horizontalLayout_2.addWidget(self.new_user_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Welcome_window)
        QtCore.QMetaObject.connectSlotsByName(Welcome_window)

    def retranslateUi(self, Welcome_window):
        _translate = QtCore.QCoreApplication.translate
        Welcome_window.setWindowTitle(_translate("Welcome_window", "Notes - Выбор пользователя"))
        self.welocom_message.setText(_translate("Welcome_window", "Выберите пользователя"))
        self.start_button.setText(_translate("Welcome_window", "Выбрать пользователя"))
        self.delete_user_button.setText(_translate("Welcome_window", "Удалить пользователя"))
        self.new_user_button.setText(_translate("Welcome_window", "Создать нового пользователя"))
