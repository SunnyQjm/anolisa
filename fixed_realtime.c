#define _GNU_SOURCE
#include <dlfcn.h>
#include <time.h>
#include <string.h>
#include <unistd.h>
static int fixed;
__attribute__((constructor)) static void setup(void) {
 char exe[4096]; ssize_t n=readlink("/proc/self/exe",exe,sizeof(exe)-1);
 if(n>0){exe[n]=0;char *base=strrchr(exe,'/');base=base?base+1:exe;fixed=!strncmp(base,"raw_cli-",8);}
}
int clock_gettime(clockid_t id, struct timespec *value) {
 if(fixed && id == CLOCK_REALTIME) { value->tv_sec=1791996516; value->tv_nsec=465894930; return 0; }
 int (*original)(clockid_t,struct timespec*)=dlsym(RTLD_NEXT,"clock_gettime");
 return original(id,value);
}
