# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    Builder for Linux ARM
"""

from os.path import join
from SCons.Script import AlwaysBuild, Default, DefaultEnvironment

from platformio.util import get_systype

def BeforeUpload(target, source, env):
    if env["CROSS"] != 1:
        print "no need for upload."
        if "gdb" in env.subst("$UPLOAD_PROTOCOL"):
            env.Replace(
                UPLOADER='$GDB',
                UPLOADERFLAGS=[

                ],
                UPLOADCMD='$UPLOADER $UPLOADERFLAGS $SOURCES',
            )
        else:
            env.Replace(
                UPLOADCMD='$SOURCES',
            )
        return
    if "gdb" in env.subst("$UPLOAD_PROTOCOL"):
        gdb_path = join(env.PioPlatform().get_package_dir("toolchain-gcc-linaro-arm-linux-gnueabihf"), 'bin', '$GDB')
        env.Replace(
            UPLOADER="uploader.py",
            UPLOADERFLAGS=[
                
            ],
            UPLOADCMD='$UPLOADER $UPLOADERFLAGS $UPLOAD_PORT $SOURCES ' + gdb_path
        )
    else:
        env.Replace(
            UPLOADER="uploader.py",
            UPLOADERFLAGS=[
                
            ],
            UPLOADCMD='$UPLOADER $UPLOADERFLAGS $UPLOAD_PORT $SOURCES scp'
        )
env = DefaultEnvironment()

env.Replace(
    _BINPREFIX="",
    AR="${_BINPREFIX}ar",
    AS="${_BINPREFIX}as",
    CC="${_BINPREFIX}gcc",
    CXX="${_BINPREFIX}g++",
    GDB="${_BINPREFIX}gdb",
    OBJCOPY="${_BINPREFIX}objcopy",
    RANLIB="${_BINPREFIX}ranlib",
    SIZETOOL="${_BINPREFIX}size",

    SIZEPRINTCMD='$SIZETOOL $SOURCES'
)

if get_systype() == "darwin_x86_64":
    env.Replace(
        _BINPREFIX="arm-linux-gnueabihf-"
    )
if get_systype() == "linux_x86_64":
    env.Replace(
        _BINPREFIX="arm-linux-gnueabihf-",
        CROSS=1
    )
#
# Target: Build executable program
#

target_bin = env.BuildProgram()

#
# Target: Print binary size
#

target_size = env.Alias("size", target_bin, env.VerboseAction(
    "$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)

#
# Target: Upload the target_bin
#

target_upload = env.Alias(
    "upload", target_bin,
    [env.VerboseAction(BeforeUpload, "Prepare for uploading"),
     env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")])
AlwaysBuild(target_upload)

#
# Default targets
#

Default([target_bin])
