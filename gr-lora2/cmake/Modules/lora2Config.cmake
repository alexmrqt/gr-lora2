INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_LORA2 lora2)

FIND_PATH(
    LORA2_INCLUDE_DIRS
    NAMES lora2/api.h
    HINTS $ENV{LORA2_DIR}/include
        ${PC_LORA2_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    LORA2_LIBRARIES
    NAMES gnuradio-lora2
    HINTS $ENV{LORA2_DIR}/lib
        ${PC_LORA2_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(LORA2 DEFAULT_MSG LORA2_LIBRARIES LORA2_INCLUDE_DIRS)
MARK_AS_ADVANCED(LORA2_LIBRARIES LORA2_INCLUDE_DIRS)

