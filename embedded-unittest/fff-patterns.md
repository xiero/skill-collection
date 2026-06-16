# FFF (Fake Function Framework) Patterns

FFF fakes plain C functions — exactly what a HAL/driver/RTOS layer exposes. Header-only, works on host and target.

## Setup (once per test binary)

In exactly one translation unit:

```cpp
#include "fff.h"
DEFINE_FFF_GLOBALS;   // exactly once across the whole test binary
```

## Declaring fakes

Match the real signature exactly. Value-returning vs. void are different macros:

```cpp
// HAL: int hal_uart_write(uint8_t channel, const uint8_t* data, size_t len);
FAKE_VALUE_FUNC(int, hal_uart_write, uint8_t, const uint8_t*, size_t);

// HAL: void hal_gpio_set(uint8_t pin, bool level);
FAKE_VOID_FUNC(hal_gpio_set, uint8_t, bool);

// variadic: use the _VARARG variants
FAKE_VALUE_FUNC_VARARG(int, hal_log, const char*, ...);
```

The fake **replaces** the real symbol at link time. Don't also link the real .c — that's a duplicate-symbol error. (On target, link the fake's TU instead of the driver.)

## Reset in the fixture — non-negotiable

FFF state is global and persists across tests. Reset it or get order-dependent flakes:

```cpp
class UartTest : public ::testing::Test {
protected:
  void SetUp() override {
    RESET_FAKE(hal_uart_write);
    RESET_FAKE(hal_gpio_set);
    FFF_RESET_HISTORY();
  }
};
```

## Controlling return values

```cpp
hal_uart_write_fake.return_val = 0;                 // always returns 0

uint8_t  rx[] = {0xAA, 0xBB};
int      seq[] = {1, 1, 0};                          // 1st call→1, 2nd→1, 3rd→0, then last repeats
SET_RETURN_SEQ(hal_uart_write, seq, 3);
```

## Asserting how it was called

```cpp
EXPECT_EQ(1u, hal_uart_write_fake.call_count);
EXPECT_EQ(2u, hal_gpio_set_fake.arg0_val);           // last call's first arg
EXPECT_TRUE(hal_gpio_set_fake.arg1_val);

// per-call history:
EXPECT_EQ(3u, hal_gpio_set_fake.arg0_history[0]);    // first call's pin
EXPECT_EQ(5u, hal_gpio_set_fake.arg0_history[1]);    // second call's pin

// call ordering across multiple fakes:
EXPECT_EQ(hal_enter_critical_fake.call_count, hal_exit_critical_fake.call_count);
```

## The #1 trap: pointer args capture the pointer, not the bytes

`argN_history` stores the **pointer value**. If the caller reuses or frees that buffer, your assertion reads the wrong data. To assert on the *contents* the fake received, copy them in a `custom_fake`:

```cpp
static uint8_t  captured[64];
static size_t   captured_len;

static int capture_uart_write(uint8_t ch, const uint8_t* data, size_t len) {
  captured_len = (len <= sizeof(captured)) ? len : sizeof(captured);
  memcpy(captured, data, captured_len);
  return 0;
}

TEST_F(UartTest, SendsEscapedFrameBytes) {
  hal_uart_write_fake.custom_fake = capture_uart_write;   // reset clears this too
  // ... act ...
  ASSERT_EQ(3u, captured_len);
  EXPECT_EQ(0x7D, captured[0]);   // escaped delimiter
}
```

The same pattern handles **out-parameters**: a `custom_fake` writes into the caller's `*out` buffer to simulate a peripheral returning data.

```cpp
static int fake_read_byte(uint8_t* out) { *out = 0x42; return 1; }
hal_read_byte_fake.custom_fake = fake_read_byte;
```

## custom_fake + return sequence together

`custom_fake` takes priority over `return_val`. If you need both behavior and a return sequence, encode the return inside the custom fake, or use `custom_fake_seq` for per-call custom fakes.

## Notes

- Function pointers and callbacks the unit registers: capture them via a `custom_fake` on the register function, then invoke the captured callback in the test to simulate the event/ISR.
- Keep custom fakes free of host-only syscalls so the test TU still links on target.
