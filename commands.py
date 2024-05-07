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

    def help_arg_present(self):
        if "help" in [k.replace("-", "").lower() for k in self.args]:
            self.command_help()
            return True

    @abstractmethod
    def command_help(self):
        return


class Exit(Command):
    def execute_command(self):
        sys.exit(0)


class Help(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
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
        if self.help_arg_present():
            return
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
        if self.help_arg_present():
            return
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


class RegisterBill(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        if len(self.args) == 0:
            connector.printUsers()
            self.args.extend([input("\nBewohner Nummer eingeben: "), input("Betrag eingeben: ")])
        if len(self.args) == 2:
            connector.registerBill(*self.args)
        else:
            self.command_help()

    def command_help(self):
        print("register_bill - Usage: register_bill <UID> <Betrag>\n")


class PrintPendingPayments(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        connector.print_payments(only_pending=True)

    def command_help(self):
        print("print_all_payments - Gebe alle unbezahlten Zahlungen aus. Keine Argumente notwendig.\n")


class PrintAllPayments(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        connector.print_payments(only_pending=False)

    def command_help(self):
        print("print_all_payments - Gebe alle Zahlungen aus.")


class SettleAccounts(Command):  # TODO refactor using Graph Theory!
    def execute_command(self):
        if self.help_arg_present():
            return
        connector.settleAccounts()


class PrintAllBills(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        connector.print_bills(only_pending=False)

    def command_help(self):
        print("print_all_bills - Gebe alle Belege aus.")


class PrintPendingBills(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        connector.print_bills(only_pending=True)

    def command_help(self):
        print("print_pending_bills - Gebe alle unbeglichenen Belege aus.")


class PrintUsers(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        connector.printUsers()

    def command_help(self):
        print("print_users - Gibt alle rregistrierten User aus.\n")


class Pay(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        if len(self.args) % 2 == 0:
            ids = self.args[:len(self.args) / 2]
            details = self.args[len(self.args) / 2:]
            connector.pay(ids, details) if len(ids) == len(details) else print(
                "Error: Unterschiedliche Anzahl an IDs und Details!")
            return
        ids = input("Payment ID? (Leerzeichen getrennte Liste erlaubt): ").split(" ")
        details = []
        for i in range(len(ids)):
            detail = input(f"Transaktionsdetails für PaymentID {ids[i]}?: (Drücke nur ENTER zum Abbrechen)\n")
            if detail == "":
                ids.pop(i)
            else:
                details.append(detail)
        connector.pay(ids, details)

    def command_help(self):
        print(
            "pay - Usage: <ID_List> <Details_List>. Gleiche Anzahl von IDs und details gefordert, jeweils getrennt durch Leerzeichen.\n")


class ChargeBudget(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        if len(self.args) == 0:
            self.args.append(float(input("Budget Aufladung?: ")))
        if len(self.args) == 1:
            connector.charge_budget(*self.args)
        else:
            self.command_help()

    def command_help(self):
        print("charge_budget - Usage: charge_budget <Amount> . Lädt das Budget um <Amount> Euro.\n")


class PrintBudget(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        connector.print_budget()

    def command_help(self):
        print("print_budget - Gibt das aktuelle Budget aus.")


class BudgetPay(Command):
    def execute_command(self):
        if self.help_arg_present():
            return
        connector.budget_pay()

    def command_help(self):
        print(
            "budget_pay - Begleicht alle möglichen Belege mit dem aktuellen Budget und fügt sie als Zahlungen hinzu.\n")
