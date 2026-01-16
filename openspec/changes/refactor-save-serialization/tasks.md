## 1. Implementation
- [x] 1.1 Define persistence snapshot dataclasses and conversion helpers
- [x] 1.2 Update save serialization to use snapshot dataclasses and `asdict`
- [x] 1.3 Add load support for version 1 and version 2 payloads (migration mapping)
- [x] 1.4 Adjust RNG state serialization to be encapsulated in snapshot helpers
- [x] 1.5 Update slot index persistence tests if schema changes impact them
- [x] 1.6 Add regression tests covering v1 load, v2 save, and determinism after load
- [x] 1.7 Update documentation/comments for persistence schema and versioning
