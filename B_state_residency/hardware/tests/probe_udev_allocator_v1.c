#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* Exercise the real system libudev. No license API, stubs or library patches. */
static void *symbol(void *handle, const char *name) {
    void *p = dlsym(handle, name);
    if (!p) { fprintf(stderr, "missing symbol %s: %s\n", name, dlerror()); exit(2); }
    return p;
}

int main(void) {
    setbuf(stdout, NULL);
    Dl_info info;
    for (int i = 0; i < 2; ++i) {
        const char *name = i ? "realloc" : "malloc";
        if (!dladdr(symbol(RTLD_DEFAULT, name), &info)) return 3;
        printf("ALLOCATOR %s %s\n", name, info.dli_fname);
    }
    void *lib = dlopen("libudev.so.1", RTLD_LAZY | RTLD_DEEPBIND);
    if (!lib) { fprintf(stderr, "%s\n", dlerror()); return 4; }
    void *(*new_udev)(void) = symbol(lib, "udev_new");
    void *(*unref_udev)(void *) = symbol(lib, "udev_unref");
    void *(*new_enum)(void *) = symbol(lib, "udev_enumerate_new");
    int (*scan)(void *) = symbol(lib, "udev_enumerate_scan_devices");
    void *(*unref_enum)(void *) = symbol(lib, "udev_enumerate_unref");
    void *(*get_list)(void *) = symbol(lib, "udev_enumerate_get_list_entry");
    void *(*get_next)(void *) = symbol(lib, "udev_list_entry_get_next");
    const char *(*get_name)(void *) = symbol(lib, "udev_list_entry_get_name");
    void *u = new_udev();
    if (!u) return 5;
    void *e = new_enum(u);
    if (!e) return 6;
    if (!dladdr((void *)scan, &info)) return 7;
    printf("SCAN_LIBRARY %s\n", info.dli_fname);
    int result = scan(e);
    if (result < 0) { fprintf(stderr, "scan failed %d\n", result); return 8; }
    uint64_t fingerprint = UINT64_C(14695981039346656037);
    unsigned count = 0;
    for (void *entry = get_list(e); entry; entry = get_next(entry)) {
        const unsigned char *s = (const unsigned char *)get_name(entry);
        if (!s) return 9;
        while (*s) { fingerprint ^= *s++; fingerprint *= UINT64_C(1099511628211); }
        fingerprint ^= '\n'; fingerprint *= UINT64_C(1099511628211);
        ++count;
    }
    printf("ENUMERATED count=%u ordered_syspath_fnv64=%016llx\n", count,
           (unsigned long long)fingerprint);
    unref_enum(e);
    unref_udev(u);
    dlclose(lib);
    return count ? 0 : 10;
}
