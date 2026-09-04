const swipeView = document.querySelector('#swipe-view');
const loginView = document.querySelector('#login-view');
const dashboardView = document.querySelector('#dashboard-view');
const loginForm = document.querySelector('#login-form');
const transactionForm = document.querySelector('#transaction-form');
const pinForm = document.querySelector('#pin-form');
const loginMessage = document.querySelector('#login-message');
const actionMessage = document.querySelector('#action-message');
const balanceElement = document.querySelector('#balance');
const dailyLimitElement = document.querySelector('#daily-limit');
const dailyWithdrawnElement = document.querySelector('#daily-withdrawn');
const atmCashElement = document.querySelector('#atm-cash');
const statementPanel = document.querySelector('#statement-panel');
const statementList = document.querySelector('#statement-list');
let selectedAction = null;

function updateClocks() {
  const currentTime = new Intl.DateTimeFormat('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }).format(new Date());
  document.querySelector('#rail-clock').textContent = currentTime;
  document.querySelector('#machine-clock').textContent = currentTime;
}

updateClocks();
setInterval(updateClocks, 1000);

const bankCard = document.querySelector('#bank-card');
bankCard.addEventListener('pointermove', (event) => {
  if (swipeView.classList.contains('swiped')) return;
  const bounds = bankCard.getBoundingClientRect();
  const rotateX = ((event.clientY - bounds.top) / bounds.height - 0.5) * -12;
  const rotateY = ((event.clientX - bounds.left) / bounds.width - 0.5) * 14;
  bankCard.style.setProperty('--rotate-x', `${rotateX}deg`);
  bankCard.style.setProperty('--rotate-y', `${rotateY}deg`);
});

bankCard.addEventListener('pointerleave', () => {
  bankCard.style.setProperty('--rotate-x', '0deg');
  bankCard.style.setProperty('--rotate-y', '0deg');
});

document.querySelector('#swipe-button').addEventListener('click', () => {
  const swipeButton = document.querySelector('#swipe-button');
  const swipeMessage = document.querySelector('#swipe-message');
  swipeButton.disabled = true;
  swipeView.classList.add('swiped');
  showMessage(swipeMessage, 'Card swiped successfully.');
  setTimeout(() => {
    swipeView.classList.add('hidden');
    loginView.classList.remove('hidden');
    document.querySelector('#pin').focus();
  }, 900);
});

function showMessage(element, text, isError = false) {
  element.textContent = text;
  element.classList.toggle('error', isError);
}

function updateBalance(balance) {
  balanceElement.textContent = `₹${Number(balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
}

function updateStatus(data) {
  updateBalance(data.balance);
  balanceElement.closest('.balance-panel').classList.remove('value-updated');
  requestAnimationFrame(() => balanceElement.closest('.balance-panel').classList.add('value-updated'));
  dailyLimitElement.textContent = `₹${Number(data.daily_limit).toLocaleString('en-IN')}`;
  dailyWithdrawnElement.textContent = `₹${Number(data.daily_withdrawal).toLocaleString('en-IN')}`;
  atmCashElement.textContent = `₹${Number(data.atm_cash).toLocaleString('en-IN')}`;
}

function renderStatement(transactions) {
  statementList.replaceChildren();
  if (!transactions.length) {
    statementList.textContent = 'No deposits or withdrawals yet.';
    return;
  }
  transactions.slice().reverse().forEach((transaction) => {
    const row = document.createElement('div');
    row.className = 'statement-row';
    row.innerHTML = `<span><strong>${transaction.type}</strong><small>${transaction.time}</small></span><span class="statement-amount">${transaction.type === 'Withdrawal' ? '-' : '+'}₹${Number(transaction.amount).toLocaleString('en-IN')}</span>`;
    statementList.appendChild(row);
  });
}

async function request(path, body) {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Something went wrong');
  return data;
}

function setButtonState(button, isBusy) {
  button.disabled = isBusy;
  button.classList.toggle('is-busy', isBusy);
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const submitButton = loginForm.querySelector('button[type="submit"]');
  setButtonState(submitButton, true);
  showMessage(loginMessage, 'Checking PIN...');
  try {
    const data = await request('/api/login', {
      card_number: document.querySelector('#card-number').value,
      pin: document.querySelector('#pin').value
    });
    updateStatus(data);
    loginView.classList.add('hidden');
    dashboardView.classList.remove('hidden');
  } catch (error) {
    showMessage(loginMessage, error.message, true);
  } finally {
    setButtonState(submitButton, false);
  }
});

document.querySelectorAll('.action-card').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.action-card').forEach((card) => card.classList.remove('active'));
    button.classList.add('active');
    selectedAction = button.dataset.action;
    transactionForm.classList.toggle('hidden', !['withdraw', 'deposit'].includes(selectedAction));
    pinForm.classList.toggle('hidden', selectedAction !== 'change-pin');
    statementPanel.classList.toggle('hidden', selectedAction !== 'statement');
    actionMessage.textContent = '';
    if (selectedAction === 'withdraw') {
      document.querySelector('#form-kicker').textContent = 'CASH OUT';
      document.querySelector('#form-title').textContent = 'Withdraw cash';
    } else if (selectedAction === 'deposit') {
      document.querySelector('#form-kicker').textContent = 'CASH IN';
      document.querySelector('#form-title').textContent = 'Deposit funds';
    } else if (selectedAction === 'balance') {
      request('/api/action', { action: 'balance' })
        .then((data) => { updateStatus(data); showMessage(actionMessage, 'Your balance is up to date.'); })
        .catch((error) => showMessage(actionMessage, error.message, true));
    } else if (selectedAction === 'statement') {
      request('/api/action', { action: 'statement' })
        .then((data) => renderStatement(data.transactions))
        .catch((error) => showMessage(actionMessage, error.message, true));
    }
  });
});

transactionForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const submitButton = transactionForm.querySelector('button[type="submit"]');
  setButtonState(submitButton, true);
  const amount = Number(document.querySelector('#amount').value);
  try {
    const data = await request('/api/action', { action: selectedAction, amount });
    updateStatus(data);
    showMessage(actionMessage, `${data.message}.`);
    transactionForm.reset();
  } catch (error) {
    showMessage(actionMessage, error.message, true);
  } finally {
    setButtonState(submitButton, false);
  }
});

pinForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const submitButton = pinForm.querySelector('button[type="submit"]');
  setButtonState(submitButton, true);
  try {
    const data = await request('/api/action', {
      action: 'change_pin',
      current_pin: document.querySelector('#current-pin').value,
      new_pin: document.querySelector('#new-pin').value
    });
    showMessage(actionMessage, `${data.message}.`);
    pinForm.reset();
  } catch (error) {
    showMessage(actionMessage, error.message, true);
  } finally {
    setButtonState(submitButton, false);
  }
});

document.querySelector('#logout-button').addEventListener('click', async () => {
  await request('/api/action', { action: 'logout' });
  dashboardView.classList.add('hidden');
  swipeView.classList.remove('hidden', 'swiped');
  loginView.classList.add('hidden');
  document.querySelector('#swipe-button').disabled = false;
  document.querySelector('#swipe-message').textContent = 'Insert your card, then press swipe.';
  loginForm.reset();
  statementPanel.classList.add('hidden');
});
