document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("riskChart");
    if (!canvas) return;

    // Extrai os dados passados pelo Django via data attributes
    const lowRisk = parseInt(canvas.getAttribute("data-low") || "0", 10);
    const mediumRisk = parseInt(canvas.getAttribute("data-medium") || "0", 10);
    const highRisk = parseInt(canvas.getAttribute("data-high") || "0", 10);
    const total = parseInt(canvas.getAttribute("data-total") || "0", 10);

    const ctx = canvas.getContext("2d");

    // Caso o usuário ainda não monitore nenhum CNPJ, exibe um gráfico neutro
    const chartData = (total === 0) 
        ? [0, 0, 0, 1] 
        : [lowRisk, mediumRisk, highRisk];

    const chartColors = (total === 0)
        ? ["#334155"]
        : ["#10b981", "#f59e0b", "#ef4444"];

    const chartLabels = (total === 0)
        ? ["Sem fornecedores na carteira"]
        : ["Baixo Risco (Score ≥ 70)", "Médio Risco (Score 50-69)", "Alto Risco (Score < 50)"];

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: chartLabels,
            datasets: [{
                data: chartData,
                backgroundColor: chartColors,
                borderWidth: 2,
                borderColor: "#1e293b", // Mesma cor do card
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: "#94a3b8",
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        },
                        padding: 16
                    }
                },
                tooltip: {
                    enabled: total > 0,
                    callbacks: {
                        label: function (context) {
                            const value = context.raw || 0;
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(0) : 0;
                            return ` ${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: "70%"
        }
    });
});