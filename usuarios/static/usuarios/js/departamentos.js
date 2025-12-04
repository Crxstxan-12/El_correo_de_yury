document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('filtersForm');
  if (!form) return;

  const debounce = (fn, ms = 500) => {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  };

  const qInput = form.querySelector('input[name="q"]');
  if (qInput) qInput.addEventListener('input', debounce(() => form.submit()));

  ['area','order'].forEach(name => {
    const sel = form.querySelector(`select[name="${name}"]`);
    if (sel) sel.addEventListener('change', () => form.submit());
  });
});