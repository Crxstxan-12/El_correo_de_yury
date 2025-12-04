document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('filtersForm');
  if (!form) return;

  const debounce = (fn, ms = 500) => {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  };

  const qInput = form.querySelector('input[name="q"]');
  if (qInput) qInput.addEventListener('input', debounce(() => form.submit()));

  const orderSel = form.querySelector('select[name="order"]');
  if (orderSel) orderSel.addEventListener('change', () => form.submit());
});