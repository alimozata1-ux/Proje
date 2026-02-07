cmake_minimum_required(VERSION 3.10)
project(SystemWidget LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(system_widget WIN32 src/main.cpp)

if (WIN32)
    target_link_libraries(system_widget PRIVATE user32 gdi32)
endif()
