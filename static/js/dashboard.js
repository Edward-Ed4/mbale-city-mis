(function () {
  const dataNode = document.getElementById("analytics-data");
  if (!dataNode) return;

  const data = JSON.parse(dataNode.textContent);
  const colors = {
    green: "#327346",
    amber: "#d89a23",
    red: "#c84b59",
    ink: "#344054",
    muted: "#687586",
    grid: "#e5e9e7",
    benchmark: "#235825",
  };

  function prepareCanvas(canvas, height) {
    const width = Math.max(300, canvas.parentElement.clientWidth - 8);
    const ratio = window.devicePixelRatio || 1;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.font = "10px Arial, sans-serif";
    return { context, width, height };
  }

  function drawCoverage() {
    const canvas = document.getElementById("coverage-chart");
    if (!canvas) return;
    const rows = data.wards || [];
    const height = Math.max(340, rows.length * 18 + 48);
    const { context: ctx, width, height: chartHeight } = prepareCanvas(canvas, height);
    const left = Math.min(115, Math.max(85, width * 0.3));
    const right = width - 34;
    const top = 18;
    const rowHeight = rows.length ? (chartHeight - top - 24) / rows.length : 18;

    ctx.clearRect(0, 0, width, chartHeight);
    ctx.fillStyle = colors.muted;
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    [0, 20, 40, 60, 80, 100].forEach((tick) => {
      const x = left + (right - left) * tick / 100;
      ctx.strokeStyle = colors.grid;
      ctx.beginPath();
      ctx.moveTo(x, top - 5);
      ctx.lineTo(x, chartHeight - 22);
      ctx.stroke();
      ctx.fillText(`${tick}%`, x, chartHeight - 10);
    });

    rows.forEach((ward, index) => {
      const y = top + index * rowHeight;
      const centerY = y + rowHeight / 2;
      const value = Math.max(0, Math.min(100, Number(ward.coverage) || 0));
      const color = value >= 65 ? colors.green : value >= 50 ? colors.amber : colors.red;
      const label = ward.name.length > 18 ? `${ward.name.slice(0, 17)}…` : ward.name;
      ctx.fillStyle = colors.ink;
      ctx.textAlign = "right";
      ctx.fillText(label, left - 8, centerY);
      ctx.fillStyle = color;
      ctx.fillRect(left, y + rowHeight * 0.2, (right - left) * value / 100, Math.max(3, rowHeight * 0.6));
      ctx.fillStyle = colors.ink;
      ctx.textAlign = "left";
      ctx.fillText(`${value.toFixed(1)}%`, Math.min(right + 4, left + (right - left) * value / 100 + 5), centerY);
    });

    const benchmarkX = left + (right - left) * 0.5985;
    ctx.save();
    ctx.strokeStyle = colors.benchmark;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 4]);
    ctx.beginPath();
    ctx.moveTo(benchmarkX, top - 8);
    ctx.lineTo(benchmarkX, chartHeight - 22);
    ctx.stroke();
    ctx.restore();
  }

  function drawVulnerability() {
    const canvas = document.getElementById("vulnerability-chart");
    if (!canvas) return;
    const { context: ctx, width, height } = prepareCanvas(canvas, 280);
    const levels = ["Low", "Medium", "High"];
    const divisions = ["Industrial City Division", "Northern City Division"];
    const palette = [colors.green, colors.amber, colors.red];
    const values = divisions.map((division) =>
      levels.map((level) => {
        const row = (data.vulnerability || []).find((item) => item.division === division && item.level === level);
        return row ? Number(row.count) : 0;
      })
    );
    const maxValue = Math.max(1, ...values.flat());
    const left = 40;
    const right = width - 15;
    const top = 18;
    const bottom = height - 42;
    const plotHeight = bottom - top;

    ctx.clearRect(0, 0, width, height);
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.fillStyle = colors.muted;
    const step = Math.max(1, Math.ceil(maxValue / 5));
    for (let tick = 0; tick <= maxValue; tick += step) {
      const y = bottom - plotHeight * tick / maxValue;
      ctx.strokeStyle = colors.grid;
      ctx.beginPath();
      ctx.moveTo(left, y);
      ctx.lineTo(right, y);
      ctx.stroke();
      ctx.fillText(String(tick), left - 7, y);
    }

    const groupWidth = (right - left) / levels.length;
    const barWidth = Math.min(30, groupWidth / 5);
    levels.forEach((level, levelIndex) => {
      const groupCenter = left + groupWidth * (levelIndex + 0.5);
      ctx.fillStyle = colors.ink;
      ctx.textAlign = "center";
      ctx.fillText(level, groupCenter, height - 20);
      divisions.forEach((division, divisionIndex) => {
        const value = values[divisionIndex][levelIndex];
        const x = groupCenter + (divisionIndex === 0 ? -barWidth - 2 : 2);
        const barHeight = plotHeight * value / maxValue;
        ctx.fillStyle = palette[levelIndex];
        ctx.fillRect(x, bottom - barHeight, barWidth, barHeight);
        ctx.fillStyle = colors.ink;
        ctx.fillText(String(value), x + barWidth / 2, bottom - barHeight - 8);
      });
    });
    ctx.textAlign = "left";
    ctx.fillStyle = colors.muted;
    ctx.fillText("Industrial", left, height - 4);
    ctx.textAlign = "right";
    ctx.fillText("Northern", right, height - 4);
  }

  function drawCharts() {
    drawCoverage();
    drawVulnerability();
  }

  drawCharts();
  window.addEventListener("resize", drawCharts);
})();
