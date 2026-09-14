document.addEventListener("DOMContentLoaded", function () {
    // Inicialização do Gráfico de Distribuição de Risco (Chart.js)
    const ctx = document.getElementById('riskChart');

    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Baixo Risco', 'Médio Risco', 'Alto Risco'],
                datasets: [{
                    data: [12, 3, 1], // Dados fictícios do panorama geral de CNPJs
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8' }
                    }
                }
            }
        });
    }
});