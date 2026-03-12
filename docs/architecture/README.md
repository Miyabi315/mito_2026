# Architecture Notes

This repository follows a separated pipeline:

1. `backend/extraction`: deterministic, rule-based parsing
2. `backend/graph`: care graph JSON generation
3. `backend/timeline`: process timeline generation
4. `frontend/*`: visualization only

Extraction outputs must preserve source evidence text.

