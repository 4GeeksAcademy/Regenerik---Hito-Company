const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const downloadBtn = document.getElementById('downloadBtn');
const fileInfo = document.getElementById('fileInfo');
const statusMessage = document.getElementById('statusMessage');
const apiBaseUrlInput = document.getElementById('apiBaseUrl');
const resultsSection = document.getElementById('results');

const kpis = document.getElementById('kpis');
const invalidList = document.getElementById('invalidList');
const satisfaction = document.getElementById('satisfaction');
const categoryTableBody = document.querySelector('#categoryTable tbody');
const statusTableBody = document.querySelector('#statusTable tbody');
const suppliersTableBody = document.querySelector('#suppliersTable tbody');
const suppliersStatus = document.getElementById('suppliersStatus');
const filterCountry = document.getElementById('filterCountry');
const filterCategory = document.getElementById('filterCategory');
const filterStatus = document.getElementById('filterStatus');
const refreshSuppliersBtn = document.getElementById('refreshSuppliersBtn');
const supplierForm = document.getElementById('supplierForm');

let selectedFile = null;

function setStatus(message, type = '') {
  statusMessage.textContent = message;
  statusMessage.className = `status ${type}`.trim();
}

function getApiBase() {
  return apiBaseUrlInput.value.trim().replace(/\/+$/, '');
}

function setSuppliersStatus(message, type = '') {
  suppliersStatus.textContent = message;
  suppliersStatus.className = `status ${type}`.trim();
}

function supplierEndpoint() {
  return `${getApiBase()}/suppliers`;
}

function onFileSelected(file) {
  selectedFile = file;
  analyzeBtn.disabled = false;
  fileInfo.textContent = `Archivo seleccionado: ${file.name} (${Math.round(file.size / 1024)} KB)`;
  setStatus('Archivo listo para analizar.', 'ok');
}

function handleDrop(event) {
  event.preventDefault();
  dropzone.classList.remove('drag-over');
  const [file] = event.dataTransfer.files;
  if (!file) {
    return;
  }
  if (!file.name.toLowerCase().endsWith('.csv')) {
    setStatus('Solo se permiten archivos CSV.', 'error');
    return;
  }
  onFileSelected(file);
}

async function analyzeFile() {
  if (!selectedFile) {
    setStatus('Selecciona un CSV antes de analizar.', 'warn');
    return;
  }

  analyzeBtn.disabled = true;
  setStatus('Analizando archivo...', 'warn');

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const response = await fetch(`${getApiBase()}/api/incidents/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || 'Error desconocido en API');
    }

    const summary = await response.json();
    renderSummary(summary);

    downloadBtn.disabled = false;
    setStatus('Análisis completado correctamente.', 'ok');
  } catch (error) {
    setStatus(`Error: ${error.message}`, 'error');
  } finally {
    analyzeBtn.disabled = false;
  }
}

function renderSummary(summary) {
  const totals = summary.totals;
  const invalid = summary.invalid_breakdown;
  const sat = summary.satisfaction_index;

  resultsSection.classList.remove('hidden');

  kpis.innerHTML = '';
  const cards = [
    ['Total', totals.total_records],
    ['Válidos', totals.valid_records],
    ['Inválidos', totals.invalid_records],
    ['Promedio satisfacción', sat.average_score.toFixed(2)],
  ];
  cards.forEach(([label, value]) => {
    const article = document.createElement('article');
    article.className = 'kpi';
    article.innerHTML = `<p class="label">${label}</p><p class="value">${value}</p>`;
    kpis.appendChild(article);
  });

  invalidList.innerHTML = `
    <li>Falta location_id: <strong>${invalid.missing_location_id}</strong></li>
    <li>Category faltante/inválida: <strong>${invalid.invalid_or_missing_category}</strong></li>
    <li>Description vacía/corta: <strong>${invalid.empty_description}</strong></li>
    <li>CLOSED sin satisfaction_score: <strong>${invalid.closed_without_score}</strong></li>
  `;

  satisfaction.innerHTML = `
    <p>Scored cases: <strong>${sat.scored_cases}</strong> de <strong>${sat.closed_cases}</strong></p>
    <p>Average score: <strong>${sat.average_score.toFixed(2)} / 5.00</strong></p>
    <ul>
      ${sat.distribution.map((item) => `<li>Score ${item.score} (${item.label}): <strong>${item.count}</strong></li>`).join('')}
    </ul>
  `;

  categoryTableBody.innerHTML = summary.breakdown_by_category
    .map(
      (item) => `<tr><td>${item.category}</td><td>${item.count}</td><td>${item.percentage.toFixed(1)}%</td></tr>`
    )
    .join('');

  statusTableBody.innerHTML = summary.breakdown_by_status
    .map(
      (item) => `<tr><td>${item.status}</td><td>${item.count}</td><td>${item.percentage.toFixed(1)}%</td></tr>`
    )
    .join('');

  const totalInvalid =
    invalid.missing_location_id +
    invalid.invalid_or_missing_category +
    invalid.empty_description +
    invalid.closed_without_score;

  if (totalInvalid > 0) {
    setStatus(`Atención: se detectaron ${totals.invalid_records} registros inválidos.`, 'warn');
  }
}

async function downloadResults() {
  try {
    const response = await fetch(`${getApiBase()}/api/incidents/results/export`);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || 'No se pudo descargar');
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'results.csv';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    setStatus('Descarga completada.', 'ok');
  } catch (error) {
    setStatus(`Error al descargar: ${error.message}`, 'error');
  }
}

function buildSupplierQuery() {
  const params = new URLSearchParams();
  if (filterCountry.value) {
    params.set('country', filterCountry.value);
  }
  if (filterCategory.value) {
    params.set('category', filterCategory.value);
  }
  if (filterStatus.value) {
    params.set('status', filterStatus.value);
  }
  const query = params.toString();
  return query ? `?${query}` : '';
}

function statusBadge(status) {
  return `<span class="status-badge ${status}">${status}</span>`;
}

function renderSuppliers(items) {
  suppliersTableBody.innerHTML = items
    .map((supplier) => {
      const nextStatus = supplier.status === 'active' ? 'suspended' : 'active';
      return `
      <tr>
        <td>${supplier.name}</td>
        <td>${supplier.country}</td>
        <td>${supplier.categories.join(', ')}</td>
        <td>${supplier.rate_per_unit}</td>
        <td>${supplier.currency}</td>
        <td>${statusBadge(supplier.status)}</td>
        <td>
          <div class="row-actions">
            <form class="inline-rate" data-action="rate" data-id="${supplier.id}">
              <input name="rate" type="number" min="0.01" step="0.01" value="${supplier.rate_per_unit}" required />
              <button class="btn" type="submit">Tarifa</button>
            </form>
            <button class="btn" data-action="status" data-id="${supplier.id}" data-status="${nextStatus}">
              ${nextStatus === 'active' ? 'Activar' : 'Suspender'}
            </button>
          </div>
        </td>
      </tr>`;
    })
    .join('');
}

async function fetchSuppliers() {
  setSuppliersStatus('Cargando proveedores...', 'warn');
  try {
    const response = await fetch(`${supplierEndpoint()}${buildSupplierQuery()}`);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || 'No se pudo cargar proveedores');
    }
    const payload = await response.json();
    renderSuppliers(payload.items || []);
    setSuppliersStatus(`Listado actualizado. Registros: ${payload.total}.`, 'ok');
  } catch (error) {
    setSuppliersStatus(`Error: ${error.message}`, 'error');
  }
}

async function createSupplier(event) {
  event.preventDefault();

  const formData = new FormData(supplierForm);
  const categories = (formData.get('categories') || '')
    .toString()
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);

  const payload = {
    name: formData.get('name'),
    country: formData.get('country'),
    categories,
    rate_per_unit: Number(formData.get('rate_per_unit')),
    currency: formData.get('currency'),
    status: formData.get('status'),
    contact_email: (formData.get('contact_email') || '').toString().trim() || null,
    notes: (formData.get('notes') || '').toString().trim() || null,
  };

  setSuppliersStatus('Creando proveedor...', 'warn');
  try {
    const response = await fetch(supplierEndpoint(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail ? JSON.stringify(err.detail) : 'Datos invalidos');
    }

    supplierForm.reset();
    setSuppliersStatus('Proveedor registrado correctamente.', 'ok');
    await fetchSuppliers();
  } catch (error) {
    setSuppliersStatus(`Error al crear proveedor: ${error.message}`, 'error');
  }
}

async function updateSupplierRate(supplierId, value) {
  const payload = { rate_per_unit: Number(value) };
  const response = await fetch(`${supplierEndpoint()}/${supplierId}/rate`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail ? JSON.stringify(err.detail) : 'No se pudo actualizar tarifa');
  }
}

async function updateSupplierStatus(supplierId, status) {
  const response = await fetch(`${supplierEndpoint()}/${supplierId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail ? JSON.stringify(err.detail) : 'No se pudo actualizar estado');
  }
}

suppliersTableBody.addEventListener('submit', async (event) => {
  const form = event.target;
  if (form.dataset.action !== 'rate') {
    return;
  }

  event.preventDefault();
  const supplierId = form.dataset.id;
  const rateInput = form.querySelector('input[name="rate"]');

  try {
    await updateSupplierRate(supplierId, rateInput.value);
    setSuppliersStatus('Tarifa actualizada.', 'ok');
    await fetchSuppliers();
  } catch (error) {
    setSuppliersStatus(`Error al actualizar tarifa: ${error.message}`, 'error');
  }
});

suppliersTableBody.addEventListener('click', async (event) => {
  const target = event.target;
  if (target.dataset.action !== 'status') {
    return;
  }

  const supplierId = target.dataset.id;
  const nextStatus = target.dataset.status;

  try {
    await updateSupplierStatus(supplierId, nextStatus);
    setSuppliersStatus('Estado actualizado.', 'ok');
    await fetchSuppliers();
  } catch (error) {
    setSuppliersStatus(`Error al actualizar estado: ${error.message}`, 'error');
  }
});

fileInput.addEventListener('change', () => {
  const [file] = fileInput.files;
  if (!file) {
    return;
  }
  if (!file.name.toLowerCase().endsWith('.csv')) {
    setStatus('Solo se permiten archivos CSV.', 'error');
    return;
  }
  onFileSelected(file);
});

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', (event) => {
  event.preventDefault();
  dropzone.classList.add('drag-over');
});
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-over'));
dropzone.addEventListener('drop', handleDrop);
dropzone.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    fileInput.click();
  }
});

analyzeBtn.addEventListener('click', analyzeFile);
downloadBtn.addEventListener('click', downloadResults);
refreshSuppliersBtn.addEventListener('click', fetchSuppliers);
filterCountry.addEventListener('change', fetchSuppliers);
filterCategory.addEventListener('change', fetchSuppliers);
filterStatus.addEventListener('change', fetchSuppliers);
supplierForm.addEventListener('submit', createSupplier);

fetchSuppliers();
