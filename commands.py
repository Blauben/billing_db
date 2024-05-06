import sys
from abc import ABC, abstractmethod
import connector


class Command(ABC):
    args: [str]

    def __init__(self, args=None):
        if args is None:
            args = []
        self.args = args

    @abstractmethod
    def execute_command(self):
        return

    @abstractmethod
    def command_help(self):
        return


class Exit(Command):
    def execute_command(self):
        sys.exit(0)


class Help(Command):
    def execute_command(self):
        help_str = """
        add_user - Fügt einen neuen Benutzer hinzu
        budget_pay - Zahle Bills mit Budget
        charge_budget - Lädt Budget auf
        delete_user - Löscht einen existierenden Benutzer (Es dürfen keine ausstehenden Zahlungen zu diesem Nutzer mehr bestehen!)
        exit - Beende das Skript
        pay - Zahle oder erhalte Geld
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

    def command_help(self):
        print("help - Zeigt eine Übersicht von allen möglichen Commands an\n")


class AddUser(Command):

    def execute_command(self):
        if "help" in [k.replace("-", "").lower() for k in self.args]:
            return self.command_help()
        if len(self.args) == 0:
            self.args.extend([input("Name: "), input("Telefon: "), input("Kontakt: ")])
        if len(self.args) == 3:
            connector.addUser(*self.args)
        else:
            self.command_help()

    def command_help(self):
        print("add_user - Usage: add_user <Name> <Telefon> <Kontakt>\n")


class DeleteUser(Command):
    def execute_command(self):
        if "help" in [k.replace("-", "").lower() for k in self.args]:
            return self.command_help()
        if len(self.args) == 0:
            connector.printUsers()
            uid = int(input("\nBewohner Nummer eingeben: "))
            self.args = [uid]
        if len(self.args) == 1:
            connector.deleteUser(*self.args)
        else:
            self.command_help()

    def command_help(self):
        print("delete_user - Usage: delete_user <UID>\n")


class RegisterBill(Command):  # TODO continue here
    def execute_command(self):
        connector.registerBill()


class PrintPendingPayments(Command):
    def execute_command(self):
        connector.print_payments(only_pending=True)


class PrintAllPayments(Command):
    def execute_command(self):
        connector.print_payments(only_pending=False)


class SettleAccounts(Command):
    def execute_command(self):
        connector.settleAccounts()


class PrintAllBills(Command):
    def execute_command(self):
        connector.print_bills(only_pending=False)


class PrintPendingBills(Command):
    def execute_command(self):
        connector.print_bills(only_pending=True)


class PrintUsers(Command):
    def execute_command(self):
        connector.printUsers()


class Pay(Command):
    def execute_command(self):
        connector.pay()


class ChargeBudget(Command):
    def execute_command(self):
        connector.charge_budget()


class PrintBudget(Command):
    def execute_command(self):
        connector.print_budget()


class BudgetPay(Command):
    def execute_command(self):
        connector.pay()
