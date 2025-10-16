import { useCallback, useEffect, useMemo, useState } from "react";
import TaskList from "./components/TaskList";
import TaskDetail from "./components/TaskDetail";
import TaskForm from "./components/TaskForm";
import ToastOverlay, { ToastMessage } from "./components/ToastOverlay";

export type TaskStatus = "PENDING" | "PROCESSING" | "DONE" | "FAILED";

export interface Task {
  task_id: string;
  title: string;
  payload?: Record<string, unknown> | null;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
  finished_at?: string | null;
}

const API_BASE = process.env.REACT_APP_API_BASE ?? "http://localhost:8000";
const WS_URL = process.env.REACT_APP_WS_URL ?? "ws://localhost:8000/ws";

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const loadTasks = useCallback(async () => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/tasks`);
      if (!response.ok) {
        throw new Error(`Failed to load tasks (${response.status})`);
      }
      const data: Task[] = await response.json();
      setTasks(data);
    } catch (err) {
      setError((err as Error).message);
    }
  }, []);

  const loadTaskDetail = useCallback(async (taskId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/tasks/${taskId}`);
      if (!response.ok) {
        throw new Error(`Failed to load task (${response.status})`);
      }
      const data: Task = await response.json();
      setSelectedTask(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  useEffect(() => {
    const socket = new WebSocket(WS_URL);
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (!payload?.task_id) {
          return;
        }

        setTasks((prev) => {
          const existingIndex = prev.findIndex((task) => task.task_id === payload.task_id);
          if (existingIndex >= 0) {
            const updated = [...prev];
            updated[existingIndex] = { ...updated[existingIndex], ...payload };
            return updated;
          }
          return [payload as Task, ...prev];
        });

        if (selectedTaskId === payload.task_id) {
          setSelectedTask((prev) => (prev ? { ...prev, ...payload } : payload));
        }

        const statusText = payload.status ?? "Unknown";
        const updatedDate =
          payload.updated_at && !Number.isNaN(new Date(payload.updated_at).valueOf())
            ? new Date(payload.updated_at).toLocaleString()
            : "Unknown";

        const toast: ToastMessage = {
          id: `${payload.task_id}-${Date.now()}`,
          title: payload.title ?? payload.task_id,
          message: (
            <>
              <div>
                <strong>Status:</strong>{" "}
                {statusText}
              </div>
              <div>
                <strong>Update Time:</strong>{" "}
                {updatedDate}
              </div>
            </>
          ),
        };

        setToasts((prev) => [...prev, toast]);

        setTimeout(() => {
          setToasts((prev) => prev.filter((item) => item.id !== toast.id));
        }, 5000);
      } catch (err) {
        console.error("Failed to parse WebSocket message", err);
      }
    };

    socket.onerror = (event) => {
      console.error("WebSocket error", event);
    };

    return () => socket.close();
  }, [selectedTaskId]);

  const handleSelectTask = useCallback(
    (taskId: string) => {
      setSelectedTaskId(taskId);
      loadTaskDetail(taskId);
    },
    [loadTaskDetail]
  );

  const handleCreateTask = useCallback(
    async (title: string, message: string) => {
      setError(null);
      try {
        const response = await fetch(`${API_BASE}/tasks`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title, payload: { message } }),
        });

        if (!response.ok) {
          const text = await response.text();
          throw new Error(text || `Failed to create task (${response.status})`);
        }

        await loadTasks();
      } catch (err) {
        setError((err as Error).message);
      }
    },
    [loadTasks]
  );

  const selectedTaskResolved = useMemo(() => {
    if (!selectedTaskId) {
      return null;
    }
    if (selectedTask && selectedTask.task_id === selectedTaskId) {
      return selectedTask;
    }
    return tasks.find((task) => task.task_id === selectedTaskId) ?? null;
  }, [selectedTaskId, selectedTask, tasks]);

  return (
    <div className="layout">
      <header>
        <h1>TaskFlow Dashboard</h1>
        <p>Monitor tasks, create new work items, and observe real-time state changes.</p>
      </header>

      {error && <div className="alert">{error}</div>}

      <section className="content">
        <aside>
          <TaskForm onSubmit={handleCreateTask} />
          <TaskList tasks={tasks} onSelect={handleSelectTask} selectedId={selectedTaskId} />
        </aside>
        <main>
          <TaskDetail task={selectedTaskResolved} loading={loading} />
        </main>
      </section>

      <ToastOverlay toasts={toasts} />
    </div>
  );
}

export default App;
