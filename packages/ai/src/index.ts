// @offside/ai — AI model router, prompt registry, structured-output helpers.
//
// This is the TypeScript surface; a parallel Python module lives at
// backend/apps/ai/ with the same prompt names and schemas. Server-side AI
// calls go through Python; UI-side calls (drafts, NL queries from the
// browser) go through this package.
//
// Real implementations land in M11 (AI surfaces in CRM). For now this is
// a typed scaffold that downstream code can import without breaking when
// real implementations arrive.

export type ModelTier = "haiku" | "sonnet" | "opus";

export type ModelId =
  | "claude-haiku-4-5-20251001"
  | "claude-sonnet-4-6"
  | "claude-opus-4-7";

export const tierToModel: Record<ModelTier, ModelId> = {
  haiku: "claude-haiku-4-5-20251001",
  sonnet: "claude-sonnet-4-6",
  opus: "claude-opus-4-7",
};

export interface PromptCallTelemetry {
  promptName: string;
  model: ModelId;
  tokensIn: number;
  tokensOut: number;
  costCents: number;
  latencyMs: number;
  runId?: string;
  stepId?: string;
}

export interface RouterOptions {
  tier?: ModelTier;
  fallback?: "openai" | "gemini" | "none";
  maxRetries?: number;
}

// Stub: the real router lives in M11.
export const router = {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async callPrompt<TIn, TOut>(_promptName: string, _input: TIn, _opts?: RouterOptions): Promise<TOut> {
    throw new Error(
      "@offside/ai router is not implemented yet — wired up in M11 (AI surfaces in CRM).",
    );
  },
};

export type { PromptCallTelemetry as Telemetry };
