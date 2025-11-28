const API_BASE = "https://smart-task-analyzer-ryka-builder-command.onrender.com/api/tasks";


let tasks = [];
let nextId = 1;

const taskForm = document.getElementById("task-form");
const tasksTable = document.getElementById("tasks-table");
const tasksTableBody = tasksTable.querySelector("tbody");
const tasksEmpty = document.getElementById("tasks-empty");
const analyzeBtn = document.getElementById("analyze-btn");
const clearTasksBtn = document.getElementById("clear-tasks-btn");
const bulkJsonTextarea = document.getElementById("bulk-json");
const loadJsonBtn = document.getElementById("load-json-btn");
const strategySelect = document.getElementById("strategy");
const statusMessage = document.getElementById("status-message");
const loadingEl = document.getElementById("loading");
const resultsContainer = document.getElementById("results-container");
const suggestList = document.getElementById("suggest-list");

function setStatus(message, type = "") {
  statusMessage.textContent = message || "";
  statusMessage.className = "status-message";
  if (type) statusMessage.classList.add(type);
}

function renderTasksTable() {
  if (!tasks.length) {
    tasksTable.classList.add("hidden");
    tasksEmpty.classList.remove("hidden");
    return;
  }

  tasksTable.classList.remove("hidden");
  tasksEmpty.classList.add("hidden");

  tasksTableBody.innerHTML = "";
  for (const task of tasks) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${task.id ?? ""}</td>
      <td>${task.title}</td>
      <td>${task.due_date || "-"}</td>
      <td>${task.estimated_hours}</td>
      <td>${task.importance}</td>
      <td>${(task.dependencies || []).join(", ")}</td>
    `;
    tasksTableBody.appendChild(tr);
  }
}

taskForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const title = document.getElementById("title").value.trim();
  const dueDate = document.getElementById("due_date").value || null;
  const estimatedHours = parseFloat(
    document.getElementById("estimated_hours").value
  );
  const importance = parseInt(document.getElementById("importance").value, 10);
  const depsRaw = document.getElementById("dependencies").value.trim();

  if (!title || !estimatedHours || !importance) {
    setStatus("Title, hours, and importance are required.", "error");
    return;
  }

  if (importance < 1 || importance > 10) {
    setStatus("Importance must be between 1 and 10.", "error");
    return;
  }

  let deps = [];
  if (depsRaw) {
    deps = depsRaw
      .split(",")
      .map((x) => x.trim())
      .filter(Boolean)
      .map((x) => Number(x))
      .filter((x) => !Number.isNaN(x));
  }

  const task = {
    id: nextId++,
    title,
    due_date: dueDate,
    estimated_hours: estimatedHours,
    importance,
    dependencies: deps,
  };

  tasks.push(task);
  renderTasksTable();
  setStatus("Task added.", "success");
  taskForm.reset();
});

loadJsonBtn.addEventListener("click", () => {
  const text = bulkJsonTextarea.value.trim();
  if (!text) {
    setStatus("Paste JSON array first.", "error");
    return;
  }
  try {
    const parsed = JSON.parse(text);
    if (!Array.isArray(parsed)) {
      setStatus("JSON must be an array of tasks.", "error");
      return;
    }
    tasks = parsed.map((t) => ({
      id: t.id ?? nextId++,
      title: t.title,
      due_date: t.due_date ?? null,
      estimated_hours: t.estimated_hours,
      importance: t.importance,
      dependencies: t.dependencies || [],
    }));
    nextId =
      tasks.reduce((maxId, t) => Math.max(maxId, t.id || 0), 0) + 1;
    renderTasksTable();
    setStatus("JSON tasks loaded.", "success");
  } catch (err) {
    console.error(err);
    setStatus("Invalid JSON.", "error");
  }
});

clearTasksBtn.addEventListener("click", () => {
  tasks = [];
  nextId = 1;
  renderTasksTable();
  resultsContainer.innerHTML = "";
  resultsContainer.classList.add("hidden");
  suggestList.innerHTML = "";
  setStatus("Tasks cleared.", "success");
});

async function analyzeTasks() {
  if (!tasks.length) {
    setStatus("Add at least one task before analyzing.", "error");
    return;
  }

  const strategy = strategySelect.value;
  setStatus("");
  loadingEl.classList.remove("hidden");
  resultsContainer.classList.add("hidden");
  suggestList.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/analyze/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ strategy, tasks }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      console.error(errData);
      throw new Error("Analyze failed");
    }

    const analyzed = await res.json();
    renderResults(analyzed);
    await loadSuggestions(); // uses latest analyzed tasks from backend

    setStatus("Analysis completed.", "success");
  } catch (err) {
    console.error(err);
    setStatus("Failed to analyze tasks. Check backend is running.", "error");
  } finally {
    loadingEl.classList.add("hidden");
  }
}

async function loadSuggestions() {
  try {
    const res = await fetch(`${API_BASE}/suggest/`);
    if (!res.ok) {
      return; // Don't spam errors – suggestions are secondary
    }
    const data = await res.json();
    renderSuggestions(data);
  } catch (err) {
    console.error(err);
  }
}

function classifyPriority(score) {
  if (score >= 75) return "high";
  if (score >= 50) return "medium";
  return "low";
}

function renderResults(tasksWithScores) {
  resultsContainer.innerHTML = "";
  if (!tasksWithScores.length) {
    resultsContainer.classList.add("hidden");
    return;
  }

  resultsContainer.classList.remove("hidden");

  tasksWithScores.forEach((task) => {
    const priority = classifyPriority(task.score);
    const card = document.createElement("div");
    card.classList.add("result-card", `priority-${priority}`);

    const badgeClass =
      priority === "high"
        ? "badge-high"
        : priority === "medium"
        ? "badge-medium"
        : "badge-low";

    card.innerHTML = `
      ${
        task.is_overdue
          ? '<div class="ribbon-overdue">OVERDUE</div>'
          : ""
      }
      <div class="result-header">
        <div>
          <div class="result-title">${task.title}</div>
          <div class="result-meta">
            Due: ${task.due_date || "—"} · Hours: ${
      task.estimated_hours
    } · Importance: ${task.importance}
          </div>
        </div>
        <div style="text-align:right;">
          <div class="result-score">${task.score}</div>
          <span class="result-badge ${badgeClass}">
            ${
              priority === "high"
                ? "High Priority"
                : priority === "medium"
                ? "Medium Priority"
                : "Low Priority"
            }
          </span>
        </div>
      </div>
      <div class="result-meta">
        Blocks: ${task.blocks_tasks || 0}${
      task.has_circular_dependency ? " · Circular dependency detected" : ""
    }
      </div>
      <div class="result-explanation">
        ${task.explanation}
      </div>
    `;

    resultsContainer.appendChild(card);
  });
}

function renderSuggestions(suggestions) {
  suggestList.innerHTML = "";
  if (!suggestions || !suggestions.length) return;

  suggestions.forEach((task, idx) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <div class="suggest-item-title">
        ${idx + 1}. ${task.title}
      </div>
      <div class="suggest-item-meta">
        Score: ${task.score} · Due: ${task.due_date || "—"} · Hours: ${
      task.estimated_hours
    }
      </div>
    `;
    suggestList.appendChild(li);
  });
}

analyzeBtn.addEventListener("click", analyzeTasks);

renderTasksTable();
