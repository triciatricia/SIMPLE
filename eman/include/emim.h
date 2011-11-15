// emim.h  Copyright 1997 Steve Ludtke
//
// This defines the emim file format. All floats and
// ints are assumed to be 4 bytes

#ifndef EMIMH
#define EMIMH

#define EMIM_COMPLEX	1	// data imaginary (real otherwise)

#define PARM_NONE	0
#define PARM_NORM	1	// std parametrization

/*
union emimP {
	struct {
		int type;
		float dx,dy,dz;		// translation
		float daz,dax,daz2;	// eulers (phi,alt,az)
	};
	

};
*/

// occurs once at the beginning of the file, 128 bytes
struct emimH1 {
char magic[4];			// 'EMIM'
int order;			// This defines the byte order, value is 2 on correct machine
int count;			// # images in the file (24 bits max)
int nx,ny,nz;		// image size (all images in 1 file same size)
int flag;			// flags are the same as well
float pixel;		// pixel/voxel size in A
int misc[7];		// misc usage
int headlen;		// length of individual image headers (currently 166 x 4)
char name[64];		// optional description of entire set of images
};

struct emimH2 {
char name[80];		// data set name
unsigned int time;	// time at which image was acquired
int mgnum;			// micrograph number or CCD frame
int clipnum;		// id of clip within micrograph/frame
int id;				// another id number

	float dx,dy,dz;		// translation
	float alt,az,phi;	// orientation
short nparm;		// number of parameter sets
int ptype[4];		// type of each parameter set
float param[4][32];	// Parameterized CTF/SNR, etc...
};

#endif
