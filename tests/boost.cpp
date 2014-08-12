#include <stdexcept>
#define BOOST_TEST_MODULE MyTest
#include <boost/test/included/unit_test.hpp>

BOOST_AUTO_TEST_CASE( test_success )
{
    BOOST_CHECK( 2 * 3 == 6 );
}

BOOST_AUTO_TEST_CASE( test_failure )
{
    BOOST_CHECK( 2 * 3 == 5 );
}

BOOST_AUTO_TEST_CASE( test_error )
{
    throw std::runtime_error("unexpected exception");
}

