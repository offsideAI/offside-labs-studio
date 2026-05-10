"use client";

import * as React from "react";

import { type RelatedType, useCreateNote, useNotesFor } from "../lib/api";
import { useActiveWorkspace } from "../lib/contexts";

interface Props {
  relatedType: RelatedType;
  relatedId: number;
}

export const NotesTab = ({ relatedType, relatedId }: Props) => {
  const { active } = useActiveWorkspace();
  const notes = useNotesFor(active?.id, relatedType, relatedId);
  const create = useCreateNote(active?.id);

  const [body, setBody] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (!body.trim()) return;
    try {
      await create.mutateAsync({
        body_md: body.trim(),
        related_type: relatedType,
        related_id: relatedId,
      });
      setBody("");
    } catch {
      setError("Could not add note.");
    }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={onSubmit} className="space-y-2">
        <label htmlFor="note-body" className="text-xs font-medium text-fg-muted">
          New note · Markdown
        </label>
        <textarea
          id="note-body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="**Key**: discount-blocked by procurement. Follow up Friday."
          rows={3}
          className="w-full rounded-sm border hairline bg-bone px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tan focus-visible:ring-offset-2"
        />
        <div className="flex items-center justify-between gap-2">
          <p className="font-mono text-[10px] text-fg-muted">
            Edits past 24 hours are recorded in an audit log.
          </p>
          <button
            type="submit"
            disabled={create.isPending || !body.trim()}
            className="rounded-sm border border-ink bg-ink px-4 py-2 text-sm font-bold text-bone hover:bg-ink-700 disabled:opacity-50"
          >
            {create.isPending ? "Adding…" : "Add note"}
          </button>
        </div>
      </form>

      {error ? (
        <p role="alert" className="text-sm text-[#8E3B30]">
          {error}
        </p>
      ) : null}

      {notes.isLoading ? (
        <p className="text-fg-muted text-sm">Loading notes…</p>
      ) : (notes.data?.results.length ?? 0) === 0 ? (
        <p className="text-fg-muted text-sm">No notes yet.</p>
      ) : (
        <ul className="space-y-3">
          {(notes.data?.results ?? []).map((note) => (
            <li key={note.id} className="rounded-md border hairline bg-bone p-3 text-sm">
              <pre className="whitespace-pre-wrap font-sans">{note.body_md}</pre>
              <p className="mt-2 font-mono text-[10px] text-fg-muted">
                {new Date(note.created_at).toLocaleString()}
                {note.edit_log.length > 0
                  ? ` · ${note.edit_log.length} late-edit${note.edit_log.length > 1 ? "s" : ""}`
                  : ""}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
