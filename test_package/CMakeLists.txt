PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

find_package("M4")

IF(M4_FOUND)
    ADD_EXECUTABLE(enough enough.c)
    include_directories(${M4_INCLUDE_DIRS})
    TARGET_LINK_LIBRARIES(enough ${M4_LIBRARIES})
ELSE()
    MESSAGE(FATAL_ERROR "M4 not found")
ENDIF()
