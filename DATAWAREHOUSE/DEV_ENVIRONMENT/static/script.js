async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Falha na requisição: ${response.status}`);
  }
  return response.json();
}

function renderChart(chartData) {
  const container = document.getElementById('chart-container');
  const labels = chartData.data.labels || [];
  const series = chartData.data.series || [];

  if (!labels.length || !series.length) {
    container.textContent = 'Nenhum dado de gráfico disponível.';
    return;
  }

  const html = [
    `<div class="chart-labels"><strong>Datas:</strong> ${labels.join(', ')}</div>`,
    ...series.map(seriesItem =>
      `<div><strong>${seriesItem.name}:</strong> ${seriesItem.values.join(', ')}</div>`
    )
  ].join('');

  container.innerHTML = html;
}

function renderSummary(data) {
  const summary = document.getElementById('data-summary');
  if (!data || data.total_registros === undefined) {
    summary.textContent = 'Nenhum resumo disponível.';
    return;
  }

  summary.innerHTML = `
    <p><strong>Total de registros:</strong> ${data.total_registros}</p>
    <p><strong>Mensagem:</strong> ${data.mensagem || 'OK'}</p>
  `;
}

function renderDiagram(diagramData) {
  const diagram = document.getElementById('diagram-json');
  diagram.textContent = JSON.stringify(diagramData.data, null, 2);
}

async function initializeDashboard() {
  const statusMessage = document.getElementById('status-message');
  try {
    const [chartData, apiData, diagramData] = await Promise.all([
      fetchJson('/api/charts'),
      fetchJson('/api/data'),
      fetchJson('/api/diagrams')
    ]);

    renderChart(chartData);
    renderSummary(apiData);
    renderDiagram(diagramData);

    statusMessage.textContent = 'Dashboard carregado com sucesso.';
  } catch (error) {
    statusMessage.textContent = `Erro ao carregar dashboard: ${error.message}`;
  }
}

window.addEventListener('DOMContentLoaded', initializeDashboard);
