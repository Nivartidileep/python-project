import copy
import json
import math
import os
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).resolve().with_name("bank_records.txt")
MINIMUM_BALANCE = 500.0


def _clean_amount(amount):
    """Validate that amount is a finite real number (excluding bool) and round to 2 decimals."""
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("Amount must be a valid finite number.")
    value = float(amount)
    if not math.isfinite(value):
        raise ValueError("Amount cannot be NaN or infinite.")
    return round(value, 2)


class Customer:
    def __init__(self, customer_id, name, phone):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone


class Account(Customer):
    def __init__(
        self,
        customer_id,
        name,
        phone,
        account_number,
        balance=MINIMUM_BALANCE,
        status="active",
    ):
        super().__init__(customer_id, name, phone)
        self.account_number = str(account_number)
        self.__balance = _clean_amount(balance)
        self.status = status
        self.transactions = []

    def is_closed(self):
        return self.status == "closed"

    def _ensure_active(self):
        if self.is_closed():
            raise ValueError("Account is closed. Normal operations are not permitted.")

    def get_balance(self):
        return self.__balance

    def add_transaction(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions.append(f"{timestamp} - {message}")

    def deposit(self, amount):
        self._ensure_active()
        clean = _clean_amount(amount)
        if clean <= 0:
            raise ValueError("Amount must be greater than zero.")

        self.__balance = round(self.__balance + clean, 2)
        self.add_transaction(f"Deposited Rs.{clean:.2f}")
        return "Deposit successful."

    def withdraw(self, amount):
        self._ensure_active()
        clean = _clean_amount(amount)
        if clean <= 0:
            raise ValueError("Amount must be greater than zero.")

        if round(self.__balance - clean, 2) < MINIMUM_BALANCE:
            raise ValueError(
                f"Insufficient funds or minimum balance (Rs.{MINIMUM_BALANCE:.2f}) violation."
            )

        self.__balance = round(self.__balance - clean, 2)
        self.add_transaction(f"Withdrawn Rs.{clean:.2f}")
        return "Withdrawal successful."

    def transfer(self, receiver, amount):
        self._ensure_active()
        receiver._ensure_active()

        if receiver.account_number == self.account_number:
            raise ValueError("Cannot transfer to the same account.")

        clean = _clean_amount(amount)
        if clean <= 0:
            raise ValueError("Amount must be greater than zero.")

        if round(self.__balance - clean, 2) < MINIMUM_BALANCE:
            raise ValueError(
                f"Insufficient balance for transfer (minimum Rs.{MINIMUM_BALANCE:.2f} required)."
            )

        self.__balance = round(self.__balance - clean, 2)
        receiver.__balance = round(receiver.__balance + clean, 2)

        self.add_transaction(
            f"Transferred Rs.{clean:.2f} to {receiver.account_number}"
        )
        receiver.add_transaction(
            f"Received Rs.{clean:.2f} from {self.account_number}"
        )
        return "Fund transfer successful."

    def settle_and_close(self):
        self._ensure_active()
        settled_amount = self.__balance
        if settled_amount > 0:
            self.add_transaction(f"Settled remaining balance Rs.{settled_amount:.2f} on closure")
        self.__balance = 0.0
        self.status = "closed"
        self.add_transaction("Account closed")
        return settled_amount

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "phone": self.phone,
            "account_number": self.account_number,
            "balance": self.__balance,
            "status": self.status,
            "transactions": list(self.transactions),
        }


class BankingSystem:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = Path(data_file)
        self.accounts = {}
        self._storage_corrupted = False
        self.load_records()

    @staticmethod
    def _validate_record(record):
        if not isinstance(record, dict):
            raise ValueError("Each account record must be a JSON object.")

        required_keys = {
            "customer_id",
            "name",
            "phone",
            "account_number",
            "balance",
        }
        if not required_keys.issubset(record.keys()):
            raise ValueError("Missing required fields in account record.")

        customer_id = str(record["customer_id"]).strip().upper()
        name = str(record["name"]).strip()
        phone = str(record["phone"]).strip()
        account_number = str(record["account_number"]).strip()
        status = record.get("status", "active")

        if not all([customer_id, name, phone, account_number]):
            raise ValueError("Blank identity fields found in saved record.")

        if not account_number.isdigit():
            raise ValueError("Invalid account number format in saved record.")

        if not (phone.isdigit() and len(phone) == 10):
            raise ValueError("Invalid phone number in saved record.")

        if status not in ("active", "closed"):
            raise ValueError("Invalid account status in saved record.")

        balance = _clean_amount(record["balance"])
        if status == "closed" and balance != 0.0:
            raise ValueError("Closed account must have a zero balance.")
        if status == "active" and balance < 0.0:
            raise ValueError("Active account cannot have a negative balance.")

        transactions = record.get("transactions", [])
        if not isinstance(transactions, list) or not all(
            isinstance(t, str) for t in transactions
        ):
            raise ValueError("Invalid transaction history format in saved record.")

        account = Account(
            customer_id=customer_id,
            name=name,
            phone=phone,
            account_number=account_number,
            balance=balance,
            status=status,
        )
        account.transactions = list(transactions)
        return account

    def load_records(self):
        self._storage_corrupted = False
        if not self.data_file.exists():
            self.accounts = {}
            return

        try:
            raw_text = self.data_file.read_text(encoding="utf-8")
            if not raw_text.strip():
                raise ValueError("Data file is empty.")

            records = json.loads(raw_text)
            if not isinstance(records, list):
                raise ValueError("Top-level JSON must be a list of accounts.")

            staged_accounts = {}
            seen_customer_ids = set()

            for item in records:
                acct = self._validate_record(item)
                if acct.account_number in staged_accounts:
                    raise ValueError(f"Duplicate account number: {acct.account_number}")
                if acct.customer_id in seen_customer_ids:
                    raise ValueError(f"Duplicate customer ID: {acct.customer_id}")

                staged_accounts[acct.account_number] = acct
                seen_customer_ids.add(acct.customer_id)

            self.accounts = staged_accounts
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as err:
            self.accounts = {}
            self._storage_corrupted = True
            print(
                f"Warning: Could not load saved records ({err}). "
                f"Existing file '{self.data_file}' was preserved and writes are paused "
                "until the file is repaired or restored.",
                flush=True,
            )

    def _can_write(self):
        if self._storage_corrupted:
            print(
                "Writes blocked: stored records failed validation on load. "
                f"Fix or restore '{self.data_file}' before making changes.",
                flush=True,
            )
            return False
        return True

    def save_records(self):
        if self._storage_corrupted:
            raise OSError("Refusing to overwrite potentially corrupted record store.")

        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.data_file.with_name(f".{self.data_file.name}.tmp")

        payload = json.dumps(
            [acct.to_dict() for acct in self.accounts.values()],
            indent=4,
            allow_nan=False,
        )

        try:
            temp_file.write_text(payload, encoding="utf-8")
            os.replace(temp_file, self.data_file)
        except Exception:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
            raise

    def _apply_mutation(self, mutate_fn, success_message):
        if not self._can_write():
            return False

        snapshot = copy.deepcopy(self.accounts)
        try:
            result = mutate_fn()
            self.save_records()
            print(success_message if result is None else result, flush=True)
            return True
        except Exception as err:
            self.accounts = snapshot
            if isinstance(err, OSError):
                print(f"Persistence failed; changes were rolled back: {err}", flush=True)
            else:
                print("Error:", err, flush=True)
            return False

    def register_customer(self):
        if not self._can_write():
            return

        customer_id = input("Enter customer ID: ").strip().upper()
        name = input("Enter customer name: ").strip()
        phone = input("Enter phone number: ").strip()
        account_number = input("Create account number (digits only): ").strip()

        if not all([customer_id, name, phone, account_number]):
            print("All fields are required.", flush=True)
            return

        if not account_number.isdigit():
            print("Account number must contain digits only.", flush=True)
            return

        if account_number in self.accounts:
            print("Account number already exists.", flush=True)
            return

        if any(a.customer_id == customer_id for a in self.accounts.values()):
            print("Customer ID already exists.", flush=True)
            return

        if not phone.isdigit() or len(phone) != 10:
            print("Enter a valid 10-digit phone number.", flush=True)
            return

        def _create():
            account = Account(
                customer_id=customer_id,
                name=name,
                phone=phone,
                account_number=account_number,
                balance=MINIMUM_BALANCE,
                status="active",
            )
            account.add_transaction(
                f"Account opened with simulated balance Rs.{MINIMUM_BALANCE:.2f}"
            )
            self.accounts[account_number] = account

        self._apply_mutation(
            _create, "Customer registered and account created."
        )

    def find_account(self):
        number = input("Enter account number: ").strip()
        account = self.accounts.get(number)
        if account is None:
            print("Account not found.", flush=True)
        return account

    def deposit_money(self):
        account = self.find_account()
        if account is None or not self._can_write():
            return

        try:
            raw_amount = input("Enter deposit amount: Rs.").strip()
            amount = float(raw_amount)
        except ValueError:
            print("Error: Invalid numeric amount.", flush=True)
            return

        target = self.accounts[account.account_number]
        self._apply_mutation(lambda: target.deposit(amount), None)

    def withdraw_money(self):
        account = self.find_account()
        if account is None or not self._can_write():
            return

        try:
            raw_amount = input("Enter withdrawal amount: Rs.").strip()
            amount = float(raw_amount)
        except ValueError:
            print("Error: Invalid numeric amount.", flush=True)
            return

        target = self.accounts[account.account_number]
        self._apply_mutation(lambda: target.withdraw(amount), None)

    def transfer_money(self):
        if not self._can_write():
            return

        print("Sender account:", flush=True)
        sender = self.find_account()
        if sender is None:
            return

        print("Receiver account:", flush=True)
        receiver = self.find_account()
        if receiver is None:
            return

        try:
            raw_amount = input("Enter transfer amount: Rs.").strip()
            amount = float(raw_amount)
        except ValueError:
            print("Error: Invalid numeric amount.", flush=True)
            return

        def _do_transfer():
            s_acct = self.accounts[sender.account_number]
            r_acct = self.accounts[receiver.account_number]
            return s_acct.transfer(r_acct, amount)

        self._apply_mutation(_do_transfer, None)

    def balance_enquiry(self):
        account = self.find_account()
        if account:
            print("Account holder:", account.name, flush=True)
            print("Status:", account.status.upper(), flush=True)
            print("Available balance: Rs.", f"{account.get_balance():.2f}", flush=True)

    def transaction_history(self):
        account = self.find_account()
        if account:
            print("\n--- Transaction History ---", flush=True)
            if not account.transactions:
                print("No transactions available.", flush=True)
            for transaction in account.transactions:
                print(transaction, flush=True)

    def close_account(self):
        account = self.find_account()
        if account is None or not self._can_write():
            return

        if account.is_closed():
            print("Account is already closed.", flush=True)
            return

        remaining = account.get_balance()
        print(f"Remaining balance to settle: Rs.{remaining:.2f}", flush=True)
        confirm = input("Confirm account closure and balance settlement? (y/n): ").strip().lower()
        if confirm != "y":
            print("Account closure cancelled.", flush=True)
            return

        def _close():
            target = self.accounts[account.account_number]
            settled = target.settle_and_close()
            return (
                f"Settled Rs.{settled:.2f} and closed account "
                f"{target.account_number} successfully."
            )

        self._apply_mutation(_close, None)

    def run(self):
        while True:
            print("\n===== BANKING MANAGEMENT SYSTEM =====", flush=True)
            print("1. Customer Registration / Account Creation", flush=True)
            print("2. Deposit", flush=True)
            print("3. Withdrawal", flush=True)
            print("4. Fund Transfer", flush=True)
            print("5. Balance Enquiry", flush=True)
            print("6. Transaction History", flush=True)
            print("7. Account Closure", flush=True)
            print("8. Exit", flush=True)

            try:
                choice = input("Enter your choice: ").strip()
            except EOFError:
                print("\nInput stream ended. Exiting.", flush=True)
                break

            try:
                if choice == "1":
                    self.register_customer()
                elif choice == "2":
                    self.deposit_money()
                elif choice == "3":
                    self.withdraw_money()
                elif choice == "4":
                    self.transfer_money()
                elif choice == "5":
                    self.balance_enquiry()
                elif choice == "6":
                    self.transaction_history()
                elif choice == "7":
                    self.close_account()
                elif choice == "8":
                    print("Thank you for using our banking system.", flush=True)
                    break
                else:
                    print("Invalid choice. Select 1 to 8.", flush=True)
            except OSError as error:
                print("File operation failed:", error, flush=True)


if __name__ == "__main__":
    bank = BankingSystem()
    bank.run()
