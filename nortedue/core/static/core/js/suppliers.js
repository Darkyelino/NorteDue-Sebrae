document.addEventListener("DOMContentLoaded", function () {
    const tableSearch = document.getElementById("tableSearch");
    const tableRows = document.querySelectorAll(".suppliers-table tbody tr");

    if (tableSearch && tableRows.length > 0) {
        tableSearch.addEventListener("keyup", function () {
            const term = this.value.toLowerCase().trim();

            tableRows.forEach(row => {
                const text = row.innerText.toLowerCase();
                if (text.includes(term)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    }
});