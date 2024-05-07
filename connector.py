import math
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
    contact: str

    def __init__(self, rID, name=None, phone=None, contact=None):
        self.rID = rID
        self.name = name if name != "" else None
        self.phone = phone if phone != "" else None
        self.contact = contact if contact != "" else None

    def __str__(self):
        return f"(Name={self.name}, Telefon={self.phone}, Kontakt={self.contact})"

    def tuple(self):
        return self.rID, self.name, self.phone, self.contact


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
        cursor.execute("pragma foreign_keys = ON")
        connection.commit()


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


def fetchImage():
    pictureFound = False
    imPath = ""
    imPathList = []
    while not pictureFound:
        input("Beleg kopieren... ENTER um fortzufahren")
        imPathList = ImageGrab.grabclipboard()
        if imPathList is None or isinstance(imPathList, list) and len(imPathList) == 0:
            continue
        imPath = imPathList[0] if isinstance(imPathList, list) else imPathList
        try:
            im = Image.open(imPath)
            pictureFound = True
        except Exception:
            return imPath
    return im


def addBill(rID, amount):
    cursor.execute("INSERT INTO bills(buyer_id, amount, accounting_period) VALUES(?,?,?);",
                   [rID, amount, fetch_current_period()])
    connection.commit()
    res = cursor.execute("SELECT last_insert_rowid() FROM bills;")
    bill_id = res.fetchone()[0]
    return bill_id


def addUser(name, phone, contact):
    cursor.execute("INSERT INTO resident VALUES(NULL,?,?,?)", [name, phone, contact])
    connection.commit()
    print("ERFOLGREICH\n")


def deleteUser(uid):
    cursor.execute(
        "DELETE FROM resident WHERE id=? AND NOT EXISTS (SELECT * FROM payments p WHERE p.status='PENDING' AND p.resident_id = ?);",
        [uid, uid])
    connection.commit()


def printUsers():
    residents = loadResidents()
    residentData = list(map(lambda r: r.tuple(), residents))
    printTable(data=residentData, column_names=["Bewohnernummer", "Name", "Telefon", "Kontakt"])


def registerBill(index, amount):
    image = fetchImage()
    bill_id = addBill(index, amount)
    image.save(f"bills/{bill_id}.{image.format}")
    print("ERFOLGREICH\n")


def print_bills(only_pending):
    registered_condition = " WHERE b.status = 'REGISTERED'"
    query = f"SELECT COALESCE(r.name, 'Deleted'), COALESCE(r.phoneNumber, 'Deleted'), COALESCE(r.contact, 'None'), b.id, b.amount, b.added, b.accounting_period FROM bills b LEFT JOIN resident r ON b.buyer_id = r.id {registered_condition if only_pending else ''};"
    res = cursor.execute(query)
    bills = res.fetchall()
    if len(bills) == 0:
        print("Keine Belege registriert!\n")
        return
    cnames = ["Name", "Telefon", "Kontakt", "Belegnummer", "Preis", "Datum", "Zahlperiode"]
    printTable(data=bills, column_names=cnames)


def print_payments(only_pending):
    registered_condition = " WHERE p.status = 'PENDING'"
    details_attribute = ", COALESCE(p.transaction_details, 'Unpaid')"
    query = f"SELECT COALESCE(r.name, 'Deleted'), p.id, COALESCE(r.phoneNumber, 'Deleted'), COALESCE(r.contact, 'None'), p.amount, p.accounting_period, p.date {'' if only_pending else details_attribute} FROM payments p LEFT JOIN resident r ON p.resident_id = r.id {registered_condition if only_pending else ''};"
    res = cursor.execute(query)
    payments = res.fetchall()
    if len(payments) == 0:
        print(
            "Keine Ausstehenden Zahlungen, bitte fügen Sie neue Belege hinzu und halten Sie ein Abrechnungs Meeting!\n")
        return 0
    cnames = ["Name", "Payment ID", "Telefon", "Kontakt", "Preis", "Zahlperiode", "Datum"]
    if not only_pending:
        cnames.append("Transaktions Details")
    printTable(data=payments, column_names=cnames)
    return len(payments)


def printTable(data, column_names):
    table = PrettyTable()
    table.field_names = column_names
    for entry in data:
        table.add_row([*entry])
    print(table)


def fetch_pending_bills():
    query = "SELECT r.id, b.amount, b.id FROM bills b, resident r WHERE r.id = b.buyer_id AND b.status = 'REGISTERED';"
    res = cursor.execute(query)
    return res.fetchall()


def calculate_resident_expenses():
    bills = fetch_pending_bills()
    resident_expenses = {}
    total = 0.0
    for bill in bills:
        total = total + bill[1]
        resident_expenses = insert_addto_map(resident_expenses, bill[0], bill[1])
    return total, resident_expenses


def insert_addto_map(data_map, key, value):
    if key in data_map.keys():
        prev = data_map[key]
        after = prev + value
        data_map.update({key: after})
    else:
        data_map[key] = value
    return data_map


def settleAccounts():
    period = fetch_current_period()
    residents = loadResidents()
    total, resident_expenses = calculate_resident_expenses()

    default_share = total / len(residents)

    for resident in residents:
        try:
            expenses = resident_expenses[resident.rID]
        except KeyError:
            expenses = 0.0

        amount = expenses - default_share
        if amount == 0.0:
            continue
        query = "INSERT INTO payments(resident_id,accounting_period,amount) VALUES(?,?,?)"
        cursor.execute(query, [resident.rID, period, round_half_up(amount)])
    cursor.execute("UPDATE bills SET status = 'PROCESSED'")
    connection.commit()
    finish_current_period()


def pay(ids, details):
    if print_payments(only_pending=True) == 0:
        return
    assert len(ids) == len(details)

    for idx in range(len(ids)):
        cursor.execute(
            "UPDATE payments SET status = 'PAID', transaction_details = ?, date = current_timestamp WHERE id = ?",
            [details[idx], ids[idx]])
    connection.commit()


def charge_budget(charge):
    print("\n")
    residents = loadResidents()
    res = cursor.execute("SELECT balance FROM budget")
    current = res.fetchone()[0]
    current = round_half_up(current + charge)
    cursor.execute("UPDATE budget set balance = ?", [current])

    share = charge / len(residents)
    for resident in residents:
        cursor.execute("INSERT INTO payments(resident_id, accounting_period, amount) VALUES(?,?,?)",
                       [resident.rID, 0, round_half_up(share * -1)])
    connection.commit()


def fetch_budget():
    res = cursor.execute("SELECT balance FROM budget")
    return res.fetchone()[0]


def print_budget():
    print(f"Budget: {fetch_budget()}\n")


def budget_pay():
    changes = False
    resident_expenses = {}
    bills = fetch_pending_bills()
    for bill in bills:
        budget = fetch_budget()
        if bill[1] > budget:
            continue
        else:
            changes = True
            cursor.execute("UPDATE budget set balance = ?", [round_half_up(budget - bill[1])])
            cursor.execute("UPDATE bills SET status = 'PROCESSED' WHERE id = ?", [bill[2]])
            cursor.execute("UPDATE bills SET accounting_period = 0 WHERE id = ?", [bill[2]])
            resident_expenses = insert_addto_map(resident_expenses, bill[0], bill[1])
            connection.commit()
    for rid, amount in resident_expenses.items():
        cursor.execute("INSERT INTO payments(resident_id, accounting_period, amount) VALUES(?,0,?);",
                       [rid, round_half_up(amount)])
        connection.commit()

    if changes:
        print("ZAHLUNGEN ERFOLGREICH HINZUGEFÜGT")


def round_half_up(n, decimals=2):
    sign = abs(n) / n
    multiplier = 10 ** decimals
    return math.floor(abs(n) * multiplier + 0.5) / multiplier * sign
