(() => {
  const preferredOrder = ["1", "10", "20", "30", "40", "50", "60", "80", "100"];
  const executionKeys = Object.keys(window.EXP1_EXECUTIONS);
  let selectedExecution = executionKeys[executionKeys.length - 1];
  const keys = preferredOrder.filter((key) => window.EXP1_EXECUTIONS[selectedExecution].levels[key]);
  const percentiles = ["p50", "p75", "p90", "p95", "p99"];
  const x = { "1": 75, "10": 170, "20": 265, "30": 360, "40": 455, "50": 550, "60": 645, "80": 740, "100": 835 };
  const chart = document.querySelector('figure[aria-label="Experiment 1 TTFT percentile chart"] svg');
  const tableBody = document.getElementById("experiment1-results");
  const runSelector = document.getElementById("experiment1-run");
  const outputLength = document.getElementById("experiment1-output-length");

  const selectedValue = (key, field, percentile) => {
    const result = window.EXP1_EXECUTIONS[selectedExecution].levels[key];
    return percentile ? result[field][percentile] : result[field];
  };
  const seconds = (value) => `${value.toFixed(2)}s`;
  const executionTime = (run) => {
    const value = String(run.executedAt || "");
    const match = value.match(/^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})$/);
    if (!match) return value;
    const utc = Date.UTC(+match[1], +match[2] - 1, +match[3], +match[4], +match[5], +match[6]);
    return `${new Date(utc + 8 * 60 * 60 * 1000).toISOString().slice(0, 19).replace("T", " ")} SGT`;
  };
  const y = (value) => Number((330 - Math.min(value, 60) / 60 * 290).toFixed(2));

  const redrawChart = () => {
    chart.querySelectorAll(".percentile-point").forEach((point) => point.remove());
    percentiles.forEach((percentile) => {
      const points = keys.map((key) => ({ key, value: selectedValue(key, "ttft", percentile), x: x[key] }));
      chart.querySelector(`.percentile-line[data-percentile="${percentile}"]`)
        .setAttribute("points", points.map((point) => `${point.x},${y(point.value)}`).join(" "));
      points.forEach((point) => {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("class", `point ${percentile} percentile-point`);
        circle.setAttribute("data-percentile", percentile);
        circle.setAttribute("cx", point.x);
        circle.setAttribute("cy", y(point.value));
        circle.setAttribute("r", "4");
        const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
        const runLabel = executionTime(window.EXP1_EXECUTIONS[selectedExecution]);
        title.textContent = `C${point.key} ${percentile}: ${seconds(point.value)} (${runLabel})`;
        circle.appendChild(title);
        chart.appendChild(circle);
      });
    });
    applyVisibility();
  };

  const redrawTable = () => {
    tableBody.replaceChildren(...keys.map((key) => {
      const row = document.createElement("tr");
      const success = selectedValue(key, "success");
      const failed = selectedValue(key, "failed");
      const values = [key, success, failed,
        ...percentiles.map((percentile) => seconds(selectedValue(key, "ttft", percentile))),
        seconds(selectedValue(key, "e2e95")), selectedValue(key, "rps").toFixed(3), selectedValue(key, "out").toFixed(2)];
      const concurrencyCell = document.createElement("td");
      concurrencyCell.textContent = values.shift();
      row.appendChild(concurrencyCell);
      const runCell = document.createElement("td");
      runCell.textContent = executionTime(window.EXP1_EXECUTIONS[selectedExecution]);
      row.appendChild(runCell);
      values.forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      });
      return row;
    }));
  };

  executionKeys.forEach((executionKey) => {
    const execution = window.EXP1_EXECUTIONS[executionKey];
    const option = document.createElement("option");
    option.value = executionKey;
    option.textContent = `${executionTime(execution)} · ${execution.outputLength} output tokens`;
    option.selected = executionKey === selectedExecution;
    runSelector.appendChild(option);
  });
  runSelector.addEventListener("change", () => {
    selectedExecution = runSelector.value;
    outputLength.textContent = `${window.EXP1_EXECUTIONS[selectedExecution].outputLength} tokens`;
    redrawChart();
    redrawTable();
  });

  const applyVisibility = () => {
    document.querySelectorAll('.exp1-toggle input[data-percentile]').forEach((input) => {
      chart.querySelectorAll(`[data-percentile="${input.dataset.percentile}"]`).forEach((element) => {
        element.classList.toggle("chart-hidden", !input.checked);
      });
    });
  };

  document.querySelectorAll('.exp1-toggle input[data-percentile]').forEach((input) => input.addEventListener("change", applyVisibility));
  redrawChart();
  redrawTable();
})();

(() => {
  const preferredOrder = ["8k", "16k", "32k", "64k", "128k", "256k", "512k", "near-1M"];
  const percentiles = ["p50", "p75", "p90", "p95", "p99"];
  const executionKeys = Object.keys(window.EXP2_EXECUTIONS || {});
  if (!executionKeys.length) return;
  let selectedExecution = executionKeys[executionKeys.length - 1];
  const chart = document.getElementById("experiment2-chart");
  const tableBody = document.getElementById("experiment2-results");
  const executionSelector = document.getElementById("experiment2-run");
  const seconds = (value) => `${value.toFixed(2)}s`;
  const executionTime = (execution) => {
    const match = String(execution.executedAt || "").match(/^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})$/);
    if (!match) return execution.executedAt || "";
    const utc = Date.UTC(+match[1], +match[2] - 1, +match[3], +match[4], +match[5], +match[6]);
    return `${new Date(utc + 8 * 60 * 60 * 1000).toISOString().slice(0, 19).replace("T", " ")} SGT`;
  };
  const svgElement = (name, attributes = {}) => {
    const element = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    return element;
  };
  const current = () => window.EXP2_EXECUTIONS[selectedExecution];

  const applyVisibility = () => {
    document.querySelectorAll('.exp2-toggle input[data-percentile]').forEach((input) => {
      chart.querySelectorAll(`[data-percentile="${input.dataset.percentile}"]`).forEach((element) => {
        element.classList.toggle("chart-hidden", !input.checked);
      });
    });
  };

  const redrawChart = () => {
    const levels = preferredOrder.filter((key) => current().levels[key]);
    const maxValue = Math.max(...levels.flatMap((key) => percentiles.map((p) => current().levels[key].ttft[p])));
    const yMax = Math.max(10, Math.ceil(maxValue / 30) * 30);
    const x = Object.fromEntries(levels.map((key, index) => [key, 75 + index * 760 / Math.max(1, levels.length - 1)]));
    const y = (value) => 330 - value / yMax * 290;

    const grid = chart.querySelector(".exp2-grid");
    const yTicks = chart.querySelector(".exp2-y-ticks");
    const xTicks = chart.querySelector(".exp2-x-ticks");
    grid.replaceChildren(); yTicks.replaceChildren(); xTicks.replaceChildren();
    for (let index = 0; index <= 5; index += 1) {
      const value = yMax * index / 5;
      const yPosition = y(value);
      grid.appendChild(svgElement("line", { x1: 75, y1: yPosition, x2: 835, y2: yPosition }));
      const label = svgElement("text", { x: 62, y: yPosition + 5, "text-anchor": "end" });
      label.textContent = `${value.toFixed(0)}s`;
      yTicks.appendChild(label);
    }
    levels.forEach((key) => {
      const label = svgElement("text", { x: x[key], y: 352, "text-anchor": "middle" });
      label.textContent = key;
      xTicks.appendChild(label);
    });

    chart.querySelectorAll(".percentile-point").forEach((point) => point.remove());
    percentiles.forEach((percentile) => {
      const points = levels.map((key) => ({ key, value: current().levels[key].ttft[percentile] }));
      chart.querySelector(`.percentile-line[data-percentile="${percentile}"]`)
        .setAttribute("points", points.map((point) => `${x[point.key]},${y(point.value)}`).join(" "));
      points.forEach((point) => {
        const circle = svgElement("circle", { class: `point ${percentile} percentile-point`, "data-percentile": percentile, cx: x[point.key], cy: y(point.value), r: 4 });
        const title = svgElement("title");
        title.textContent = `${point.key} ${percentile}: ${seconds(point.value)} (${current().levels[point.key].waves} accepted wave${current().levels[point.key].waves === 1 ? "" : "s"})`;
        circle.appendChild(title);
        chart.appendChild(circle);
      });
    });
    applyVisibility();
  };

  const redrawTable = () => {
    const levels = preferredOrder.filter((key) => current().levels[key]);
    tableBody.replaceChildren(...levels.map((key) => {
      const result = current().levels[key];
      const values = [key, result.waves, result.success, result.failed,
        ...percentiles.map((percentile) => seconds(result.ttft[percentile])),
        seconds(result.e2e95), result.rps.toFixed(3), result.out.toFixed(2)];
      const row = document.createElement("tr");
      values.forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      });
      return row;
    }));
  };

  executionKeys.forEach((executionKey) => {
    const execution = window.EXP2_EXECUTIONS[executionKey];
    const option = document.createElement("option");
    option.value = executionKey;
    option.textContent = `${executionTime(execution)} · C${execution.concurrency}`;
    executionSelector.appendChild(option);
  });
  executionSelector.value = selectedExecution;
  executionSelector.addEventListener("change", () => {
    selectedExecution = executionSelector.value;
    redrawChart(); redrawTable();
  });
  document.querySelectorAll('.exp2-toggle input[data-percentile]').forEach((input) => input.addEventListener("change", applyVisibility));
  redrawChart(); redrawTable();
})();
