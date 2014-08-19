#include <stdexcept>
#include "gtest/gtest.h"

namespace {

// The fixture for testing class Foo.
class FooTest : public ::testing::Test {
};

// Tests that the Foo::Bar() method does Abc.
TEST_F(FooTest, test_success) {
  EXPECT_EQ(2 * 3, 6);
}

// Tests that the Foo::Bar() method does Abc.
TEST_F(FooTest, test_failure) {
  EXPECT_EQ(2 * 3, 5);
  EXPECT_EQ(2 * 6, 15);
}

// Tests that the Foo::Bar() method does Abc.
TEST_F(FooTest, test_error) {
  throw std::runtime_error("unexpected exception");
}

// Tests that the Foo::Bar() method does Abc.
TEST_F(FooTest, DISABLED_test_disabled) {
  EXPECT_EQ(2 * 6, 10);
}


}  // namespace

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

