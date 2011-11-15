#ifndef UTILDEF
#define UTILDEF

#include "config.h"

#include "vector"
#include "string"
using namespace std;

#include <cstdio>
#include <cstdlib>
#include <cmath>
#include "emver.h"
#include <sys/types.h>
#include "EMTypes.h"

#if defined(__sparc)
#include <ieeefp.h>
#endif

#ifdef _WIN32
#include "UnixToWin.h"
#else
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/param.h>
#endif

#define PI (3.141592654)
#define RTOD (57.29577951)


#define PEAKMAX 2

//#define MSB_FIRST

#define ERR_EXIT	0
#define ERR_CRIT	1
#define ERR_ERROR	2
#define ERR_WARN	3
#define ERR_MSG		4
#define ERR_INFO	5
#define ERR_DEBUG	6

#define DBUG printf

#ifndef MAXPATHLEN
#define MAXPATHLEN	1024
#endif


struct ANG {
float a1[PEAKMAX+1];
float a2[PEAKMAX+1];
float l[PEAKMAX+1];
};

const char *tmpnam2();

unsigned long resolv(char *host = NULL);
int sock_open(unsigned long addr,unsigned short port);
int readsock(int sock,char *data,int len,int almtime=480);
int readsocknz(int sock,char *data,int len,int almtime=480);
int writesock(int sock,const char *data,int len,int almtime=480);

char *readTextFile(const char *fsp, off_t *size);

int FSsend(int command, int datalen, const char *fsp, const char *data,int fileno=0);
enum FsType { FS_TEXT, FS_IMAGIC, FS_DONE, FS_LST, FS_NULL, FS_BIN, FS_MRC, FS_HDF, FS_READIMAGE, FS_FILECOUNT,FS_READFILE };

#ifdef FILESERVER
struct FSCOMMAND { int command; int key; int pathlen; int filelen; int fileno; int datalen; int headonly; };
extern unsigned short FSPORT; extern unsigned int FSHOST;
extern unsigned int FSKEY;
extern int FSSOCK;
#endif

extern unsigned int DEBUGHOST;

#ifdef AIX
// This is basically finite(), but shouldn't crash on an alpha
// if exponent is 255, number is infinte or nan
inline int goodf(float *f) { 
// the first is abnormal zero the second is +-inf or NaN
if (finite(*f)) return 1;
return 0;
}
#else
// This is basically finite(), but shouldn't crash on an alpha
// if exponent is 255, number is infinte or nan
inline int goodf(float *f) { 

	//This is the old way to judge a good float, which cause problem on 
	//Fedora Core 64 bit system. Now use isinff() and isnanf() on Linux.
#if defined(_WIN32) || defined(__APPLE__) || defined(__sgi) || defined(aix) || defined(_AIX)
	// the first is abnormal zero the second is +-inf or NaN
	if ((((int *)f)[0] & 0x7f800000)==0 || (((int *)f)[0] & 0x7f800000)==255) return 0;
#else
	if(isinff(*f) || isnanf(*f)) return 0;
#endif	//_WIN32 || __APPLE__ || IRIX
	return 1;
}
#endif	//AIX
inline float maxf(float f1, float f2) { return f1<f2?f2:f1; }

inline float minf(float f1, float f2) { return f1<f2?f1:f2; }

inline float maxf(float f1,float f2,float f3) {
	if (f1>=f2 && f1>=f3) return f1;
	if (f2>=f1 && f2>=f3) return f2;
	return f3;
}

inline float maxf(float f1,float f2,float f3,float f4) {
	float m=f1;
	if (f2>m) m=f2;
	if (f3>m) m=f3;
	if (f4>m) m=f4;
	return m;
}

inline float minf(float f1,float f2,float f3) {
	if (f1<=f2 && f1<=f3) return f1;
	if (f2<=f1 && f2<=f3) return f2;
	return f3;
}

inline float minf(float f1,float f2,float f3,float f4) {
	float m=f1;
	if (f2<m) m=f2;
	if (f3<m) m=f3;
	if (f4<m) m=f4;
	return m;
}

// faster than floor
inline int floor2(float x) {
	if (x<0) return(int)x-1;
	return (int)x;
}

// faster than floor(x+.5)
inline int round(float x) {
	if (x<0) return (int)(x-.5);
	return (int)(x+.5);
}

// hypot squared
inline float hypot2(float x, float y) { return x*x+y*y; }

// this returns hypot^2 for 3 args
inline float hypot3(float x,float y,float z) { return x*x+y*y+z*z; }

// used for parsing special delimited HTML files for generating
// custom sets of instructions
void addHTMLSection(char *sourcefile,FILE *out,char *secid);

struct euler { float alt,az,phi; };

void error(char *msg,int pri);
void error(int pri,char *msg);	// sigh...
void progress(float pct);

char *memmem(char *haystack,int hsize,char *needle,int nsize);

int file_lock_wait(FILE *file);
int file_lock(FILE *file);
void file_unlock(FILE *file);

long file_size(FILE* file);

// default file opening
FILE *DFopenr(const char *name);
FILE *DFopenw(const char *name);
FILE *DFopena(const char *name);
char *DFdir();

char *EMDIR();

// ref is a reference number returned by LOGbegin
#define LOG_MISC		0	
#define LOG_BEGIN		1	// program begin
#define LOG_END			2	// program end
#define LOG_INFILE		10	// input file for processing
#define LOG_OUTFILE		11	// output file for processing
#define LOG_REFFILE		12	// reference file, used with other files
#define LOG_EXTIN		20	// file accessed by a program in another directory
#define LOG_EXTOUT		21
#define LOG_EXTREF		22
#define LOG_ERROR		999
void LOG(int ref,char *file,int mode,char *text);
int  LOGbegin(int argc,char *argv[],int ppid=0);
void LOGerror(int ref,int err,char *text);

// All applications should call this before parsing the command line
void appinit(int argc,char *argv[]);

void appusage(char *argv0);

float frand(float min,float max);

// random number with gaussian distribution
float grand(float mean,float sigma);

// just like modulus, except forces negatives to be in the positive range
inline int cyc(int i,int n) {
	if (i<0) return(n-((-i)%n)-1);
	else return i%n;
}

// linear interpolation in an x/y array at x=xl
float interpolate(float xl,int n,float *x,float *y);

// bilinear interpolation p1=x0,y0; p2=x1,y0; p3=x1,y1; p4=x0,y1
inline float bilin(float p1, float p2, float p3, float p4, float t, float u) {
	return (1.0f-t)*(1.0f-u)*p1+t*(1.0f-u)*p2+t*u*p3+(1.0f-t)*u*p4;
}

// trilinear interpolation p1=x0,y0,z0; p2=x1,y0,z0; p3=x0,y1,z0; etc... (binary pattern)
inline float trilin(float p1,float p2,float p3,float p4,float p5,float p6,float p7,float p8,float t,float u, float v) {
	return (1.0-t)*(1.0-u)*(1.0-v)*p1+t*(1.0-u)*(1.0-v)*p2+
		(1.0-t)*u*(1.0-v)*p3+t*u*(1.0-v)*p4+
		(1.0-t)*(1.0-u)*v*p5+t*(1.0-u)*v*p6+
		(1.0-t)*u*v*p7+t*u*v*p8;
}

// this will interpolate a peak location. v3 is considered to be at x=0
// The other points are nearest neighbors
// returns 0 if not well defined
float p5peak(float v1, float v2,float v3, float v4,float v5);

inline float agauss(float a,float dx,float dy, float dz,float d) {
	return a*exp(-(dx*dx+dy*dy+dz*dz)/d);
}

inline float SQR(float x) { return x*x; }

// 'trackball' rotation of a set of euler angles
// rotates the euler angles about a vector perpendicular to dx,dy
// by an amount proportional to their length
void roteulertb(float *alt,float *az,float *phi, float dx,float dy);

void swapint(char *d,int n);
void swapshort(char *d,int n);
void swapdouble(char* d, int n);

int npfa(int low);
int isvalidfft(int low);
int bestfftsize(int low);	// returns a good fft size >= than low

void save_data(float *x, float *y, int n, const char *fsp);
void save_data(float x0,float dx, float *y, int n, const char *fsp);

// memory allocation routines
#ifdef MEMDEBUG
inline void *Smalloc(int size,int shared) {
void *ret = malloc(size);
if (!ret) { printf("Memory allocation error %d\n",size); exit(1); }
return ret;
}

inline void *Srealloc(void *ptr, int size, int shared) {
void *ret=realloc(ptr,size);
if (!ret) { printf("Memory realloc failed %d\n",size); exit(1); }
return ret;
}
#else
inline void *Smalloc(int size,int shared) {
return malloc(size);
}

inline void *Srealloc(void *ptr, int size, int shared) {
return realloc(ptr,size);
}
#endif

inline void Sfree(void *ptr, int shared) {
free(ptr);
}

// These are routines for measuring timing of code sections
// note that the section between start and stop should require several
// clock ticks to achieve any level of accuracy
void benchmark_start(int tag);
void benchmark_stop(int tag);
void benchmark_report();

// least squares fit returns slope, m, and intercept, b
void lsqfit(int n,float *dx,float *dy,float *m,float *b,int ign0=1);

// This is basically just a version of 'system'
int run(char *s);

// prototypes when I start using shared mem
/*
void *Smalloc(int size,int shared);
void Sfree(void *ptr, int shared);
void *Srealloc(void *ptr, int size, int shared);
*/

bool is_little_endian();	// check if this machine is little endian
bool is_big_endian();		// check if this machine is big endian
int generate_machine_stamp();	// output a machine stamp in MRC/CCP4/HDF convention. this only output the ieee_big_endian (ox44440000) and ieee_little_endian (0x11110000) and ignoring other specific types

bool check_byte_order(char* num_addr);
bool check_file_type(const char* filename, const char* file_ext);
FILE* open_image_file(const char* filename, bool *is_zipped);
char* file_basename(const char* filename); // /abs/path/filename.ext -> filename
const char* get_imagetype_name(ImageType t);

int split(const char* str, vector<string>& results, const char* delim=0, bool empties = false); // split string, white space is used when delim=0
	
// This routine is used to prefetch memory for better pipelining
// on modern processors
extern int p_fetch;                                   // this "anchor" variable helps us
                                               // fool the C optimizer

inline static const void  BLOCK_PREFETCH_4K(void *addr) {
        int* a = (int*) addr;                  // cast as INT pointer for speed

        p_fetch +=  a[0] +  a[16] +  a[32] +  a[48]// Grab every
                      +  a[64] +  a[80] +  a[96] + a[112] // 64th address,
                      + a[128] + a[144] + a[160] + a[176] // to hit each
                      + a[192] + a[208] + a[224] + a[240];// cache line once.

        a += 256;         // point to second 1K stretch of addresses

        p_fetch +=  a[0] +  a[16] +  a[32] +  a[48]
                      +  a[64] +  a[80] +  a[96] + a[112]
                      + a[128] + a[144] + a[160] + a[176]
                      + a[192] + a[208] + a[224] + a[240];

        a += 256;         // point to third 1K stretch of addresses

        p_fetch +=  a[0] +  a[16] +  a[32] +  a[48]
                      +  a[64] +  a[80] +  a[96] + a[112]
                      + a[128] + a[144] + a[160] + a[176]
                      + a[192] + a[208] + a[224] + a[240];

        a += 256;         // point to fourth 1K stretch of addresses

        p_fetch +=  a[0] +  a[16] +  a[32] +  a[48]
                      +  a[64] +  a[80] +  a[96] + a[112]
                      + a[128] + a[144] + a[160] + a[176]
                      + a[192] + a[208] + a[224] + a[240];
}

#endif
