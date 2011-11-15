#ifndef _spider_h_
#define _spider_h_

// File format for Spider files

struct SPIDERH {
float nslice;		//0    1 for images
float ny;
float u1;			//unused, actually used for SPIDER --Grant
float u2;			
float type;		//4   type of data 1=2d image,3=volume,-11=2d fft odd, -12=2d fft even, -21=3d fft odd, -22=3dfft even 
float mmvalid;		// 1 if max and min are valid
float max;
float min;
float mean;		//8
float sigma;		// std dev, -1=unknown
float u3;
float nx;
float headrec;		//12   # records in header
float angvalid;		// 1 if tilt angles have been computed
float phi,theta;
float gamma;		//16
float dx,dy,dz;		// translations
float scale;		//20
float headlen;		// in bytes
float reclen;
float istack;		// file contains a stack of images (2 in overall header, 0 in images)
float inuse;		//24    indicates that the current image is present in the stack
float maxim,imgnum,lastindx, u6,u7;
float ang2valid;	// additional angles
float phi1,theta1,psi1;
float phi2,theta2,psi2;
char u8[48];
float xf[27];		// Jose Maria's transforms
float u9[135];
char date[11];
char time[8];
char name[160];
};

#endif
