@echo off
if not defined FLS_ACTIVE_THIRD_PARTY_LIBS_DIR (
  set FLS_THIRD_PARTY_COMPILER_DIR=%FSL_GRAPHICS_SDK_THIRD_PARTY_LIBS_DIR%\Windows\VS2015_X64
  echo WARNING: FLS_ACTIVE_THIRD_PARTY_LIBS_DIR was not defined, taking a educated guess.
)
echo %FLS_ACTIVE_THIRD_PARTY_LIBS_DIR%

set FSL_GLES_EMULATOR_PATH=%FLS_ACTIVE_THIRD_PARTY_LIBS_DIR%\openvg-ri
set FSL_GLES_INCLUDE_PATH=%FSL_GLES_EMULATOR_PATH%\include
set FSL_GLES_LIB_PATH=%FSL_GLES_EMULATOR_PATH%\lib
set FSL_GLES_LIB_EGL=libEGL.lib
set FSL_GLES_LIB_GLES=libOpenVG.lib
set FSL_GLES_NAME=OpenVGReference