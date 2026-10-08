(() => {
  const root = document.querySelector('.merch-shop'), key = 'hydepark-merch-cart-v1';
  const sizes = ['S', 'M', 'L', 'XL', 'XXL'];
  const status = document.getElementById('shop-status'), checkout = document.getElementById('checkout');
  const money = value => `${value.toLocaleString('da-DK')} kr.`;
  let cart = [], busy = false;
  try { const saved = JSON.parse(localStorage.getItem(key) || '[]'); if (Array.isArray(saved)) cart = saved.filter(x => x && sizes.includes(x.size) && Number.isInteger(x.quantity) && x.quantity > 0 && x.quantity <= 10).filter((x,i,a) => a.findIndex(y => y.size === x.size) === i); if (cart.reduce((n,x) => n+x.quantity,0)>10) cart=[]; } catch (_) {}
  function render() {
    try { localStorage.setItem(key, JSON.stringify(cart)); } catch (_) {}
    const list = document.getElementById('cart-items'); list.replaceChildren();
    if (!cart.length) { const p = document.createElement('p'); p.textContent = 'Din kurv er tom. Find din størrelse og læg en T-shirt i kurven.'; list.append(p); }
    cart.forEach(item => {
      const row = document.createElement('div'); row.className = 'cart-row';
      const text = document.createElement('p'); text.textContent = `T-shirt · ${item.size} · ${money(item.quantity * 200)}`;
      const actions = document.createElement('div'); actions.className = 'cart-actions';
      [-1, 1].forEach(delta => { const b = document.createElement('button'); b.type = 'button'; b.textContent = delta < 0 ? '−' : '+'; b.setAttribute('aria-label', `${delta < 0 ? 'Færre' : 'Flere'} T-shirts i ${item.size}`); b.disabled = busy; b.onclick = () => { if (delta > 0 && cart.reduce((n,x)=>n+x.quantity,0)>=10) { status.textContent='Maks. 10 T-shirts pr. ordre.'; return; } item.quantity += delta; cart = cart.filter(x=>x.quantity>0); render(); }; actions.append(b); if(delta<0){const span=document.createElement('span');span.textContent=item.quantity;actions.append(span);} });
      const remove = document.createElement('button'); remove.type='button'; remove.textContent='Fjern'; remove.disabled=busy; remove.setAttribute('aria-label', `Fjern T-shirt i ${item.size}`); remove.onclick=()=>{cart=cart.filter(x=>x!==item);render();}; actions.append(remove); row.append(text, actions); list.append(row);
    });
    const subtotal = cart.reduce((n,x)=>n+x.quantity*200,0), shipping = root.dataset.shipping;
    document.getElementById('subtotal').textContent=money(subtotal);
    document.getElementById('total').textContent=shipping === '' && cart.length ? `${money(subtotal)} + fragt` : money(subtotal+(cart.length ? Number(shipping) : 0));
    checkout.disabled = busy || !cart.length || root.dataset.ready !== 'true';
  }
  document.getElementById('product-form').onsubmit = e => { e.preventDefault(); if(busy)return; const size=document.getElementById('size').value, quantity=Number(document.getElementById('quantity').value); if(!sizes.includes(size)||!Number.isInteger(quantity)||quantity<1||cart.reduce((n,x)=>n+x.quantity,0)+quantity>10){status.textContent='Vælg mellem 1 og 10 T-shirts i alt.';return;} const existing=cart.find(x=>x.size===size);if(existing)existing.quantity+=quantity;else cart.push({size,quantity});render();status.textContent=`T-shirt i ${size} er lagt i kurven.`; };
  checkout.onclick = async () => { busy=true;render();status.textContent='Åbner sikker betaling…';try{const response=await fetch('/shop/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({items:cart})});const result=await response.json();if(!response.ok)throw new Error(result.error||'Betaling kunne ikke startes.');const target=new URL(result.url);if(target.protocol!=='https:'||target.hostname!=='checkout.stripe.com')throw new Error('Ugyldig betalingsadresse.');window.location.assign(target.href);}catch(error){status.textContent=error.message;busy=false;render();}};
  render();
})();
