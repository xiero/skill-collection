# GoogleTest / gmock Patterns

## Test shape

```cpp
TEST(RingBuffer, Push_WhenFull_RejectsAndKeepsCount) {
  // Arrange
  rb_t rb; rb_init(&rb);
  fill_to_capacity(&rb);
  // Act
  bool ok = rb_push(&rb, 0x42);
  // Assert
  EXPECT_FALSE(ok);
  EXPECT_EQ(RB_CAPACITY, rb_count(&rb));
}
```

- **Name:** `TEST(Module, Action_WhenCondition_ExpectsResult)`. Reads cleanly in CI logs.
- **`EXPECT_*` vs `ASSERT_*`:** `EXPECT_` keeps running and reports every failure; `ASSERT_` aborts the current test. Use `ASSERT_` only when continuing would dereference garbage (e.g. right after a not-null check). Pattern: `ASSERT` the precondition, then `EXPECT` the details.
- Use unsigned literals (`0u`, `RB_CAPACITY`) when comparing against `size_t`/unsigned to avoid signed/unsigned warnings that become errors under `-Werror`.

## Fixtures (TEST_F)

Use when several tests share fake reset + buffers:

```cpp
class ParserTest : public ::testing::Test {
protected:
  parser_t p;
  void SetUp() override {
    RESET_FAKE(hal_uart_write);
    FFF_RESET_HISTORY();
    parser_init(&p);
  }
};
TEST_F(ParserTest, Decode_EmptyFrame_ReportsIncomplete) { /* ... */ }
```

## Parameterized tests (TEST_P) for boundary tables

Don't copy-paste the 0/1/N-1/N/N+1 cases — table them:

```cpp
struct LenCase { size_t len; bool expect_ok; };

class WriteLenTest : public ::testing::TestWithParam<LenCase> {};

TEST_P(WriteLenTest, RespectsCapacity) {
  uint8_t dst[8];
  const auto& c = GetParam();
  EXPECT_EQ(c.expect_ok, buf_write(dst, sizeof(dst), c.len));
}

INSTANTIATE_TEST_SUITE_P(Boundaries, WriteLenTest, ::testing::Values(
  LenCase{0, true}, LenCase{7, true}, LenCase{8, true},
  LenCase{9, false}, LenCase{SIZE_MAX, false}));
```

## Typed tests for width matrices

When the same logic must hold across `uint8_t/uint16_t/uint32_t` (e.g. a generic wraparound):

```cpp
template <typename T> class WrapTest : public ::testing::Test {};
using WidthTypes = ::testing::Types<uint8_t, uint16_t, uint32_t>;
TYPED_TEST_SUITE(WrapTest, WidthTypes);
TYPED_TEST(WrapTest, IncrementPastMaxWrapsToZero) {
  TypeParam v = std::numeric_limits<TypeParam>::max();
  EXPECT_EQ(TypeParam{0}, static_cast<TypeParam>(v + 1));
}
```

## Asserting on buffers/arrays

Use matchers, not hand loops:

```cpp
#include "gmock/gmock.h"
using ::testing::ElementsAreArray;
using ::testing::Pointwise;
using ::testing::Eq;

uint8_t expected[] = {0x7D, 0x5E, 0x10};
EXPECT_THAT(std::vector<uint8_t>(out, out + out_len), ElementsAreArray(expected));
```

## gmock — only for real C++ interfaces

If the collaborator is an abstract C++ class (virtual methods), mock it with gmock. (Plain C HAL → FFF, not this.)

```cpp
class ITransport {
 public:
  virtual ~ITransport() = default;
  virtual int send(const uint8_t* d, size_t n) = 0;
};
class MockTransport : public ITransport {
 public:
  MOCK_METHOD(int, send, (const uint8_t* d, size_t n), (override));
};

TEST(Proto, RetriesThenGivesUp) {
  MockTransport t;
  using ::testing::Return;
  EXPECT_CALL(t, send(::testing::_, ::testing::_))
      .Times(3)
      .WillRepeatedly(Return(-1));
  EXPECT_FALSE(proto_send(&t, payload, len));   // 3 failed attempts -> false
}
```

- `EXPECT_CALL` sets an expectation verified at mock destruction. `ON_CALL` only sets behavior without requiring the call.
- Matchers: `_`, `Eq()`, `Pointee()`, `ElementsAreArray()`. Use them to assert the bytes sent.

## Floating point / fixed point

If the unit does float or fixed-point math, never `EXPECT_EQ` on floats:

```cpp
EXPECT_NEAR(expected, actual, 1e-4);   // pick tolerance from the fixed-point resolution
EXPECT_FLOAT_EQ(a, b);                 // 4-ULP tolerance
```

## Portability: death tests are host-only

Death tests fork — not available on target/simulator builds. Guard them:

```cpp
#if defined(GTEST_HAS_DEATH_TEST) && !defined(TARGET_BUILD)
TEST(ConfigDeathTest, NullPointerAborts) {
  EXPECT_DEATH(config_apply(nullptr), "");
}
#endif
```

Prefer testing the *error return* path (host + target) over the abort path (host only) whenever the API offers one. Name death-test suites `*DeathTest` so GoogleTest runs them first.
