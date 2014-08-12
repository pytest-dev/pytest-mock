cl boost.cpp /I x:\boost-1_56_0_b1\  /EHsc
cl gtest.cpp /I x:\gtest-1.7.0\include /EHsc /link /LIBPATH:x:\gtest-1.7.0\Release gtest.lib
