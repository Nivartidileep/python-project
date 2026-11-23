# Banking Transaction Management System

## Project Overview

The **Banking Transaction Management System** is a Core Python console application that simulates basic banking operations. The system allows customers to create bank accounts and perform operations such as deposits, withdrawals, fund transfers, balance enquiries, transaction history lookups, and simulated account closures. The project demonstrates Python fundamentals, functions, Object-Oriented Programming (OOP), exception handling, data validation, and JSON-based TXT file handling.

---

## Problem Statement

Banks manage multiple customers and account operations such as deposits, withdrawals, fund transfers, and balance checks. The objective of this project is to build a reliable Python banking application that performs these operations with strict validation, minimum-balance enforcement, and safe file persistence.

---

## Objectives

- Register customers and create bank accounts.
- Deposit and withdraw money with input and balance validation.
- Transfer funds safely between active accounts.
- Check current account balances and status.
- Enforce a minimum balance of `₹500.00` consistently across transactions and loaded records.
- Display timestamped transaction histories.
- Close accounts after user confirmation by simulating the settlement of any remaining balance.
- Store account records safely in a JSON-formatted TXT file (`bank_records.txt`).
- Apply Core Python and OOP concepts in a practical, maintainable project.

---

## Features

1. **Customer Registration**: Accepts Customer ID, Customer Name, 10-digit Phone Number, and numeric Account Number, validating format and uniqueness before creating an account.
2. **Account Creation**: Opens a new active account with a simulated initial minimum balance of `₹500.00`.
3. **Deposit**: Adds funds to an active account while rejecting zero, negative, non-numeric, or excessively large amounts.
4. **Withdrawal**: Deducts funds from an active account after verifying the amount is positive and the remaining balance stays at or above `₹500.00`.
5. **Fund Transfer**: Transfers funds between two distinct active accounts while preserving their combined balance and maintaining the `₹500.00` minimum balance on the sender's account.
6. **Balance Enquiry**: Displays the account holder's name, current status (`ACTIVE` or `CLOSED`), and available balance.
7. **Transaction History**: Records and displays timestamped logs for account opening, deposits, withdrawals, sent/received transfers, simulated closure settlement, and account closure.
8. **Simulated Account Closure**: Prompts for confirmation, **simulates** settling any remaining balance (no real payout occurs), resets the balance to `₹0.00`, and marks the account status as `closed`.
9. **Safe File Handling**: Loads records from `bank_records.txt` at startup with strict type and minimum-balance validation, and writes updates atomically using a temporary file.

---

## Technologies & Modules Used

- **Python 3.x** (Core Python, Object-Oriented Programming, Exception Handling)
- **JSON & File Handling** (`bank_records.txt`)

```python
import copy
import json
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
```

### Python Concepts Used

- **Variables & Data Types**: Stores customer details, account numbers, `Decimal` monetary amounts, and status flags.
- **Operators**: Arithmetic and comparison operators perform exact monetary calculations and balance checks.
- **Conditional Statements & Loops**: `if`/`elif`/`else` statements validate inputs, while a `while` loop drives the interactive menu.
- **Collections**: Dictionaries map account numbers to `Account` objects; lists store transaction logs.
- **Classes, Inheritance & Encapsulation**: `Account` inherits from `Customer` and protects balance state via a private attribute (`self.__balance`).
- **Exception Handling**: `try`, `except`, and `raise` catch invalid inputs, business-rule violations, and file I/O errors with automatic rollback.

---

## Project Structure

```text
Banking-Transaction-Management-System/
├── .gitignore
├── project.py
├── test_project.py
└── README.md
```

### File Description

| File | Description |
| :--- | :--- |
| `project.py` | Main Python banking application |
| `test_project.py` | Automated unit tests for transactions, validation, closure, and persistence |
| `README.md` | Project documentation and usage guide |
| `.gitignore` | Excludes runtime data (`bank_records.txt`), temp files, and Python cache files |

> **Note:** `bank_records.txt` is generated automatically at runtime to store account data. Do not commit real customer or financial information to version control.

---

## How to Run the Project

### Step 1: Install Python

Ensure **Python 3.x** is installed on your system.

### Step 2: Clone the Repository

```bash
git clone https://github.com/your-username/Banking-Transaction-Management-System.git
```

### Step 3: Open the Project Folder

```bash
cd Banking-Transaction-Management-System
```

### Step 4: Run the Application

```bash
python project.py
```

### Step 5: Run the Test Suite

```bash
python -m unittest discover -v
```

---

## Main Menu

```text
===== BANKING MANAGEMENT SYSTEM =====
1. Customer Registration / Account Creation
2. Deposit
3. Withdrawal
4. Fund Transfer
5. Balance Enquiry
6. Transaction History
7. Account Closure
8. Exit
```

---

## Sample Workflow

1. **Create Account**
   - Customer ID: `C101` | Name: `Dileep` | Phone: `9876543210` | Account Number: `1001`
   - *Output:* `Customer registered and account created.` (Initial simulated balance: `Rs.500.00`)
2. **Deposit**
   - Account Number: `1001` | Deposit Amount: `Rs.1000`
   - *Output:* `Deposit successful.`
3. **Balance Enquiry**
   - Account Number: `1001`
   - *Output:* `Account holder: Dileep` | `Status: ACTIVE` | `Available balance: Rs. 1500.00`
4. **Withdrawal**
   - Account Number: `1001` | Withdrawal Amount: `Rs.200`
   - *Output:* `Withdrawal successful.` (Remaining balance: `Rs.1300.00`)
5. **Fund Transfer**
   - Transfer funds from `1001` to a second account (e.g., `1002`), updating both balances and recording entries in both transaction histories.
6. **Account Closure**
   - Account Number: `1001` -> Confirm (`y`)
   - *Output:* Simulates settling `Rs.1300.00`, sets balance to `Rs.0.00`, and marks account `1001` as `CLOSED`.

---

## Validation and Exception Handling

The system validates inputs and protects stored data against:

- Missing, `null`, or non-string identity fields in saved records
- Duplicate account numbers or duplicate customer IDs
- Invalid 10-digit phone numbers or non-numeric account numbers
- Zero, negative, `NaN`, `Infinity`, or excessively large monetary amounts
- Withdrawals or transfers that drop an active account below `₹500.00`
- Saved active records with balances below `₹500.00` (rejected without altering the file)
- Transfers to the same account or operations on `closed` accounts
- Failed disk writes (automatically rolls back in-memory state)

---

## Test Cases

| Test Case | Input / Situation | Expected Result |
| :--- | :--- | :--- |
| **TC01** | Valid customer registration | Account created with simulated `₹500.00` balance |
| **TC02** | Duplicate account number or customer ID | Registration rejected |
| **TC03** | Deposit `₹1,000.00` into active account | Balance increases by exact `₹1,000.00` |
| **TC04** | Deposit zero or negative amount | Transaction rejected |
| **TC05** | Withdraw valid amount keeping `>= ₹500.00` | Balance decreases by exact withdrawal amount |
| **TC06** | Withdraw amount exceeding available funds | Transaction rejected |
| **TC07** | Withdraw amount dropping balance below `₹500.00` | Minimum-balance violation; transaction rejected |
| **TC08** | Valid fund transfer between two accounts | Sender & receiver updated; combined balance unchanged |
| **TC09** | Transfer to the same account | Transaction rejected |
| **TC10** | Balance enquiry | Displays holder name, status, and exact balance |
| **TC11** | Transaction history lookup | Displays all timestamped account events |
| **TC12** | Close active account and cancel confirmation (`n`) | Closure cancelled; account remains active |
| **TC13** | Close active account and confirm (`y`) | Remaining balance settlement simulated, balance set to `₹0.00`, account marked `closed` |
| **TC14** | Restart application with valid `bank_records.txt` | Saved accounts, balances, and histories restored |
| **TC15** | Load record with `null` identity or active balance `< ₹500.00` | Load rejected; original file preserved and writes paused |

---

## OOP Design

```text
Customer
 ├── customer_id
 ├── name
 └── phone
      ▲
      │ (inherits)
   Account
    ├── account_number
    ├── __balance (private Decimal)
    ├── status ("active" | "closed")
    └── transactions (list[str])
```

- **`Customer`**: Stores core customer identity attributes.
- **`Account`**: Inherits from `Customer` and encapsulates deposit, withdrawal, transfer, transaction logging, and simulated closure logic.
- **`BankingSystem`**: Manages the collection of accounts, input prompts, record validation, atomic JSON persistence, and the CLI menu.

---

## GitHub Commit Strategy

```bash
git init
git add .gitignore README.md
git commit -m "Add project documentation and gitignore"

git add project.py
git commit -m "Add banking management system with Decimal precision and validation"

git add test_project.py
git commit -m "Add unit tests for transactions, closure, and persistence"

git branch -M main
git remote add origin https://github.com/your-username/Banking-Transaction-Management-System.git
git push -u origin main
```

---

## Future Enhancements

- User authentication and password hashing
- Role-based admin dashboard
- Database storage (SQLite / PostgreSQL / MySQL)
- Savings vs. Current account types with interest calculation
- Exportable PDF/CSV account statements

---

## Conclusion

The Banking Transaction Management System demonstrates how Core Python and Object-Oriented Programming can be combined to build a clean, reliable console application with strict input validation, exact `Decimal` accounting, simulated account settlement, and safe file persistence.