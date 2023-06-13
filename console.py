from controller import *


def print_help():
    help_str = """
    add_user - Fügt einen neuen Benutzer hinzu
    budget_pay - Zahle Bills mit Budget
    charge_budget - Lädt Budget auf
    exit - Beende das Skript
    pay - Pay money or collect money
    print_all_bills - Gebe alle Belege aus
    print_all_payments - Gebe alle Zahlungen aus
    print_budget - Gebe Budget aus
    print_pending_bills - Gebe alle unbeglichenen Belege aus
    print_pending_payments - Gebe alle austehenden Zahlungen aus
    print_users - Gebe alle Benutzer aus
    register_bill - Fügt einen neuen Beleg hinzu
    settle_accounts - Berechne Ausgleichszahlungen
    
    Kurzformen (Anfangsbuchstaben) sind erlaubt.
    """
    print(help_str)


def run():
    print_help()
    while True:
        command = input("> ")
        if "exit" == command:
            break
        elif "help" == command:
            print_help()
        elif "add_user" == command or "au" == command:
            addUser()
        elif "register_bill" == command or "rb" == command:
            registerBill()
        elif "print_pending_payments" == command or "ppp" == command:
            print_payments(only_pending=True)
        elif "print_all_payments" == command or "pap" == command:
            print_payments(only_pending=False)
        elif "settle_accounts" == command or "sa" == command:
            settleAccounts()
        elif "print_all_bills" == command or "pab" == command:
            print_bills(only_pending=False)
        elif "print_pending_bills" == command or "ppb" == command:
            print_bills(only_pending=True)
        elif "print_users" == command or "pu" == command:
            printResidents()
        elif "pay" == command or "p" == command:
            pay()
        elif "charge_budget" == command or "cb" == command:
            charge_budget()
        elif "print_budget" == command or "pb" == command:
            print_budget()
        elif "budget_pay" == command or "bp" == command:
            budget_pay()
        else:
            print(f"Unbekannter Befehl \"{command}\". Geben Sie \"help\" für eine Liste von Befehlen ein.\n")
