## 1. Implementation
- [ ] 1.1 Replace `*Definition` dataclasses with core model dataclasses and add `from_dict`/`to_dict` helpers.
- [ ] 1.2 Update data loaders to use the new helpers and standard `dataclasses.asdict`.
- [ ] 1.3 Update GameState/session initialization and any call sites referencing `*Definition` types.
- [ ] 1.4 Update tests to cover loading/serialization with the new model helpers.
- [ ] 1.5 Update documentation that references `*Definition` classes or the previous loading approach.
- [ ] 1.6 Run all tests and ensure they pass.
