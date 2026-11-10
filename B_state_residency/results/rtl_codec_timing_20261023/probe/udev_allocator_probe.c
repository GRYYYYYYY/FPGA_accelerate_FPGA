#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>

// Reproduce device enumeration with the tool's allocator and a deep-bound DSO.
// No license API, device writes, or hardware identity substitution.
int main(void) {
    void *lib = dlopen("libudev.so.1", RTLD_NOW | RTLD_DEEPBIND);
    if (!lib) { fprintf(stderr, "%s\n", dlerror()); return 2; }
    void *(*make_udev)(void) = dlsym(lib, "udev_new");
    void *(*make_enum)(void *) = dlsym(lib, "udev_enumerate_new");
    int (*scan)(void *) = dlsym(lib, "udev_enumerate_scan_devices");
    void *(*free_enum)(void *) = dlsym(lib, "udev_enumerate_unref");
    void *(*free_udev)(void *) = dlsym(lib, "udev_unref");
    if (!make_udev || !make_enum || !scan || !free_enum || !free_udev) return 3;
    void *udev = make_udev();
    if (!udev) return 4;
    void *enumeration = make_enum(udev);
    if (!enumeration) return 5;
    int result = scan(enumeration);
    printf("scan_return=%d\n", result);
    free_enum(enumeration);
    free_udev(udev);
    dlclose(lib);
    return result < 0 ? 6 : 0;
}
