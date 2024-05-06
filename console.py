from commands import *


def run():
    Help().execute_command()
    while True:
        command = input("> ").split(" ")
        args = command[1:] if len(command) > 0 else []
        if "exit" == command[0]:
            Exit(args).execute_command()
        elif "help" == command[0]:
            Help(args).execute_command()
        elif "add_user" == command or "au" == command[0]:
            AddUser(args).execute_command()
        elif "delete_user" == command or "du" == command[0]:
            DeleteUser(args).execute_command()
        elif "register_bill" == command or "rb" == command[0]:
            RegisterBill(args).execute_command()
        elif "print_pending_payments" == command or "ppp" == command[0]:
            PrintPendingPayments(args).execute_command()
        elif "print_all_payments" == command or "pap" == command[0]:
            PrintAllPayments(args).execute_command()
        elif "settle_accounts" == command or "sa" == command[0]:
            SettleAccounts(args).execute_command()
        elif "print_all_bills" == command or "pab" == command[0]:
            PrintAllBills(args).execute_command()
        elif "print_pending_bills" == command or "ppb" == command[0]:
            PrintPendingBills(args).execute_command()
        elif "print_users" == command or "pu" == command[0]:
            PrintUsers(args).execute_command()
        elif "pay" == command or "p" == command[0]:
            Pay(args).execute_command()
        elif "charge_budget" == command or "cb" == command[0]:
            ChargeBudget(args).execute_command()
        elif "print_budget" == command or "pb" == command[0]:
            PrintBudget(args).execute_command()
        elif "budget_pay" == command or "bp" == command[0]:
            BudgetPay(args).execute_command()
        else:
            print(f"Unbekannter Befehl \"{command}\". Geben Sie \"help\" für eine Liste von Befehlen ein.\n")
