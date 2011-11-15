#ifndef _pif_h_
#define _pif_h_

// note there are no floats in these files. Floats are stored as ints with
// a scaling factor.


// top of file
struct PifFileHeader {
    int magic[2];	      // magic number; identify PIF file
    char scalefactor[16];     // to convert float ints -> floats
    int nimg;		      // # images in file
    int endian;		      // endianness, 0 -> vax,intel (little), 1 -> SGI, PowerPC (big)
    char program[32];	      // program which generated image
    int htype;		      // 1 - all images same nm pixels and depth, 0 - otherwise
    int nx;                   // number of columns
    int ny;                   // number of rows
    int nz;	              // number of sections
    int mode;		      // image data type                              
    int pad[107];
};

struct PifColorMap{
    short r[256],g[256],b[256];	// color map for depthcued images
};

// each image
struct  PifImageHeader{
    int nx,ny,nz;		// size of this image
    int mode;			// image data type
    int bkg;			// background value
    int radius;			// boxed image radius
    int xstart,ystart,zstart;	// starting number of each axis
    int mx,my,mz;		// intervals along x,y,z
    int xlen,ylen,zlen;		// cell dimensions (floatints)
    int alpha,beta,gamma;	// angles (floatints)
    int mapc,mapr,maps;		// axes->sections (1,2,3=x,y,z)
    int min,max,mean,sigma;	// statistics (floatints)
    int ispg;			// spacegroup
    int nsymbt;			// bytes for symmetry ops
    int xorigin,yorigin;	// origin (floatint)
    char title[80];
    char time[32];
    char imagenum[16];		// unique micrograph number
    char scannum[8];		// scan number of micrograph
    int aoverb,mapabang;	// ?
    int pad[63];		// later use
};

enum PifDataMode {
    PIF_CHAR = 0,
    PIF_SHORT = 1,
    PIF_FLOAT_INT = 2,
    PIF_SHORT_COMPLEX = 3,
    PIF_FLOAT_INT_COMPLEX = 4,
    PIF_BOXED_DATA = 6,
    PIF_SHORT_FLOAT = 7,
    PIF_SHORT_FLOAT_COMPLEX = 8,
    PIF_FLOAT = 9,
    PIF_FLOAT_COMPLEX = 10,
    PIF_MAP_FLOAT_SHORT = 20,
    PIF_MAP_FLOAT_INT = 21,
    PIF_INVALID
};

#define PIF_MAGIC_NUM 8

#endif
