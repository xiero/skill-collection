---
name: embedded-cpp-unit-tests
description: Write GoogleTest unit tests for embedded C/C++ code, with FFF fakes for the HAL and gmock for C++ interfaces. Use this whenever the user wants tests for firmware, driver, protocol-parser, ring-buffer, state-machine, or any MCU-targeted C/C++ function — and especially when correctness depends on embedded-specific hazards like string null-termination, buffer/boundary overflow, fixed-width integer wraparound, byte-stuffing/escape framing, endianness, no-heap invariants, or ISR/volatile concerns. Trigger this even when the user just says "write tests for this function", "add coverage", "test this driver/parser", or pastes a .c/.cpp/.h with embedded types (uint8_t, volatile, packed structs, char buffers). Tests must stay portable across host (x86) and target/simulator builds.
---

# Embedded C/C++ Unit Tests (GoogleTest + FFF)

Generate **runnable, portable** unit tests for embedded code. The value of this skill is not "produce a test file" — Claude can do that already. The value is systematically applying the embedded hazard catalog so the generated tests catch the bugs that actually ship in firmware (truncated strings, off-by-one ring buffers, `uint8_t` wraparound, escape sequences split across frame boundaries) instead of only the happy path.

## Stack assumptions

- **Runner / assertions:** GoogleTest (C++17/20/23).
- **C HAL faking:** FFF (Fake Function Framework). C HAL/driver/RTOS functions are plain C functions — gmock cannot mock them (it needs virtual methods), so fake them with FFF.
- **C++ collaborators:** gmock, only when there is an actual C++ interface (abstract class / virtual methods) to mock.
- **Execution:** tests must compile and pass on **both** host (x86) and target/simulator (QEMU, Renode). Keep host-only features out of the shared test body (see Portability).

## Workflow

Do these in order. Don't skip recon — matching the project's existing conventions matters more than any default this skill prescribes.

### 1. Recon the unit and the project

- Read the function/module under test. Note the **exact types** in every signature: pointer + length pairs, `char*`, fixed-width ints (`uint8_t/uint16_t/...`), `size_t`, `bool`, enums, packed/`volatile` structs, function pointers.
- Identify every **external dependency** the unit calls: HAL functions, RTOS calls, ISR hooks, other modules. These become fakes.
- Find existing tests (`test_*.cpp`, `*_test.cc`, a `test/` or `tests/` dir, a Ceedling/CMake setup). **Match their conventions**: file naming, fixture style, where fakes are declared, the build system, the include layout. If conventions exist, they win over this skill's examples.
- Determine the build wiring you'll need to mention (a CMake test target, or how the file slots into the existing harness). Don't invent a build system if one exists.

### 2. Plan the fakes

For each external **C** function the unit calls, plan an FFF fake. For each **C++ interface**, plan a gmock mock. See `references/fff-patterns.md` for the mechanics (declaration, reset, return sequences, argument capture, custom fakes for pointer/out-params). Two rules that bite people:

- **Reset every fake in `SetUp()`** (`RESET_FAKE(x)`) and call `FFF_RESET_HISTORY()`. Leaked state across tests produces flaky, order-dependent passes.
- FFF's `argN_history` captures the **pointer**, not the pointed-to bytes. To assert on buffer *contents* a fake received, copy them in a `custom_fake`. This is the single most common FFF mistake.

### 3. Select edge cases from the hazard catalog — by type, not by rote

Open `references/edge-case-catalog.md` and apply only the categories the signature actually implicates. Don't dump every case onto every function; pick what the types justify, e.g.:

- `char* / size_t len` present → string termination + buffer boundary cases.
- `uint8_t/uint16_t` counters, indices, checksums → wraparound / overflow cases.
- parses a byte stream / builds a frame → framing, byte-stuffing, escape, split-across-reads cases.
- writes into a caller buffer → off-by-one and "exactly fits / one too small" cases.
- no-heap module → allocation-failure / static-pool-exhaustion cases.
- `volatile` / shared-with-ISR state → reentrancy / ordering cases (where unit-testable).

Always include the universal boundaries: null pointer, zero length, empty input, single element, and the maximum supported size.

### 4. Write the tests

Follow `references/gtest-patterns.md`. Core conventions:

- **AAA layout** (Arrange / Act / Assert), one logical behavior per test.
- **Descriptive names**: `TEST(Module, Behavior_WhenCondition_ExpectsResult)` — readable in CI output without opening the file.
- `EXPECT_*` by default (keep going to report all failures); `ASSERT_*` only when continuing would crash or assert on garbage (e.g. after a null check).
- Use a **fixture** (`TEST_F`) when several tests share fake setup / buffers.
- Use **parameterized tests** (`TEST_P`) for boundary tables (lengths 0,1,N-1,N,N+1) instead of copy-pasting.
- For buffer/array content assertions, use `::testing::ElementsAreArray` / `Pointwise`, not hand-rolled loops.
- Each test must be **deterministic and self-contained** — no reliance on previous-test state, no real time/delays (fake the tick).

### 5. Enforce portability (host + target)

Because tests run on both host and target, before finishing:

- **No GoogleTest death tests in the shared body** — they fork and are host-only. If a death/abort path must be tested, isolate it behind `#if defined(GTEST_HAS_DEATH_TEST) && !defined(TARGET_BUILD)` (or the project's equivalent guard) and say so.
- **No `int`-width assumptions.** Assert with fixed-width types and explicit literals (`uint16_t{0xFFFF}`), never assume `sizeof(int)`.
- **No host-only headers** in shared code; keep `<iostream>`/filesystem out of target paths.
- Keep fakes free of host-only syscalls so the same fake links on target.

### 6. Deliver

Output the runnable test file(s). Then in one short block, state: which fakes were created, which catalog categories you applied (and any you deliberately skipped and why), and the exact build line / target name needed to compile them. If something about the unit is untestable as written (hidden global state, no seam to inject the fake), say so and suggest the minimal seam.

## References

- `references/edge-case-catalog.md` — the embedded hazard catalog (strings, buffers, integers, framing/escape, memory/no-heap, concurrency/volatile, state/timeouts). Read this in step 3.
- `references/fff-patterns.md` — FFF fake mechanics: declaration, reset, return value sequences, call counts, argument history, capturing pointer/out-param contents via custom fakes. Read this in step 2.
- `references/gtest-patterns.md` — GoogleTest/gmock structure: fixtures, parameterized & typed tests, matchers for buffers, gmock for C++ interfaces, death-test portability guard. Read this in step 4.
