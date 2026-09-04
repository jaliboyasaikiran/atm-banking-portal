from datetime import date, datetime


def Atm_machine():
    balance = 10000
    card_number = "8328679614"
    atm_pin = "1234"
    attempts = 5
    daily_limit = 20000
    daily_withdrawal = 0
    atm_notes = {2000: 1000, 500: 1000, 200: 500, 100: 500}
    transactions = []

    while attempts > 0:
        entered_card = input("Enter card number: ").replace(" ", "")
        entered_pin = input("Enter PIN: ")

        if entered_card == card_number and entered_pin == atm_pin:
            break

        attempts -= 1
        print(f"Incorrect card number or PIN. Attempts remaining: {attempts}")

    if attempts == 0:
        print("Too many incorrect attempts. Please take your card.")
        return

    while True:
        print("\n------------ menu ------------")
        print("1. Check balance")
        print("2. Withdraw")
        print("3. Deposit")
        print("4. Mini statement")
        print("5. Change PIN")
        print("6. Exit")
        print("------------------------------")

        try:
            choice = int(input("Enter the choice: "))
        except ValueError:
            print("Please enter a number from 1 to 6.")
            continue

        if choice == 1:
            print("Your available balance is:", balance)
        elif choice == 2:
            try:
                amount = int(input("Enter the money to withdraw: "))
            except ValueError:
                print("Please enter a valid amount.")
                continue

            if amount < 500 or amount % 100 != 0:
                print("The minimum withdrawal amount is 500.")
            elif amount > balance:
                print("Insufficient balance.")
            elif amount > sum(note * count for note, count in atm_notes.items()):
                print("The ATM does not have enough cash.")
            elif amount > daily_limit - daily_withdrawal:
                print(f"Daily withdrawal limit exceeded. Remaining: {daily_limit - daily_withdrawal}")
            else:
                remaining = amount
                dispensed = {}
                for note in sorted(atm_notes, reverse=True):
                    count = min(remaining // note, atm_notes[note])
                    if count:
                        dispensed[note] = count
                        remaining -= note * count
                if remaining:
                    print("The ATM cannot dispense that exact amount.")
                    continue
                balance -= amount
                daily_withdrawal += amount
                for note, count in dispensed.items():
                    atm_notes[note] -= count
                transactions.append(("Withdrawal", amount, balance, datetime.now()))
                notes = ", ".join(f"{count} x ₹{note}" for note, count in dispensed.items())
                print(f"Withdrawal successful ({notes}). Your available balance is:", balance)
        elif choice == 3:
            try:
                amount = int(input("Enter the amount to deposit: "))
            except ValueError:
                print("Please enter a valid amount.")
                continue

            if amount < 500:
                print("The minimum deposit amount is 500.")
            else:
                balance += amount
                transactions.append(("Deposit", amount, balance, datetime.now()))
                print("Deposit successful. Your available balance is:", balance)
        elif choice == 4:
            if not transactions:
                print("No deposits or withdrawals yet.")
            else:
                print("\nRecent transactions:")
                for transaction_type, amount, current_balance, timestamp in transactions[-10:]:
                    print(f"{timestamp:%Y-%m-%d %H:%M} - {transaction_type}: ₹{amount} (Balance: ₹{current_balance})")
        elif choice == 5:
            try:
                current_pin = input("Enter your current PIN: ")
                new_pin = input("Enter your new four-digit PIN: ")
            except ValueError:
                print("PIN must contain numbers only.")
                continue

            if current_pin != atm_pin:
                print("Incorrect current PIN.")
            elif len(new_pin) != 4 or not new_pin.isdigit():
                print("The new PIN must contain four digits.")
            else:
                atm_pin = new_pin
                print("PIN changed successfully.")
        elif choice == 6:
            print("Thank you for visiting. Please take your card.")
            break
        else:
            print("Invalid choice. Please select an option from 1 to 6.")

if __name__ == "__main__":
    try:
        Atm_machine()
    except KeyboardInterrupt:
        print("\nATM session cancelled.")