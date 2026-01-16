## 1. Implementation
- [ ] 1.1 Define persistence snapshot dataclasses and conversion helpers
- [ ] 1.2 Update save serialization to use snapshot dataclasses and `asdict`
- [ ] 1.3 Add load support for version 1 and version 2 payloads (migration mapping)
- [ ] 1.4 Adjust RNG state serialization to be encapsulated in snapshot helpers
- [ ] 1.5 Update slot index persistence tests if schema changes impact them
- [ ] 1.6 Add regression tests covering v1 load, v2 save, and determinism after load
- [ ] 1.7 Update documentation/comments for persistence schema and versioning
