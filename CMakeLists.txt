cmake_minimum_required(VERSION 3.16)
project(NeonBrowser LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets WebEngineWidgets)

add_executable(neon_browser
    src/main.cpp
    src/browser_window.h
    src/browser_window.cpp
    src/settings_dialog.h
    src/settings_dialog.cpp
)

target_link_libraries(neon_browser PRIVATE Qt6::Widgets Qt6::WebEngineWidgets)

if (WIN32)
    set_target_properties(neon_browser PROPERTIES WIN32_EXECUTABLE TRUE)
endif()

install(TARGETS neon_browser RUNTIME DESTINATION .)
