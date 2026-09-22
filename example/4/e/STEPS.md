# 4/e — DELETE, step by step

1. **Check the index exists first** — the same bounds check as every
   other route in this topic.

2. **`status_code=status.HTTP_204_NO_CONTENT`** on the decorator — `204`
   means "it worked, and there's nothing to send back." The function
   doesn't `return` anything at all; a `204` response has no body by
   convention.

3. **`data.pop(item_index)`** — removes that one entry, shifting
   everything after it down by one position. That's why indexes aren't
   stable identifiers in a plain list — deleting index `0` makes the old
   index `1` become the new index `0`. A real database uses a fixed ID
   per row instead, precisely to avoid this.
