# 4/d — PATCH, step by step

1. **`value: Optional[str] = None`** makes the query parameter optional
   — unlike [4/c](../c/STEPS.md)'s `value: str`, which is required.
   That's the first difference between `PUT` and `PATCH`: PUT demands
   the full representation, PATCH lets you send only what changed.

2. **`if value is not None: data[item_index] += value`** — merges
   onto the existing value instead of overwriting it, and only runs at
   all if the client actually sent a value. Leaving `value` out of the
   request leaves the item untouched.

3. **`+=` instead of `=` is the point of this example** — with a
   single-field item, PUT and PATCH would otherwise look identical
   (both just set the one field). Making PATCH merge instead of
   replace is a stand-in for "update only part of the resource,"
   which is what PATCH means in real APIs once a resource has several
   fields.
