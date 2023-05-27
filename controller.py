import os
import sys
from functools import reduce
import sqlite3
from os.path import exists
from prettytable import PrettyTable

from PIL import ImageGrab
from PIL import Image

connection = None
cursor = None


class Resident:
    rID: int
    name: str
    phone: str
    paypal: str

    def __init__(self, rID, name=None, phone=None, paypal=None):
        self.rID = rID
        self.name = name if name != "" else None
        self.phone = phone if phone != "" else None
        self.paypal = paypal if paypal != "" else None

    def __str__(self):
        return f"(Name={self.name}, Telefon={self.phone}, PayPal={self.paypal})"

    def tuple(self):
        return self.rID, self.name, self.phone, self.paypal


def initDatabase():
    create = False
    if not exists("data.db"):
        create = True
    global connection, cursor
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    if create:
        fd = open("data.ddl")
        ddl = reduce(lambda s1, s2: s1 + s2, fd.readlines(), "")
        fd.close()
        connection.executescript(ddl)


def initFileStructure():
    if not exists("bills"):
        os.mkdir("bills")


def loadResidents():
    res = cursor.execute("SELECT * FROM resident")
    residents = []
    resTuple = res.fetchone()
    while resTuple is not None:
        residents.append(Resident(*resTuple))
        resTuple = res.fetchone()
    return residents


def addResidentToDB(resident):
    cursor.execute("INSERT INTO resident VALUES(NULL,?,?,?)", [resident.name, resident.phone, resident.paypal])
    connection.commit()


def fetchImage():
    pictureFound = False
    imPath = ""
    while not pictureFound:
        imPathList = ImageGrab.grabclipboard()
        if imPathList is None or len(imPathList) == 0:
            input("Beleg kopieren... ENTER um fortzufahren")
        else:
            pictureFound = True
            imPath = imPathList[0]
    im = Image.open(imPath)
    return im


def addBill(rID, amount):
    cursor.execute("INSERT INTO bills(buyer_id, amount) VALUES(?,?);", [rID, amount])
    connection.commit()
    res = cursor.execute("SELECT last_insert_rowid() FROM bills;")
    bill_id = res.fetchone()[0]
    return bill_id


def addUser():
    name = input("Name: ")
    phone = input("Phone: ")
    paypal = input("PayPal: ")
    addResidentToDB(Resident(-1, name, phone, paypal))
    print("ERFOLGREICH\n")


def printResidents():
    residents = loadResidents()
    residentData = list(map(lambda r: r.tuple(), residents))
    printTable(data=residentData, column_names=["Bewohnernummer", "Name", "Telefon", "PayPal"])


def registerBill():
    printResidents()
    index = input("\nBewohner Nummer eingeben: ")
    amount = input("Betrag eingeben: ")
    image = fetchImage()
    bill_id = addBill(index, amount)
    image.save(f"bills/{bill_id}.jpg")
    print("ERFOLGREICH\n")


def payoutBill():
    print_bills(only_pending=True)
    bID = input("\nZahle Beleg mit Nummer: ")
    details = input("Transaktionsdetails: ")
    cursor.execute("UPDATE bills SET status = 'REPAID', transaction_details = ? where id = ?;", [details, bID])
    connection.commit()


def print_bills(only_pending):
    query = "SELECT r.name, r.phoneNumber, COALESCE(r.paypal, 'None'), b.id, b.amount, b.added FROM bills b, resident r WHERE r.id = b.buyer_id;"
    if only_pending:
        query = f"{query[:-1]} AND b.status = 'REGISTERED';"
    res = cursor.execute(query)
    bills = res.fetchall()
    if len(bills) == 0:
        print("Keine Belege registriert!\n")
        return
    printTable(data=bills, column_names=["Name", "Telefon", "PayPal", "Belegnummer", "Preis", "Datum"])


def printTable(data, column_names):
    table = PrettyTable()
    table.field_names = column_names
    for entry in data:
        table.add_row([*entry])
    print(table)


def responseToBool(rep):
    rep = rep.lower()
    if "n" in rep or len(rep) == 0:
        return False
    return True


def settleAccounts():
    pass
