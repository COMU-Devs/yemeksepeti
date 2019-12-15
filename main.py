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

authInfo = {
    'id': 'thmyris',
    'password': '5',
    'type': 'customer'
}


conn = sqlite3.connect('yemeksepeti.db')
cur = conn.cursor()


class productQWidget(QWidget):
    def __init__(self, row, imagepath='assets/empty.png', parent=None):
        super(productQWidget, self).__init__(parent)
        self.parent = parent
        self.values = row

        productId, name, price, r_id, category, ingredients = row
        imageUrl = self.getProductImage(productId)
        self.imageLabel = QLabel()

        self.imgsizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        self.imgsizePolicy.setHorizontalStretch(0)
        self.imgsizePolicy.setVerticalStretch(0)
        self.imgsizePolicy.setHeightForWidth(
            self.imageLabel.sizePolicy().hasHeightForWidth())
        self.pixmap = QPixmap(imageUrl).scaled(
            30, 30, QtCore.Qt.KeepAspectRatio)

        self.imageLabel.setSizePolicy(self.imgsizePolicy)
        self.imageLabel.setPixmap(self.pixmap)
        self.nameLabel = QLabel(str(name))
        self.ingredientsLabel = QLabel(str(ingredients))
        self.categoryLabel = QLabel(str(category))
        self.priceLabel = QLabel(str(price))
        self.button = QPushButton("+")

        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addWidget(self.nameLabel)
        self.vLayout.addWidget(self.ingredientsLabel)
        self.vLayout.addWidget(self.categoryLabel)
        self.hLayout.addWidget(self.imageLabel)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.button)

        self.setLayout(self.hLayout)
        self.button.clicked.connect(
            lambda: self.parent.grandparent.sepet.addSepetItem(productId))

    def getProductImage(self, productId):
        global cur
        url = 'assets/empty.png'
        cur.execute(
            'SELECT url FROM product_image WHERE p_id=' + str(productId))
        result = cur.fetchall()
        if len(result) == 1:
            url = result[0]

        return url


class restaurantQWidget(QWidget):
    def __init__(self, row, parent=None):
        super(restaurantQWidget, self).__init__(parent)
        self.parent = parent
        self.values = row

        restaurantId = self.values[0]
        name, address, minPayment = self.values[2:]

        self.nameLabel = QLabel(str(name))
        self.addressLabel = QLabel(str(address))
        self.minpaymentLabel = QLabel(str(address))

        self.button = QPushButton("sec")

        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.nameLabel)
        self.vLayout.addWidget(self.addressLabel)
        self.hLayout = QHBoxLayout()
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.minpaymentLabel)
        self.hLayout.addWidget(self.button)
        self.setLayout(self.hLayout)

        self.button.clicked.connect(
            lambda: self.parent.listProducts(restaurantId=restaurantId))


class menuQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.grandparent = grandparent
        self.listRestaurants()

    def listRestaurants(self):
        global cur
        cur.execute('SELECT * FROM restaurant')
        result = cur.fetchall()
        for row in (result):
            item = QListWidgetItem(self)
            item_widget = restaurantQWidget(
                row, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def listProducts(self, restaurantId):
        self.clear()
        global cur
        cur.execute('SELECT * FROM product WHERE r_id=' +
                    str(restaurantId))
        result = cur.fetchall()
        for row in result:
            item = QListWidgetItem(self)
            item_widget = productQWidget(
                row, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)


class sepetItemQWidget(QWidget):
    def __init__(self, row, parent=None):
        super(sepetItemQWidget, self).__init__(parent)
        self.parent = parent
        orderLineId, quantity, p_id, order_id = row
        productName, productPrice = self.getProduct(p_id)

        self.productNameLabel = QLabel(str(productName))
        self.quantityLabel = QLabel(str(quantity))
        self.priceLabel = QLabel(str(int(quantity) * int(productPrice)))

        self.hLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()
        # TODO: buttonIncrease, buttonDecrease olarak degistirilir mi bu button degisken isimleri?
        self.button = QPushButton("+")
        self.button2 = QPushButton('-')

        self.vLayout.addWidget(self.button)
        self.vLayout.addWidget(self.button2)

        self.hLayout.addWidget(self.productNameLabel)
        self.hLayout.addWidget(self.quantityLabel)
        self.hLayout.addLayout(self.vLayout)

        self.setLayout(self.hLayout)
        # TODO: add button1's connection.
        # self.button2.clicked.connect(
        #     lambda: self.parent.removeSepetItem(self.name))

    def getProduct(self, productId):
        global cur
        cur.execute('SELECT * FROM product WHERE id = ' + str(productId))
        result = cur.fetchall()
        return result


class sepetQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.orderId = self.getOrderId()
        # self.listSepetItems()

    def getOrderId(self):
        global conn, cur, authInfo
        # eger bos sepet varsa id o sepetin id sini dondur
        # yoksa bos bir sepet olustur ve id sini dondur
        cur.execute('SELECT id FROM order_table WHERE cus_id = \"' +
                    str(authInfo['id']) + '\" and purchase_date is NULL')
        result = cur.fetchall()
        if len(result) == 1:
            orderId = result[0][0]
            return orderId

        else:
            # insert new record with date = NULL
            cur.execute("INSERT INTO order_table(id, purchase_date, cus_id)" +
                        "VALUES( NULL, NULL, \"" + str(authInfo['id']) + "\")"
                        )

            conn.commit()

            cur.execute('SELECT id FROM order_table WHERE cus_id = \"' +
                        str(authInfo['id']) + '\" and purchase_date is NULL LIMIT 1')

            orderId = cur.fetchall()[0]
            return orderId

    def listSepetItems(self):
        global authInfo, cur
        self.clear()
        cur.execute('SELECT * FROM order_line WHERE ')
        result = cur.fetchall()
        for row in result:
            item = QListWidgetItem(self)
            item_widget = sepetItemQWidget(row, 1, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def addSepetItem(self, productId):
        # print(productId)
        global cur
        x, y, z, t = str(randint(0, 99999999)), randint(
            0, 99999999), name, randint(0, 99999999)
        cur.execute(
            "INSERT INTO order_line(pname,pnumber,plocation,dnum)" +
            f"VALUES('{x}', '{y}', '{z}', '{t}')"
        )

        # self.listSepetItems()

    def removeSepetItem(self, name):
        # if not item's amount == 1:
        global cur
        cur.execute(
            "DELETE FROM project WHERE pname =" + str(name)
        )
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
        global cur
        cur.execute('SELECT * FROM works_on')
        result = cur.fetchall()
        for row in result:
            item = QListWidgetItem(self)
            item_widget = orderItemQWidget(row, 1, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)


# TODO admin/restorantablosubox na donusturulecek. menuQWidgetin kopyasiydi.
class adminRestaurantBoxQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.grandparent = grandparent
        self.listRestaurants()

    def listRestaurants(self):  # TODO listRestaurantsi duzelt
        global cur
        cur.execute('SELECT * FROM restaurant')
        result = cur.fetchall()
        for row in (result):
            item = QListWidgetItem(self)
            item_widget = adminRestaurantBoxItemQWidget(
                row, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)


# TODO admin/restorantablosulistesi ne donusturulecek. restaurantQWidgetin kopyasiydi.
class adminRestaurantBoxItemQWidget(QWidget):
    def __init__(self, row, parent=None):
        super(adminRestaurantBoxItemQWidget, self).__init__(parent)
        self.parent = parent
        self.values = row

        restaurantId = self.values[0]
        restId, restPass, name, address, minPayment = self.values[0:]

        self.restIdLabel = QLabel(str(restId))
        self.restPassLabel = QLabel(str(restId))
        self.nameLabel = QLabel(str(name))
        self.addressLabel = QLabel(str(address))
        self.minPaymentLabel = QLabel(str(minPayment))

        self.button = QPushButton("Seç")

        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addWidget(self.nameLabel)
        self.vLayout.addWidget(self.addressLabel)
        self.hLayout.addWidget(self.button)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.minPaymentLabel)
        self.setLayout(self.hLayout)

        self.button.clicked.connect(
            lambda: self.parent.listProducts(restaurantId=restaurantId))


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

        # ---INIT TAB: ANASAYFA
        self.tab = QtWidgets.QWidget()  # tab = anasayfa
        self.tab.setObjectName("Anasayfa")

        self.menu = menuQWidget(self.tab, grandparent=self)
        self.menu.setGeometry(QtCore.QRect(30, 40, 421, 441))
        self.menu.setObjectName('listOfProducts')

        self.sepet = sepetQWidget(self.tab, grandparent=self)
        self.sepet.setGeometry(QtCore.QRect(450, 40, 421, 220))
        self.sepet.setObjectName('sepet')

        self.orders = orderQWidget(self.tab, grandparent=self)
        self.orders.setGeometry(QtCore.QRect(450, 260, 421, 220))
        self.orders.setObjectName('orders')

        self.tabWidget.addTab(self.tab, "")  # adding tab to tabWidget
        # ---END OF TAB: ANASAYFA

        # ---INIT TAB: ADMIN
        self.tab_2 = QtWidgets.QWidget()  # tab_2 = Admin
        self.tab_2.setObjectName("Admin")

        self.adminRestaurantBox = adminRestaurantBoxQWidget(
            self.tab_2, grandparent=self)
        self.adminRestaurantBox.setGeometry(QtCore.QRect(30, 40, 1000, 250))
        self.adminRestaurantBox.setObjectName('listOfRestaurants')

        self.tabWidget.addTab(self.tab_2, "")  # adding tab_2 to tabWidget
        # ---END OF TAB: ADMIN

        # ---INIT TAB: SATICI
        self.tab_3 = QtWidgets.QWidget()  # tab_3 = Satici
        self.tab_3.setObjectName("Satici")

        self.tabWidget.addTab(self.tab_3, "")  # adding tab_3 to tabWidget
        # ---END OF TAB: SATICI

        # ---INIT TAB: PROFIL
        self.tab_4 = QtWidgets.QWidget()  # tab_4 = Profil
        self.tab_4.setObjectName("Profil")

        self.tabWidget.addTab(self.tab_4, "")  # adding tab_4 to tabWidget
        # ---END OF TAB: PROFIL

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
            self.tab_2), _translate("MainWindow", "Admin"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_3), _translate("MainWindow", "Satici"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_4), _translate("MainWindow", "Profil"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
