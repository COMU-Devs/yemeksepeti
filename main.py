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
        cur.execute('SELECT * FROM product WHERE r_id='
                    + str(restaurantId))
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
        cur.execute('SELECT id FROM order_table WHERE cus_id = \"'
                    + str(authInfo['id']) + '\" and purchase_date is NULL')
        result = cur.fetchall()
        if len(result) == 1:
            orderId = result[0][0]
            return orderId

        else:
            # insert new record with date = NULL
            cur.execute("INSERT INTO order_table(id, purchase_date, cus_id)"
                        + "VALUES( NULL, NULL, \"" + str(authInfo['id']) + "\")"
                        )

            conn.commit()

            cur.execute('SELECT id FROM order_table WHERE cus_id = \"'
                        + str(authInfo['id']) + '\" and purchase_date is NULL LIMIT 1')

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
            "INSERT INTO order_line(pname,pnumber,plocation,dnum)"
            + f"VALUES('{x}', '{y}', '{z}', '{t}')"
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


# TODO admin/restorantablosubox na donusturulecek. menuQWidget in kopyasiydi.
class adminRestaurantBoxQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.grandparent = grandparent
        self.listRestaurants()

    def listRestaurants(self):
        global cur
        self.clear()
        cur.execute('SELECT * FROM restaurant')
        result = cur.fetchall()
        for row in (result):
            item = QListWidgetItem(self)
            item_widget = adminRestaurantBoxItemQWidget(
                row, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def adminListedenCikar(self, travellingrestid):
        global cur, conn
        cur.execute(
            "DELETE FROM restaurant WHERE id =" + travellingrestid
        )
        conn.commit()
        self.listRestaurants()


# TODO admin/restorantablosulistesi ne donusturulecek. restaurantQWidget in kopyasiydi.
class adminRestaurantBoxItemQWidget(QWidget):
    def __init__(self, row, parent=None):
        super(adminRestaurantBoxItemQWidget, self).__init__(parent)
        self.parent = parent
        self.values = row

        restId, restPass, name, address, minPayment = self.values

        self.restIdLabel = QLabel(str(restId))
        self.restPassLabel = QLabel(str(restPass))
        self.nameLabel = QLabel(str(name))
        self.addressLabel = QLabel(str(address))
        self.minPaymentLabel = QLabel(str(minPayment))
        self.buttonSelect = QPushButton("Düzenle")
        self.buttonDelete = QPushButton("Sil")
        self.buttonDelete.setFixedSize(40, 30)
        self.buttonSelect.setFixedSize(70, 30)

        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.restIdLabel)
        self.hLayout.addWidget(self.restPassLabel)
        self.hLayout.addWidget(self.nameLabel)
        self.hLayout.addWidget(self.addressLabel)
        self.hLayout.addWidget(self.minPaymentLabel)
        self.hLayout.addWidget(self.buttonDelete)
        self.hLayout.addWidget(self.buttonSelect)
        # self.hLayout.addLayout(self.vLayout)
        self.setLayout(self.hLayout)

        self.buttonSelect.clicked.connect(
            lambda: self.parent.listProducts(restaurantId=restaurantId))
        self.buttonDelete.clicked.connect(
            lambda: self.parent.adminListedenCikar(travellingrestid=restId))


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
        self.adminRestaurantBox.setGeometry(QtCore.QRect(30, 40, 1011, 250))
        self.adminRestaurantBox.setObjectName('listOfRestaurants')

        self.adminRestEkleLabel = QtWidgets.QLabel(self.tab_2)
        self.adminRestEkleLabel.setGeometry(QtCore.QRect(33, 309, 151, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.adminRestEkleLabel.setFont(font)
        self.adminRestEkleLabel.setObjectName("adminRestEkleLabel")
        self.adminId1 = QtWidgets.QLabel(self.tab_2)
        self.adminId1.setGeometry(QtCore.QRect(33, 355, 25, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminId1.setFont(font)
        self.adminId1.setObjectName("adminId1")
        self.adminPlainTextEdit = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit.setGeometry(QtCore.QRect(57, 345, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit.setFont(font)
        self.adminPlainTextEdit.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit.setPlainText("")
        self.adminPlainTextEdit.setObjectName("adminPlainTextEdit")
        self.adminPlainTextEdit_2 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_2.setGeometry(QtCore.QRect(156, 345, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_2.setFont(font)
        self.adminPlainTextEdit_2.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_2.setPlainText("")
        self.adminPlainTextEdit_2.setObjectName("adminPlainTextEdit_2")
        self.adminPlainTextEdit_3 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_3.setGeometry(QtCore.QRect(563, 345, 291, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_3.setFont(font)
        self.adminPlainTextEdit_3.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_3.setPlainText("")
        self.adminPlainTextEdit_3.setObjectName("adminPlainTextEdit_3")
        self.adminPlainTextEdit_4 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_4.setGeometry(QtCore.QRect(293, 345, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_4.setFont(font)
        self.adminPlainTextEdit_4.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_4.setPlainText("")
        self.adminPlainTextEdit_4.setObjectName("adminPlainTextEdit_4")
        self.adminPlainTextEdit_5 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_5.setGeometry(QtCore.QRect(993, 345, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_5.setFont(font)
        self.adminPlainTextEdit_5.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_5.setPlainText("")
        self.adminPlainTextEdit_5.setObjectName("adminPlainTextEdit_5")
        self.adminPass1 = QtWidgets.QLabel(self.tab_2)
        self.adminPass1.setGeometry(QtCore.QRect(113, 351, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPass1.setFont(font)
        self.adminPass1.setObjectName("adminPass1")
        self.adminIsim1 = QtWidgets.QLabel(self.tab_2)
        self.adminIsim1.setGeometry(QtCore.QRect(253, 355, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminIsim1.setFont(font)
        self.adminIsim1.setObjectName("adminIsim1")
        self.adminAdres1 = QtWidgets.QLabel(self.tab_2)
        self.adminAdres1.setGeometry(QtCore.QRect(513, 350, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminAdres1.setFont(font)
        self.adminAdres1.setObjectName("adminAdres1")
        self.adminOdeme1 = QtWidgets.QLabel(self.tab_2)
        self.adminOdeme1.setGeometry(QtCore.QRect(863, 345, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminOdeme1.setFont(font)
        self.adminOdeme1.setObjectName("adminOdeme1")
        self.adminOnayla1 = QtWidgets.QPushButton(self.tab_2)
        self.adminOnayla1.setGeometry(QtCore.QRect(953, 385, 93, 28))
        self.adminOnayla1.setObjectName("adminOnayla1")
        self.adminOnayla1.clicked.connect(self.adminListeyeEkle)
        self.adminGuncelleLabel = QtWidgets.QLabel(self.tab_2)
        self.adminGuncelleLabel.setGeometry(QtCore.QRect(34, 420, 191, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.adminGuncelleLabel.setFont(font)
        self.adminGuncelleLabel.setObjectName("adminGuncelleLabel")
        self.adminPlainTextEdit_6 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_6.setGeometry(QtCore.QRect(994, 455, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_6.setFont(font)
        self.adminPlainTextEdit_6.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_6.setPlainText("")
        self.adminPlainTextEdit_6.setObjectName("adminPlainTextEdit_6")
        self.adminOdeme2 = QtWidgets.QLabel(self.tab_2)
        self.adminOdeme2.setGeometry(QtCore.QRect(864, 455, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminOdeme2.setFont(font)
        self.adminOdeme2.setObjectName("adminOdeme2")
        self.adminId2 = QtWidgets.QLabel(self.tab_2)
        self.adminId2.setGeometry(QtCore.QRect(34, 465, 25, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminId2.setFont(font)
        self.adminId2.setObjectName("adminId2")
        self.adminPlainTextEdit_7 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_7.setGeometry(QtCore.QRect(57, 455, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_7.setFont(font)
        self.adminPlainTextEdit_7.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_7.setPlainText("")
        self.adminPlainTextEdit_7.setObjectName("adminPlainTextEdit_7")
        self.adminPlainTextEdit_8 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_8.setGeometry(QtCore.QRect(294, 455, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_8.setFont(font)
        self.adminPlainTextEdit_8.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_8.setPlainText("")
        self.adminPlainTextEdit_8.setObjectName("adminPlainTextEdit_8")
        self.adminPlainTextEdit_9 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_9.setGeometry(QtCore.QRect(564, 455, 291, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_9.setFont(font)
        self.adminPlainTextEdit_9.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_9.setPlainText("")
        self.adminPlainTextEdit_9.setObjectName("adminPlainTextEdit_9")
        self.adminPlainTextEdit_10 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.adminPlainTextEdit_10.setGeometry(QtCore.QRect(157, 455, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPlainTextEdit_10.setFont(font)
        self.adminPlainTextEdit_10.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.adminPlainTextEdit_10.setPlainText("")
        self.adminPlainTextEdit_10.setObjectName("adminPlainTextEdit_10")
        self.adminIsim2 = QtWidgets.QLabel(self.tab_2)
        self.adminIsim2.setGeometry(QtCore.QRect(254, 465, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminIsim2.setFont(font)
        self.adminIsim2.setObjectName("adminIsim2")
        self.adminPass2 = QtWidgets.QLabel(self.tab_2)
        self.adminPass2.setGeometry(QtCore.QRect(114, 461, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminPass2.setFont(font)
        self.adminPass2.setObjectName("adminPass2")
        self.adminAdres2 = QtWidgets.QLabel(self.tab_2)
        self.adminAdres2.setGeometry(QtCore.QRect(514, 460, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.adminAdres2.setFont(font)
        self.adminAdres2.setObjectName("adminAdres2")
        self.adminOnayla2 = QtWidgets.QPushButton(self.tab_2)
        self.adminOnayla2.setGeometry(QtCore.QRect(954, 495, 93, 28))
        self.adminOnayla2.setObjectName("adminOnayla2")
        self.adminId0 = QtWidgets.QLabel(self.tab_2)
        self.adminId0.setGeometry(QtCore.QRect(38, 15, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.adminId0.setFont(font)
        self.adminId0.setObjectName("adminId0")
        self.adminPass0 = QtWidgets.QLabel(self.tab_2)
        self.adminPass0.setGeometry(QtCore.QRect(110, 15, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.adminPass0.setFont(font)
        self.adminPass0.setObjectName("adminPass0")
        self.adminIsim0 = QtWidgets.QLabel(self.tab_2)
        self.adminIsim0.setGeometry(QtCore.QRect(240, 15, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.adminIsim0.setFont(font)
        self.adminIsim0.setObjectName("adminIsim0")
        self.adminAdres0 = QtWidgets.QLabel(self.tab_2)
        self.adminAdres0.setGeometry(QtCore.QRect(430, 15, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.adminAdres0.setFont(font)
        self.adminAdres0.setObjectName("adminAdres0")
        self.adminOdeme0 = QtWidgets.QLabel(self.tab_2)
        self.adminOdeme0.setGeometry(QtCore.QRect(690, 15, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.adminOdeme0.setFont(font)
        self.adminOdeme0.setObjectName("adminOdeme0")
        self.adminSeciliRestLabel = QtWidgets.QLabel(self.tab_2)
        self.adminSeciliRestLabel.setGeometry(QtCore.QRect(260, 420, 491, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.adminSeciliRestLabel.setFont(font)
        self.adminSeciliRestLabel.setObjectName("adminSeciliRestLabel")

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

        # --INIT FARUK RETRANSLATE
        self.adminRestEkleLabel.setText(
            _translate("MainWindow", "Restoran Ekle"))
        self.adminId1.setText(_translate("MainWindow", "ID:"))
        self.adminPass1.setText(_translate("MainWindow", "Pass:"))
        self.adminIsim1.setText(_translate("MainWindow", "İsim:"))
        self.adminAdres1.setText(_translate("MainWindow", "Adres:"))
        self.adminOdeme1.setText(_translate("MainWindow", "Ödeme Sınırı(TL):"))
        self.adminOnayla1.setText(_translate("MainWindow", "Onayla"))
        self.adminGuncelleLabel.setText(
            _translate("MainWindow", "Restoran Güncelle"))
        self.adminOdeme2.setText(_translate("MainWindow", "Ödeme Sınırı(TL):"))
        self.adminId2.setText(_translate("MainWindow", "ID:"))
        self.adminIsim2.setText(_translate("MainWindow", "İsim:"))
        self.adminPass2.setText(_translate("MainWindow", "Pass:"))
        self.adminAdres2.setText(_translate("MainWindow", "Adres:"))
        self.adminOnayla2.setText(_translate("MainWindow", "Onayla"))
        self.adminId0.setText(_translate("MainWindow", "ID"))
        self.adminPass0.setText(_translate("MainWindow", "PASS"))
        self.adminIsim0.setText(_translate("MainWindow", "NAME"))
        self.adminAdres0.setText(_translate("MainWindow", "ADDRESS"))
        self.adminOdeme0.setText(_translate("MainWindow", "MIN_PAY"))
        self.adminSeciliRestLabel.setText(
            _translate("MainWindow", "(Secili Restoran:"))
        # --END FARUK RETRANSLATE

    # --- INIT FARUK BUTTON HANDLING
    def adminListeyeEkle(self):
        global cur, conn, authInfo

        ekleid = self.adminPlainTextEdit.toPlainText()
        eklepass = self.adminPlainTextEdit_2.toPlainText()
        ekleisim = self.adminPlainTextEdit_4.toPlainText()
        ekleadres = self.adminPlainTextEdit_3.toPlainText()
        eklesinir = self.adminPlainTextEdit_5.toPlainText()

        myid = authInfo['id']
        cur.execute(  # BUG burda hata veriyor
            "INSERT INTO restaurant(id,pass,name,address,min_pay)"
            + f"VALUES('{ekleid}','{eklepass}','{ekleisim}','{ekleadres}', '{eklesinir}')"
        )
        conn.commit()
        self.adminRestaurantBox.listRestaurants()


    # TODO gokselin showSaticiGuncelleme, bunu adminRestoranLabelDoldur a cevir, secilirestoran: labelini sil
    def showSaticiGuncelleme(self, travelingrestid):
        global cur, conn
        cur.execute(
            'SELECT * FROM restaurant WHERE id =' + str(travellingrestid)
        )
        result = cur.fetchall()
        restid = result[0][0]
        print(result[0][0])
        restpass = result[0][1]
        restname = result[0][2]
        restaddr = result[0][3]
        restminpay = result[0][4]
        self.adminSetFields(restid, restpass, restname, restaddr, restminpay)
        self.adminRestaurantBox.listRestaurants()

    # TODO gokselin setfields kendiminkine cevrilcek
    def adminSetFields(self, restid2, restpass2, restname2, restaddr2, restminpay2):
        _translate = QtCore.QCoreApplication.translate
        self.adminPlainTextEdit_7.setPlainText(
            _translate("Form", restid2))
        self.adminPlainTextEdit_10.setPlainText(_translate("Form", restpass2))
        self.adminPlainTextEdit_8.setPlainText(_translate("Form", restname2))
        self.adminPlainTextEdit_9.setPlainText(_translate("Form", restaddr2))
        self.adminPlainTextEdit_6.setPlainText(
            _translate("Form", str(restminpay2)))

    # --- END FARUK BUTTON HANDLING


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
