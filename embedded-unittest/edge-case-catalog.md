# Embedded Hazard Catalog

Apply only the categories the function's types implicate (see SKILL.md step 3). For each relevant category, generate the listed cases as concrete tests. Each bullet is a *behavior to verify*, phrased so you can name the test after it.

## 1. Strings & character buffers

The classic firmware bugs. Trigger when the unit takes/returns `char*`, fills a text buffer, or formats output.

- **`strncpy` does not null-terminate** when the source is >= the buffer. Verify the unit terminates explicitly: feed a source exactly `len` long and assert `buf[len-1] == '\0'`.
- **Buffer size includes the terminator.** A "32-char" buffer holds 31 chars + `\0`. Test the input that is exactly `capacity-1`, exactly `capacity`, and `capacity+1` long.
- **`snprintf` return value is the *would-be* length**, not bytes written. If the unit uses it to advance a cursor, feed input that truncates and assert the cursor / length is clamped, not advanced past the buffer.
- **Empty string vs. single `'\0'` vs. missing terminator.** Pass a non-terminated input region (fill with non-zero, no `\0`) and assert the unit respects the explicit length and never reads past it.
- **Embedded NUL inside the payload** when the data is binary-but-treated-as-string: assert length-based handling, not `strlen`.
- **Truncation reports.** If the API signals truncation (return code / out-param), assert it fires at the boundary and the output is still terminated.

## 2. Buffers & boundaries (ring buffers, FIFOs, packet buffers)

Trigger on any fixed-size buffer, index, head/tail, or write-into-caller-buffer.

- **Off-by-one at both ends.** Write `N-1`, `N`, and `N+1` elements into an `N`-capacity buffer; assert the `N+1` case rejects/clamps and never writes element `N`.
- **Ring buffer full-vs-empty ambiguity.** `head == tail` can mean empty *or* full depending on scheme. Test: fill to capacity, then read all, asserting count is correct at each step and full != empty.
- **Wrap-around correctness.** Advance head/tail past the end so they wrap; push/pop across the wrap point and assert ordering (FIFO stays FIFO) and that the wrapped region isn't corrupted.
- **Exactly-fits vs. one-too-small destination.** When writing into a caller buffer, test a destination that is exactly big enough and one byte too small; the too-small case must not overflow.
- **Zero-capacity / zero-length** calls are no-ops, not crashes.

## 3. Integers & arithmetic

Trigger on fixed-width counters, indices, checksums, timers, sizes.

- **Fixed-width wraparound.** Increment a `uint8_t` past 255 (→ 0) / `uint16_t` past 65535; assert the unit's behavior at the wrap is intended (saturate vs. roll over).
- **Signed/unsigned mixing & negative→unsigned conversion.** Pass a negative value where a `size_t`/`uint*` is expected (e.g. `-1` becoming a huge length) and assert it's rejected, not used as a giant size.
- **Implicit integer promotion.** Operations on `uint8_t`/`uint16_t` promote to `int`; a mask/shift may not behave as the narrow type. Test values where the difference shows (`(uint8_t)0xFF << 8`, top-bit shifts).
- **Boundary values:** `0`, `1`, `MAX-1`, `MAX`, and `MAX+1` (wrapped) for the relevant width; `SIZE_MAX` for sizes.
- **Checksum/CRC edges:** all-zero input, all-`0xFF` input, single-bit change flips the checksum, and the checksum of an empty buffer.

## 4. Protocol framing & escaping

Trigger when the unit parses/builds a byte stream, frames packets, or escapes/unescapes (SLIP, COBS, byte-stuffing, AT-command escapes).

- **Escape sequence in payload.** A payload byte equal to the frame delimiter or escape byte must be escaped on encode and restored on decode (round-trip test: `decode(encode(x)) == x` for payloads containing the special bytes).
- **Escape/delimiter split across reads.** Feed the frame in two chunks that split right on an escape byte or delimiter; assert the parser holds state and reassembles correctly.
- **Truncated / partial frame.** Delimiter never arrives, or arrives mid-escape; assert the parser waits / reports incomplete instead of emitting garbage.
- **Back-to-back frames** in one buffer; assert both are parsed and no bytes are dropped between them.
- **Spurious delimiters / control chars** (`\r`, `\n`, `0x00`, `0x1B`) inside binary payload are treated as data when escaped, as control when not.
- **Max-length frame and overlong frame**: at limit succeeds, over limit is rejected without overflow.

## 5. Memory & no-heap invariants

Trigger on no-heap modules, static pools, fixed allocators.

- **No dynamic allocation occurs.** Where the project forbids the heap, assert it: override/instrument `operator new`/`malloc` to fail or count, and assert zero calls.
- **Static pool exhaustion.** Allocate from a fixed pool until empty; assert the next request fails gracefully (null / error), and that freeing then allows reuse.
- **Double-free / use-after-free of pool slots** is detected or prevented, where the API allows checking.
- **Alignment.** If the unit hands out memory or casts buffers to structs, assert returned pointers meet the type's alignment.

## 6. Concurrency, ISR & volatile (unit-testable slices only)

You can't truly test races in a host unit test, but you can test the *logic* that guards them.

- **Reentrancy of the consumer.** Simulate "ISR ran mid-update" by having a fake invoke the producer path (via `custom_fake`) during a consume, and assert no item is lost/duplicated.
- **Critical-section pairing.** Fake the enter/exit-critical HAL calls and assert they're balanced (equal call counts) and that the protected section calls them around the right region.
- **Volatile-flag handshakes.** Drive a `volatile` flag the way an ISR would (set it from a fake) and assert the polling code observes and clears it exactly once.

## 7. State machines & timeouts

Trigger on explicit state machines, retry logic, timeouts, debouncing.

- **Every transition** from the spec: for each state, each input → assert resulting state and side effects (which fakes were called).
- **Illegal input in each state** is ignored or errors, never silently corrupts state.
- **Timeout boundary.** Fake the tick/clock; assert the timeout fires at exactly the threshold (`t == limit`), not before (`t == limit-1`) and not skipped.
- **Retry exhaustion.** Assert it retries exactly N times then gives up, and that a success on the last attempt is honored.

## Universal cases (always include)

Regardless of category, add: **null pointer**, **zero length**, **empty input**, **single element**, and **maximum supported size**. These four lines catch a startling share of real defects.
