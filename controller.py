import os
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
    res = cursor.execute("SELECT * FROM resident;")
    residents = []
    resTuple = res.fetchone()
    while resTuple is not None:
        residents.append(Resident(*resTuple))
        resTuple = res.fetchone()
    return residents


def fetch_current_period():
    res = cursor.execute("SELECT MAX(number) FROM accounting_periods;")
    return res.fetchone()[0]


def finish_current_period():
    period = fetch_current_period()
    cursor.execute("UPDATE accounting_periods SET end = current_timestamp WHERE number = ?;", [period])
    cursor.execute("INSERT INTO accounting_periods(number) VALUES(?)", [period + 1])
    connection.commit()


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
    cursor.execute("INSERT INTO bills(buyer_id, amount, accounting_period) VALUES(?,?,?);",
                   [rID, amount, fetch_current_period()])
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


def print_bills(only_pending):
    query = "SELECT r.name, r.phoneNumber, COALESCE(r.paypal, 'None'), b.id, b.amount, b.added FROM bills b, " \
            "resident r WHERE r.id = b.buyer_id;"
    if only_pending:
        query = f"{query[:-1]} AND b.status = 'REGISTERED';"
    res = cursor.execute(query)
    bills = res.fetchall()
    if len(bills) == 0:
        print("Keine Belege registriert!\n")
        return
    printTable(data=bills, column_names=["Name", "Telefon", "PayPal", "Belegnummer", "Preis", "Datum"])


def print_payments(only_pending):
    query = "SELECT r.name, r.phoneNumber, COALESCE(r.paypal, 'None'),p.id, p.amount FROM resident r, payments p WHERE\
      r.id = p.resident_id;"
    if only_pending:
        query = f"{query[:-1]} AND p.status = 'PENDING';"
    res = cursor.execute(query)
    payments = res.fetchall()
    if len(payments) == 0:
        print("Keine Ausstehenden Zahlungen, bitte fügen Sie neue Belege hinzu und halten Sie ein Abrechnungs "
              "Meeting!\n")
        return 0
    printTable(data=payments, column_names=["Name", "Telefon", "PayPal", "Payment ID","Preis"])
    return len(payments)


def printTable(data, column_names):
    table = PrettyTable()
    table.field_names = column_names
    for entry in data:
        table.add_row([*entry])
    print(table)


def fetch_pending_bills():
    query = "SELECT r.id, b.amount FROM bills b, resident r WHERE r.id = b.buyer_id AND b.status = 'REGISTERED';"
    res = cursor.execute(query)
    return res.fetchall()


def calculate_resident_expenses():
    bills = fetch_pending_bills()
    resident_expenses = {}
    total = 0.0
    for bill in bills:
        total = total + bill[1]
        if bill[0] in resident_expenses.keys():
            prev = resident_expenses[bill[0]]
            after = prev + bill[1]
            resident_expenses.update({bill[0]: after})
        else:
            resident_expenses[bill[0]] = bill[1]
    return total, resident_expenses


def settleAccounts():
    period = fetch_current_period()
    residents = loadResidents()
    total, resident_expenses = calculate_resident_expenses()

    default_share = round(total / len(residents), 2)

    for resident in residents:
        try:
            expenses = resident_expenses[resident.rID]
        except KeyError:
            expenses = 0.0

        amount = expenses - default_share
        if amount == 0.0:
            continue
        query = "INSERT INTO payments(resident_id,accounting_period,amount) VALUES(?,?,?)"
        cursor.execute(query, [resident.rID, period, amount])
    cursor.execute("UPDATE bills SET status = 'PROCESSED'")
    connection.commit()
    finish_current_period()


def pay():
    if print_payments(only_pending=True) == 0:
        return
    id_string = input("Payment ID?: ")
    ids = id_string.split(" ")
    for id_ in ids:
        details = input(f"Transaktionsdetails für PaymentID {id_}?:\n")
        cursor.execute("UPDATE payments SET status = 'PAID', transaction_details = ? WHERE id = ?", [details,id_])
    connection.commit()
