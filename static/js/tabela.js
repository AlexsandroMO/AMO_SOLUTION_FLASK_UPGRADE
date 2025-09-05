


const tabelaContainer = document.getElementById("tabelaContainer");
const tabelaOriginal = JSON.parse(localStorage.getItem("excelData")) || [];
let tabelaFiltrada = JSON.parse(JSON.stringify(tabelaOriginal));
let filtros = [];

function createResizableTh(th) {
  th.classList.add("resizable");
  const resizer = document.createElement("div");
  resizer.className = "resizer";
  th.appendChild(resizer);

  let startX, startMinWidth;

  resizer.addEventListener("mousedown", (e) => {
    startX = e.pageX;
    startMinWidth = parseInt(window.getComputedStyle(th).minWidth, 10) || th.offsetWidth;

    function onMouseMove(e) {
      const newWidth = startMinWidth + (e.pageX - startX);
      if (newWidth > 30) {
        th.style.minWidth = newWidth + "px";
      }
    }

    function onMouseUp() {
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    }

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  });
}

function atualizarContadorLinhas() {
  const contador = document.getElementById("contadorLinhas");
  if (contador) {
    contador.textContent = `Linhas visíveis: ${tabelaFiltrada.length - 1}`;
  }
}

function renderTable() {
  const activeElement = document.activeElement;
  const activeColIndex = activeElement?.dataset?.col;
  const cursorPos = activeElement?.selectionStart || 0;

  const table = document.createElement("table");
  table.classList.add("styled-table");

  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  const filterRow = document.createElement("tr");

  const colCount = tabelaOriginal[0].length;
  if (filtros.length !== colCount) {
    filtros = new Array(colCount).fill("");
  }

  tabelaOriginal[0].forEach((header, colIndex) => {
    const th = document.createElement("th");
    th.textContent = header;
    createResizableTh(th);
    headerRow.appendChild(th);

    const filterCell = document.createElement("th");
    const filterInput = document.createElement("input");
    filterInput.type = "text";
    filterInput.placeholder = "Filtrar...";
    filterInput.value = filtros[colIndex];
    filterInput.dataset.col = colIndex;

    filterInput.addEventListener("input", (e) => {
      filtros[colIndex] = e.target.value.toLowerCase();
      applyFilters();
    });

    filterCell.appendChild(filterInput);
    filterRow.appendChild(filterCell);
  });

  thead.appendChild(headerRow);
  thead.appendChild(filterRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");

  tabelaFiltrada.forEach((row, rowIndex) => {
    if (rowIndex === 0) return;

    const tr = document.createElement("tr");

    row.forEach((cell, colIndex) => {
      const td = document.createElement("td");
      const input = document.createElement("input");
      input.value = cell;

      input.addEventListener("change", (e) => {
        tabelaFiltrada[rowIndex][colIndex] = e.target.value;
        tabelaOriginal[rowIndex][colIndex] = e.target.value;
        localStorage.setItem("excelData", JSON.stringify(tabelaOriginal));
      });

      td.appendChild(input);
      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  tabelaContainer.innerHTML = "";
  tabelaContainer.appendChild(table);

  if (activeColIndex !== undefined) {
    const inputs = tabelaContainer.querySelectorAll(`input[data-col="${activeColIndex}"]`);
    if (inputs.length > 0) {
      const input = inputs[0];
      input.focus();
      input.setSelectionRange(cursorPos, cursorPos);
    }
  }

  atualizarContadorLinhas();
}

function applyFilters() {
  tabelaFiltrada = tabelaOriginal.filter((row, rowIndex) => {
    if (rowIndex === 0) return true;

    return row.every((cell, colIndex) => {
      const filtro = filtros[colIndex];
      if (!filtro) return true;
      return String(cell).toLowerCase().includes(filtro);
    });
  });

  renderTable();
}

function exportarExcel() {
  const ws = XLSX.utils.aoa_to_sheet(tabelaOriginal);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Editado");
  XLSX.writeFile(wb, "PLANILHA_EDITADA.xlsx");
}

function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
}

renderTable();