// VolFrag.h  Copyright 2000  Steve Ludtke		7/20/00

#ifndef VOLFRAGH
#define VOLFRAGH

#include <cmath>
#include <cstdio>
#include "util.h"

class VolFrag {
	int size;		// basic volume is a cube, this is the size of the cube
	int *xmax;	// array of size x size  xmax values 
	float **data;	// Actual data, this is a size x size array of pointers
	
	public:
	VolFrag();
	~VolFrag();
	
	void setSize(int s);	// sets object size. Data meaningless after
	inline int getSize() { return size; }
	void setSizeYZ(int nx,int y, int z);
	void setSizeI(int nx,int i);
	void setupIcos(); 
	
	void zero();	// zero all elements
	
	inline int validXYZ(int x, int y, int z);
	inline float valueAt(int x, int y, int z);
	inline void setValue(int x, int y, int z, float val);
	inline void addValue(int x, int y, int z, float val);
	inline void multValue(int x, int y, int z, float val);

	void addFrag(VolFrag *src);	// only within the intersection of the 2 frags

	int writeFile(char *file);		// zero on success
	int readFile(char *file);		// zero on success
};

inline int VolFrag::validXYZ(int x, int y, int z) {
	if (y>=size || y<0 || z>=size || z<0 || x<0 || x>=xmax[y+z*size]) return 0;
	return 1;
}

inline float VolFrag::valueAt(int x, int y, int z) {
	if (validXYZ(x,y,z)) return data[y+z*size][x];
	return 0;
}

inline void VolFrag::setValue(int x, int y, int z, float val) {
	if (validXYZ(x,y,z)) data[y+z*size][x]=val;
}

inline void VolFrag::addValue(int x, int y, int z, float val) {
	if (validXYZ(x,y,z)) data[y+z*size][x]+=val;
}

inline void VolFrag::multValue(int x, int y, int z, float val) {
	if (validXYZ(x,y,z)) data[y+z*size][x]*=val;
}

#endif
