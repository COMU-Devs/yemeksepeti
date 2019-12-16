# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deneme.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!
import PyQt5

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QLabel, QPushButton, QListWidgetItem, \
    QHBoxLayout

from PyQt5.QtGui import QIcon, QPixmap

import sqlite3
from random import randint

authInfo = {
    'id': 'thmyris',
    'password': '54',
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
        cur.execute('SELECT * FROM product WHERE id = '+str(productId))
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


class saticiItemQWidget(QWidget):
    def __init__(self, row, parent=None):
        super(saticiItemQWidget, self).__init__(parent)
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
        self.button = QPushButton("Guncelle")
        self.buttonsil = QPushButton("Sil")

        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addWidget(self.nameLabel)
        self.vLayout.addWidget(self.ingredientsLabel)
        self.vLayout.addWidget(self.categoryLabel)
        self.hLayout.addWidget(self.imageLabel)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.button)
        self.hLayout.addWidget(self.buttonsil)

        self.setLayout(self.hLayout)
        self.buttonsil.clicked.connect(
            lambda: self.parent.silme(productId))
        self.button.clicked.connect(
            lambda: self.parent.grandparent.showSaticiGuncelleme(productId))

    def getProductImage(self, productId):
        global cur
        url = 'assets/empty.png'
        cur.execute(
            'SELECT url FROM product_image WHERE p_id=' + str(productId))
        result = cur.fetchall()

        if len(result) == 1:
            url = result[0][0]

        return url


class saticiQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.grandparent = grandparent
        self.listOrders()

    def listOrders(self):
        self.clear()
        global cur, authInfo
        restId = authInfo['id']
        cur.execute(
            'SELECT product.id, product.name, product.price, product.r_id, product.category, product.ingredients FROM product , restaurant WHERE restaurant.id = product.r_id and restaurant.id = '+str(restId))
        # SELECT product.name, product.price, product.category, product.ingredients
        # FROM product , restaurant
        # WHERE restaurant.id ='1' and restaurant.id = product.r_id
        result = cur.fetchall()
        for row in result:
            item = QListWidgetItem(self)
            item_widget = saticiItemQWidget(row, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def silme(self, productId):
        global cur, conn, authInfo
        cur. execute(
            ' DELETE FROM product WHERE product.id = ' + str(productId))
        cur.execute(
            'DELETE FROM product_image WHERE product_image.p_id = ' +
            str(productId)
        )
        conn.commit()
        self.listOrders()


class saticiUrunGuncelleme_Ui(object):
    def setupUi(self, Form):
        self.Form = Form
        Form.setObjectName("Form")
        Form.resize(682, 558)
        self.satici_ingredientsUpdate = QtWidgets.QLabel(Form)
        self.satici_ingredientsUpdate.setGeometry(
            QtCore.QRect(70, 260, 111, 21))
        self.satici_ingredientsUpdate.setObjectName("satici_ingredientsUpdate")
        self.satici_categoryUpdateText = QtWidgets.QPlainTextEdit(Form)
        self.satici_categoryUpdateText.setGeometry(
            QtCore.QRect(210, 200, 371, 31))
        self.satici_categoryUpdateText.setObjectName(
            "satici_categoryUpdateText")
        self.satici_productPriceUpdate = QtWidgets.QLabel(Form)
        self.satici_productPriceUpdate.setGeometry(
            QtCore.QRect(60, 160, 121, 20))
        self.satici_productPriceUpdate.setObjectName(
            "satici_productPriceUpdate")
        self.GuncellemeSayfasi = QtWidgets.QLabel(Form)
        self.GuncellemeSayfasi.setGeometry(QtCore.QRect(200, 60, 301, 17))
        self.GuncellemeSayfasi.setObjectName("GuncellemeSayfasi")
        self.satici_productPriceUpdateText = QtWidgets.QPlainTextEdit(Form)
        self.satici_productPriceUpdateText.setGeometry(
            QtCore.QRect(210, 150, 371, 31))
        self.satici_productPriceUpdateText.setObjectName(
            "satici_productPriceUpdateText")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(490, 310, 89, 25))
        self.pushButton.setObjectName("pushButton")
        self.satici_categoryUpdate = QtWidgets.QLabel(Form)
        self.satici_categoryUpdate.setGeometry(QtCore.QRect(70, 210, 121, 20))
        self.satici_categoryUpdate.setObjectName("satici_categoryUpdate")
        self.satici_productNameUpdate = QtWidgets.QLabel(Form)
        self.satici_productNameUpdate.setGeometry(
            QtCore.QRect(60, 110, 121, 20))
        self.satici_productNameUpdate.setObjectName("satici_productNameUpdate")
        self.satici_productNameUpdateText = QtWidgets.QPlainTextEdit(Form)
        self.satici_productNameUpdateText.setGeometry(
            QtCore.QRect(210, 100, 371, 31))
        self.satici_productNameUpdateText.setObjectName(
            "satici_productNameUpdateText")
        self.satici_ingredientsUpdateText = QtWidgets.QPlainTextEdit(Form)
        self.satici_ingredientsUpdateText.setGeometry(
            QtCore.QRect(210, 250, 371, 31))
        self.satici_ingredientsUpdateText.setObjectName(
            "satici_ingredientsUpdateText")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        global cur, conn, authInfo

        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.satici_ingredientsUpdate.setText(
            _translate("Form", "icindekiler:"))
        self.satici_productPriceUpdate.setText(
            _translate("Form", "Yemek Fiyati: "))
        self.GuncellemeSayfasi.setText(
            _translate("Form", "Guncelleme Sayfasi"))
        self.pushButton.setText(_translate("Form", "Guncelle"))
        self.satici_categoryUpdate.setText(_translate("Form", "Kategori:"))
        self.satici_productNameUpdate.setText(
            _translate("Form", "Yemek İsmi:"))

    def setFields(self, name, price, cat, ing):
        _translate = QtCore.QCoreApplication.translate
        self.satici_productNameUpdateText.setPlainText(
            _translate("Form", name))
        self.satici_ingredientsUpdateText.setPlainText(_translate("Form", ing))
        self.satici_productPriceUpdateText.setPlainText(
            _translate("Form", str(price)))
        self.satici_categoryUpdateText.setPlainText(_translate("Form", cat))


class saticiUrunGuncelleme(PyQt5.QtWidgets.QDialog):
    def __init__(self, grandparent):
        super().__init__()
        self.grandparent = grandparent
        self.setFixedSize(666, 666)
        self.ui = saticiUrunGuncelleme_Ui()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.Guncelle)
        self.p_id = 0  # init

    def Guncelle(self):
        global cur, conn

        productName = self.ui.satici_productNameUpdateText.toPlainText()
        productPrice = self.ui.satici_productPriceUpdateText.toPlainText()
        category = self.ui.satici_categoryUpdateText.toPlainText()
        ingredient = self.ui.satici_ingredientsUpdateText.toPlainText()

        cur.execute('UPDATE product SET name = \"'+str(productName)+'\" , price = '+str(productPrice) +
                    ', category = \"'+str(category)+'\" , ingredients = \"'+str(ingredient)+'\" WHERE id ='+str(self.p_id))
        conn.commit()
        self.grandparent.satici_listView.listOrders()

        self.close()


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1087, 666)
        global authInfo
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

        self.tabWidget.addTab(self.tab_2, "")  # adding tab_2 to tabWidget
# ---END OF TAB: ADMIN
# ---INIT TAB: SATICI
        if authInfo['type'] == 'restaurant':
            self.tab_3 = QtWidgets.QWidget()  # tab_3 = Satici
            self.tab_3.setObjectName("Satici")

            self.satici_listView = saticiQWidget(self.tab_3, grandparent=self)
            self.satici_listView.setGeometry(QtCore.QRect(50, 50, 441, 231))
            self.satici_listView.setObjectName("listView")  # yemekler

            self.satici_yemekler = QtWidgets.QLabel(self.tab_3)
            self.satici_yemekler.setGeometry(QtCore.QRect(50, 30, 67, 17))
            self.satici_yemekler.setObjectName("yemekler")

            self.satici_listeyeEkleButton = QtWidgets.QPushButton(self.tab_3)
            self.satici_listeyeEkleButton.setGeometry(
                QtCore.QRect(390, 450, 89, 25))
            self.satici_listeyeEkleButton.setCheckable(True)
            self.satici_listeyeEkleButton.setObjectName("listeyeEkleButton")
            self.satici_listeyeEkleButton.clicked.connect(self.listeyeEkle)

            self.satici_productNameText = QtWidgets.QTextEdit(self.tab_3)
            self.satici_productNameText.setGeometry(
                QtCore.QRect(190, 290, 301, 31))
            self.satici_productNameText.setObjectName("productNameText")

            self.satici_productPriceText = QtWidgets.QTextEdit(self.tab_3)
            self.satici_productPriceText.setGeometry(
                QtCore.QRect(190, 330, 301, 31))
            self.satici_productPriceText.setObjectName("productPriceText")

            self.satici_categoryText = QtWidgets.QTextEdit(self.tab_3)
            self.satici_categoryText.setGeometry(
                QtCore.QRect(190, 370, 301, 31))
            self.satici_categoryText.setObjectName("categoryText")

            self.satici_ingredientsText = QtWidgets.QTextEdit(self.tab_3)
            self.satici_ingredientsText.setGeometry(
                QtCore.QRect(190, 410, 301, 31))
            self.satici_ingredientsText.setObjectName("ingredientsText")

            self.satici_productName = QtWidgets.QLabel(self.tab_3)
            self.satici_productName.setGeometry(QtCore.QRect(60, 300, 101, 16))
            self.satici_productName.setObjectName("productName")

            self.satici_productPrice = QtWidgets.QLabel(self.tab_3)
            self.satici_productPrice.setGeometry(
                QtCore.QRect(60, 340, 101, 17))
            self.satici_productPrice.setObjectName("productPrice")

            self.satici_category = QtWidgets.QLabel(self.tab_3)
            self.satici_category.setGeometry(QtCore.QRect(60, 380, 101, 17))
            self.satici_category.setObjectName("category")

            self.satici_ingredients = QtWidgets.QLabel(self.tab_3)
            self.satici_ingredients.setGeometry(QtCore.QRect(60, 420, 101, 17))
            self.satici_ingredients.setObjectName("ingredients")

            self.satici_productImage = QtWidgets.QLabel(self.tab_3)
            self.satici_productImage.setGeometry(
                QtCore.QRect(60, 460, 101, 17))
            self.satici_productImage.setObjectName("productImage")

            self.satici_imageOpenButton = QtWidgets.QPushButton(self.tab_3)
            self.satici_imageOpenButton.setGeometry(
                QtCore.QRect(190, 450, 89, 25))
            self.satici_imageOpenButton.setObjectName("imageOpenButton")
            self.satici_imageOpenButton.clicked.connect(self.importInput)

            self.satici_minPriceUpdate = QtWidgets.QLabel(self.tab_3)
            self.satici_minPriceUpdate.setGeometry(
                QtCore.QRect(560, 50, 171, 31))
            self.satici_minPriceUpdate.setObjectName("minPriceUpdate")

            self.satici_minPriceUpdateText = QtWidgets.QTextEdit(self.tab_3)
            self.satici_minPriceUpdateText.setGeometry(
                QtCore.QRect(740, 50, 301, 31))
            self.satici_minPriceUpdateText.setObjectName("minPriceUpdateText")

            self.satici_minPriceUpdateButton = QtWidgets.QPushButton(
                self.tab_3)
            self.satici_minPriceUpdateButton.setGeometry(
                QtCore.QRect(1050, 50, 89, 25))
            self.satici_minPriceUpdateButton.setObjectName(
                "minPriceUpdateButton")
            self.satici_minPriceUpdateButton.clicked.connect(
                self.minFiyatGuncelleme)

            self.satici_restAddressUpdate = QtWidgets.QLabel(self.tab_3)
            self.satici_restAddressUpdate.setGeometry(
                QtCore.QRect(560, 100, 171, 31))
            self.satici_restAddressUpdate.setObjectName("restAddressUpdate")

            self.satici_restAddressUpdateText = QtWidgets.QTextEdit(self.tab_3)
            self.satici_restAddressUpdateText.setGeometry(
                QtCore.QRect(740, 100, 301, 31))
            self.satici_restAddressUpdateText.setObjectName(
                "restAddressUpdateText")

            self.satici_restAddressUpdateButton = QtWidgets.QPushButton(
                self.tab_3)
            self.satici_restAddressUpdateButton.setGeometry(
                QtCore.QRect(1050, 100, 89, 25))
            self.satici_restAddressUpdateButton.setObjectName(
                "restAddressUpdateButton")
            self.satici_restAddressUpdateButton.clicked.connect(
                self.restAddressGuncelleme)

            self.satici_restNameUpdate = QtWidgets.QLabel(self.tab_3)
            self.satici_restNameUpdate.setGeometry(
                QtCore.QRect(560, 150, 171, 31))
            self.satici_restNameUpdate.setObjectName("restNameUpdate")

            self.satici_restNameUpdateText = QtWidgets.QTextEdit(self.tab_3)
            self.satici_restNameUpdateText.setGeometry(
                QtCore.QRect(740, 150, 301, 31))
            self.satici_restNameUpdateText.setObjectName("restNameUpdateText")

            self.satici_restNameUpdateButton = QtWidgets.QPushButton(
                self.tab_3)
            self.satici_restNameUpdateButton.setGeometry(
                QtCore.QRect(1050, 150, 89, 25))
            self.satici_restNameUpdateButton.setObjectName(
                "restNameUpdateButton")
            self.satici_restNameUpdateButton.clicked.connect(
                self.restIsmiGuncelleme)

            self.tabWidget.addTab(self.tab_3, "")  # adding tab_3 to tabWidget
# ---END OF TAB: SATICI
# ---INIT TAB: PROFIL
        if authInfo['type'] == 'customer':
            self.tab_4 = QtWidgets.QWidget()  # tab_4 = Profil
            self.tab_4.setObjectName("Profil")

            self.profil_customerPasswordText = QtWidgets.QPlainTextEdit(
                self.tab_4)
            self.profil_customerPasswordText.setGeometry(
                QtCore.QRect(230, 80, 201, 41))
            self.profil_customerPasswordText.setObjectName(
                "profil_customerPasswordText")

            self.profil_customerPassword = QtWidgets.QLabel(self.tab_4)
            self.profil_customerPassword.setGeometry(
                QtCore.QRect(50, 80, 181, 41))
            self.profil_customerPassword.setObjectName(
                "profil_customerPassword")

            self.profil_customerFnameText = QtWidgets.QPlainTextEdit(
                self.tab_4)
            self.profil_customerFnameText.setGeometry(
                QtCore.QRect(230, 140, 201, 41))
            self.profil_customerFnameText.setObjectName(
                "profil_customerFnameText")

            self.profil_customerFname = QtWidgets.QLabel(self.tab_4)
            self.profil_customerFname.setGeometry(
                QtCore.QRect(50, 140, 181, 41))
            self.profil_customerFname.setObjectName("profil_customerFname")

            self.profil_customerLnameText = QtWidgets.QPlainTextEdit(
                self.tab_4)
            self.profil_customerLnameText.setGeometry(
                QtCore.QRect(230, 200, 201, 41))
            self.profil_customerLnameText.setObjectName(
                "profil_customerLnameText")

            self.profil_customerLname = QtWidgets.QLabel(self.tab_4)
            self.profil_customerLname.setGeometry(
                QtCore.QRect(50, 200, 181, 41))
            self.profil_customerLname.setObjectName("profil_customerLname")

            self.profil_customerTelNoText = QtWidgets.QPlainTextEdit(
                self.tab_4)
            self.profil_customerTelNoText.setGeometry(
                QtCore.QRect(230, 260, 201, 41))
            self.profil_customerTelNoText.setObjectName(
                "profil_customerTelNoText")

            self.profil_customerTelNo = QtWidgets.QLabel(self.tab_4)
            self.profil_customerTelNo.setGeometry(
                QtCore.QRect(50, 260, 181, 41))
            self.profil_customerTelNo.setObjectName("profil_customerTelNo")

            self.profil_customerAddress = QtWidgets.QLabel(self.tab_4)
            self.profil_customerAddress.setGeometry(
                QtCore.QRect(50, 320, 181, 41))
            self.profil_customerAddress.setObjectName("profil_customerAddress")

            self.profil_customerAddressText = QtWidgets.QPlainTextEdit(
                self.tab_4)
            self.profil_customerAddressText.setGeometry(
                QtCore.QRect(230, 320, 201, 41))
            self.profil_customerAddressText.setObjectName(
                "profil_customerAddressText")

            self.bilgileriGuncelle = QtWidgets.QLabel(self.tab_4)
            self.bilgileriGuncelle.setGeometry(QtCore.QRect(50, 20, 381, 31))
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.bilgileriGuncelle.sizePolicy().hasHeightForWidth())
            self.bilgileriGuncelle.setSizePolicy(sizePolicy)
            self.bilgileriGuncelle.setTextFormat(QtCore.Qt.AutoText)
            self.bilgileriGuncelle.setObjectName("bilgileriGuncelle")

            self.pushButton = QtWidgets.QPushButton(self.tab_4)
            self.pushButton.setGeometry(QtCore.QRect(50, 390, 391, 61))
            self.pushButton.setObjectName("KAYDET")

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
        # goksel =========================================================================
        self.importImagePath = "NULL"
        self.saticiguncelleme = saticiUrunGuncelleme(grandparent=self)

        self.pushButton.clicked.connect(
            self.profilGuncelleme)  # BUTTONA BASILDIGINDA

    def showSaticiGuncelleme(self, productId):
        # sorgu(productId)
        global cur
        cur.execute(
            'SELECT * FROM product WHERE id = '+str(productId)
        )
        result = cur.fetchall()
        name = result[0][1]
        price = result[0][2]
        category = result[0][4]
        ingred = result[0][5]
        self.saticiguncelleme.p_id = productId
        self.saticiguncelleme.ui.setFields(name, price, category, ingred)
        self.saticiguncelleme.show()

    def profileUpdate(self):
        # customer id yi getiremiyorum
        global cur, authInfo

        cur.execute('SELECT * FROM customer WHERE id =\"' +
                    str(authInfo['id'])+"\"")
        result = cur.fetchall()
        password = result[0][1]
        fname = result[0][2]
        lname = result[0][3]
        telNo = result[0][4]
        address = result[0][5]
        self.profilSetFields(password, fname, lname, telNo, address)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab), _translate("MainWindow", "Anasayfa"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_2), _translate("MainWindow", "Admin"))

        # goksel ========================================================================================
        if authInfo['type'] == 'restaurant':
            self.tabWidget.setTabText(self.tabWidget.indexOf(
                self.tab_3), _translate("MainWindow", "Satici"))
            self.satici_yemekler.setText(_translate("MainWindow", "Yemekler"))
            self.satici_listeyeEkleButton.setText(
                _translate("MainWindow", "Listeye Ekle"))
            self.satici_productName.setText(
                _translate("MainWindow", "Yemek ismi"))
            self.satici_productPrice.setText(
                _translate("MainWindow", "Yemek Fiyati"))
            self.satici_category.setText(_translate("MainWindow", "Kategori"))
            self.satici_ingredients.setText(
                _translate("MainWindow", "Icindekiler"))
            self.satici_productImage.setText(
                _translate("MainWindow", "Yemek Resmi"))
            self.satici_imageOpenButton.setText(
                _translate("MainWindow", "Dosya Ac"))
            self.satici_minPriceUpdate.setText(
                _translate("MainWindow", "Minimum Fiyat Guncelle"))
            self.satici_minPriceUpdateButton.setText(
                _translate("MainWindow", "Guncelle"))
            self.satici_restAddressUpdate.setText(
                _translate("MainWindow", "Restoran Adresi Guncelle"))
            self.satici_restAddressUpdateButton.setText(
                _translate("MainWindow", "Guncelle"))
            self.satici_restNameUpdate.setText(
                _translate("MainWindow", "Restoran ismi Guncelle"))
            self.satici_restNameUpdateButton.setText(
                _translate("MainWindow", "Guncelle"))

        # Goksel PROFIL ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if authInfo['type'] == 'customer':
            self.tabWidget.setTabText(self.tabWidget.indexOf(
                self.tab_4), _translate("MainWindow", "Profil"))
            self.profil_customerPassword.setText(
                _translate("MainWindow", "Kullanici Sifre"))
            self.profil_customerFname.setText(
                _translate("MainWindow", "Kullanici isim"))
            self.profil_customerLname.setText(
                _translate("MainWindow", "Kullanici Soyisim"))
            self.profil_customerTelNo.setText(
                _translate("MainWindow", "Telefon No"))
            self.profil_customerAddress.setText(
                _translate("MainWindow", "Adres"))
            self.bilgileriGuncelle.setText(_translate(
                "MainWindow", "KULLANICI BILGILERI GUNCELLEME"))
            self.pushButton.setText(_translate("MainWindow", "KAYDET"))
            self.profileUpdate()

    def importInput(self):
        imagepath = ''
        fileName = QtWidgets.QFileDialog.getOpenFileName(
            caption='Open File')
        if fileName[0] is not None and fileName[0] != "":
            imagepath = fileName[0]
        imagepathList = imagepath.split('/')
        imagepath = imagepathList[-1]
        imagepath = "assets/" + imagepath
        self.importImagePath = imagepath

    def listeyeEkle(self):
        global cur, conn, authInfo

        productName = self.satici_productNameText.toPlainText()
        productPrice = self.satici_productPriceText.toPlainText()
        category = self.satici_categoryText.toPlainText()
        ingredients = self.satici_ingredientsText.toPlainText()
        restId = authInfo['id']

        cur.execute(
            "INSERT INTO product(id,name,price,r_id,category,ingredients)" +
            f"VALUES(NULL,'{productName}','{productPrice}','{restId}','{category}','{ingredients}')"
        )
        conn.commit()
        if self.importImagePath != "NULL":
            cur.execute('SELECT id FROM product WHERE name =\"'+str(productName)+'\" and price ='+str(productPrice) +
                        ' and r_id = '+str(restId)+' and category = \"'+str(category)+'\" and ingredients = \"'+str(ingredients)+'\"')
            result = cur.fetchall()
            cur.execute(
                "INSERT INTO product_image(id,url,p_id)" +
                f"VALUES(NULL,'{self.importImagePath}','{result[0][0]}')"
            )
            conn.commit()
        self.importImagePath = "NULL"
        self.satici_listView.listOrders()

    def minFiyatGuncelleme(self):
        global cur, conn, authInfo
        restId = authInfo['id']
        minfiyat = self.satici_minPriceUpdateText.toPlainText()

        cur.execute('UPDATE restaurant SET min_pay = ' +
                    str(minfiyat)+' WHERE id = '+str(restId))
        conn.commit()

    def restAddressGuncelleme(self):
        global cur, conn, authInfo
        restId = authInfo['id']
        address = self.satici_restAddressUpdateText.toPlainText()

        cur.execute('UPDATE restaurant SET address = \"' +
                    str(address)+'\" WHERE id = '+str(restId))
        conn.commit()

    def restIsmiGuncelleme(self):
        global cur, conn, authInfo
        restId = authInfo['id']

        restAd = self.satici_restNameUpdateText.toPlainText()
        cur.execute('UPDATE restaurant SET name = \"' +
                    str(restAd)+'\" WHERE id = '+str(restId))
        conn.commit()

    def profilSetFields(self, password, fname, lname, telNo, address):
        _translate = QtCore.QCoreApplication.translate
        self.profil_customerPasswordText.setPlainText(
            _translate("MainWindow", password))
        self.profil_customerFnameText.setPlainText(
            _translate("MainWindow", fname))
        self.profil_customerLnameText.setPlainText(
            _translate("MainWindow", lname))
        self.profil_customerTelNoText.setPlainText(
            _translate("MainWindow", str(telNo)))
        self.profil_customerAddressText.setPlainText(
            _translate("MainWindow", str(address)))

    def profilGuncelleme(self):
        global cur, conn, authInfo
        profilpassword = self.profil_customerPasswordText.toPlainText()
        profilFname = self.profil_customerFnameText.toPlainText()
        profilLname = self.profil_customerLnameText.toPlainText()
        profilTelNo = self.profil_customerTelNoText.toPlainText()
        profilAddress = self.profil_customerAddressText.toPlainText()
        # GUNCELLEME SORUGSU YAPIIYORUZ
        cur.execute('UPDATE customer SET pass = \"'+str(profilpassword)+'\", fname = \"'+str(profilFname) +
                    '\" , lname = \"'+str(profilLname)+'\", telNo = '+str(profilTelNo)+', address = \"'+str(profilAddress)+'\" WHERE id = \"' + str(authInfo['id']) + "\"")
        conn.commit()

        # goksel ==============================================================================================


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
