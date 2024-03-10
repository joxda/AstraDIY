cmake_minimum_required(VERSION 2.4.7)
PROJECT(indi-astralim-diy CXX C)

LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/")

include(GNUInstallDirs)

set (VERSION_MAJOR 2)
set (VERSION_MINOR 10)

find_package(INDI REQUIRED)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/config.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/config.h)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/indi_astralim_system.xml.cmake ${CMAKE_CURRENT_BINARY_DIR}/indi_astralim_system.xml)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/indi_astralim_focuser.xml.cmake ${CMAKE_CURRENT_BINARY_DIR}/indi_astralim_focuser.xml)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/indi_astralim_relays.xml.cmake ${CMAKE_CURRENT_BINARY_DIR}/indi_astralim_relays.xml)

include_directories(${CMAKE_CURRENT_BINARY_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR})
include_directories(${INDI_INCLUDE_DIR})

include(CMakeCommon)

set(GPIO_LIBRARIES "libgpiod.so")

################ astralim System ################
set(indi_astralim_system_SRCS
        ${CMAKE_CURRENT_SOURCE_DIR}/astralim_system.cpp
   )

IF (UNITY_BUILD)
    ENABLE_UNITY_BUILD(indi_astralim_system indi_astralim_system_SRCS 6 cpp)
ENDIF ()

add_executable(indi_astralim_system ${indi_astralim_system_SRCS})
target_link_libraries(indi_astralim_system ${INDI_LIBRARIES})
install(TARGETS indi_astralim_system RUNTIME DESTINATION bin )
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/indi_astralim_system.xml DESTINATION ${INDI_DATA_DIR})

################ astralim Focuser ################
set(indi_astralim_focuser_SRCS
        ${CMAKE_CURRENT_SOURCE_DIR}/astralim_focuser.cpp
   )

IF (UNITY_BUILD)
    ENABLE_UNITY_BUILD(indi_astralim_focuser indi_astralim_focuser_SRCS 6 cpp)
ENDIF ()

add_executable(indi_astralim_focuser ${indi_astralim_focuser_SRCS})
target_link_libraries(indi_astralim_focuser ${INDI_DRIVER_LIBRARIES} ${GPIO_LIBRARIES})
install(TARGETS indi_astralim_focuser RUNTIME DESTINATION bin )
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/indi_astralim_focuser.xml DESTINATION ${INDI_DATA_DIR})

################ astralim Relays ################
set(indi_astralim_relays_SRCS
        ${CMAKE_CURRENT_SOURCE_DIR}/astralim_relays.cpp
   )

IF (UNITY_BUILD)
    ENABLE_UNITY_BUILD(indi_astralim_relays indi_astralim_relays_SRCS 6 cpp)
ENDIF ()

add_executable(indi_astralim_relays ${indi_astralim_relays_SRCS})
target_link_libraries(indi_astralim_relays ${INDI_LIBRARIES} ${GPIO_LIBRARIES})
install(TARGETS indi_astralim_relays RUNTIME DESTINATION bin )
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/indi_astralim_relays.xml DESTINATION ${INDI_DATA_DIR})
