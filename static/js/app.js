const form = document.getElementById("benchmarkForm");
const descriptionInput = document.getElementById("description");
const generateBtn = document.getElementById("generateBtn");
const resultsTabs = document.getElementById("resultsTabs");
const emptyState = document.getElementById("emptyState");
const statusIndicator = document.getElementById("statusIndicator");
const statsPanel = document.getElementById("statsPanel");
const statsContent = document.getElementById("stats");

const modelTimings = {};
let isGenerating = false;

function setStatus(text, status = "idle") {
  statusIndicator.textContent = text;
  statusIndicator.classList.remove("generating", "complete");
  if (status === "generating") statusIndicator.classList.add("generating");
  if (status === "complete") statusIndicator.classList.add("complete");
}

function getSelectedModels() {
  const checked = document.querySelectorAll(".model-select:checked");
  return Array.from(checked).map((el) => el.value);
}

function createTabButton(model) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tab-button";
  btn.textContent = model.toUpperCase();
  btn.dataset.model = model;

  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`content_${model}`).classList.add("active");
  });

  return btn;
}

function createTabContent(model) {
  const content = document.createElement("div");
  content.id = `content_${model}`;
  content.className = "tab-content";

  const indicator = document.createElement("div");
  indicator.className = "generating-indicator";
  indicator.innerHTML = `<div class="spinner"></div> <span>Generating...</span>`;
  indicator.id = `indicator_${model}`;

  const frame = document.createElement("div");
  frame.className = "preview-frame";

  const htmlContent = document.createElement("div");
  htmlContent.id = `html_${model}`;
  htmlContent.style.padding = "2rem";
  htmlContent.style.overflow = "auto";
  htmlContent.style.height = "600px";

  frame.appendChild(htmlContent);
  content.appendChild(indicator);
  content.appendChild(frame);

  return content;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (isGenerating) return;

  const description = descriptionInput.value.trim();
  const models = getSelectedModels();

  if (!description) {
    setStatus("Enter a description", "idle");
    return;
  }

  if (models.length === 0) {
    setStatus("Select at least one model", "idle");
    return;
  }

  isGenerating = true;
  generateBtn.disabled = true;
  resultsTabs.innerHTML = "";
  emptyState.style.display = "none";
  setStatus(`Generating for ${models.length} model(s)...`, "generating");

  Object.keys(modelTimings).forEach((k) => delete modelTimings[k]);

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description, models }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || "Request failed");
    }

    if (!response.body) {
      throw new Error("Streaming not supported");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    const modelStartTime = {};

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const event = JSON.parse(line.slice(6));
            const model = event.model;

            if (!modelStartTime[model]) {
              modelStartTime[model] = Date.now();

              // Create tab button and content
              const btn = createTabButton(model);
              const content = createTabContent(model);
              resultsTabs.appendChild(btn);
              document.body.appendChild(content);
              // Move content after tabs
              resultsTabs.parentElement.appendChild(content);

              if (resultsTabs.children.length === 1) {
                btn.classList.add("active");
                content.classList.add("active");
              }
            }

            if (event.status === "generating" && event.chunk) {
              const htmlEl = document.getElementById(`html_${model}`);
              htmlEl.innerHTML += event.chunk;
            } else if (event.status === "complete") {
              const elapsed = Date.now() - modelStartTime[model];
              modelTimings[model] = (elapsed / 1000).toFixed(2);

              const indicator = document.getElementById(`indicator_${model}`);
              indicator.innerHTML = `<span style="color: #10b981; font-weight: 600;">✓ Complete in ${modelTimings[model]}s</span>`;

              const htmlEl = document.getElementById(`html_${model}`);
              if (event.html) {
                htmlEl.innerHTML = event.html;
              }
            } else if (event.error) {
              const indicator = document.getElementById(`indicator_${model}`);
              indicator.innerHTML = `<span style="color: #ef4444;">❌ Error: ${event.error}</span>`;
            }
          } catch (e) {
            console.error("Parse error:", e);
          }
        }
      }
    }

    setStatus("Complete", "complete");
    updateStats();
  } catch (error) {
    setStatus("Failed", "idle");
    console.error("Generation error:", error);
  } finally {
    isGenerating = false;
    generateBtn.disabled = false;
  }
});

function updateStats() {
  if (Object.keys(modelTimings).length === 0) return;

  statsPanel.style.display = "block";
  let html = "";
  for (const [model, timing] of Object.entries(modelTimings)) {
    html += `<div class="d-flex justify-content-between mb-2"><span>${model.toUpperCase()}</span><strong>${timing}s</strong></div>`;
  }
  statsContent.innerHTML = html;
}
