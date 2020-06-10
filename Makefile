# Copyright (c) 2011-2020 Eric Froemling
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------

# This Makefile encompasses most high level functionality you should need when
# working with Ballistica. These build rules are also handy as reference or a
# starting point if you need specific funtionality beyond that exposed here.
# Targets in this top level Makefile do not expect -jX to be passed to them
# and generally handle spawning an appropriate number of child jobs themselves.

# Prefix used for output of docs/changelogs/etc. targets for use in webpages.
DOCPREFIX = "ballisticacore_"


################################################################################
#                                                                              #
#                                   General                                    #
#                                                                              #
################################################################################

# List targets in this Makefile and basic descriptions for them.
help:
	@tools/snippets makefile_target_list Makefile

PREREQS = .cache/checkenv .dir-locals.el \
  .mypy.ini .pycheckers .pylintrc .style.yapf .clang-format \
  .projectile .editorconfig

# Target that should be built before running most any other build.
# This installs tool config files, runs environment checks, etc.
prereqs: ${PREREQS}

prereqs-clean:
	@rm -rf ${PREREQS} .irony

# Build all assets for all platforms.
assets: prereqs
	@cd assets && make -j${CPUS}

# Build assets required for cmake builds (linux, mac)
assets-cmake: prereqs
	@cd assets && ${MAKE} -j${CPUS} cmake

# Build assets required for WINDOWS_PLATFORM windows builds.
assets-windows: prereqs
	@cd assets && ${MAKE} -j${CPUS} win-${WINDOWS_PLATFORM}

# Build assets required for Win32 windows builds.
assets-windows-Win32: prereqs
	@cd assets && ${MAKE} -j${CPUS} win-Win32

# Build assets required for x64 windows builds.
assets-windows-x64: prereqs
	@cd assets && ${MAKE} -j${CPUS} win-x64

# Build assets required for mac xcode builds
assets-mac: prereqs
	@cd assets && ${MAKE} -j${CPUS} mac

# Build assets required for ios.
assets-ios: prereqs
	@cd assets && ${MAKE} -j${CPUS} ios

# Build assets required for android.
assets-android: prereqs
	@cd assets && ${MAKE} -j${CPUS} android

# Clean all assets.
assets-clean:
	@cd assets && ${MAKE} clean

# Remove *ALL* files and directories that aren't managed by git
# (except for a few things such as localconfig.json).
clean:
	@${CHECK_CLEAN_SAFETY}
	@git clean -dfx ${ROOT_CLEAN_IGNORES}

# Show what clean would delete without actually deleting it.
clean-list:
	@${CHECK_CLEAN_SAFETY}
	@git clean -dnx ${ROOT_CLEAN_IGNORES}

# Tell make which of these targets don't represent files.
.PHONY: list prereqs prereqs-clean assets assets-cmake assets-windows \
  assets-windows-Win32 assets-windows-x64 \
  assets-mac assets-ios assets-android assets-clean \
 -clean-clean\
  clean clean-list


################################################################################
#                                                                              #
#                                    Prefab                                    #
#                                                                              #
################################################################################

# Prebuilt binaries for various platforms.

# Assemble & run a debug build for this platform.
prefab-debug: prefab-debug-build
	${${shell tools/snippets prefab_run_var debug}}

# Assemble & run a release build for this platform.
prefab-release: prefab-release-build
	${${shell tools/snippets prefab_run_var release}}

# Assemble a debug build for this platform.
prefab-debug-build:
	@tools/snippets make_prefab debug

# Assemble a release build for this platform.
prefab-release-build:
	@tools/snippets make_prefab release

# Assemble & run a server debug build for this platform.
prefab-server-debug: prefab-server-debug-build
	${${shell tools/snippets prefab_run_var server-debug}}

# Assemble & run a server release build for this platform.
prefab-server-release: prefab-server-release-build
	${${shell tools/snippets prefab_run_var server-release}}

# Assemble a server debug build for this platform.
prefab-server-debug-build:
	@tools/snippets make_prefab server-debug

# Assemble a server release build for this platform.
prefab-server-release-build:
	@tools/snippets make_prefab server-release

# Specific platform prefab targets:

RUN_PREFAB_MAC_DEBUG = cd build/prefab/mac/debug && ./ballisticacore

prefab-mac-debug: prefab-mac-debug-build
	@tools/snippets ensure_prefab_platform mac
	@${RUN_PREFAB_MAC_DEBUG}

prefab-mac-debug-build: prereqs assets-cmake \
 build/prefab/mac/debug/ballisticacore
	@${STAGE_ASSETS} -cmake build/prefab/mac/debug

build/prefab/mac/debug/ballisticacore: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_MAC_RELEASE = cd build/prefab/mac/release && ./ballisticacore

prefab-mac-release: prefab-mac-release-build
	@tools/snippets ensure_prefab_platform mac
	@${RUN_PREFAB_MAC_RELEASE}

prefab-mac-release-build: prereqs assets-cmake \
 build/prefab/mac/release/ballisticacore
	@${STAGE_ASSETS} -cmake build/prefab/mac/release

build/prefab/mac/release/ballisticacore: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_MAC_SERVER_DEBUG = cd build/prefab/mac-server/debug \
 && ./ballisticacore_server

prefab-mac-server-debug: prefab-mac-server-debug-build
	@tools/snippets ensure_prefab_platform mac
	@${RUN_PREFAB_MAC_SERVER_DEBUG}

prefab-mac-server-debug-build: prereqs assets-cmake \
 build/prefab/mac-server/debug/dist/ballisticacore_headless \
 build/prefab/mac-server/debug/ballisticacore_server \
 build/prefab/mac-server/debug/config_template.yaml \
 build/prefab/mac-server/debug/README.txt
	@${STAGE_ASSETS} -cmake-server build/prefab/mac-server/debug/dist

build/prefab/mac-server/debug/ballisticacore_server: \
 assets/src/server/ballisticacore_server.py
	@cp $< $@

build/prefab/mac-server/debug/config_template.yaml: \
 assets/src/server/config_template.yaml \
 tools/batools/build.py \
 tools/bacommon/servermanager.py
	@tools/snippets filter_server_config $< $@

build/prefab/mac-server/debug/README.txt: \
 assets/src/server/README.txt
	@cp $< $@

build/prefab/mac-server/debug/dist/ballisticacore_headless: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_MAC_SERVER_RELEASE = cd build/prefab/mac-server/release \
 && ./ballisticacore_server

prefab-mac-server-release: prefab-mac-server-release-build
	@tools/snippets ensure_prefab_platform mac
	@${RUN_PREFAB_MAC_SERVER_RELEASE}

prefab-mac-server-release-build: prereqs assets-cmake \
 build/prefab/mac-server/release/dist/ballisticacore_headless \
 build/prefab/mac-server/release/ballisticacore_server \
 build/prefab/mac-server/release/config_template.yaml \
 build/prefab/mac-server/release/README.txt
	@${STAGE_ASSETS} -cmake-server build/prefab/mac-server/release/dist

build/prefab/mac-server/release/ballisticacore_server: \
 assets/src/server/ballisticacore_server.py
	@cp $< $@

build/prefab/mac-server/release/config_template.yaml: \
 assets/src/server/config_template.yaml \
 tools/batools/build.py \
 tools/bacommon/servermanager.py
	@tools/snippets filter_server_config $< $@

build/prefab/mac-server/release/README.txt: \
 assets/src/server/README.txt
	@cp $< $@

build/prefab/mac-server/release/dist/ballisticacore_headless: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_LINUX_DEBUG = cd build/prefab/linux/debug && ./ballisticacore

prefab-linux-debug: prefab-linux-debug-build
	@tools/snippets ensure_prefab_platform linux
	@${RUN_PREFAB_LINUX_DEBUG}

prefab-linux-debug-build: prereqs assets-cmake \
 build/prefab/linux/debug/ballisticacore
	@${STAGE_ASSETS} -cmake build/prefab/linux/debug

build/prefab/linux/debug/ballisticacore: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_LINUX_RELEASE = cd build/prefab/linux/release && ./ballisticacore

prefab-linux-release: prefab-linux-release-build
	@tools/snippets ensure_prefab_platform linux
	@${RUN_PREFAB_LINUX_RELEASE}

prefab-linux-release-build: prereqs assets-cmake \
 build/prefab/linux/release/ballisticacore
	@${STAGE_ASSETS} -cmake build/prefab/linux/release

build/prefab/linux/release/ballisticacore: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_LINUX_SERVER_DEBUG = cd build/prefab/linux-server/debug \
 && ./ballisticacore_server

prefab-linux-server-debug: prefab-linux-server-debug-build
	@tools/snippets ensure_prefab_platform linux
	@${RUN_PREFAB_LINUX_SERVER_DEBUG}

prefab-linux-server-debug-build: prereqs assets-cmake \
 build/prefab/linux-server/debug/dist/ballisticacore_headless \
 build/prefab/linux-server/debug/ballisticacore_server \
 build/prefab/linux-server/debug/config_template.yaml \
 build/prefab/linux-server/debug/README.txt
	@${STAGE_ASSETS} -cmake-server build/prefab/linux-server/debug/dist

build/prefab/linux-server/debug/ballisticacore_server: \
 assets/src/server/ballisticacore_server.py
	@cp $< $@

build/prefab/linux-server/debug/config_template.yaml: \
 assets/src/server/config_template.yaml \
 tools/batools/build.py \
 tools/bacommon/servermanager.py
	@tools/snippets filter_server_config $< $@

build/prefab/linux-server/debug/README.txt: \
 assets/src/server/README.txt
	@cp $< $@

build/prefab/linux-server/debug/dist/ballisticacore_headless: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_LINUX_SERVER_RELEASE = cd build/prefab/linux-server/release \
 && ./ballisticacore_server

prefab-linux-server-release: prefab-linux-server-release-build
	@tools/snippets ensure_prefab_platform linux
	@${RUN_PREFAB_LINUX_SERVER_RELEASE}

prefab-linux-server-release-build: prereqs assets-cmake \
 build/prefab/linux-server/release/dist/ballisticacore_headless \
 build/prefab/linux-server/release/ballisticacore_server \
 build/prefab/linux-server/release/config_template.yaml \
 build/prefab/linux-server/release/README.txt
	@${STAGE_ASSETS} -cmake-server build/prefab/linux-server/release/dist

build/prefab/linux-server/release/ballisticacore_server: \
 assets/src/server/ballisticacore_server.py
	@cp $< $@

build/prefab/linux-server/release/config_template.yaml: \
 assets/src/server/config_template.yaml \
 tools/batools/build.py \
 tools/bacommon/servermanager.py
	@tools/snippets filter_server_config $< $@

build/prefab/linux-server/release/README.txt: \
 assets/src/server/README.txt
	@cp $< $@

build/prefab/linux-server/release/dist/ballisticacore_headless: .efrocachemap
	@tools/snippets efrocache_get $@

PREFAB_WINDOWS_PLATFORM = x64

RUN_PREFAB_WINDOWS_DEBUG = cd build/prefab/windows/debug && ./BallisticaCore.exe

prefab-windows-debug: prefab-windows-debug-build
	@tools/snippets ensure_prefab_platform windows
	@{RUN_PREFAB_WINDOWS_DEBUG}

prefab-windows-debug-build: prereqs assets-windows-${PREFAB_WINDOWS_PLATFORM} \
 build/prefab/windows/debug/BallisticaCore.exe
	@${STAGE_ASSETS} -win-$(PREFAB_WINDOWS_PLATFORM) build/prefab/windows/debug

build/prefab/windows/debug/BallisticaCore.exe: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_WINDOWS_RELEASE = cd build/prefab/windows/release \
 && ./BallisticaCore.exe

prefab-windows-release: prefab-windows-release-build
	@tools/snippets ensure_prefab_platform windows
	@{RUN_PREFAB_WINDOWS_RELEASE}

prefab-windows-release-build: prereqs \
 assets-windows-${PREFAB_WINDOWS_PLATFORM} \
 build/prefab/windows/release/BallisticaCore.exe
	@${STAGE_ASSETS} -win-$(PREFAB_WINDOWS_PLATFORM) build/prefab/windows/release

build/prefab/windows/release/BallisticaCore.exe: .efrocachemap
	@tools/snippets efrocache_get $@

RUN_PREFAB_WINDOWS_SERVER_DEBUG = cd build/prefab/windows-server/debug \
 && dist/python.exe ballisticacore_server.py

prefab-windows-server-debug: prefab-windows-server-debug-build
	@tools/snippets ensure_prefab_platform windows
	@{RUN_PREFAB_WINDOWS_SERVER_DEBUG}

prefab-windows-server-debug-build: prereqs \
 assets-windows-${PREFAB_WINDOWS_PLATFORM} \
 build/prefab/windows-server/debug/dist/ballisticacore_headless.exe \
 build/prefab/windows-server/debug/launch_ballisticacore_server.bat \
 build/prefab/windows-server/debug/ballisticacore_server.py \
 build/prefab/windows-server/debug/config_template.yaml \
 build/prefab/windows-server/debug/README.txt
	@${STAGE_ASSETS} -win-$(PREFAB_WINDOWS_PLATFORM) \
 build/prefab/windows-server/debug/dist

build/prefab/windows-server/debug/dist/ballisticacore_headless.exe: .efrocachemap
	@tools/snippets efrocache_get $@

build/prefab/windows-server/debug/ballisticacore_server.py: \
 assets/src/server/ballisticacore_server.py
	@cp $< $@

build/prefab/windows-server/debug/launch_ballisticacore_server.bat: \
 assets/src/server/launch_ballisticacore_server.bat
	@cp $< $@

build/prefab/windows-server/debug/config_template.yaml: \
 assets/src/server/config_template.yaml \
 tools/batools/build.py \
 tools/bacommon/servermanager.py
	@tools/snippets filter_server_config $< $@

build/prefab/windows-server/debug/README.txt: \
 assets/src/server/README.txt
	@cp $< $@

RUN_PREFAB_WINDOWS_SERVER_RELEASE = cd build/prefab/windows-server/release \
 && dist/python.exe ballisticacore_server.py

prefab-windows-server-release: prefab-windows-server-release-build
	@tools/snippets ensure_prefab_platform windows
	@{RUN_PREFAB_WINDOWS_SERVER_RELEASE}

prefab-windows-server-release-build: prereqs \
 assets-windows-${PREFAB_WINDOWS_PLATFORM} \
 build/prefab/windows-server/release/dist/ballisticacore_headless.exe \
 build/prefab/windows-server/release/launch_ballisticacore_server.bat \
 build/prefab/windows-server/release/ballisticacore_server.py \
 build/prefab/windows-server/release/config_template.yaml \
 build/prefab/windows-server/release/README.txt
	@${STAGE_ASSETS} -win-$(PREFAB_WINDOWS_PLATFORM) \
 build/prefab/windows-server/release/dist

build/prefab/windows-server/release/dist/ballisticacore_headless.exe: .efrocachemap
	@tools/snippets efrocache_get $@

build/prefab/windows-server/release/ballisticacore_server.py: \
 assets/src/server/ballisticacore_server.py
	@cp $< $@

build/prefab/windows-server/release/launch_ballisticacore_server.bat: \
 assets/src/server/launch_ballisticacore_server.bat
	@cp $< $@

build/prefab/windows-server/release/config_template.yaml: \
 assets/src/server/config_template.yaml \
 tools/batools/build.py \
 tools/bacommon/servermanager.py
	@tools/snippets filter_server_config $< $@

build/prefab/windows-server/release/README.txt: \
 assets/src/server/README.txt
	@cp $< $@

prefab-clean:
	rm -rf build/prefab

# Tell make which of these targets don't represent files.
.PHONY: prefab-debug prefab-debug-build prefab-release prefab-release-build \
 prefab-server-debug prefab-server-debug-build prefab-server-release \
 prefab-server-release-build prefab-mac-debug prefab-mac-debug-build \
 prefab-mac-release prefab-mac-release-build prefab-mac-server-debug \
 prefab-mac-server-debug-build prefab-mac-server-release \
 prefab-mac-server-release-build prefab-linux-debug prefab-linux-debug-build \
 prefab-linux-release prefab-linux-release-build prefab-linux-server-debug \
 prefab-linux-server-debug-build prefab-linux-server-release \
 prefab-linux-server-release-build prefab-windows-debug \
 prefab-windows-debug-build prefab-windows-release \
 prefab-windows-release-build prefab-windows-server-debug \
 prefab-windows-server-debug-build prefab-windows-server-release \
 prefab-windows-server-release-build prefab-clean


################################################################################
#                                                                              #
#                                   Updating                                   #
#                                                                              #
################################################################################

# Update any project files that need it (does NOT build projects).
update: prereqs
	@tools/update_project

# Don't update but fail if anything needs it.
update-check: prereqs
	@tools/update_project --check

# Tell make which of these targets don't represent files.
.PHONY: update update-check


################################################################################
#                                                                              #
#                                  Formatting                                  #
#                                                                              #
################################################################################

# Run formatting on all files in the project considered 'dirty'.
format:
	@${MAKE} -j3 format-code format-scripts format-makefile
	@tools/snippets echo GRN Formatting complete!

# Same but always formats; ignores dirty state.
format-full:
	@${MAKE} -j3 format-code-full format-scripts-full format-makefile
	@tools/snippets echo GRN Formatting complete!

# Run formatting for compiled code sources (.cc, .h, etc.).
format-code: prereqs
	@tools/snippets formatcode

# Same but always formats; ignores dirty state.
format-code-full: prereqs
	@tools/snippets formatcode -full

# Runs formatting for scripts (.py, etc).
format-scripts: prereqs
	@tools/snippets formatscripts

# Same but always formats; ignores dirty state.
format-scripts-full: prereqs
	@tools/snippets formatscripts -full

# Runs formatting on the project Makefile.
format-makefile: prereqs
	@tools/snippets formatmakefile

.PHONY: format format-full format-code format-code-full format-scripts \
 format-scripts-full


################################################################################
#                                                                              #
#                                   Checking                                   #
#                                                                              #
################################################################################

# Run all project checks. (static analysis)
check: update-check
	@${MAKE} -j3 cpplint pylint mypy
	@tools/snippets echo GRN ALL CHECKS PASSED!

# Same as check but no caching (all files are checked).
check-full: update-check
	@${MAKE} -j3 cpplint-full pylint-full mypy-full
	@tools/snippets echo GRN ALL CHECKS PASSED!

# Same as 'check' plus optional/slow extra checks.
check2: update-check
	@${MAKE} -j4 cpplint pylint mypy pycharm
	@tools/snippets echo GRN ALL CHECKS PASSED!

# Same as check2 but no caching (all files are checked).
check2-full: update-check
	@${MAKE} -j4 cpplint-full pylint-full mypy-full pycharm-full
	@tools/snippets echo GRN ALL CHECKS PASSED!

# Run Cpplint checks on all C/C++ code.
cpplint: prereqs
	@tools/snippets cpplint

# Run Cpplint checks without caching (all files are checked).
cpplint-full: prereqs
	@tools/snippets cpplint -full

# Run Pylint checks on all Python Code.
pylint: prereqs
	@tools/snippets pylint

# Run Pylint checks without caching (all files are checked).
pylint-full: prereqs
	@tools/snippets pylint -full

# Run Mypy checks on all Python code.
mypy: prereqs
	@tools/snippets mypy

# Run Mypy checks without caching (all files are checked).
mypy-full: prereqs
	@tools/snippets mypy -full

# Run Mypy checks on all Python code using daemon mode.
dmypy: prereqs
	@tools/snippets dmypy

# Stop the mypy daemon
dmypy-stop: prereqs
	@tools/snippets dmypy -stop

# Run PyCharm checks on all Python code.
pycharm: prereqs
	@tools/snippets pycharm

# Run PyCharm checks without caching (all files are checked).
pycharm-full: prereqs
	@tools/snippets pycharm -full

# Tell make which of these targets don't represent files.
.PHONY: check check-full check2 check2-full \
  cpplint cpplint-full pylint pylint-full mypy \
  mypy-full pycharm pycharm-full


################################################################################
#                                                                              #
#                                   Testing                                    #
#                                                                              #
################################################################################

# Run all tests. (live execution verification)
test: prereqs
	@tools/snippets echo BLU Running all tests...
	@tools/snippets pytest -v tests

# Run tests with any caching disabled.
test-full: test

# Iterate on individual tests with extra debug output enabled.
test-assetmanager:
	@tools/snippets pytest -o log_cli=true -o log_cli_level=debug -s -v \
      tests/test_ba/test_assetmanager.py::test_assetmanager

test-dataclasses:
	@tools/snippets pytest -o log_cli=true -o log_cli_level=debug -s -v \
      tests/test_efro/test_dataclasses.py

# Tell make which of these targets don't represent files.
.PHONY: test test-full test-assetmanager


################################################################################
#                                                                              #
#                                 Preflighting                                 #
#                                                                              #
################################################################################

# Format, update, check, & test the project. Do this before commits.
preflight:
	@${MAKE} format
	@${MAKE} update
	@${MAKE} -j4 cpplint pylint mypy test
	@tools/snippets echo SGRN BLD PREFLIGHT SUCCESSFUL!

# Same as 'preflight' without caching (all files are visited).
preflight-full:
	@${MAKE} format-full
	@${MAKE} update
	@${MAKE} -j4 cpplint-full pylint-full mypy-full test-full
	@tools/snippets echo SGRN BLD PREFLIGHT SUCCESSFUL!

# Same as 'preflight' plus optional/slow extra checks.
preflight2:
	@${MAKE} format
	@${MAKE} update
	@${MAKE} -j5 cpplint pylint mypy pycharm test
	@tools/snippets echo SGRN BLD PREFLIGHT SUCCESSFUL!

# Same as 'preflight2' but without caching (all files visited).
preflight2-full:
	@${MAKE} format-full
	@${MAKE} update
	@${MAKE} -j5 cpplint-full pylint-full mypy-full pycharm-full test-full
	@tools/snippets echo SGRN BLD PREFLIGHT SUCCESSFUL!

# Tell make which of these targets don't represent files.
.PHONY: preflight preflight-full preflight2 preflight2-full


################################################################################
#                                                                              #
#                                  Auxiliary                                   #
#                                                                              #
################################################################################

# This should give the cpu count on linux and mac; may need to expand this
# if using this on other platforms.
CPUS = $(shell getconf _NPROCESSORS_ONLN || echo 8)
PROJ_DIR = ${abspath ${CURDIR}}
VERSION = $(shell tools/version_utils version)
BUILD_NUMBER = $(shell tools/version_utils build)
BUILD_DIR = ${PROJ_DIR}/build
LAZYBUILDDIR = .cache/lazybuild
STAGE_ASSETS = ${PROJ_DIR}/tools/stage_assets

# Things to ignore when doing root level cleans.
ROOT_CLEAN_IGNORES = --exclude=assets/src_master \
  --exclude=config/localconfig.json \
  --exclude=.spinoffdata

CHECK_CLEAN_SAFETY = ${PROJ_DIR}/tools/snippets check_clean_safety

# Some tool configs that need filtering (mainly injecting projroot path).
TOOL_CFG_INST = tools/snippets tool_config_install

# Anything that affects tool-config generation.
TOOL_CFG_SRC = tools/efrotools/snippets.py config/config.json

# Anything that should trigger an environment-check when changed.
ENV_SRC = tools/snippets tools/batools/build.py

.clang-format: config/toolconfigsrc/clang-format ${TOOL_CFG_SRC}
	@${TOOL_CFG_INST} $< $@

.style.yapf: config/toolconfigsrc/style.yapf ${TOOL_CFG_SRC}
	@${TOOL_CFG_INST} $< $@

.pylintrc: config/toolconfigsrc/pylintrc ${TOOL_CFG_SRC}
	@${TOOL_CFG_INST} $< $@

.projectile: config/toolconfigsrc/projectile ${TOOL_CFG_SRC}
	@${TOOL_CFG_INST} $< $@

.editorconfig: config/toolconfigsrc/editorconfig ${TOOL_CFG_SRC}
	@${TOOL_CFG_INST} $< $@

.dir-locals.el: config/toolconfigsrc/dir-locals.el ${TOOL_CFG_SRC}
	@${TOOL_CFG_INST} $< $@

.mypy.ini: config/toolconfigsrc/mypy.ini ${TOOL_CFG_SRC}
	@${TOOL_CFG_INST} $< $@

.pycheckers: config/toolconfigsrc/pycheckers ${TOOL_CFG_SRC}
	@${TOOL_CFG_INST} $< $@

# Include anything as sources here that should require
.cache/checkenv: ${ENV_SRC}
	@tools/snippets checkenv
	@mkdir -p .cache
	@touch .cache/checkenv

# Tell make which of these targets don't represent files.
.PHONY:
