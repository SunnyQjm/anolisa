#define _GNU_SOURCE
#include <dlfcn.h>
#include <time.h>
int clock_gettime(clockid_t id, struct timespec *value) {
 if(id == CLOCK_REALTIME) { value->tv_sec=1791996516; value->tv_nsec=465894930; return 0; }
 int (*original)(clockid_t,struct timespec*)=dlsym(RTLD_NEXT,"clock_gettime");
 return original(id,value);
}
