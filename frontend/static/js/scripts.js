// frontend/static/js/scripts.js

document.addEventListener('DOMContentLoaded', () => {
    const monthSelect = document.getElementById('monthSelect');
    const searchBox = document.getElementById('searchBox');
    const transactionsTableBody = document.querySelector('#transactionsTable tbody');
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const currentPageSpan = document.getElementById('currentPage');

    const totalSaleAmount = document.getElementById('totalSaleAmount');
    const totalSoldItems = document.getElementById('totalSoldItems');
    const totalNotSoldItems = document.getElementById('totalNotSoldItems');

    const barChartCtx = document.getElementById('barChart').getContext('2d');
    const pieChartCtx = document.getElementById('pieChart').getContext('2d');

    let currentPage = 1;
    let totalPages = 1;
    let currentMonth = monthSelect.value;
    let currentSearch = '';

    let barChart;
    let pieChart;

    const fetchTransactions = async () => {
        try {
            const response = await axios.get('/api/transactions', {
                params: {
                    month: currentMonth,
                    search: currentSearch,
                    page: currentPage,
                    per_page: 10
                }
            });
            const data = response.data;
            populateTransactions(data.transactions);
            totalPages = data.pages;
            currentPageSpan.textContent = `${currentPage} / ${totalPages}`;
            prevPageBtn.disabled = currentPage === 1;
            nextPageBtn.disabled = currentPage === totalPages;
        } catch (error) {
            console.error(error);
        }
    };

    const populateTransactions = (transactions) => {
        transactionsTableBody.innerHTML = '';
        transactions.forEach(tx => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${tx.id}</td>
                <td>${tx.product_id}</td>
                <td>${tx.title}</td>
                <td>${tx.description || ''}</td>
                <td>$${tx.price.toFixed(2)}</td>
                <td>${tx.dateOfSale}</td>
                <td>${tx.status}</td>
                <td>${tx.category || ''}</td>
            `;
            transactionsTableBody.appendChild(row);
        });
    };

    const fetchStatistics = async () => {
        try {
            const response = await axios.get('/api/statistics', {
                params: {
                    month: currentMonth
                }
            });
            const data = response.data;
            totalSaleAmount.textContent = `$${data.totalSaleAmount.toFixed(2)}`;
            totalSoldItems.textContent = data.totalSoldItems;
            totalNotSoldItems.textContent = data.totalNotSoldItems;
        } catch (error) {
            console.error(error);
        }
    };

    const fetchBarChart = async () => {
        try {
            const response = await axios.get('/api/bar-chart', {
                params: {
                    month: currentMonth
                }
            });
            const data = response.data;
            if (barChart) {
                barChart.destroy();
            }
            barChart = new Chart(barChartCtx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: '# of Items',
                        data: data.data,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision:0
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error(error);
        }
    };

    const fetchPieChart = async () => {
        try {
            const response = await axios.get('/api/pie-chart', {
                params: {
                    month: currentMonth
                }
            });
            const data = response.data;
            const labels = Object.keys(data);
            const counts = Object.values(data);
            const backgroundColors = generateColors(labels.length);

            if (pieChart) {
                pieChart.destroy();
            }
            pieChart = new Chart(pieChartCtx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: backgroundColors
                    }]
                },
                options: {
                    responsive: true
                }
            });
        } catch (error) {
            console.error(error);
        }
    };

    const fetchAllData = async () => {
        await Promise.all([
            fetchTransactions(),
            fetchStatistics(),
            fetchBarChart(),
            fetchPieChart()
        ]);
    };

    monthSelect.addEventListener('change', () => {
        currentMonth = monthSelect.value;
        currentPage = 1;
        fetchAllData();
    });

    searchBox.addEventListener('input', () => {
        currentSearch = searchBox.value.trim();
        currentPage = 1;
        fetchTransactions();
    });

    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchTransactions();
        }
    });

    nextPageBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            fetchTransactions();
        }
    });

    const generateColors = (num) => {
        const colors = [];
        for (let i = 0; i < num; i++) {
            const r = Math.floor(Math.random() * 255);
            const g = Math.floor(Math.random() * 255);
            const b = Math.floor(Math.random() * 255);
            colors.push(`rgba(${r}, ${g}, ${b}, 0.6)`);
        }
        return colors;
    };

    // Initial Data Fetch
    fetchAllData();
});
