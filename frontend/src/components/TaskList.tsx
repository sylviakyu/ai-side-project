import { Task } from "../App";

interface TaskListProps {
  tasks: Task[];
  selectedId: string | null;
  onSelect: (taskId: string) => void;
}

const STATUS_LABEL: Record<string, string> = {
  PENDING: "Pending",
  PROCESSING: "Processing",
  DONE: "Done",
  FAILED: "Failed",
};

function TaskList({ tasks, selectedId, onSelect }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="panel">
        <h2>Tasks</h2>
        <p className="muted">No tasks created yet.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Tasks</h2>
      <ul className="task-list">
        {tasks.map((task) => (
          <li
            key={task.task_id}
            className={task.task_id === selectedId ? "selected" : ""}
            onClick={() => onSelect(task.task_id)}
          >
            <div className={`status status-${task.status.toLowerCase()}`}></div>
            <div>
              <strong>{task.task_id}</strong>
              <br />
              <strong>Title: </strong>{task.title}
              <div className="meta">
                {STATUS_LABEL[task.status] ?? task.status} · {new Date(task.updated_at).toLocaleString()}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TaskList;
