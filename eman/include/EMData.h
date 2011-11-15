// EMData.h - Steve Ludtke  6/97
// This is the heart of the EMAN project. It does just about all of the
// hard stuff. It reads and writes EM images in various formats, does FFTs,
// filters, etc...
//
// $Id: EMData.h,v 1.204 2008/05/15 23:57:44 gtang Exp $
//
#ifndef EMDATAH
#define EMDATAH

#include "config.h"

#include <climits>
#include <cassert>
#include <iostream>
#include <cstring>
#include <vector>
using namespace std;
// windows compatibility section

#ifdef _WIN32
 #include "UnixToWin.h"
#else
 #include <unistd.h>
#endif

#ifndef FLT_MAX
#define FLT_MAX 3.402823466e+38f
#endif
#ifdef HDF5
#include "EMhdf.h"
#endif
#include <cfloat>
#include "mrc.h"
#include "icosH.h"
#include "imagic.h"
#include "spider.h"
#include "util.h"
#include "List.h"
#include "Euler.h"
#include "fftw.h"
#include "rfftw.h"
#include "srfftw.h"	// ~~~ycong, see FRM2D.c
#include "XYData.h"
#ifdef TIF
#include <tiffio.h>
#endif
//#include "VolTable.h"
#include "EMTypes.h"
//#include "crossCommonLine.h"

class ccmlParm;
class ccmlOutputParm;
class VolTable;
class CTF;
#define EMDATA_COMPLEX	1
#define EMDATA_RI		(1<<1)		// real/imaginary or amp/phase
#define EMDATA_BUSY		(1<<2)		// someone is modifying data
#define EMDATA_SHARED	(1<<3)		// Stored in shared memory
#define EMDATA_SWAPPED	(1<<4)		// Data is swapped (may be offloaded if memory is tight)
#define EMDATA_NEWFFT	(1<<5)		// Data has changed, redo fft
#define EMDATA_HASCTF	(1<<6)		// has CTF info
#define EMDATA_NEEDUPD	(1<<7)		// needs a realupdate()
#define EMDATA_NEEDHIST	(1<<8)		// histogram needs update
#define EMDATA_NEWRFP	(1<<9)		// needs new rotational footprint
#define EMDATA_NODATA	(1<<10)		// no actual data
#define EMDATA_COMPLEXX	(1<<11)		// 1D fft's in X

#define EMDATA_CHANGED	(EMDATA_NEWFFT+EMDATA_NEEDUPD+EMDATA_NEEDHIST+EMDATA_NEWRFP)

#define EMDATA_FLIP		(1<<11)		// a flag only

#define CTFOS	5			// curve oversampling, generates ny*CTFOS/2 points

// used to get statistics on a set of numbers

//class VolTable;
class floatStat {
int nf,n;
float *v;

public:
floatStat(int s) { nf=s; v=(float *)malloc(nf*sizeof(float)); n=0; }
~floatStat() { free(v); }

void clear() { n=0; }
void add(float f) { 
	if (n>=nf) { nf+=3; v=(float *)realloc(v,nf*sizeof(float)); }
	v[n]=f; 
	n++; 
}
float* getData() { return v; }
int N() { return n; } 
inline void qadd(float f) {
	v[n]=f; 
	n++; 
}
float mean() { float rt=0; for (int i=0; i<n; i++) rt+=v[i]; return rt/(float)n; }
float sigma() { 
	float rt=0,sg=0; 
	for (int i=0; i<n; i++) { rt+=v[i]; sg+=v[i]*v[i]; } 
	rt/=(float)n;
	return sqrt(sg/(float)n-rt*rt);		// sqrt added later, correct? 
}

float Min(){ 
	float rt=1.0e38; 
	for (int i=0; i<n; i++) 
		if (v[i]<rt) rt=v[i]; 
	return rt; 
}

float Max() { float rt=-1.0e38; for (int i=0; i<n; i++) if (v[i]>rt) rt=v[i]; return rt; }
float median() {
	int i,j;
	float s;
	for (i=0; i<=n/2; i++) {
		for (j=i+1; j<n; j++) {
			if (v[i]<v[j]) { s=v[i]; v[i]=v[j]; v[j]=s; }
		}
	}
	if (n%2) return v[n/2];
	return (v[n/2]+v[n/2-1])/2.0;
}

};

int fileCount(const char *filespec,int *type=NULL);	// number of images in a file, should be static
List *readImages(const char *filespec,int n0,int n1,int nodata=0);	// reads a set of images, should be static
List *readImagesExt(const char *filespec,const char *xt,int n0,int n1,int nodata=0);	// reads a set of images, should be static
SPIDERH *readSpiHed(const char *fsp);

struct EMDataHeader {

int samplebits;
int flags;
int rocount;
float alipeak;
int nx,ny,nz;		// image size
float dx,dy,dz;		// translation from original image
float alt, az, phi;		// orientation of slice or model
int nimg;			// when averaging, # images in average

float min,max;		// image density limits
int minloc,maxloc;	// location of min and max value
double mean,sigma;	// image stats
double sumsq;
float mean2,sigma2;	// these are statistics for a 4 pixel strip at the edge of the image

float pixel;		// A/pixel (or voxel)
float xorigin, yorigin, zorigin;	// the origin coordinates in Angstrom for the first pixel (0,0,0).

char path[MAXPATHLEN];	// path image was read from
int pathnum;			// image number in file pointed to by path
char name[80];			// descriptive name

float ctf[11];		// ctf parameters, check HASCTF flag before using
	// 0 - defocus (neg underfocus)
	// 1 - B factor (A^2)
	// 2 - amplitude
	// 3 - ampcont (0 - 1)
	// 4 - noise1	(noise3*exp(-((pi/2*noise4*x0)^2)-x0*noise2-sqrt(fabs(x0))*noise1))
	// 5 - noise2	(noise expression is intensity)
	// 6 - noise3
	// 7 - noise4
	// 8 - voltage (kv)
	// 9 - Cs (mm)
	//10 - A/pix
char micrograph_id[32];
float particle_location_center_x;
float particle_location_center_y;
float center_x;
float center_y;
MapInfoType map_type;
Euler::EulerType  orientation_convention;
};

class EMData {

int samplebits;
int flags;
int rocount;
float *rdata;
float *supp;
float alipeak;
int nx,ny,nz;		// image size
float dx,dy,dz;		// translation from original image
Euler euler;		// orientation of slice or model
//float daz,dax,daz2;	// angles from original image
int nimg;			// when averaging, # images in average

float min,max;		// image density limits
int minloc,maxloc;	// location of min and max value
double mean,sigma;	// image stats
double sumsq;
float mean2,sigma2;	// these are statistics for a 4 pixel strip at the edge of the image

float pixel;		// A/pixel (or voxel)
float xorigin, yorigin, zorigin;	// the origin coordinates in Angstrom for the first pixel (0,0,0).

char ptype[4];		// type of parameter sets
float param[4][25];	// parameters

long atime;			// access time
int tmp;			// # of temp file when swapped out

mrcH *mrch;			// MRC header when read from MRC file
imagicH *imagich;	// imagic header when read from imagic file
SPIDERH *spiderH;	// spider header when read from spider file

char path[MAXPATHLEN];	// path image was read from
int pathnum;			// image number in file pointed to by path
char name[80];			// descriptive name

EMData *parent;		// if this image was generated from another, this is it
EMData *fft;		// this avoids doing multiple ffts of the same set
EMData *rfp;		// avoids multiple rotational footprints
VolTable *vol_table;    // avoids multiple remap image data
float *frm2dhhat;       // avoids multiple FRM2D H_hat

static List *ralfp;		// rotational alignment basis images
static int rali,ralo,rals;	// rotational alignment inner/outer rad and im size

float ctf[11];		// ctf parameters, check HASCTF flag before using
	// 0 - defocus (neg underfocus)
	// 1 - B factor (A^2)
	// 2 - amplitude
	// 3 - ampcont (0 - 1)
	// 4 - noise1	(noise3*exp(-((pi/2*noise4*x0)^2)-x0*noise2-sqrt(fabs(x0))*noise1))
	// 5 - noise2	(noise expression is intensity)
	// 6 - noise3
	// 7 - noise4
	// 8 - voltage (kv)
	// 9 - Cs (mm)
	//10 - A/pix
static int plans;
static int dimplan[6];
static int nplan[6][3];
static int fwplan[6];
static rfftwnd_plan plan[6];

char micrograph_id[32];
float particle_location_center_x;
float particle_location_center_y;
float center_x;
float center_y;
float scale;	// relative scale of this image
int   num_run;
MapInfoType map_type;
Euler::EulerType  orientation_convention;

// callback for progress display in long routines, if return!=0, routine should abort
int (*updProgress)(int num,int denom,const char *msg);

void realupdate();

public:
// These are for temporary application specific use
// they are NEVER stored in a file
union { int unum; float ufloat;  };
union { int unum2; float ufloat2; };
union { int unum3; float ufloat3; };
union { int unum4; float ufloat4; void *upoint4;};

EMData();
~EMData();
void *operator new(size_t size);
void operator delete(void *ptr);

static rfftwnd_plan makeplan(int,int,int,int,int fw,int measure=0);	// generally for internal use in FFT

void setProgCB(int (*cb)(int num,int denom,const char *msg)) { updProgress = cb; }

// general creation
int readImage(const char *filespec, int n, int nodata=0);
										// reads a single image, 0 on sucess
										// n<0 -> read image as 3d data if possible

EMDataHeader* copyToEMDataHeader();
void pasteFromEMDataHeader(const EMDataHeader * header);
EMData *copy(int withfft=0,int withparent=1);		// returns an exact copy of itself
EMData *copyHead();	// copies descriptive info, but not data
EMData *clip(int x0,int y0,int w,int h);		// inclusive clip. Pads if larger than data
EMData *clip(int x0,int y0,int z0,int w,int h,int d);
void insertClip(EMData *block,int x0, int y0);	// 2d only

// read routines for specific formats
int readLST(const char *filespec,int n,int nodata=0,const char *ext=NULL);	// writes a pointer to an image file to a LST file
int readSAL(const char *filespec,int nodata=0);	//scans-a-lot
int readPGM(const char *filespec,int nodata=0);	//portable greymap (and other pix formats)
int readICOS(const char *filespec,int nodata=0);//brandeis format used in Hong's reconstruction map	
int readMRC(const char *filespec,int nodata=0, int n=-1);	//read z section n, -1 to read whole map	
int readIMAGIC(const char *filespec, int n=0,int nodata=0);
int readIMAGIC3d(const char *filespec,int nodata=0);
int readEMIM(const char *filespec, int n=0,int nodata=0);
int readSPIDER(const char *filespec,int n=0,int nodata=0);
int readMRCArea(const char *fsp,int x0,int y0,int w,int h);
int readMRCArea(const char *fsp,int x0,int y0,int z0,int xl,int yl,int zl);
int readANALYZE(const char*, int);
int readGatan(const char *fsp,int nodata=0);	// old dm2 format, should work for all images
//int readGatan3(const char *fsp,int nodata=0);	// new dm3 format, only reads some files
void serialIn(int filedes, int headonly=0);
int readPIF(const char *filespec, int n = 0, int nodata = 0);
int readDM3(const char* filespec, int nodata = 0);
int readVTK(const char* filespec, int nodata = 0);
int readTIF(const char* filespec, int nodata=0); // tiff format with
						  // libtiff lib
int readHDF(const char *filespec, int n = 0, int nodata=0);
int readHDF2(const char *filespec, int n = 0, int nodata=0);
int readPNG(const char *filespec);
int readEM(const char* filespec, int n = 0, int nodata=0);    
int readAMIRA(const char* filespec, int n = 0, int nodata=0);    

// write routines for specific formats
int writeImage(const char* filename, int n, int headonly=false);	// convnience function, it will actually call the following functions by guessing image types
int writeLST(const char *filespec,int n,const char *reffile = NULL, int refn=-1,const char *comment=NULL);
int writeIMAGIC3D(const char *filespec, int nolock=0); 
int writeIMAGIC(const char *filespec, int n,int nolock=0,bool headonly=false);	// n=-1 appends 
								// nolock for internal use only!
int writeICOS(const char *filespec);
int writeMRC(const char *filespec,int mode=MODE_float,int n=-1);
int writeSPIDER(const char *filespec, int n,int swap=0);	// n=-1 appends, swap allows byte-reversed files to be written
int writeSingleSPIDER(const char *filespec,int swap=0);	//write non-stack SPIDER file
int writeEMIM(const char *filespec, int n);	// n=-1 appends
int writeVTK(const char *filespec);
int writeAMIRA(const char *filespec, char* type = "float", int as_labels=0);
int writeRawIV(const char *filespec);
int writeXPLOR(const char *filespec);
int writePIF(const char* filename);
int writeHDF(const char* filename, int n, int headonly=0);
int writeHDF2(const char* filename, int n, int headonly=0);
int writePNG(const char* filename,float gmin=0.0,float gmax=0.0);
int writePGM(const char *filespec,float gmin=0.0,float gmax=0.0);
int writeEM(const char* filename);
int writeDF3(const char* filename);
int writeTIF(const char* filename);	//write to 16 bit grey scale TIFF without compression
void writeDebug(int n);		// write to a special graphical debug viewer
void serialOut(int filedes, int headonly=0);	// used ONLY for FILESERVER operation, not safe otherwise

void BilateralFilter(float sigma1, float sigma2, int iter=1, int  localWidth=1);

// update statistics
void calcHist(float *hist,int n,float hmin=0,float hmax=0,int add=0);
void update();

// general parameter set/gets
void setPixel(float pix);
float Pixel();
void setXYZOrigin(float x, float y, float z);
float getXorigin();
float getYorigin();
float getZorigin();
float Min();
float Max();
int MinLoc();
int MaxLoc();
int *MaxLocs(int n);
float Mean();
float Sigma();
float SumSq();
float Mean2();
float Sigma2();
float Skewness();
float Kurtosis();
void setMin(float min);
void setMax(float max);
void setMinLoc(int m);
void setMaxLoc(int m);
void setMean(float m);
void setSigma(float s);
void setSumSq(float ss);
void setMean2(float m2);
void setSigma2(float s2);    
float edgeMean();
float cirMean();
void setParent(EMData *data);
EMData *Parent();
void setName(const char *name);
const char *Name();
void setPath(const char *path);
const char *Path();
void setPathN(int n);
int PathN();
int xSize();
int ySize();
int zSize();
int setSize(int x,int y=1, int z=1);
bool isSquare();
bool isEvenSize();

void setRI(int i);		// sets/resets the RI flag, does not modify data

void get_bounding_box(float thresh, int* xmin, int* ymin, int* zmin, int* xmax, int* ymax, int* zmax);

const char* getMicrographId() const;
void setMicrographId(const char *);

float get_particle_location_center_x() const;
void set_particle_location_center_x(float);
float get_particle_location_center_y() const;
void set_particle_location_center_y(float);

float get_center_x() const;
void set_center_x(float);
float get_center_y() const;
void set_center_y(float);
float getScale() const;
void setScale(float s);
int  get_num_run() const;
void set_num_run(int);

MapInfoType get_map_type() const;
void set_map_type(MapInfoType);
Euler::EulerType  get_orientation_convention() const;
void set_orientation_convention(Euler::EulerType);

						// use ap2ri() for conversion
void setComplex(int i);
int isComplex();
void setComplexX(int i);
int isComplexX();
int hasCTF();
int hasCTFF();
int getFlags();
void setFlags(int flag);
float aliPeak();
void setAliPeak(float p);
void setFlipped(int f);	// This is just a flag, it doesn't cause any actual flipping
int isFlipped();
float Dx();
float Dy();
float Dz();
float alt();
float az();
float phi();
Euler *getEuler();
void setTAlign(float x,float y,float z=0);
void setRAlign(float Alt,float Az=0,float Phi=0);
void setRAlign(Euler *angle);
void setNImg(int n);
int NImg();
long getATime();

imagicH *getImagicHed();
void setImagicHed(imagicH *hed);
mrcH *getMRCHed();
SPIDERH *getSpiHed();

// Access to raw data, swapping
float *getData();	// This returns a pointer to the raw float data
float *getDataRO();	// Returns data pointer for reading only
void doneData();	// MUST be called when the data is no longer being
					// modified. Another getData while the data is
					// out will return NULL
int Busy();			// Returns 1 if data is checked out
int waitReady(int ro);	// waits for data to be available
void Wait();		// Why 2 ?    don't recall...
int swapout();		// offloads the data to disk when mem is tight
int swapin();		// reloads the data when necessary

void zero(float sigma=0);		// clears the image to zero
void one();			// all elements -> 1

// Rendering
int renderAmp8( unsigned char * data , int x , int y, int xsize, int ysize,
	int bpl, float scale, int mingray, int maxgray,float renMin, float renMax);
int renderAmp24( unsigned char * data , int x , int y, int xsize, int ysize,
	int bpl, float scale, int mingray, int maxgray,float renMin, float renMax,
	void *ref,void cmap(void *,int coord,unsigned char *tri));
int renderPha24( unsigned char * data , int x , int y , int xsize , int ysize ,
	int bpl , float scale, float renMin, float renMax);

// for complex images
void ri2ap();			// converts real/imaginary to amp/pha (complex only)
void ap2ri();			// the opposite

// fourier ops
EMData *doFFT();		// obvious, note that result is initially R,I not A,P
EMData *doIFT();		// obvious
void gimmeFFT();		// This gives the caller ownership of the
						// recently obtained fft so it won't be freed automatically
						// this means a new fft will be calculated next time

// Radon Transform
EMData *doRadon();		// Radon transform of image, comes out square

// vertical autocorrelation calculated in real-space over a range of translations
EMData *vertACF(int maxdy);

// wavelet ops - unimplimented
void doDWT(int basis, int level);	// in place DWT, basis/level defined elsewhere
void doIWT(int basis, int level);	// inverse wavelet x-form
void DWTFilt(int basis, int level, float thresh);
						// in place nonlinear threshold wavelet filter
						// thresh is with respect to the 'ideal' threshold

EMData *convolute(EMData *with);

EMData *calcCCF(EMData *with,int tocorner=0,EMData *filter=NULL);	// cross correlation between 2 images
								// mirror ACF if with=NULL


EMData *calcFLCF(EMData *with,int r=50,int type=4);	// cross correlation with local normalization between 2 images
								// mirror ACF if with=NULL


EMData *calcCCFX(EMData *with,int y0=0,int y1=-1,int nosum=0);	// calculates sum of x-axis CCFs

EMData *calcMCF(EMData *with,int tocorner=0,EMData *filter=NULL);	// mutual correlation between 2 images

EMData *littleBigDot(EMData *with,int sigma=0);		// CCF in real-space, designed for cases where with is small

// if parent is set, each new interpolation will be done from the
// original parent's data, and additional calls to *Align will modify
// dx,dy,daz cumulatively. With no parent dx,dy,daz are reset each time

// translational alignment using CCF
float transAlign(EMData *with,int useparent,int intonly,int maxshift,float *peak=NULL);

// rotational alignment using angular correlation
float rotAlign(EMData *with);

// rotational alignment assuming centers are correct
float rotAlignPrecen(EMData *with);

// rotational alignment via circular harmonic
float rotAlignCH(EMData *with,int irad=8,int orad=0);

// translational alignment using CCF
float transAlign3d(EMData *with,int useparent=0,int intonly=0);

// rotational, translational and flip alignment with Radon transforms
EMData *RTFAlignRadon(EMData *with,int maxshift=-1,EMData *thisf=NULL,EMData *radonwith=NULL
	,EMData *radonthis=NULL,EMData *radonthisf=NULL);

EMData *RTAlignRadon(EMData *with,int maxshift=-1,EMData *radonwith=NULL,EMData *radonthis=NULL);

// rotational, translational and flip alignment using real-space methods, SLOW
EMData *RTFAlignSlow(EMData *with,EMData *flip=NULL,int maxshift=-1);

// rotational, translational and flip alignment using exhaustive search. VERY SLOW
EMData *RTFAlignSlowest(EMData *with,EMData *flip=NULL,int maxshift=-1);

// rotational, translational and flip alignment
EMData *RTFAlign(EMData *with=NULL,EMData *flip=NULL,int usedot=1,int maxshift=-1);

// rotational, translational and flip alignment using fscmp at multiple locations, slow
// but this routine probably produces the best results
EMData *RTFAlignBest(EMData *with,EMData *flip=NULL,int maxshift=-1,float *SNR=NULL);

// rotational and flip alignment
EMData *RFAlign(EMData *with,EMData *flip=NULL,int imask=0);

// rotational, translational alignment used by RTF
EMData *RTAlign(EMData *with,int usedot=0,int maxshift=-1);

// rotational, translational alignment used by RTFAlignBest
EMData *RTAlignBest(EMData *with,int maxshift=-1,float *SNR=NULL);


void refineAlign(EMData *with,int mode=2,float *snr=NULL);

// Makes a 'rotational footprint', which is an 'unwound' autocorrelation function
// if unwrap is 0 the rfp is not cached
// generally the image should be edgenormalized and masked before using this
EMData *makeRFP(int premasked=0,int unwrap=1);

// 2D alignment using FRM2D 
float* makeFRM2D_H_hat(float rhomax, float rhomin, float rmaxH, int size, float tstep, float r_size);
float frm2dAlign(EMData *with, float *frm2dhhat, EMData* selfpcsfft, float rmax, float MAXR_f, float tstep, float angstep, float r_size, float &com_self_x,float &com_self_y, float &com_with_x, float &com_with_y, int neg_rt);
EMData *frm2dAlignFlip(EMData *drf, float &dot_frm, EMData *with, int usedot, float *raw_hhat, float rmax, float MAXR_f, float tstep, float angstep, float r_size, float &com_self_x, float &com_self_y, float &com_with_x, float &com_with_y, int neg_rt);
EMData *oneDfftPolar(int size, float rmax, float MAXR);
// determine and return the rmax and rmin of an 2D object
void R_min_max(float rmax, float nang, float &rmin_I, float &rmax_I);
// determine and return the center of mass
void COM(int intonly, float &, float &); //determine the center of mass
void exact_COM(int intonly, float *Dens_r, float &cx, float &cy, int rmaxH);
void norm_frm2d();
float retuZero() {return 0.0;}
EMData *sample_map(int r1, int MAXR, float cx, float cy, int bw, int &rmin_I, int &rmax_I);
EMData *unwrap_largerR(int r1=-1,int r2=-1,int xs=-1, float rmax=-1);         // for FRM2D, get polar sampling with large radius

// maps polar coordinates to Cartesian coordinates
EMData *unwrap(int r1=-1,int r2=-1,int xs=-1,int dx=0,int dy=0,int do360=0);


void calcRCF(EMData *with,float *sum,int NS);

void rotateX(int dx);	// This performs a translation of each line along x with wraparound
						// this is equivalent to a rotation when performed on 'unwrapped' maps


void rotateAndTranslate(float scale=1.0,float dxc=0,float dyc=0,float dzc=0,int r=0);
								// rotate and translate using current settings
								// behavior changes if parent is/not set

void rotateAndTranslateFast(float scale=1.0);
								// rotate and translate using current settings
								// behavior changes if parent is/not set

void fastTranslate(int inplace=1);			// fast integer-only translation

void rot180();					// fast rotation by 180 degrees

void cmCenter(int intonly=1);				// center at center of mass, ignores old dx,dy

// other maniuplations
void applyMask(int r,int type,float dx0=0, float dy0=0, float dz0=0);	// applies a circular mask to the data
								// type=0 is a step cutoff to the mean value
								// type=4 is a step cutoff to zero
								// type=1 fills in with flatband random noise

void autoMask(float thresh,float filter=.1);	// Attempts to automatically mask out the
								// particle, excluding other particles in the box, etc.
								// thresh runs from ~ -2 to 2, negative numbers for dark
								// protien and positive numbers for light protein (stain)
								// filter is expressed as a fraction of the Fourier radius 

void applyRadFn(int n,float x0,float dx,float *y,int interp=1);
								// multiplies by a radial function in
								// fourier space

void addRadNoise(int n,float x0,float dx,float *y,int interp);
								// adds random noise with sigma defined
								// by the radial function

void subtract(EMData *data);	// subtracts 'data' from the current set

void vFlip();					// flips image vertically

void hFlip();					// flips image horizontally

void normalize();		// mean -> 0, std dev -> 1

void normalizeTo(EMData *noisy,int keepzero=0,int invert=0,float *mult=0,float *add=0);	// This will multiply 'this' by a constant so
								// it is scaled to the signal in 'to'
								// keepzero will exclude zero values, and keep them at zero in the result

void normalizeMax();		// mean -> 0, std dev -> 1

void edgeNormalize(int mode=0);	// normalizes so mean -> value at edge
						// of image, if mode=1, uses 2 pixel circular
						// border, if mode==2 uses 2 pixels on left and right edge

void xNormalize(int mode=0);	// normalizes each row in the image individually

void addMaskShell(int shells);	// Will add additional shells/rings to an existing 1/0 mask image

void leastSquareNormalizeTo(EMData *to, float low_thresh=FLT_MIN, float high_thresh=FLT_MAX, float* scale=NULL, float* shift=NULL);

void maskNormalize(EMData *mask,int sigmatoo=1); 	// Uses a 1/0 mask defining a region to use for the zero-normalization, if sigma is 0, std-dev not modified

EMData* leastSquarePlaneFit();	// find a least square fit of a plane to the image pixel values. i.e. find the gradient. use nonzero pixels to fit

void invert();			// multiply by -1

void calcRadDist(int n,float x0,float dx,float *y);
void calcRadDist(int n,float x0,float dx,float *y,float acen,float arange, bool smoothing = true);
						// calculates radial distribution, works for real
						// and imaginary images. x must be defined on input
						// and y must be allocated. acen the direction,arange is angular range around the direction in radians 
						// smooting will control if the returned curve in y is smoothed

void calcAzDist(int n,float a0,float da,float *d,float rmin,float rmax);

void radialAverage();	// makes image circularly symmetric

void radialSubtract();	// subtracts circularly symmetric part of image

void toCorner();	// Translates a centered image to the corner

double dotRT(EMData *data,float dx,float dy,float da);	// dot product of 2 images 'this' is rotated/translated
		// much faster than R/T then dot

float dot(EMData *data,int evenonly=0);	// dot product of 2 images (same size !)

float ncccmp(EMData *noisy);	// normalized correlation coefficient comparision (-1->1, larger better), only use non-zero pixels of this

float lcmp(EMData *noisy,int keepzero=0,int invert=0,float *scale=NULL,float *shift=NULL);	// linear comparison of 2 data sets (smaller better)

float pcmp(EMData *data,float *snr=NULL);	// amplitude weighted mean phase error, 'data' should be less noisy than 'this'

float fscmp(EMData *with,float *snr=NULL);	// returns a quality factor based on FSC between images
				// larger numbers indicate a better match

float *fsc(EMData *with);	// returns the Fourier ring/shell correlation coef.
							// as an array with ysize/2 elements (corners not calculated)
							// the calling process must free the array

float dCenter();	// This will find the density value at the peak of the
					// image histogram, sort of like the mode of the density

float sigDiff();	// Calculates sigma above and below the mean and returns the difference between them

void realFilter(int type, float val1=0,float val2=0, float val3=0);
						//a variety of real-space filters

void filter(float highpass,float lowpass,int type);
						// fourier filters an image, real or imaginary

EMData* matchFilter(EMData *to);			// Fourier filter so radial power spectrum of 'this' matches 'to'
						
void makeAverage(List *in,EMData *sigma=NULL,int ignore0=0,int nweight=0);
						// averages the images in the list, result in 'this'
						// optionally makes a sigma image as well
						// nweight will trust the NImg value for each image and weight the average accordingly

void makeAverageIter(List *in);

void makeAverageWT(List *in,EMData *curves,XYData *sf);
						// averages the images in the list with SNR weighting
						// but no CTF correction

void makeAverageCTFC(List *in,float filtr);
						// averages the images in the list with CTF correction
						// filtr is in angstroms,

void makeAverageCTFCWauto(List *in,char *outfile=NULL);
						// This does CTF correction with a Wiener filter
						// where the filter is estimated directly
						// from the data

void makeAverageCTFCW(List *in,XYData *sf,float *SNR=NULL,int phaseopt=0);
						// averages the images in the list with CTF correction

void makeMedian(List *in);
						// Median of the images in the list, result in 'this'

void add(EMData *in);	// adds 'in' to 'this'
void add(float d);	// add const number to each element

void addAsMask(EMData* mask2); // add another mask to current mask, overlapping area set to 0
void addIncoherent(EMData *in);	// adds 'in' to 'this'
						
void mult(EMData *in,int recip=0);	// multiplies 'in' by 'this', if recip, then divide
void mult_sqrt(EMData *in); // mult 'obj' by 'this' then do sqrt, keep the sign of this object


void multConst(float);	// multiply by constant

void addConst(float);	// add a constant

void meanShrink(float sf);		// reduces the size of the image by a factor of sf
							// using the average value of the pixels in a block
							// sf must be a >1 integer or 1.5

void medianShrink(int i);	// reduces the size of the image by a factor of i
							// using a local median filter

void commonLines(EMData *d1,EMData *d2,int mode=0,int steps=180,int horiz=0);	// this function does not assume any symmetry, just blindly compute the "sinogram" and the user has to take care how to interpret the returned "sinogram". it only considers inplane rotation and assumes prefect centering and identical scale
				// finds common lines between 2 complex images
				// mode 0 is a summed dot-product, larger value means better match
				// mode 1 is weighted phase residual, lower value means better match
				// steps is 1/2 the resolution of the map
void commonLinesR(EMData *data1,EMData *data2,int steps=180,int horiz=0);
				// real version


float crossCommonLineRefine(vector< EMData * > refs, float angle_step=1.0, float center_step=1.0, float scale_step=0, int mode = 0);


// refine the orientation, center, and scale of this. assuming refs orientation and centers are known.
/////////////**************************************************//////////////////////////
/////////////     New functions are added by Xiangan Liu       //////////////////////////
/////////////**************************************************//////////////////////////
void crossCommonLineSearchPrepare(ccmlParm* parm);
void crossCommonLineSearchReadRawParticle(ccmlParm* parm);
void crossCommonLineSearchReleaseParticle(ccmlParm* parm);
void crossCommonLineSearchFinalize(ccmlParm* parm);

ccmlOutputParm crossCommonLineSearch(ccmlParm* parm);

//define a type of function pointer which will point to the following 2 functions
typedef ccmlOutputParm (EMData::*crossCommonLineSearchMethod) (ccmlParm *parm);
ccmlOutputParm crossCommonLineCoarseSearch(ccmlParm *parm);
ccmlOutputParm crossCommonLineRefinement(ccmlParm *parm);

void GetCommonLineValueWithSymetry(ccmlParm *parm);
inline void GetCommonLineValueNoScale(ccmlParm *parm, float theta, float *amplitude, float *phase);
inline void GetCommonLineValueWithScale(ccmlParm *parm, float theta, float *amplitude, float *phase);

void phaseChangeByCenterShift(ccmlParm *parm, float cx, float cy, float *phaseIn, float *phaseOut);

float phaseResidualMultiProjectionWithCenterShift(ccmlParm *parm);
float phaseResidual(ccmlParm *parm, float *amplitude1, float *amplitude2, float *phase1, float *phase2);
float onePairCommonLinesPhaseResidualMode(ccmlParm *parm, float *amplitude1, float *amplitude2, float *phase1, float *phase2);

EMData* doOverSampleFFT(int scale = 1);

EMData* doOverSampleFFTShift(int scale, int xx, int yy);

/////////////**************************************************//////////////////////////




EMData *project3d(float alt,float az, float phi,int mode, float thr=1.0,int ri =0, int dcx = 0,int dcy=0,int dcz=0);
				// makes a 3d projection of a volume, mode=-1 does real space
				// projection, 1-5 use fftslice for fourier projection
				// see EMData.h for other important notes

EMData* project3dOpt(float alt, float az, float phi, int r = 0, int dcx = 0, int dcy = 0, int dcz = 0);
EMData *fftSlice(float alt,float az,float phi,int mode=5);
													// takes a slice from a 3d complex image
													// for generating projections
// Supplementary functions for fftSlice
void setup4Slice(int redo=1);
void interpFT3d(float x,float y,float z,float *ret,int mode);

// this initializes a new image to receive 'insertSlice' operations
// for fourier volume inversion. If the image has a parent, it will also
// be affected. WARNING: will use 8*size^3 bytes of memory.
void setup4IS(int size);

// This will try to make sure the slice is normalized properly
float normSlice(EMData *slice,float alt,float az,float phi,float *phaseresid=NULL);

// this inserts a complex slice into an image that has been setup4IS()
void insertSlice(EMData *slice,  float alt,float az,float phi,int mode=5,float weight=1.0);

// this inserts a complex slice into an image that has been setup4IS()
void insertSliceWF(EMData *slice,  float alt,float az,float phi,int mode,float *SNR,float padratio, int deWF=1, int snr_ndim=1);


// once all of the slices have been added with insertSlice(), this routine
// does a normalization and returns a real 3d volume
void doneSlice(int log=0);

// This should only be used in conjunction with insertSliceWF
void doneSliceWF(int log=0);

void insertSlice3DReal(EMData *slice,float weight);

// this will cut a slice out of a real 3D map
void cutSlice(EMData *map,float z,Euler *ort=NULL,int interp=1,float x=0,float y=0);

// Opposite of the above, sort of. It will take a slice and insert
// the data into a real 3D map. It does not interpolate, it uses
// the nearest neighbor
void uncutSlice(EMData *map,float z,Euler *ort=NULL,float x=0,float y=0);

float *ctfCurve(int type=0,XYData *sf=NULL);
	// calculates a CTF curve
	// optional structure factor data for true SNR calc
	
void ctfMap(int type,XYData *sf=NULL);
float *getCTF();
void setCTF(float *c);
void setCTFF(const char *s);
void clearCTF();
int CTFCmp(EMData *with);	// used to detect if 2 images have the same CTF parameters
void applyCTF(float* ctfcurve=NULL);

void subNoise();

// This does an IFT of a volume reconstructed from slices. Includes a
// real-space correction for the linear interpolation in Fourier space
EMData *iftSlice();

// These get a single value with no data locking. risky in some cases!
float valueAt(int x, int y, int z);
float valueAt(int x, int y);
float valueAtInterp(float x, float y);
float valueAtInterp(float x, float y, float z);
float valueAtSafe(int x, int y, int z);
float valueAtSafe(int x, int y);
void setValueAt(int x, int y, int z, float v);	// this does NOT set the changed flag !

// Matrix/Vector operations for EMData objects, not exceptionally
// efficient, but functional
EMData *row(int n);		// extract vector from matrix
EMData *col(int n);
void setRow(EMData *d,int n);	// insert vector into matrix
void setCol(EMData *d,int n);
EMData *mxMult(EMData *second);	// 'this' is first
float dist(EMData *second,int n=0);
};

inline int EMData::PathN() { return pathnum; }
inline int EMData::xSize() { return nx; }
inline int EMData::ySize() { return ny; }
inline int EMData::zSize() { return nz; }
inline float EMData::valueAtInterp(float xx,float yy) {
	int x=(int)floor(xx);
	int y=(int)floor(yy);
	return(bilin(valueAtSafe(x,y),valueAtSafe(x+1,y),valueAtSafe(x+1,y+1),valueAtSafe(x,y+1),xx-x,yy-y));
}
inline float EMData::valueAtInterp(float xx,float yy,float zz) {
	int x=(int)floor(xx);
	int y=(int)floor(yy);
	int z=(int)floor(zz);
	float p1 = valueAtSafe(x,y,z);
	float p2 = valueAtSafe(x+1,y,z);
	float p3 = valueAtSafe(x,y+1,z);
	float p4 = valueAtSafe(x+1,y+1,z);

	float p5 = valueAtSafe(x,y,z+1);
	float p6 = valueAtSafe(x+1,y,z+1);
	float p7 = valueAtSafe(x,y+1,z+1);
	float p8 = valueAtSafe(x+1,y+1,z+1);
	
	return trilin(p1, p2, p3, p4, p5, p6, p7, p8, xx-x, yy-y, zz-z);
}

inline float EMData::valueAt(int x, int y, int z) { return rdata[x+y*nx+z*nx*ny]; }
inline float EMData::valueAt(int x, int y) { return rdata[x+y*nx]; }
inline float EMData::valueAtSafe(int x, int y, int z) { if (x<0||y<0||z<0||x>=xSize()||y>=ySize()||z>=zSize()) return 0; return rdata[x+y*nx+z*nx*ny]; }
inline float EMData::valueAtSafe(int x, int y) { if (x<0||y<0||x>=xSize()||y>=ySize()) return 0; return rdata[x+y*nx]; }
inline void EMData::setValueAt(int x, int y, int z,float v) { rdata[x+y*nx+z*nx*ny]=v; }
inline float *EMData::getCTF() { return ctf; }
inline void EMData::setCTF(float *f) { flags|=EMDATA_HASCTF; memcpy(ctf,f,11*sizeof(float)); return; }
inline void EMData::clearCTF() { flags &=~EMDATA_HASCTF; }
inline void EMData::setRI(int i) { if (i) flags|=EMDATA_RI; else flags&=~EMDATA_RI; }
inline void EMData::setComplex(int i) { if (i) flags|=EMDATA_COMPLEX; else flags&=~EMDATA_COMPLEX; }
inline int EMData::isComplex() { if (flags&EMDATA_COMPLEX) return 1; else return 0; }
inline void EMData::setComplexX(int i) { if (i) flags|=EMDATA_COMPLEXX; else flags&=~EMDATA_COMPLEXX; }
inline int EMData::isComplexX() { if (flags&EMDATA_COMPLEXX) return 1; else return 0; }
inline void EMData::setFlipped(int f) { if (f) flags|=EMDATA_FLIP; else flags&=~EMDATA_FLIP; }
inline int EMData::isFlipped() { if (flags&EMDATA_FLIP) return 1; return 0; }
inline void EMData::setCTFF(const char *s) { setName(s); }
inline int EMData::getFlags() { return flags; }
inline void EMData::setFlags(int flag) { flags = flag; }
inline int EMData::hasCTF() { if ((flags&EMDATA_HASCTF)) return 1; else return 0; }
inline int EMData::hasCTFF() { if (name[0]=='!' && name[1]=='$') return 1; else return 0; }
inline long EMData::getATime() { return atime; }
inline void EMData::setPixel(float pix) { pixel=pix; }
inline float EMData::Pixel() { return pixel; }
inline void EMData::setXYZOrigin(float x, float y, float z) {xorigin=x; yorigin=y; zorigin=z; };
inline float EMData::getXorigin() { return xorigin; };
inline float EMData::getYorigin() { return yorigin; };
inline float EMData::getZorigin() { return zorigin; };
inline void EMData::update() { flags|=EMDATA_CHANGED; }
inline float EMData::Min() { if (flags&EMDATA_NEEDUPD) realupdate(); return min; }
inline float EMData::Max() { if (flags&EMDATA_NEEDUPD) realupdate(); return max; }
inline int EMData::MinLoc() { if (flags&EMDATA_NEEDUPD) realupdate(); return minloc; }
inline int EMData::MaxLoc() { if (flags&EMDATA_NEEDUPD) realupdate(); return maxloc; }
inline float EMData::Mean() { if (flags&EMDATA_NEEDUPD) realupdate(); return mean; }
inline float EMData::Mean2() { if (flags&EMDATA_NEEDUPD) realupdate(); return mean2; }
inline float EMData::SumSq() { if (flags&EMDATA_NEEDUPD) realupdate(); return sumsq; }
inline float EMData::Sigma() { if (flags&EMDATA_NEEDUPD) realupdate(); return sigma; }
inline float EMData::Sigma2() { if (flags&EMDATA_NEEDUPD) realupdate(); return sigma2; }
inline void EMData::setMin(float m) { min = m; }
inline void EMData::setMax(float m) { max = m; }
inline void EMData::setMinLoc(int m) { minloc = m; }
inline void EMData::setMaxLoc(int m) { maxloc = m; }
inline void EMData::setMean(float m) { mean = m; }
inline void EMData::setSigma(float s) { sigma = s; }
inline void EMData::setSumSq(float ss) { sumsq = ss; }
inline void EMData::setMean2(float m2) { mean2 = m2; }
inline void EMData::setSigma2(float s2) { sigma2 = s2; }
inline mrcH *EMData::getMRCHed() { return mrch; }
inline imagicH *EMData::getImagicHed() { return imagich; }
inline void EMData::setImagicHed(imagicH *hed) { imagich=hed; }
inline SPIDERH *EMData::getSpiHed() { return spiderH; }
inline void EMData::setParent(EMData *data) { parent=data; }
inline EMData *EMData::Parent() { return parent; }
inline void EMData::setName(const char *n) { strncpy(name,n,79); name[79]=0; }
inline const char *EMData::Name() { return name; }
inline void EMData::setPath(const char *p) { strncpy(path,p,MAXPATHLEN-1); path[MAXPATHLEN-1]=0; } 
inline void EMData::setPathN(int n) { pathnum=n; }
inline const char *EMData::Path() { return path; }
inline float EMData::aliPeak() { return alipeak; }
inline void EMData::setAliPeak(float p) { alipeak=p; }
inline float EMData::Dx() { return dx; }
inline float EMData::Dy() { return dy; }
inline float EMData::Dz() { return dz; }
inline float EMData::phi() { return euler.phi(); }	// daz
inline float EMData::alt() { return euler.alt(); }	// dax
inline float EMData::az() { return euler.az(); }	// daz2
inline Euler *EMData::getEuler() { return &euler; }
inline void EMData::setTAlign(float x,float y,float z) { dx=x; dy=y; dz=z; }
//inline void EMData::setRAlign(float z,float x,float z2) { euler.setAngle(x,z2,z); }
inline void EMData::setRAlign(float Alt,float Az,float Phi) { 
	if (!goodf(&Alt)) Alt=0; 
	if (!goodf(&Az)) Az=0;
	if (!goodf(&Phi)) Phi=0; 
	euler.setAngle(Alt,Az,Phi); 
}
inline void EMData::setRAlign(Euler *ang) { euler=*ang; }
inline void EMData::setNImg(int n) { nimg=n; }
inline int EMData::NImg() { return nimg; }
inline void EMData::Wait() { while (flags&EMDATA_BUSY) sleep(1); }
inline const char* EMData::getMicrographId() const {return micrograph_id;}
inline void EMData::setMicrographId(const char* theId) { strncpy(micrograph_id, theId, 31); micrograph_id[31]=0; }

inline float EMData::get_particle_location_center_x() const { return particle_location_center_x; }
inline void EMData::set_particle_location_center_x(float x) { particle_location_center_x = x; }
inline float EMData::get_particle_location_center_y() const {return particle_location_center_y;}
inline void EMData::set_particle_location_center_y(float y) {particle_location_center_y = y;}

inline float EMData::get_center_x() const {if(center_x<0) return nx/2; else return center_x;}
inline void EMData::set_center_x(float x) {center_x = x;}
inline float EMData::get_center_y() const {if(center_y<0) return ny/2; else return center_y;}
inline void EMData::set_center_y(float y) {center_y = y;}
inline float EMData::getScale() const {return scale;}
inline void EMData::setScale(float s) {scale = s;}
inline int EMData::get_num_run() const {return num_run;}
inline void EMData::set_num_run(int numRun) {num_run = numRun;}

inline MapInfoType EMData::get_map_type() const {return map_type;}
inline void EMData::set_map_type(MapInfoType thetype) {map_type = thetype;}
inline Euler::EulerType EMData::get_orientation_convention() const{return orientation_convention;}
inline void EMData::set_orientation_convention(Euler::EulerType theType) {orientation_convention = theType;}

inline bool EMData::isSquare(){return nz==1?nx==ny:(nx==ny && nx==nz && ny==nz);}
inline bool EMData::isEvenSize(){return nz==1?(nx==nx/2*2 && ny==ny/2*2):(nx==nx/2*2 && ny==ny/2*2 && nz==nz/2*2);}


#endif


