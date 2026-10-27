# State Reducers

Control how state updates combine instead of overwriting each other.
By default, when two nodes write to the same field, the second one
wins — so the fraud screen's signals vanish the moment the AVS check
reports. A reducer is a function attached to a field that says how to
merge an incoming update — append to a list, sum numbers, merge
dicts, keep the max, and so on — so every payment check's signals land
in one authorization state.

What you'll see:

- `Annotated[type, reducer]` on a Pydantic state schema declares the rule.
- Built-in reducers: `add_messages`, `add_numbers`, `merge_dict`,
  `append_list`, `last_value`.
- `@reducer` turns any `(current, new) -> merged` function into a custom one.
- Multiple reducers on one schema — each field merges independently.
- Two LLM-producing nodes appending to the same case log.

Runs on the same default (mock) as the rest of the notebooks:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_14_state_reducers.py
# or, the zero-setup default (mock):
LOCUS_MODEL_PROVIDER=mock python examples/notebook_14_state_reducers.py
```

## Source

````python
--8<-- "examples/notebook_14_state_reducers.py"
````
