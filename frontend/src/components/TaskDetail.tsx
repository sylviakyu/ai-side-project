import { Task } from "../App";

interface TaskDetailProps {
  task: Task | null;
  loading: boolean;
}

function TaskDetail({ task, loading }: TaskDetailProps) {
  if (loading) {
    return (
      <div className="panel">
        <h2>Task Detail</h2>
        <p className="muted">Loading…</p>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="panel">
        <h2>Task Detail</h2>
        <p className="muted">Select a task to see its details.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Task Detail</h2>
      <dl className="detail">
        <div>
          <dt>ID</dt>
          <dd>{task.task_id}</dd>
        </div>
        <div>
          <dt>Title</dt>
          <dd>{task.title}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{task.status}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{new Date(task.created_at).toLocaleString()}</dd>
        </div>
        <div>
          <dt>Updated</dt>
          <dd>{new Date(task.updated_at).toLocaleString()}</dd>
        </div>
        <div>
          <dt>Finished</dt>
          <dd>{task.finished_at ? new Date(task.finished_at).toLocaleString() : "—"}</dd>
        </div>
        <div>
          <dt>Payload</dt>
          <dd>
            <pre>{JSON.stringify(task.payload ?? {}, null, 2)}</pre>
          </dd>
        </div>
      </dl>
    </div>
  );
}

export default TaskDetail;
