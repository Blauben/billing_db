from controller import *


def print_help():
    help_str = """
    add_user - Fügt einen neuen Benutzer hinzu
    exit - Beende das Skript
    payout_bill - Zahle Geld an einen Bewohner aus
    print_all_bills - Gebe alle Belege aus
    print_pending_bills - Gebe alle unbeglichenen Belege aus
    print_users - Gebe alle Benutzer aus
    register_bill - Fügt einen neuen Beleg hinzu
    settle_accounts - Berechne Ausgleichszahlungen
    """
    print(help_str)


def run():
    print_help()
    while True:
        command = input("> ")
        if "exit" in command:
            break
        elif "help" in command:
            print_help()
        elif "add_user" in command:
            addUser()
        elif "register_bill" in command:
            registerBill()
        elif "payout_bill" in command:
            payoutBill()
        elif "settle_accounts" in command:
            settleAccounts()
        elif "print_all_bills" in command:
            print_bills(only_pending=False)
        elif "print_pending_bills" in command:
            print_bills(only_pending=True)
        elif "print_users" in command:
            printResidents()
        else:
            print(f"Unbekannter Befehl \"{command}\". Geben Sie \"help\" für eine Liste von Befehlen ein.\n")
