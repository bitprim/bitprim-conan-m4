#
# Copyright (c) 2017 Bitprim developers (see AUTHORS)
#
# This file is part of Bitprim.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment
from conans.util import files
from conans import __version__ as conan_version
import os


class GnuM4Conan(ConanFile):
    name = "m4"
    version = "1.4.18"
    ZIP_FOLDER_NAME = "m4-%s" % version

    settings = "os", "arch", "compiler", "build_type"

    # options = {"shared": [True, False]}
    # default_options = "shared=False"

    generators = "cmake"
    # exports = ["CMakeLists.txt"]

    # generators = "txt"

    url = "https://github.com/fpelliccioni/bitprim-conan-m4"
    license = "http://www.gnu.org/licenses/licenses.html"

    description = "GNU M4 is a macro processor in the sense that it copies its input to the output expanding macros as it goes. "

    build_policy = "missing"
    
    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):

        if self.settings.os == "Windows":
            # Workaround
            # http://downloads.sourceforge.net/gnuwin32/m4-1.4.14-1-bin.zip

            tools.download("http://downloads.sourceforge.net/gnuwin32/m4-1.4.14-1-bin.zip", 'm4-1.4.14-1-bin.zip')
            tools.unzip('m4-1.4.14-1-bin.zip')
            # os.unlink('m4-1.4.14-1-bin.zip')
            
            self.run("dir %s" % 'm4-1.4.14-1-bin')

            bin_dir = os.path.join('m4-1.4.14-1-bin', "bin")
            build_dir = os.path.join(self.ZIP_FOLDER_NAME, "src")

            self.run("dir %s" % bin_dir)

            # self.copy(pattern="m4", dst="bin", src=build_dir, keep_path=False)
            self.copy(pattern="m4.exe", dst=build_dir, src=bin_dir, keep_path=False)

            self.run("dir %s" % build_dir)

        else:
            zip_name = "m4-%s.tar.gz" % self.version

            # tools.download("https://zlib.net/fossils/%s" % (zip_name), zip_name)
            tools.download("http://ftp.gnu.org/gnu/m4/%s" % (zip_name), zip_name)

            tools.unzip(zip_name)
            os.unlink(zip_name)
            files.rmdir("%s/contrib" % self.ZIP_FOLDER_NAME)
            if self.settings.os != "Windows":
                self.run("chmod +x ./%s/configure" % self.ZIP_FOLDER_NAME)
            

    def generic_env_configure_vars(self, verbose=False):
        """Reusable in any lib with configure!!"""
        command = ""
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            libs = 'LIBS="%s"' % " ".join(["-l%s" % lib for lib in self.deps_cpp_info.libs])
            ldflags = 'LDFLAGS="%s"' % " ".join(["-L%s" % lib for lib in self.deps_cpp_info.lib_paths])
            archflag = "-m32" if self.settings.arch == "x86" else ""
            cflags = 'CFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cflags))
            cpp_flags = 'CPPFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cppflags))
            command = "env %s %s %s %s" % (libs, ldflags, cflags, cpp_flags)
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cl_args = " ".join(['/I"%s"' % lib for lib in self.deps_cpp_info.include_paths])
            lib_paths= ";".join(['"%s"' % lib for lib in self.deps_cpp_info.lib_paths])
            command = "SET LIB=%s;%%LIB%% && SET CL=%s" % (lib_paths, cl_args)
            if verbose:
                command += " && SET LINK=/VERBOSE"
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            libs = 'LIBS="%s"' % " ".join(["-l%s" % lib for lib in self.deps_cpp_info.libs])
            ldflags = 'LDFLAGS="%s"' % " ".join(["-L%s" % lib for lib in self.deps_cpp_info.lib_paths])
            archflag = "-m32" if self.settings.arch == "x86" else ""
            cflags = 'CFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cflags))
            cpp_flags = 'CPPFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cppflags))
            command = "env %s %s %s %s" % (libs, ldflags, cflags, cpp_flags)

        return command
            
    def build(self):
        if self.settings.os != "Windows":
            with tools.chdir(self.ZIP_FOLDER_NAME):
                env_build = AutoToolsBuildEnvironment(self)
                if self.settings.compiler == "clang":
                    self.run("./configure CFLAGS='-rtlib=compiler-rt'")
                else:
                    # env_build.configure("./", build=False, host=False, target=False)
                    self.run("./configure'")
                env_build.make()
        # else:
        #     # http://downloads.sourceforge.net/gnuwin32/m4-1.4.14-1-bin.zip
        #     config_options_string = ""

        #     for option_name in self.options.values.fields:
        #         activated = getattr(self.options, option_name)
        #         if activated:
        #             self.output.info("Activated option! %s" % option_name)
        #             config_options_string += " --%s" % option_name.replace("_", "-")

        #     self.output.warn("*** Detected OS: %s" % (self.settings.os))

        #     if self.settings.os == "Macos":
        #         config_options_string += " --with-pic"

            
        #     disable_assembly = "--disable-assembly" if self.settings.arch == "x86" else ""

        #     configure_command = "cd %s && %s ./configure %s %s" % (self.ZIP_FOLDER_NAME, self.generic_env_configure_vars(), config_options_string, disable_assembly)
        #     self.output.warn("*** configure_command: %s" % (configure_command))
        #     # self.output.warn(configure_command)
        #     self.run(configure_command)


        #     self.output.warn("*** configure_command OK")

        #     # if self.settings.os == "Linux" or self.settings.os == "Macos":
        #     if self.settings.os != "Windows":
        #         self.run("cd %s && make" % self.ZIP_FOLDER_NAME)
        #     else:
        #         # make_command = "cd %s && C:\MinGw\bin\make" % self.ZIP_FOLDER_NAME
        #         make_command = "cd %s && mingw32-make.exe" % self.ZIP_FOLDER_NAME
        #         self.output.warn("*** make_command: %s" % (make_command))

        #         self.run("dir %s" % self.ZIP_FOLDER_NAME)

        #         # self.run("dir C:\MinGw\bin\")
        #         self.run(make_command)


    def package(self):

        # # Extract the License/s from the header to a file
        # with tools.chdir(self.ZIP_FOLDER_NAME):
        #     tmp = tools.load("zlib.h")
        #     license_contents = tmp[2:tmp.find("*/", 1)]
        #     tools.save("LICENSE", license_contents)

        # # Copy the license files
        # self.copy("LICENSE", src=self.ZIP_FOLDER_NAME, dst=".")

        # # Copy pc file
        # self.copy("*.pc", dst="", keep_path=False)
        
        # # Copying zlib.h, zutil.h, zconf.h
        # self.copy("*.h", "include", "%s" % self.ZIP_FOLDER_NAME, keep_path=False)
        # self.copy("*.h", "include", "%s" % "_build", keep_path=False)

        build_dir = os.path.join(self.ZIP_FOLDER_NAME, "src")
        self.copy(pattern="m4", dst="bin", src=build_dir, keep_path=False)
        self.copy(pattern="m4.exe", dst="bin", src=build_dir, keep_path=False)


        # # Copying static and dynamic libs
        # if tools.os_info.is_windows:
        #     if self.options.shared:
        #         build_dir = os.path.join(self.ZIP_FOLDER_NAME, "_build")
        #         self.copy(pattern="*.dll", dst="bin", src=build_dir, keep_path=False)
        #         build_dir = os.path.join(self.ZIP_FOLDER_NAME, "_build/lib")
        #         self.copy(pattern="*zlibd.lib", dst="lib", src=build_dir, keep_path=False)
        #         self.copy(pattern="*zlib.lib", dst="lib", src=build_dir, keep_path=False)
        #         self.copy(pattern="*zlib.dll.a", dst="lib", src=build_dir, keep_path=False)
        #     else:
        #         build_dir = os.path.join(self.ZIP_FOLDER_NAME, "_build/lib")
        #         # MinGW
        #         self.copy(pattern="libzlibstaticd.a", dst="lib", src=build_dir, keep_path=False)
        #         self.copy(pattern="libzlibstatic.a", dst="lib", src=build_dir, keep_path=False)
        #         # Visual Studio
        #         self.copy(pattern="zlibstaticd.lib", dst="lib", src=build_dir, keep_path=False)
        #         self.copy(pattern="zlibstatic.lib", dst="lib", src=build_dir, keep_path=False)
                
        #         lib_path = os.path.join(self.package_folder, "lib")
        #         suffix = "d" if self.settings.build_type == "Debug" else ""
        #         if self.settings.compiler == "Visual Studio":
        #             current_lib = os.path.join(lib_path, "zlibstatic%s.lib" % suffix)
        #             os.rename(current_lib, os.path.join(lib_path, "zlib%s.lib" % suffix))
        #         elif self.settings.compiler == "gcc":
        #             current_lib = os.path.join(lib_path, "libzlibstatic.a")
        #             os.rename(current_lib, os.path.join(lib_path, "libzlib.a"))
        # else:
        #     build_dir = os.path.join(self.ZIP_FOLDER_NAME)
        #     if self.options.shared:
        #         if self.settings.os == "Macos":
        #             self.copy(pattern="*.dylib", dst="lib", src=build_dir, keep_path=False)
        #         else:
        #             self.copy(pattern="*.so*", dst="lib", src=build_dir, keep_path=False)
        #     else:
        #         self.copy(pattern="*.a", dst="lib", src=build_dir, keep_path=False)

    def package_info(self):
        pass
        # if self.settings.os == "Windows":
        #     self.cpp_info.libs = ['zlib']
        #     if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
        #         self.cpp_info.libs[0] += "d"
        # else:
        #     self.cpp_info.libs = ['z']
