import json
import sys
from functools import reduce
import sqlite3
from os.path import exists

from PIL import ImageGrab
from PIL import Image



class Resident:
    name: str
    phone: str
    paypal: str

    def __init__(self, name=None, phone=None, paypal=None):
        self.name = name if name != "" else None
        self.phone = phone if phone != "" else None
        self.paypal = paypal if paypal != "" else None

    def __str__(self):
        return f"(Name={self.name}, Telefon={self.phone}, PayPal={self.paypal})"


def initDatabase():
    if not exists("data.db"):
        open("data.db")

def loadResidents():
    fd = open("residents.json")
    return json.load(fd, object_hook=json2Resident)


def addResident(resident):
    cursor.execute("INSERT INTO resident VALUES(?,?,?)", resident.name, resident.phone, resident.paypal)
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


def addRoutine():
    name = input("Name: ")
    phone = input("Phone: ")
    paypal = input("PayPal: ")
    addResident(Resident(name, phone, paypal))


def main():
    if "add" in (reduce(lambda a1, a2: a1 + a2, sys.argv[1:], "")):
        addRoutine()
        exit(0)
    residents = loadResidents()
    print("Bewohner angeben...\n")
    for i in range(len(residents)):
        print(f"{i}: {residents[i]}")
    index = input("Nummer: ")





if __name__ == "__main__":
    main()
