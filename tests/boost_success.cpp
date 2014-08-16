#include <stdexcept>
#define BOOST_TEST_MODULE MyTest
#include <boost/test/included/unit_test.hpp>

BOOST_AUTO_TEST_CASE( test_success_1 )
{
    BOOST_CHECK( 2 * 3 == 6 );
}

BOOST_AUTO_TEST_CASE( test_success_2 )
{
    BOOST_CHECK( 4 * 3 == 12 );
}
