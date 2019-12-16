# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deneme.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

import sqlite3
from datetime import datetime
from random import randint

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout, QWidget

authInfo = {
    'id': 'thmyris',
    'password': '5',
    'type': 'restaurant'
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
        self.priceLabel = QLabel(str(price))
        self.button = QPushButton("+")
        self.button.setMaximumSize(QtCore.QSize(44, 44))

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
        # TODO: buttonIncrease, buttonDecrease olarak degistirilir mi bu button degisken isimleri?
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
        self.tab_2 = QtWidgets.QWidget()  # tab_2 = Admin
        self.tab_2.setObjectName("Admin")

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
            self.tab_2), _translate("MainWindow", "Admin"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_3), _translate("MainWindow", "Satici"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_4), _translate("MainWindow", "Profil"))

        if authInfo['type'] == 'customer':
            self.tabWidget.setTabText(self.tabWidget.indexOf(
                self.tab), _translate("MainWindow", "Anasayfa"))
            self.anasayfaPurchaseButton.setText(
                _translate("MainWindow", "Satin al"))

    def showDetails(self, orderId):
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


class Login(QtWidgets.QWidget):

    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Login')
        self.resize(500, 120)

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
