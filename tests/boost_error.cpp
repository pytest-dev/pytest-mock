#include <stdexcept>
#define BOOST_TEST_MODULE MyTest
#include <boost/test/included/unit_test.hpp>

BOOST_AUTO_TEST_CASE( test_error_1 )
{
    throw std::runtime_error("unexpected exception");
}

BOOST_AUTO_TEST_CASE( test_error_2 )
{
    throw std::runtime_error("another unexpected exception");
}

