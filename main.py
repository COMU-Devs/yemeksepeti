import sqlite3
from datetime import datetime
from random import randint

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout, QWidget

authInfo = {
    'id': 'placeholder',
    'password': 'placeholder',
    'type': 'placeholder'
}

conn = sqlite3.connect('yemeksepeti.db')
cur = conn.cursor()


class productQWidget(QWidget):
    def __init__(self, row, parent=None):
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
        self.priceLabel = QLabel(str(price)+'tl')
        self.button = QPushButton("+")
        self.button.setMaximumSize(QtCore.QSize(44, 44))

        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addWidget(self.nameLabel)
        self.vLayout.addWidget(self.ingredientsLabel)
        self.vLayout.addWidget(self.categoryLabel)
        self.hLayout.addWidget(self.imageLabel)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.priceLabel)
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
            url = result[0][0]

        return url


class restaurantQWidget(QWidget):
    def __init__(self, row, parent=None):
        super(restaurantQWidget, self).__init__(parent)
        self.parent = parent
        self.values = row

        restaurantId = self.values[0]
        name, address, minPayment = self.values[2:]

        self.nameLabel = QLabel(str(name))
        self.nameLabel.setWordWrap(True)
        self.addressLabel = QLabel(str(address))
        self.addressLabel.setWordWrap(True)
        self.minpaymentLabel = QLabel('min: ' + str(minPayment) + ' tl')
        self.minpaymentLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        self.button = QPushButton("sec")
        self.button.setMaximumSize(QtCore.QSize(44, 44))

        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.nameLabel)
        self.vLayout.addWidget(self.addressLabel)
        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.button)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.minpaymentLabel)

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
        self.clear()
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
        productName, productPrice = self.getProduct(p_id)[0]

        self.productNameLabel = QLabel(str(productName))
        self.quantityLabel = QLabel(str(quantity))
        self.priceLabel = QLabel(str(int(quantity) * int(productPrice)))

        self.hLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()

        self.button = QPushButton("+")
        self.button2 = QPushButton('-')

        self.vLayout.addWidget(self.button)
        self.vLayout.addWidget(self.button2)

        self.hLayout.addWidget(self.productNameLabel)
        self.hLayout.addWidget(self.quantityLabel)
        self.hLayout.addLayout(self.vLayout)

        self.setLayout(self.hLayout)

        self.button.clicked.connect(
            lambda: self.parent.addSepetItem(p_id)
        )

        self.button2.clicked.connect(
            lambda: self.parent.removeSepetItem(p_id))

    def getProduct(self, productId):
        global cur
        cur.execute(
            'SELECT name, price FROM product WHERE id = '+str(productId))
        result = cur.fetchall()
        return result


class sepetQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.grandparent = grandparent
        self.orderId = -1  # for init
        self.setOrderId()
        self.listSepetItems()

    def setOrderId(self):
        global conn, cur, authInfo
        # eger bos sepet varsa id o sepetin id sini dondur
        # yoksa bos bir sepet olustur ve id sini dondur
        cur.execute('SELECT id FROM order_table WHERE cus_id = \"' +
                    str(authInfo['id']) + '\" and purchase_date is NULL LIMIT 1')
        result = cur.fetchall()
        if len(result) == 1:
            orderId = result[0][0]
            self.orderId = orderId

        else:
            # insert new record with date = NULL
            cur.execute("INSERT INTO order_table(id, purchase_date, cus_id)" +
                        "VALUES( NULL, NULL, \"" + str(authInfo['id']) + "\")"
                        )

            conn.commit()

            cur.execute('SELECT id FROM order_table WHERE cus_id = \"' +
                        str(authInfo['id']) + '\" and purchase_date is NULL LIMIT 1')

            orderId = cur.fetchall()[0][0]
            self.orderId = orderId

    def listSepetItems(self):
        global authInfo, cur
        self.clear()
        cur.execute('SELECT * FROM order_line WHERE order_id = ' +
                    str(self.orderId))
        result = cur.fetchall()
        for row in result:
            item = QListWidgetItem(self)
            item_widget = sepetItemQWidget(row, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def addSepetItem(self, productId):
        global conn, cur, authInfo
        cur.execute('SELECT * FROM order_line WHERE order_id = ' + str(self.orderId) +
                    ' and p_id = ' + str(productId)
                    )
        result = cur.fetchall()
        if len(result) > 0:
            orderlineId = result[0][0]
            currentQuantity = result[0][1]
            cur.execute('UPDATE order_line SET quantity = ' + str(currentQuantity+1) +
                        ' WHERE id = ' + str(orderlineId))
            conn.commit()
        else:
            cur.execute("INSERT INTO order_line(id, quantity, p_id, order_id)" +
                        "VALUES( NULL, 1, \"" + str(productId) +
                        "\", " + str(self.orderId) + ")"
                        )
            conn.commit()

        self.listSepetItems()

    def removeSepetItem(self, productId):
        global conn, cur, authInfo
        cur.execute('SELECT * FROM order_line WHERE order_id = ' + str(self.orderId) +
                    ' and p_id = ' + str(productId)
                    )
        result = cur.fetchall()
        orderlineId = result[0][0]
        currentQuantity = result[0][1]

        if currentQuantity > 1:
            cur.execute('UPDATE order_line SET quantity = ' + str(currentQuantity-1) +
                        ' WHERE id = ' + str(orderlineId))
            conn.commit()

        else:
            cur.execute(
                "DELETE FROM order_line WHERE id = " + str(orderlineId)
            )

            conn.commit()

        self.listSepetItems()

    def purchase(self):
        global conn, cur

        cur.execute('SELECT COUNT(*) ' +
                    'FROM order_line ' +
                    'WHERE order_id = ' + str(self.orderId)
                    )
        amountOfItem = cur.fetchall()[0][0]

        if amountOfItem > 0:
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            cur.execute('UPDATE order_table SET purchase_date = \"' + str(now) +
                        '\" WHERE id = \"' + str(self.orderId) + "\""
                        )
            conn.commit()

        self.setOrderId()
        self.listSepetItems()
        self.grandparent.orders.listOrders()


class orderItemQWidget(QWidget):
    def __init__(self, row, parent=None):
        super(orderItemQWidget, self).__init__(parent)
        self.parent = parent
        orderId, purchaseDate = row[0], row[1]
        totalPrice = self.calculatePrice(orderId)
        self.hLayout = QHBoxLayout()
        self.vLayout = QVBoxLayout()

        self.orderIdLabel = QLabel(str(orderId))
        self.priceLabel = QLabel(str(totalPrice) + ' tl')
        self.purchaseDateLabel = QLabel(str(purchaseDate))
        self.detailsButton = QPushButton('details')
        self.detailsButton.setMaximumSize(QtCore.QSize(88, 44))
        self.detailsButton.clicked.connect(
            lambda: self.parent.grandparent.showDetails(orderId))

        self.hLayout.addWidget(self.orderIdLabel)
        self.hLayout.addWidget(self.purchaseDateLabel)
        self.hLayout.addWidget(self.priceLabel)
        self.hLayout.addWidget(self.detailsButton)
        self.setLayout(self.hLayout)

    def calculatePrice(self, orderId):
        global cur, authInfo
        cur.execute('SELECT * ' +
                    'FROM order_line ' +
                    'WHERE order_id = ' + str(orderId)
                    )
        result = cur.fetchall()
        totalPrice = 0
        for row in result:
            orderLineId, quantity, productId, orderId = row
            cur.execute('SELECT price ' +
                        'FROM product ' +
                        'WHERE id = ' + str(productId)
                        )
            productResult = cur.fetchall()
            productPrice = productResult[0][0]
            totalPrice += quantity * productPrice

        return totalPrice


class orderQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.grandparent = grandparent
        self.listOrders()

    def listOrders(self):
        self.clear()
        global cur, authInfo
        cur.execute('SELECT * ' +
                    'FROM order_table ' +
                    'WHERE cus_id = \"' + str(authInfo['id']) +
                    '\" and purchase_date is not NULL '
                    )

        result = cur.fetchall()
        for row in result:
            item = QListWidgetItem(self)
            item_widget = orderItemQWidget(row, parent=self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)



# NOTE FARUK:admin/restorantablosubox na donusturulecek. menuQWidget in kopyasiydi.
class adminRestaurantBoxQWidget(QListWidget):
    def __init__(self, parent=None, grandparent=None):
        QListWidget.__init__(self, parent)
        self.grandparent = grandparent
        self.SUPERrestid = -1
        self.adminListRestaurants()

    def adminListRestaurants(self):
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
        if type(travellingrestid) == int:
            cur.execute(
                "DELETE FROM restaurant WHERE id =" + travellingrestid
            )
        if type(travellingrestid) == str:
            cur.execute(
                "DELETE FROM restaurant WHERE id =\"" + travellingrestid + "\""
            )
        conn.commit()
        self.adminListRestaurants()

    def adminRestoranGuncelleLabelBilgisiCek(self, travellingrestid2):
        global cur, conn
        if type(travellingrestid2) == int:
            cur.execute(
                'SELECT * FROM restaurant WHERE id =' + str(travellingrestid2)
            )
        if type(travellingrestid2) == str:
            cur.execute(
                'SELECT * FROM restaurant WHERE id =\"' + str(travellingrestid2) + "\""
            )
        result = cur.fetchall()
        # bunu self yapma sebebim ui icindeki onayla2clickeventhandlerin bu degiskene erisip adminsqlguncelle fonkuna degisken olarak gonderebilmesi
        self.SUPERrestid = result[0][0]
        restpass = result[0][1]
        restname = result[0][2]
        restaddr = result[0][3]
        restminpay = result[0][4]
        self.grandparent.adminRestoranGuncelleLabelBilgisiDoldur(
            self.SUPERrestid, restpass, restname, restaddr, restminpay)
        self.adminListRestaurants()


# NOTE FARUK:admin/restorantablosulistesi ne donusturulecek. restaurantQWidget in kopyasiydi.
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
            lambda: self.parent.adminRestoranGuncelleLabelBilgisiCek(travellingrestid2=restId))
        self.buttonDelete.clicked.connect(
            lambda: self.parent.adminListedenCikar(travellingrestid=restId))
class details_Ui(object):
    def __init__(self):
        super().__init__()
        self.text = ''

    def setupUi(self, Form):
        Form.setObjectName("Detaylar")
        Form.resize(620, 282)
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(0, 0, 621, 291))
        self.textBrowser.setObjectName("textBrowser")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Details"))
        self.textBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" + self.text + "</p></body></html>"))

    def setText(self, txt):
        self.text = txt
        _translate = QtCore.QCoreApplication.translate
        self.textBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" + self.text + "</p></body></html>"))


class details(PyQt5.QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(420, 280)
        self.ui = details_Ui()
        self.ui.setupUi(self)

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
        global authInfo
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1087, 666)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        # ---INIT TAB: ANASAYFA
        if authInfo['type'] == 'customer':
            self.tab = QtWidgets.QWidget()  # tab = anasayfa
            self.tab.setObjectName("Anasayfa")

            self.menu = menuQWidget(self.tab, grandparent=self)
            self.menu.setObjectName('listOfProducts')

            self.sepet = sepetQWidget(self.tab, grandparent=self)
            self.sepet.setObjectName('sepet')

            self.details = details()
            self.details.setObjectName('details')

            self.orders = orderQWidget(self.tab, grandparent=self)
            self.orders.setObjectName('orders')

            self.anasayfaPurchaseButton = QPushButton(self.tab)
            # self.anasayfaPurchaseButton.setGeometry(QtCore.QRect(900, 400, 89, 25))
            self.anasayfaPurchaseButton.setObjectName('satinAlButon')
            self.anasayfaPurchaseButton.clicked.connect(self.sepet.purchase)

            self.backButton = QPushButton(self.tab)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.backButton.sizePolicy().hasHeightForWidth())
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("assets/back.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.backButton.setIcon(icon)
            self.backButton.setSizePolicy(sizePolicy)
            self.backButton.setMaximumSize(QtCore.QSize(25, 25))
            spacerItem = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.backButton.clicked.connect(self.menu.listRestaurants)
            self.tabVertical2 = QtWidgets.QVBoxLayout()
            self.tabVertical2.addWidget(self.backButton)
            self.tabVertical2.addItem(spacerItem)

            self.tabHorizantal = QtWidgets.QHBoxLayout(self.tab)
            self.tabHorizantal2 = QtWidgets.QHBoxLayout()
            self.tabHorizantal2.addLayout(self.tabVertical2)
            self.tabHorizantal2.addWidget(self.menu)

            self.tabVertical = QtWidgets.QVBoxLayout()
            self.tabVertical.addWidget(self.sepet)
            self.tabVertical.addWidget(self.anasayfaPurchaseButton)
            self.tabVertical.addWidget(self.orders)
            self.tabHorizantal2.addLayout(self.tabVertical)
            self.tabHorizantal.addLayout(self.tabHorizantal2)

            self.tabWidget.addTab(self.tab, "")  # adding tab to tabWidget
        # ---END OF TAB: ANASAYFA
        # ---INIT TAB: ADMIN
        if authInfo['type'] == 'admin':
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
            self.adminPlainTextEdit = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit.setGeometry(QtCore.QRect(57, 345, 51, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit.setFont(font)
            self.adminPlainTextEdit.setObjectName("adminPlainTextEdit")
            self.adminPlainTextEdit_2 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_2.setGeometry(QtCore.QRect(156, 345, 81, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_2.setFont(font)
            self.adminPlainTextEdit_2.setObjectName("adminPlainTextEdit_2")
            self.adminPlainTextEdit_3 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_3.setGeometry(QtCore.QRect(563, 345, 291, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_3.setFont(font)
            self.adminPlainTextEdit_3.setObjectName("adminPlainTextEdit_3")
            self.adminPlainTextEdit_4 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_4.setGeometry(QtCore.QRect(293, 345, 211, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_4.setFont(font)
            self.adminPlainTextEdit_4.setObjectName("adminPlainTextEdit_4")
            self.adminPlainTextEdit_5 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_5.setGeometry(QtCore.QRect(993, 345, 51, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_5.setFont(font)
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
            self.adminPlainTextEdit_6 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_6.setGeometry(QtCore.QRect(994, 455, 51, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_6.setFont(font)
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
            self.adminPlainTextEdit_7 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_7.setGeometry(QtCore.QRect(57, 455, 51, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_7.setFont(font)
            self.adminPlainTextEdit_7.setObjectName("adminPlainTextEdit_7")
            self.adminPlainTextEdit_8 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_8.setGeometry(QtCore.QRect(294, 455, 211, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_8.setFont(font)
            self.adminPlainTextEdit_8.setObjectName("adminPlainTextEdit_8")
            self.adminPlainTextEdit_9 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_9.setGeometry(QtCore.QRect(564, 455, 291, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_9.setFont(font)
            self.adminPlainTextEdit_9.setObjectName("adminPlainTextEdit_9")
            self.adminPlainTextEdit_10 = QtWidgets.QLineEdit(self.tab_2)
            self.adminPlainTextEdit_10.setGeometry(QtCore.QRect(157, 455, 81, 31))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.adminPlainTextEdit_10.setFont(font)
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
            self.adminOnayla2.clicked.connect(self.adminSQLGuncelle)
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
            self.pushButton.clicked.connect(
                self.profilGuncelleme)  # BUTTONA BASILDIGINDA

            self.tabWidget.addTab(self.tab_4, "")  # adding tab_4 to tabWidget
# ---END OF TAB: PROFIL

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
        print(type(telNo))
        if telNo is None:
            telNo = ''
        address = result[0][5]
        if address is None:
            address = ''
        self.profilSetFields(password, fname, lname, telNo, address)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        
        
        
        
        if authInfo['type'] == 'customer':
            self.tabWidget.setTabText(self.tabWidget.indexOf(
                self.tab), _translate("MainWindow", "Anasayfa"))
            self.anasayfaPurchaseButton.setText(
                _translate("MainWindow", "Satin al"))


        # --INIT FARUK RETRANSLATE
        if authInfo['type'] == 'admin':
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
            self.tabWidget.setTabText(self.tabWidget.indexOf(
                self.tab_2), _translate("MainWindow", "Admin"))
        
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
        # --END FARUK RETRANSLATE

        # --- INIT FARUK BUTTON HANDLING
    def adminListeyeEkle(self):
        global cur, conn, authInfo

        ekleid = self.adminPlainTextEdit.text()
        eklepass = self.adminPlainTextEdit_2.text()
        ekleisim = self.adminPlainTextEdit_4.text()
        ekleadres = self.adminPlainTextEdit_3.text()
        eklesinir = self.adminPlainTextEdit_5.text()

        myid = authInfo['id']
        cur.execute(
            "INSERT INTO restaurant(id,pass,name,address,min_pay)" +
            f"VALUES('{ekleid}','{eklepass}','{ekleisim}','{ekleadres}', '{eklesinir}')"
        )
        conn.commit()
        self.adminRestaurantBox.adminListRestaurants()

    def adminSQLGuncelle(self):
        global cur, conn, authInfo
        gelenid = self.adminRestaurantBox.SUPERrestid
        updateid = self.adminPlainTextEdit_7.text()
        updatepass = self.adminPlainTextEdit_10.text()
        updatename = self.adminPlainTextEdit_8.text()
        updateaddress = self.adminPlainTextEdit_9.text()
        updateminpay = self.adminPlainTextEdit_6.text()

        myid = authInfo['id']
        cur.execute('UPDATE restaurant SET id = \"' + str(updateid) + '\", pass = \"' + str(updatepass) + '\", name = \"' + str(
            updatename) + '\", address = \"' + str(updateaddress) + '\" , min_pay = \"' + str(updateminpay) + '\" WHERE id = \"' + str(gelenid) + '\"')
        conn.commit()
        self.adminRestaurantBox.adminListRestaurants()

        self.adminPlainTextEdit_7.setText("")
        self.adminPlainTextEdit_10.setText("")
        self.adminPlainTextEdit_8.setText("")
        self.adminPlainTextEdit_9.setText("")
        self.adminPlainTextEdit_6.setText("")

    def adminRestoranGuncelleLabelBilgisiDoldur(self, restid2, restpass2, restname2, restaddr2, restminpay2):
        _translate = QtCore.QCoreApplication.translate
        self.adminPlainTextEdit_7.setText(
            _translate("Form", restid2))
        self.adminPlainTextEdit_10.setText(_translate("Form", restpass2))
        self.adminPlainTextEdit_8.setText(_translate("Form", restname2))
        self.adminPlainTextEdit_9.setText(_translate("Form", restaddr2))
        self.adminPlainTextEdit_6.setText(
            _translate("Form", str(restminpay2)))

    # --- END FARUK BUTTON HANDLING
        

    def showDetails(self, orderId):
        # can
        adisyon = ''
        cur.execute('SELECT quantity, p_id ' +
                    'FROM order_line ' +
                    'WHERE order_id = ' + str(orderId)
                    )
        result = cur.fetchall()
        for row in result:
            quantity, productId = row
            cur.execute('SELECT name ' +
                        'FROM product ' +
                        'WHERE id = ' + str(productId)
                        )

            productName = cur.fetchall()[0][0]
            line = str(quantity) + 'x ' + str(productName) + '<br />'
            adisyon += line
        self.details.ui.setText(adisyon)
        self.details.show()

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
        if profilTelNo == "":
            profilTelNo = 'NULL'
        profilAddress = self.profil_customerAddressText.toPlainText()
        if profilAddress == "":
            profilAddress = 'NULL'
            cur.execute('UPDATE customer SET pass = \"'+str(profilpassword)+'\", fname = \"'+str(profilFname) +
                        '\" , lname = \"'+str(profilLname)+'\", telNo = '+str(profilTelNo)+', address = '+str(profilAddress)+' WHERE id = \"' + str(authInfo['id']) + "\"")
        # GUNCELLEME SORUGSU YAPIIYORUZ
        else:
            cur.execute('UPDATE customer SET pass = \"'+str(profilpassword)+'\", fname = \"'+str(profilFname) +
                        '\" , lname = \"'+str(profilLname)+'\", telNo = '+str(profilTelNo)+', address = \"'+str(profilAddress)+'\" WHERE id = \"' + str(authInfo['id']) + "\"")
        conn.commit()

        # goksel ==============================================================================================



class Login(QtWidgets.QWidget):

    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Login')
        self.resize(700, 320)

        layout = QtWidgets.QGridLayout()
        self.loginLayout = QVBoxLayout()
        self.singupLayout = QVBoxLayout()
        self.GeneralLayout = QHBoxLayout()
        self.msg = QMessageBox()

        # login side
        self.loginButton = QtWidgets.QPushButton('Login')

        self.loginButton.clicked.connect(self.login)
        self.loginUsernameLabel = QLabel('<font size="4"> Username </font>')
        self.loginUsernameLineEdit = QLineEdit()
        self.loginUsernameLineEdit.setPlaceholderText(
            'Please enter your username')

        self.loginPasswordLabel = QLabel('<font size="4"> Password </font>')
        self.loginPasswordLineEdit = QLineEdit()
        self.loginPasswordLineEdit.setPlaceholderText(
            'Please enter your password')

        self.loginRow1 = QHBoxLayout()
        self.loginRow1.addWidget(self.loginUsernameLabel)
        self.loginRow1.addWidget(self.loginUsernameLineEdit)

        self.loginRow2 = QHBoxLayout()
        self.loginRow2.addWidget(self.loginPasswordLabel)
        self.loginRow2.addWidget(self.loginPasswordLineEdit)

        self.loginLayout.addLayout(self.loginRow1)
        self.loginLayout.addLayout(self.loginRow2)
        self.loginLayout.addWidget(self.loginButton)

        # signup side
        self.signupButton = QtWidgets.QPushButton('Signup')
        self.signupButton.clicked.connect(self.signup)

        self.signupUsernameLabel = QLabel('<font size="4"> Username </font>')
        self.signupUsernameLineEdit = QLineEdit()
        self.signupUsernameLineEdit.setPlaceholderText(
            'Please enter your username')

        self.signupPasswordLabel = QLabel('<font size="4"> Password </font>')
        self.signupPasswordLineEdit = QLineEdit()
        self.signupPasswordLineEdit.setPlaceholderText(
            'Please enter your password')

        self.signupNameLabel = QLabel('<font size="4"> Name </font>')
        self.signupNameLineEdit = QLineEdit()
        self.signupNameLineEdit.setPlaceholderText(
            'Please enter your name')

        self.signupSurnameLabel = QLabel('<font size="4"> Surname </font>')
        self.signupSurnameLineEdit = QLineEdit()
        self.signupSurnameLineEdit.setPlaceholderText(
            'Please enter your surname')

        self.signupPhoneLabel = QLabel('<font size="4"> Phone </font>')
        self.signupPhoneLineEdit = QLineEdit()
        self.signupPhoneLineEdit.setPlaceholderText(
            'Please enter your phone')

        self.signupAddressLabel = QLabel('<font size="4"> Address </font>')
        self.signupAddressLineEdit = QLineEdit()
        self.signupAddressLineEdit.setPlaceholderText(
            'Please enter your address')        

        

        self.singupRow1 = QHBoxLayout()
        self.singupRow1.addWidget(self.signupUsernameLabel)
        self.singupRow1.addWidget(self.signupUsernameLineEdit)

        self.singupRow2 = QHBoxLayout()
        self.singupRow2.addWidget(self.signupPasswordLabel)
        self.singupRow2.addWidget(self.signupPasswordLineEdit)

        self.singupRow3 = QHBoxLayout()
        self.singupRow3.addWidget(self.signupNameLabel)
        self.singupRow3.addWidget(self.signupNameLineEdit)

        self.singupRow4 = QHBoxLayout()
        self.singupRow4.addWidget(self.signupSurnameLabel)
        self.singupRow4.addWidget(self.signupSurnameLineEdit)

        self.singupRow5 = QHBoxLayout()
        self.singupRow5.addWidget(self.signupPhoneLabel)
        self.singupRow5.addWidget(self.signupPhoneLineEdit)

        self.singupRow6 = QHBoxLayout()
        self.singupRow6.addWidget(self.signupAddressLabel)
        self.singupRow6.addWidget(self.signupAddressLineEdit)

        self.singupLayout.addLayout(self.singupRow1)
        self.singupLayout.addLayout(self.singupRow2)
        self.singupLayout.addLayout(self.singupRow3)
        self.singupLayout.addLayout(self.singupRow4)
        self.singupLayout.addLayout(self.singupRow5)
        self.singupLayout.addLayout(self.singupRow6)

        self.singupLayout.addWidget(self.signupButton)

        self.GeneralLayout.addLayout(self.loginLayout)
        self.GeneralLayout.addLayout(self.singupLayout)

        layout.addLayout(self.GeneralLayout, 1, 1)

        self.setLayout(layout)

    def login(self):
        global conn, cur, authInfo
        uid = self.loginUsernameLineEdit.text()
        upw = self.loginPasswordLineEdit.text()
        cur.execute('SELECT * ' +
                    'FROM customer ' +
                    'WHERE id = \"' + str(uid) + 
                    '\" and pass = \"' + str(upw) + '\"'
        )
        resultCustomer = cur.fetchall()
        if len(resultCustomer) > 0:
            authInfo['id'] = uid
            authInfo['password'] = upw
            authInfo['type'] = 'customer'
            self.switch_window.emit()
        
        else:
            cur.execute('SELECT * ' +
                    'FROM restaurant ' +
                    'WHERE id = \"' + str(uid) + 
                    '\" and pass = \"' + str(upw) + '\"'
            )
            resultRestaurant = cur.fetchall()
            if len(resultRestaurant) > 0:
                authInfo['id'] = uid
                authInfo['password'] = upw
                authInfo['type'] = 'restaurant'
                self.switch_window.emit()
            
            else:
                if uid == 'admin' and upw == 'admin':
                    authInfo['id'] = str(uid)
                    authInfo['password'] = str(upw)
                    authInfo['type'] = 'admin'
                    self.switch_window.emit()
                else:
                    self.msg.setText('Incorrect Id or Password')
                    self.msg.exec_()


    def signup(self):
        global conn, cur, authInfo
        uid = self.signupUsernameLineEdit.text()
        pw = self.signupPasswordLineEdit.text()
        name = self.signupNameLineEdit.text()
        surname = self.signupSurnameLineEdit.text()
        phone = self.signupPhoneLineEdit.text()
        address = self.signupAddressLineEdit.text()

        valid = self.checkUniqueConstraint(uid)
        if valid :
            cur.execute('INSERT INTO customer ' + 
                        'VALUES('
                            +"\"" + uid + "\" ," 
                            +"\"" + pw + "\" ,"
                            +"\"" + name + "\", "
                            +"\"" + surname + "\", "
                            + str(phone) 
                            + ", \"" + address + "\""
                        +')'
            )
            conn.commit()
            self.msg.setText('Sign up successful!')
            self.msg.exec_()

        else:
            self.msg.setText('That user ID is taken.')
            self.msg.exec_()

    def checkUniqueConstraint(self, userid):
        global cur
        if userid == 'admin':
            print('error')
            return False

        cur.execute('SELECT * ' + 
                    'FROM customer ' +
                    'WHERE id = \"' + str(userid) + "\""
        )
        cusresult = cur.fetchall()
        if len(cusresult) > 0:
            print('error!')
            return False
        else:
            cur.execute('SELECT * ' + 
                        'FROM restaurant ' +
                        'WHERE id = \"' + str(userid) + "\""
            )

            resresult = cur.fetchall()
            
            if len(resresult) > 0:
                print('error!')
                return False
            
        return True


class Program:
    def __init__(self):
        pass

    def show_login(self):
        self.login = Login()
        self.login.switch_window.connect(self.show_main)
        self.login.show()

    def show_main(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.login.close()
        self.window.show()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_program = Program()
    main_program.show_login()
    sys.exit(app.exec_())
