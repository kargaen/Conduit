## 3. The Contracts (Ports)

These interfaces are the load-bearing part of the whole system. Method *shapes*
are firm; concrete types are indicative until the language is chosen.

```
// A source knows only how to pull content out of its platform.
port Source {
  id: string                       // "remarkable", "teams"
  fetch(since: Cursor): RawItem[]  // RawItem = { text, source_ref, kind }
}

// Extraction turns unstructured text into candidate tasks.
port Extractor {
  extract(item: RawItem): CandidateTask[]   // each carries a confidence score
}

// A sink knows only how to write the canonical model into one target.
port Sink {
  id: string
  push(tasks: Task[]): PushResult
}

// Persistence is hidden behind the core, never used directly by adapters.
port TaskStore {
  upsert(tasks: Task[]): void      // idempotent on Task.id
  seen(id: string): boolean        // exact-dedup check
  cursor(sourceId): Cursor         // watermark per source
}

// LLM provider — abstraction over any model backend.
// Orchestration passes a tier hint; if the provider has only one model
// configured, it is used for both tiers — never fail on a missing tier.
port LLMProvider {
  id: string                              // "anthropic", "openai", …
  complete(
    prompt: string,
    output_schema: JSONSchema,
    tier: "bulk" | "accurate"            // bulk = fast/cheap; accurate = quality
  ): structured_output                    // validated against output_schema
}

// Registry holds one or more LLMProvider implementations.
// active_provider() returns the configured default.
// Switching providers = change config, not code.
port LLMRegistry {
  register(provider: LLMProvider): void
  active_provider(): LLMProvider
}
```

Adding "whatever meeting platform" = implement `Source`. Adding a target = implement
`Sink`. Adding a model backend = implement `LLMProvider` and register it.
The core and orchestration never change for any of these.

**`Decision: open`** — whether the deterministic fast-path (explicit `TODO:` syntax)
is a second `Extractor` implementation or a pre-filter in orchestration. Lean:
pre-filter, so the LLM extractor stays single-purpose.

---
