document.addEventListener("DOMContentLoaded", function () {
  const ingredientsTableBody = document.querySelector(
    "#ingredients-table tbody"
  );

  // Add new function to update indexes
  function updateIndexes() {
    const rows = ingredientsTableBody.querySelectorAll("tr");
    rows.forEach((row, index) => {
      const select = row.querySelector("select");
      const input = row.querySelector("input");

      select.id = `ingredients-${index}-ingredient`;
      select.name = `ingredients-${index}-ingredient`;
      input.id = `ingredients-${index}-quantity`;
      input.name = `ingredients-${index}-quantity`;
    });
  }

  // Function to attach change listener to a select element.
  function attachListener(selectElement) {
    selectElement.addEventListener("change", function (event) {
      // If this select is in the last row and is non-empty add a new row
      const rows = ingredientsTableBody.querySelectorAll("tr");
      const lastRowSelect = rows[rows.length - 1].querySelector("select");
      if (lastRowSelect === event.target && event.target.value !== "") {
        addEmptyRow();
      }

      // Remove all empty rows except the last one
      const allSelects = ingredientsTableBody.querySelectorAll("select");
      const emptyRows = [];

      // Gather all empty rows
      allSelects.forEach((select) => {
        if (select.value === "") {
          emptyRows.push(select.closest("tr"));
        }
      });

      // Keep only the last empty row, remove others
      if (emptyRows.length > 1) {
        emptyRows.slice(0, -1).forEach((row) => row.remove());
        updateIndexes(); // Update indexes after removing rows
      }
    });
  }

  // Function to add an empty ingredients row.
  function addEmptyRow() {
    const index = ingredientsTableBody.querySelectorAll("tr").length;
    const newRow = document.createElement("tr");

    // Clone the first row's select and input elements
    const firstRowSelect = document
      .querySelector("#ingredients-0-ingredient")
      .cloneNode(true);
    const firstRowInput = document
      .querySelector("#ingredients-0-quantity")
      .cloneNode(true);

    // Update IDs and names for the new elements
    firstRowSelect.id = `ingredients-${index}-ingredient`;
    firstRowSelect.name = `ingredients-${index}-ingredient`;
    firstRowInput.id = `ingredients-${index}-quantity`;
    firstRowInput.name = `ingredients-${index}-quantity`;

    // Clear the selected value
    firstRowSelect.value = "";
    firstRowInput.value = "";

    newRow.innerHTML = `
        <td>
          <div class="select"></div>
        </td>
        <td></td>
      `;

    // Append the cloned elements to the new row
    newRow.querySelector(".select").appendChild(firstRowSelect);
    newRow.querySelector("td:last-child").appendChild(firstRowInput);

    ingredientsTableBody.appendChild(newRow);
    attachListener(firstRowSelect);
  }

  // Attach listeners to all existing select fields.
  document
    .querySelectorAll("#ingredients-table tbody select")
    .forEach(function (selectElem) {
      attachListener(selectElem);
    });
});
