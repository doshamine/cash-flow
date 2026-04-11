document.addEventListener("DOMContentLoaded", function () {
    const operationTypeSelect = document.getElementById("id_operation_type");
    const categorySelect = document.getElementById("id_category");
    const subcategorySelect = document.getElementById("id_subcategory");

    if (!operationTypeSelect || !categorySelect || !subcategorySelect) {
        return;
    }

    operationTypeSelect.addEventListener("change", function () {
        const operationTypeId = this.value;

        categorySelect.innerHTML = '<option value="">---------</option>';
        subcategorySelect.innerHTML = '<option value="">---------</option>';

        if (!operationTypeId) {
            return;
        }

        fetch(`/ajax/load-categories/?operation_type=${operationTypeId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(item => {
                    const option = document.createElement("option");
                    option.value = item.id;
                    option.textContent = item.name;
                    categorySelect.appendChild(option);
                });
            });
    });

    categorySelect.addEventListener("change", function () {
        const categoryId = this.value;

        subcategorySelect.innerHTML = '<option value="">---------</option>';

        if (!categoryId) {
            return;
        }

        fetch(`/ajax/load-subcategories/?category=${categoryId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(item => {
                    const option = document.createElement("option");
                    option.value = item.id;
                    option.textContent = item.name;
                    subcategorySelect.appendChild(option);
                });
            });
    });
});