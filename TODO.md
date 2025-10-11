# Epistemic Fortitude - HealthBench Experiment TODO

## Phase 1: Research & Setup

- [x] Research ADK programmatic invocation methods
- [x] Create project structure (utils/, logs/experiments/ folders)
- [x] Test invoking epistemic_coordinator with session state

## Phase 2: Single Example Validation

- [x] Load and parse 1 HealthBench example from JSONL
- [x] Build simple ADK client wrapper for single example
- [x] Test multi-turn conversation replay with 1 example
- [x] Verify agent responses and debug issues

## Phase 3: Logging Infrastructure

- [ ] Design comprehensive log JSON schema
- [ ] Build experiment logger (utils/experiment_logger.py)
- [ ] Add token counting and latency tracking
- [ ] Test logging with 1 example end-to-end

## Phase 4: Scale to 100 Examples

- [ ] Build main experiment runner (scripts/run_healthbench_experiment.py)
- [ ] Implement multi-turn conversation handler
- [ ] Add error handling and retry logic
- [ ] Test with 10 examples first

## Phase 5: Run Both Experiments

- [ ] Run baseline experiment (ENABLE_ARBITER=false, 100 examples)
- [ ] Run arbiter experiment (ENABLE_ARBITER=true, same 100 examples)
- [ ] Verify both log sets are complete

## Phase 6: Rubric Scoring (Separate Script)

- [ ] Build LLM-as-judge rubric scorer (scripts/score_rubrics.py)
- [ ] Score baseline experiment logs
- [ ] Score arbiter experiment logs
- [ ] Validate scoring on sample (manual review)

## Phase 7: Comparison & Analysis

- [ ] Build comparison script (scripts/compare_experiments.py)
- [ ] Calculate score deltas and statistical tests
- [ ] Generate summary metrics and tables
- [ ] Create visualizations (optional)

---

## Notes

- Use same 100 examples for both baseline and arbiter runs
- Log format: One JSON file per conversation
- Token counting: Extract from Gemini API response
- Rubric scoring: Use LLM-as-judge (Gemini API)

---

Last updated: 2025-10-11
