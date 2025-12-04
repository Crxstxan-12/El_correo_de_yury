document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('filtersForm');
  if (!form) return;

  const debounce = (fn, ms = 500) => {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  };

  // Auto-submit en búsqueda (q) únicamente con debounce
  ['q'].forEach(name => {
    const input = form.querySelector(`input[name="${name}"]`);
    if (input && !input.disabled) {
      input.addEventListener('input', debounce(() => form.submit()));
    }
  });

  // En RUT, enviar solo al presionar Enter para evitar recargas por cada dígito
  const rutInput = form.querySelector('input[name="rut"]');
  if (rutInput && !rutInput.disabled) {
    rutInput.addEventListener('keyup', (e) => {
      if (e.key === 'Enter') form.submit();
    });
  }

  // Auto-submit en selects
  ['area','depto','cargo','order'].forEach(name => {
    const sel = form.querySelector(`select[name="${name}"]`);
    if (sel) sel.addEventListener('change', () => form.submit());
  });
});