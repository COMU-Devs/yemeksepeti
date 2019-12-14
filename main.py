# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deneme.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QLabel, QPushButton, QListWidgetItem, \
    QHBoxLayout

from PyQt5.QtGui import QIcon, QPixmap

import sqlite3
from random import randint


class productQWidget(QWidget):
    def __init__(self, productName, ingredients='icindekiler:', imagepath='assets/empty.png', parent=None):
        super(productQWidget, self).__init__(parent)
        self.parent = parent
        self.productimage = QLabel()
        self.name = productName
        self.imgpath = imagepath
        self.imgsizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        self.imgsizePolicy.setHorizontalStretch(0)
        self.imgsizePolicy.setVerticalStretch(0)
        self.imgsizePolicy.setHeightForWidth(
            self.productimage.sizePolicy().hasHeightForWidth())
        self.pixmap = QPixmap(self.imgpath).scaled(
            30, 30, QtCore.Qt.KeepAspectRatio)
        self.productimage.setSizePolicy(self.imgsizePolicy)
        self.productimage.setPixmap(self.pixmap)
        self.productNameLabel = QLabel(self.name)
        self.ingredientsLabel = QLabel(ingredients)
        self.button = QPushButton("+")
        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addWidget(self.productNameLabel)
        self.vLayout.addWidget(self.ingredientsLabel)
        self.hLayout.addWidget(self.productimage)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.button)

        self.setLayout(self.hLayout)
        self.button.clicked.connect(
            lambda: self.parent.grandparent.sepet.addSepetItem(self.name))


class restaurantQWidget(QWidget):
    def __init__(self, row, parent=None):
        super(restaurantQWidget, self).__init__(parent)
        self.parent = parent
        self.values = row
        name, address, minPayment = row[2:]

        self.restaurantNameLabel = QLabel(row)
        self.button = QPushButton("sec")

        self.hLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.restaurantNameLabel)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.button)
        self.setLayout(self.hLayout)

        self.button.clicked.connect(
            lambda: self.parent.listProducts(restaurantName=self.name))


class menuQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.grandparent = grandparent
        self.listRestaurants()

    def listRestaurants(self):
        conn = sqlite3.connect('company.db')
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT dnumber FROM department')
            result = cur.fetchall()
            for row in (result):
                item = QListWidgetItem(self)
                item_widget = restaurantQWidget(
                    str(row[0]), parent=self)
                item.setSizeHint(item_widget.sizeHint())
                self.addItem(item)
                self.setItemWidget(item, item_widget)
            cur = None
        conn = None

    def listProducts(self, restaurantName):
        self.clear()
        print(restaurantName)
        conn = sqlite3.connect('company.db')
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM employee WHERE dno = ' + restaurantName)
            result = cur.fetchall()
            for row in (result):
                item = QListWidgetItem(self)
                item_widget = productQWidget(
                    str(row[0]), parent=self)
                item.setSizeHint(item_widget.sizeHint())
                self.addItem(item)
                self.setItemWidget(item, item_widget)
            cur = None
        conn = None


class sepetItemQWidget(QWidget):
    def __init__(self, itemName, amount, imagepath='assets/empty.png', parent=None):
        super(sepetItemQWidget, self).__init__(parent)
        self.parent = parent
        self.name = itemName
        self.amount = amount
        self.productimage = QLabel()
        self.imgsizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        self.imgsizePolicy.setHorizontalStretch(0)
        self.imgsizePolicy.setVerticalStretch(0)
        self.imgsizePolicy.setHeightForWidth(
            self.productimage.sizePolicy().hasHeightForWidth())
        self.pixmap = QPixmap(imagepath).scaled(
            30, 30, QtCore.Qt.KeepAspectRatio)
        self.productimage.setSizePolicy(self.imgsizePolicy)
        self.productimage.setPixmap(self.pixmap)
        self.productNameLabel = QLabel(self.name)
        self.hLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()
        self.button = QPushButton("+")
        self.button2 = QPushButton('-')
        self.amountLabel = QLabel(str(self.amount))
        self.hLayout.addWidget(self.productimage)
        self.hLayout.addWidget(self.productNameLabel)
        self.hLayout.addWidget(self.amountLabel)
        self.hLayout.addWidget(self.button)
        self.hLayout.addWidget(self.button2)
        self.setLayout(self.hLayout)
        # TODO: add button1's connection.
        self.button2.clicked.connect(
            lambda: self.parent.removeSepetItem(self.name))


class sepetQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        # self.listSepetItems()

    def listSepetItems(self):
        self.clear()
        conn = sqlite3.connect('yemeksepeti.db')
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM restaurant')
            result = cur.fetchall()
            for row in (result):
                item = QListWidgetItem(self)
                item_widget = sepetItemQWidget(row, 1, parent=self)
                item.setSizeHint(item_widget.sizeHint())
                self.addItem(item)
                self.setItemWidget(item, item_widget)
            cur = None
        conn = None

    def addSepetItem(self, name):
        conn = None
        conn = sqlite3.connect('company.db')
        with conn:
            cur = conn.cursor()
            x, y, z, t = str(randint(0, 99999999)), randint(
                0, 99999999), name, randint(0, 99999999)
            cur.execute(
                "INSERT INTO project(pname,pnumber,plocation,dnum)" +
                f"VALUES('{x}', '{y}', '{z}', '{t}')"
            )
            cur = None
        conn = None

        self.listSepetItems()

    def removeSepetItem(self, name):
        # if not item's amount == 1:
        conn = None
        conn = sqlite3.connect('company.db')
        with conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM project WHERE pname =" + str(name)
            )
            cur = None
        conn = None
        # else amount -= 1

        self.listSepetItems()


class orderItemQWidget(QWidget):
    def __init__(self, orderName, imagepath='assets/empty.png', parent=None):
        super(orderItemQWidget, self).__init__(parent)
        self.parent = parent
        self.name = orderName

        self.hLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()

        self.orderNameLabel = QLabel(self.name)
        self.price = randint(0, 999)
        self.priceLabel = QLabel(str(self.price))

        self.hLayout.addWidget(self.orderNameLabel)
        self.hLayout.addWidget(self.priceLabel)
        self.setLayout(self.hLayout)


class orderQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        # self.listOrders()

    def listOrders(self):
        self.clear()
        conn = sqlite3.connect('company.db')
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM works_on')
            result = cur.fetchall()
            for row in (result):
                item = QListWidgetItem(self)
                item_widget = orderItemQWidget(
                    str(row[0]), 1, parent=self)
                item.setSizeHint(item_widget.sizeHint())
                self.addItem(item)
                self.setItemWidget(item, item_widget)
            cur = None
        conn = None


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1087, 666)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")

        self.menu = menuQWidget(self.tab, grandparent=self)
        self.menu.setGeometry(QtCore.QRect(30, 40, 421, 441))
        self.menu.setObjectName('listOfProducts')

        self.sepet = sepetQWidget(self.tab, grandparent=self)
        self.sepet.setGeometry(QtCore.QRect(450, 40, 421, 220))
        self.sepet.setObjectName('sepet')

        self.orders = orderQWidget(self.tab, grandparent=self)
        self.orders.setGeometry(QtCore.QRect(450, 260, 421, 220))
        self.orders.setObjectName('orders')

        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1087, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab), _translate("MainWindow", "Anasayfa"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_3), _translate("MainWindow", "Profil"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_4), _translate("MainWindow", "Satıcı"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_2), _translate("MainWindow", "Admin"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
