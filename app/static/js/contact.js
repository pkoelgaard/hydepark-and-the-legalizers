const form = document.querySelector('#booking-form');
form.addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(form);
  document.querySelector('#request-text').value = `Bookingforespørgsel\n\nNavn: ${data.get('name')}\nE-mail: ${data.get('email')}\nArrangement: ${data.get('event')}\nDato: ${data.get('date') || 'Efter aftale'}\n\n${data.get('message')}`;
  document.querySelector('#prepared').hidden = false;
  document.querySelector('#request-text').focus();
});
document.querySelector('#copy-request').addEventListener('click', async () => {
  const field = document.querySelector('#request-text');
  try { await navigator.clipboard.writeText(field.value); document.querySelector('#copy-status').textContent = 'Teksten er kopieret. Send den via Messenger.'; }
  catch { field.focus(); field.select(); document.querySelector('#copy-status').textContent = 'Markér og kopiér teksten manuelt.'; }
});
