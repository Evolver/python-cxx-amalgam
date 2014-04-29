
#include <first.hpp>
#   include <first.hpp>
    #include <second/my-header.hpp>
#include "includes2/second/my-header.hpp"  // some comment
#include <iostream> /* not to be expanded */

int main( int, char** )
{
    std::cout << "Hello, World!" << std::endl;
    #include "third.hpp"
    return 0;
}
