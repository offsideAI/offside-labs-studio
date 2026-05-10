"use client";

import { StatusPill } from "@offside/ui";
import * as React from "react";

import {
  type RelatedType,
  type Task,
  type TaskStatus,
  useCreateTask,
  useTasksFor,
  useUpdateTask,
} from "../lib/api";
import { useActiveWorkspace } from "../lib/contexts";

interface Props {
  relatedType: RelatedType;
  relatedId: number;
}

const STATUS_OPTIONS: TaskStatus[] = ["open", "in_progress", "done", "cancelled"];

export const TasksTab = ({ relatedType, relatedId }: Props) => {
  const { active } = useActiveWorkspace();
  const tasks = useTasksFor(active?.id, relatedType, relatedId);
  const create = useCreateTask(active?.id);
  const update = useUpdateTask(active?.id);

  const [title, setTitle] = React.useState("");
  const [dueAt, setDueAt] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (!title.trim()) return;
    try {
      await create.mutateAsync({
        title: title.trim(),
        due_at: dueAt || null,
        related_type: relatedType,
        related_id: relatedId,
      });
      setTitle("");
      setDueAt("");
    } catch {
      setError("Could not add task.");
    }
  };

  const onStatusChange = (task: Task, status: TaskStatus) => {
    update.mutate({ id: task.id, patch: { status } });
  };

  return (
    <div className="space-y-4">
      <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-[200px]">
          <label htmlFor="task-title" className="text-xs font-medium text-fg-muted">
            New task
          </label>
          <input
            id="task-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Send pricing"
            required
            className="mt-1 w-full rounded-sm border hairline bg-bone px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
          />
        </div>
        <div>
          <label htmlFor="task-due" className="text-xs font-medium text-fg-muted">
            Due
          </label>
          <input
            id="task-due"
            type="datetime-local"
            value={dueAt}
            onChange={(e) => setDueAt(e.target.value)}
            className="mt-1 rounded-sm border hairline bg-bone px-3 py-2 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={create.isPending}
          className="rounded-sm border border-ink bg-ink px-4 py-2 text-sm font-bold text-bone hover:bg-ink-700 disabled:opacity-50"
        >
          {create.isPending ? "Adding…" : "Add task"}
        </button>
      </form>

      {error ? (
        <p role="alert" className="text-sm text-[#8E3B30]">
          {error}
        </p>
      ) : null}

      {tasks.isLoading ? (
        <p className="text-fg-muted text-sm">Loading tasks…</p>
      ) : (tasks.data?.results.length ?? 0) === 0 ? (
        <p className="text-fg-muted text-sm">No tasks yet.</p>
      ) : (
        <ul className="divide-y hairline">
          {(tasks.data?.results ?? []).map((task) => (
            <li key={task.id} className="flex items-center justify-between gap-4 py-3">
              <div className="space-y-0.5">
                <p
                  className={
                    "text-sm " +
                    (task.status === "done"
                      ? "text-fg-muted line-through"
                      : task.due_at && new Date(task.due_at) < new Date()
                        ? "font-medium text-tan-text"
                        : "")
                  }
                >
                  {task.title}
                </p>
                <p className="font-mono text-[10px] text-fg-muted">
                  {task.due_at ? `due ${new Date(task.due_at).toLocaleString()}` : "no due date"}
                  {task.due_at && new Date(task.due_at) < new Date() && task.status !== "done"
                    ? " · Overdue"
                    : ""}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={task.status}
                  onChange={(e) => onStatusChange(task, e.target.value as TaskStatus)}
                  className="rounded-sm border hairline bg-bone px-2 py-1 text-xs"
                  aria-label={`Status of ${task.title}`}
                >
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s} value={s}>
                      {s.replace("_", " ")}
                    </option>
                  ))}
                </select>
                <StatusPill
                  tone={
                    task.status === "done"
                      ? "success"
                      : task.status === "cancelled"
                        ? "neutral"
                        : "info"
                  }
                >
                  {task.priority}
                </StatusPill>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
