#ifndef _gatan_h_
#define _gatan_h_

// Gatan image file format

struct gatanH {
//short tag;
//short tagl;
short version;
short un1;
short un2;
short nx;
short ny;
short len;	// 1=byte, 2=short, 4=float,long
short type;	// 1=short, 2=float, 3=complex, 5=packed complex, 6=byte, 7=long
};

#endif
