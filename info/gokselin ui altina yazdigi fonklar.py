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

        a = self.satici_productNameText.toPlainText()
        b = self.satici_productPriceText.toPlainText()
        c = self.satici_categoryText.toPlainText()
        d = self.satici_ingredientsText.toPlainText()
        myid = authInfo['id']
        
        cur.execute(
            "INSERT INTO product(id,name,price,r_id,category,ingredients)"+
            f"VALUES(NULL,'{a}','{b}',{myid},'{c}','{d}')"
        )
        conn.commit()
        if self.importImagePath != "NULL":
            pass
        self.importImagePath = "NULL"
		
		
# BU DA gokselin o fonku nasil calistirdigi (yine ui altinda.)
self.satici_listeyeEkleButton.clicked.connect(self.listeyeEkle)


#BU DA GOKSELIN FIELD DOLDURMAK ICIN SQL SONUCUNDAN DEGISKENE VERILERI GERI ALMASI
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