import json
import os
import sys
from functools import reduce
import sqlite3
from os.path import exists

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


def addResident(resident):
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

def inputAddRoutine():
    name = input("Name: ")
    phone = input("Phone: ")
    paypal = input("PayPal: ")
    addResident(Resident(name, phone, paypal))


def registerBill():
    residents = loadResidents()
    for r in residents:
        print(f"{r.rID}: {r}")
    index = input("\nBewohner Nummer eingeben: ")
    amount = input("Betrag eingeben: ")
    image = fetchImage()
    bill_id = addBill(index, amount)
    image.save(f"bills/{bill_id}.jpg")


def responseToBool(rep):
    rep = rep.lower()
    if "n" in rep or len(rep) == 0:
        return False
    return True


def main():
    initDatabase()
    initFileStructure()
    if "add" in (reduce(lambda a1, a2: a1 + a2, sys.argv[1:], "")):
        inputAddRoutine()
        return

    register_bill = responseToBool(input("Wollen Sie einen neuen Beleg hinzufügen?"))
    if register_bill:
        registerBill()
        return

    lend_money = responseToBool(input("Wollen Sie Geld auslegen?"))
    # TODO continue here


if __name__ == "__main__":
    main()
