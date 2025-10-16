import { FormEvent, useState } from "react";

interface TaskFormProps {
  onSubmit: (title: string, message: string) => Promise<void>;
}

function TaskForm({ onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!title.trim() || !message.trim()) {
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit(title.trim(), message.trim());
      setTitle("");
      setMessage("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <h2>Create Task</h2>
      <label>
        Title
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Summarise the work"
          required
        />
      </label>
      <label>
        Message
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Describe what the worker should do"
          rows={3}
          required
        />
      </label>
      <button type="submit" disabled={submitting}>
        {submitting ? "Creating…" : "Create task"}
      </button>
    </form>
  );
}

export default TaskForm;
