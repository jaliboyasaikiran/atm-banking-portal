# atm-banking-portal

![ATM banking portal](Screenshot%202026-09-04%20220116.png)

## About the Website

ATM Banking Portal is a browser-based ATM simulation designed around a simple, guided banking experience. Users begin by swiping a virtual card, sign in with a card number and PIN, and then manage their account from a responsive dashboard.

## What Is Included

- Virtual card swipe entry screen
- Card number and four-digit PIN authentication
- Account balance display
- Cash withdrawals with a minimum amount of Rs 500
- Deposit functionality
- Mini statement showing recent transactions
- PIN change workflow
- Logout and return-to-card flow
- Failed-login protection that locks the card after three incorrect attempts
- Daily withdrawal limit of Rs 20,000
- Balance and ATM cash availability checks
- ATM denomination handling for Rs 2,000, Rs 500, Rs 200, and Rs 100 notes
- Clear success and validation messages for each action

## How It Helps

This project demonstrates how a banking workflow can be designed to feel clear and approachable while still enforcing important transaction rules. It helps users understand:

- How a typical ATM interaction moves from authentication to account actions
- How deposits and withdrawals affect the available balance
- How transaction history can provide a quick account summary
- How daily limits, insufficient funds, and ATM cash availability protect transactions
- How failed login attempts and PIN changes support account security

It is also useful as a learning project for practicing frontend interactions, HTTP APIs, form validation, state management, and deployment configuration.

## Technology Used

- **Python 3.12** for the backend server and banking logic
- **Python `http.server`** for serving the application and API endpoints
- **HTML5** for the page structure and accessible forms
- **CSS3** for the responsive SBI-inspired interface and card interaction
- **Vanilla JavaScript** for login, dashboard actions, API requests, and dynamic updates
- **JSON** for communication between the frontend and backend
- **Render** deployment configuration through `render.yaml`

## Demo Login

Use these demo credentials to access the portal:

```text
Card number: 8328679614
PIN: 1234
```

## Running Locally

From the project directory, run:

```bash
python web_app.py
```

Then open [http://localhost:8000](http://localhost:8000) in a browser. The server uses the `PORT` environment variable when one is provided, which makes it suitable for deployment platforms such as Render.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/status` | Returns the current account and ATM status |
| `POST` | `/api/login` | Authenticates a card number and PIN |
| `POST` | `/api/action` | Handles balance, deposit, withdrawal, statement, PIN change, and logout actions |

## Deployment

The included `render.yaml` defines a Python web service named `sbi-atm`:

```text
Build command: python -m py_compile web_app.py
Start command: python web_app.py
```

The repository can be connected to Render as a Blueprint so the service is built and started using this configuration.