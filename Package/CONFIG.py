import ops
import iopc

TARBALL_FILE="libinput-1.7.902.tar.xz"
TARBALL_DIR="libinput-1.7.902"
INSTALL_DIR="libinput-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    global dst_bin_dir
    global dst_usr_local_libexec_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")
    dst_bin_dir = ops.path_join(install_dir, "bin")
    dst_usr_local_libexec_dir = ops.path_join(install_dir, "usr/local/libexec")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))

    '''
    ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    ops.exportEnv(ops.setEnv("LIBS", libs))
    '''
    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    cflags = iopc.get_includes()
    libs = iopc.get_libs()

    extra_conf = []
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("--disable-documentation")
    extra_conf.append("--disable-libwacom")
    extra_conf.append("--disable-libudev")
    extra_conf.append("--disable-debug-gui")
    extra_conf.append("--disable-tests")
    extra_conf.append("--without-libunwind")
    extra_conf.append('MTDEV_CFLAGS=' + cflags)
    extra_conf.append('MTDEV_LIBS=' + libs)
    extra_conf.append('LIBUDEV_CFLAGS=' + cflags)
    extra_conf.append('LIBUDEV_LIBS=' + libs)
    extra_conf.append('LIBEVDEV_CFLAGS=' + cflags)
    extra_conf.append('LIBEVDEV_LIBS=' + libs)
    extra_conf.append('CAIRO_CFLAGS=' + cflags)
    extra_conf.append('CAIRO_LIBS=' + libs)
    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(dst_bin_dir)
    #ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/libinput"), dst_bin_dir)
    #ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/libinput-debug-events"), dst_bin_dir)
    #ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/libinput-list-devices"), dst_bin_dir)

    ops.mkdir(dst_lib_dir)
    libinput = "libinput.so.10.13.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libinput), dst_lib_dir)
    ops.ln(dst_lib_dir, libinput, "libinput.so.10.13")
    ops.ln(dst_lib_dir, libinput, "libinput.so.10")
    ops.ln(dst_lib_dir, libinput, "libinput.so")

    ops.mkdir(dst_usr_local_libexec_dir)
    #ops.copyto(ops.path_join(install_tmp_dir, "usr/local/libexec/."), dst_usr_local_libexec_dir)

    ops.mkdir(tmp_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)
    return True

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(dst_lib_dir, "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_bin_dir, "."), "bin")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_usr_local_libexec_dir, "."), "usr/local/libexec")
    iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)

    return False

def MAIN_SDKENV(args):
    set_global(args)

    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/' + args["pkg_name"])
    iopc.add_includes(cflags)

    libs = ""
    libs += " -linput"
    iopc.add_libs(libs)

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

