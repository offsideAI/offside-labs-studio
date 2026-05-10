"use client";

import * as React from "react";

interface ShortcutOptions {
  /** Require Cmd (macOS) or Ctrl (other platforms). */
  meta?: boolean;
  /** Allow firing while focus is inside a text input. Default: false. */
  allowInInput?: boolean;
}

/**
 * Subscribe to a global keydown shortcut.
 *
 *   useKeyboardShortcut("k", () => setOpen(true), { meta: true })
 *   useKeyboardShortcut("/", () => focusSearch())
 *   useKeyboardShortcut("Escape", () => setOpen(false), { allowInInput: true })
 */
export const useKeyboardShortcut = (
  key: string,
  callback: () => void,
  options: ShortcutOptions = {},
) => {
  const callbackRef = React.useRef(callback);
  React.useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  React.useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key !== key) return;
      if (options.meta && !(event.metaKey || event.ctrlKey)) return;
      if (!options.allowInInput) {
        const target = event.target as HTMLElement | null;
        if (
          target instanceof HTMLInputElement ||
          target instanceof HTMLTextAreaElement ||
          target?.isContentEditable
        ) {
          return;
        }
      }
      event.preventDefault();
      callbackRef.current();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [key, options.meta, options.allowInInput]);
};
