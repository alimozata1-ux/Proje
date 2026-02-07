cmake_minimum_required(VERSION 3.16)
project(SystemWidget LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(SystemWidget WIN32 main.cpp)
target_link_libraries(SystemWidget PRIVATE Comdlg32)
