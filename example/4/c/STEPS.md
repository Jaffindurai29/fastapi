# 4/c — PUT, step by step

1. **Check the index exists first** — same bounds check as
   [4/a](../a/STEPS.md), so an out-of-range `PUT` returns a clean `404`
   instead of crashing.

2. **`data[item_index] = value`** — overwrites that slot entirely.
   `PUT` means "here is the complete new representation of this
   resource" — the client sends the whole value, not just the part
   that changed. `value` is a query parameter here (same style as
   [4/b](../b/STEPS.md)), not a JSON body.

3. **Compare to [4/d — PATCH](../d/STEPS.md)** next: same idea, but the
   client can send only what it wants to change.
