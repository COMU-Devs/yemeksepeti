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
    'id': '1',
    'password': '2342324',
    'type': 'restaurant'
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
        self.pixmap = QPixmap(imageUrl[0]).scaled(
            30, 30, QtCore.Qt.KeepAspectRatio)

        self.imageLabel.setSizePolicy(self.imgsizePolicy)
        self.imageLabel.setPixmap(self.pixmap)
        self.nameLabel = QLabel(str(name))
        self.ingredientsLabel = QLabel(str(ingredients))
        self.categoryLabel = QLabel(str(category))
        self.priceLabel = QLabel(str(price))
        self.button = QPushButton("Guncelle")
        self.button_2 = QPushButton("Sil")

        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addWidget(self.nameLabel)
        self.vLayout.addWidget(self.ingredientsLabel)
        self.vLayout.addWidget(self.categoryLabel)
        self.hLayout.addWidget(self.imageLabel)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.button)
        self.hLayout.addWidget(self.button_2)

        self.setLayout(self.hLayout)
     # self.button.clicked.connect(
        #    lambda: self.parent.grandparent.sepet.addSepetItem(productId))
    def getProductImage(self, productId):
        global cur
        url = 'assets/empty.png'
        cur.execute(
            'SELECT url FROM product_image WHERE p_id=' + str(productId))
        result = cur.fetchall()
        if len(result) == 1:
            url = result[0]

        return url


class saticiQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.listOrders()

    def listOrders(self):
        self.clear()
        global cur , authInfo
        restId = authInfo['id']
        cur.execute(
            'SELECT product.id, product.name, product.price, product.r_id, product.category, product.ingredients FROM product , restaurant WHERE restaurant.id = product.r_id and restaurant.id = '+str(restId))
        #SELECT product.name, product.price, product.category, product.ingredients 
        #FROM product , restaurant 
        #WHERE restaurant.id ='1' and restaurant.id = product.r_id
        result = cur.fetchall()
        print(result)
        for row in result:
            item = QListWidgetItem(self)
            item_widget = saticiItemQWidget(row, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)



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

        self.tabWidget.addTab(self.tab, "")  #adding tab to tabWidget

# ---END OF TAB: ANASAYFA
# ---INIT TAB: ADMIN
        self.tab_2 = QtWidgets.QWidget()  # tab_2 = Admin
        self.tab_2.setObjectName("Admin")

        self.tabWidget.addTab(self.tab_2, "")  # adding tab_2 to tabWidget
# ---END OF TAB: ADMIN
# ---INIT TAB: SATICI
        self.tab_3 = QtWidgets.QWidget()  # tab_3 = Satici
        self.tab_3.setObjectName("Satici")

        self.satici_listView = saticiQWidget(self.tab_3, grandparent=self)
        self.satici_listView.setGeometry(QtCore.QRect(50, 50, 441, 231))
        self.satici_listView.setObjectName("listView")#yemekler
        
        self.satici_yemekler = QtWidgets.QLabel(self.tab_3)
        self.satici_yemekler.setGeometry(QtCore.QRect(50, 30, 67, 17))
        self.satici_yemekler.setObjectName("yemekler")

        self.satici_listeyeEkleButton = QtWidgets.QPushButton(self.tab_3)
        self.satici_listeyeEkleButton.setGeometry(QtCore.QRect(390, 450, 89, 25))
        self.satici_listeyeEkleButton.setCheckable(True)
        self.satici_listeyeEkleButton.setObjectName("listeyeEkleButton")
        self.satici_listeyeEkleButton.clicked.connect(self.listeyeEkle)

        self.satici_productNameText = QtWidgets.QTextEdit(self.tab_3)
        self.satici_productNameText.setGeometry(QtCore.QRect(190, 290, 301, 31))
        self.satici_productNameText.setObjectName("productNameText")

        self.satici_productPriceText = QtWidgets.QTextEdit(self.tab_3)
        self.satici_productPriceText.setGeometry(QtCore.QRect(190, 330, 301, 31))
        self.satici_productPriceText.setObjectName("productPriceText")

        self.satici_categoryText = QtWidgets.QTextEdit(self.tab_3)
        self.satici_categoryText.setGeometry(QtCore.QRect(190, 370, 301, 31))
        self.satici_categoryText.setObjectName("categoryText")

        self.satici_ingredientsText = QtWidgets.QTextEdit(self.tab_3)
        self.satici_ingredientsText.setGeometry(QtCore.QRect(190, 410, 301, 31))
        self.satici_ingredientsText.setObjectName("ingredientsText")

        self.satici_productName = QtWidgets.QLabel(self.tab_3)
        self.satici_productName.setGeometry(QtCore.QRect(60, 300, 101, 16))
        self.satici_productName.setObjectName("productName")

        self.satici_productPrice = QtWidgets.QLabel(self.tab_3)
        self.satici_productPrice.setGeometry(QtCore.QRect(60, 340, 101, 17))
        self.satici_productPrice.setObjectName("productPrice")

        self.satici_category = QtWidgets.QLabel(self.tab_3)
        self.satici_category.setGeometry(QtCore.QRect(60, 380, 101, 17))
        self.satici_category.setObjectName("category")

        self.satici_ingredients = QtWidgets.QLabel(self.tab_3)
        self.satici_ingredients.setGeometry(QtCore.QRect(60, 420, 101, 17))
        self.satici_ingredients.setObjectName("ingredients")

        self.satici_productImage = QtWidgets.QLabel(self.tab_3)
        self.satici_productImage.setGeometry(QtCore.QRect(60, 460, 101, 17))
        self.satici_productImage.setObjectName("productImage")

        self.satici_imageOpenButton = QtWidgets.QPushButton(self.tab_3)
        self.satici_imageOpenButton.setGeometry(QtCore.QRect(190, 450, 89, 25))
        self.satici_imageOpenButton.setObjectName("imageOpenButton")
        self.satici_imageOpenButton.clicked.connect(self.importInput)

        self.satici_minPriceUpdate = QtWidgets.QLabel(self.tab_3)
        self.satici_minPriceUpdate.setGeometry(QtCore.QRect(560, 50, 171, 31))
        self.satici_minPriceUpdate.setObjectName("minPriceUpdate")
        

        self.satici_minPriceUpdateText = QtWidgets.QTextEdit(self.tab_3)
        self.satici_minPriceUpdateText.setGeometry(QtCore.QRect(740, 50, 301, 31))
        self.satici_minPriceUpdateText.setObjectName("minPriceUpdateText")

        self.satici_minPriceUpdateButton = QtWidgets.QPushButton(self.tab_3)
        self.satici_minPriceUpdateButton.setGeometry(QtCore.QRect(1050, 50, 89, 25))
        self.satici_minPriceUpdateButton.setObjectName("minPriceUpdateButton")
        self.satici_minPriceUpdateButton.clicked.connect(self.minFiyatGuncelleme)

        self.satici_restAddressUpdate = QtWidgets.QLabel(self.tab_3)
        self.satici_restAddressUpdate.setGeometry(QtCore.QRect(560, 100, 171, 31))
        self.satici_restAddressUpdate.setObjectName("restAddressUpdate")

        self.satici_restAddressUpdateText = QtWidgets.QTextEdit(self.tab_3)
        self.satici_restAddressUpdateText.setGeometry(QtCore.QRect(740, 100, 301, 31))
        self.satici_restAddressUpdateText.setObjectName("restAddressUpdateText")

        self.satici_restAddressUpdateButton = QtWidgets.QPushButton(self.tab_3)
        self.satici_restAddressUpdateButton.setGeometry(QtCore.QRect(1050, 100, 89, 25))
        self.satici_restAddressUpdateButton.setObjectName("restAddressUpdateButton")
        self.satici_restAddressUpdateButton.clicked.connect(self.restAddressGuncelleme)

        self.satici_restNameUpdate = QtWidgets.QLabel(self.tab_3)
        self.satici_restNameUpdate.setGeometry(QtCore.QRect(560, 150, 171, 31))
        self.satici_restNameUpdate.setObjectName("restNameUpdate")

        self.satici_restNameUpdateText = QtWidgets.QTextEdit(self.tab_3)
        self.satici_restNameUpdateText.setGeometry(QtCore.QRect(740, 150, 301, 31))
        self.satici_restNameUpdateText.setObjectName("restNameUpdateText")

        self.satici_restNameUpdateButton = QtWidgets.QPushButton(self.tab_3)
        self.satici_restNameUpdateButton.setGeometry(QtCore.QRect(1050, 150, 89, 25))
        self.satici_restNameUpdateButton.setObjectName("restNameUpdateButton")
        self.satici_restNameUpdateButton.clicked.connect(self.restIsmiGuncelleme)

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
        self.importImagePath = "NULL" #goksel 1 satir


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
        

        #goksel
        self.satici_yemekler.setText(_translate("MainWindow", "Yemekler"))
        self.satici_listeyeEkleButton.setText(_translate("MainWindow", "Listeye Ekle"))
        self.satici_productName.setText(_translate("MainWindow", "Yemek ismi"))
        self.satici_productPrice.setText(_translate("MainWindow", "Yemek Fiyati"))
        self.satici_category.setText(_translate("MainWindow", "Kategori"))
        self.satici_ingredients.setText(_translate("MainWindow", "Icindekiler"))
        self.satici_productImage.setText(_translate("MainWindow", "Yemek Resmi"))
        self.satici_imageOpenButton.setText(_translate("MainWindow", "Dosya Ac"))
        self.satici_minPriceUpdate.setText(_translate("MainWindow", "Minimum Fiyat Guncelle"))
        self.satici_minPriceUpdateButton.setText(_translate("MainWindow", "Guncelle"))
        self.satici_restAddressUpdate.setText(_translate("MainWindow", "Restoran Adresi Guncelle"))
        self.satici_restAddressUpdateButton.setText(_translate("MainWindow", "Guncelle"))
        self.satici_restNameUpdate.setText(_translate("MainWindow", "Restoran ismi Guncelle"))
        self.satici_restNameUpdateButton.setText(_translate("MainWindow", "Guncelle"))
        


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

    def listeyeEkle (self):
        global cur ,conn, authInfo

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
        print(self.importImagePath)
        if self.importImagePath != "NULL":
            cur.execute('SELECT id FROM product WHERE name =\"'+str(productName)+'\" and price ='+str(productPrice)+' and r_id = '+str(restId)+' and category = \"'+str(category)+'\" and ingredients = \"'+str(ingredients)+'\"' )
            result = cur.fetchall()
            cur.execute(
                "INSERT INTO product_image(id,url,p_id)"+
                f"VALUES(NULL,'{self.importImagePath}','{result[0][0]}')"
            )
            conn.commit()
        self.importImagePath = "NULL"


    def minFiyatGuncelleme(self):
        global cur, conn, authInfo
        restId = authInfo['id']
        minfiyat = self.satici_minPriceUpdateText.toPlainText()

        cur.execute('UPDATE restaurant SET min_pay = '+str(minfiyat)+' WHERE id = '+str(restId))
        conn.commit()

    def restAddressGuncelleme(self):
        global cur, conn, authInfo
        restId = authInfo['id']
        address = self.satici_restAddressUpdateText.toPlainText()

        cur.execute('UPDATE restaurant SET address = \"'+str(address)+'\" WHERE id = '+str(restId))
        conn.commit()

    def restIsmiGuncelleme(self):
        global cur, conn, authInfo
        restId = authInfo['id']

        restAd = self.satici_restNameUpdateText.toPlainText()

        cur.execute('UPDATE restaurant SET name = \"'+str(restAd)+'\" WHERE id = '+str(restId))

        conn.commit()
        
        #goksel

        
        


        
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
