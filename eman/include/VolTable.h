// VolTable.h  Copyright 2003  Shunming Fang		1/02/03

#ifndef VOLTABLEH
#define VOLTABLEH

#include <cmath>
#include <cstdio>
#include "util.h"
#include "EMData.h"

class VolTable
{
    int nx,ny,nz; // basic volume is a nx*ny*nz, this is the size of the volume
    int cx, cy, cz;//store the orgin of image
    int r_; //store the radius 
    int nrow; //store how many rows have real data;
    int npixel;//store how many pixels is real pixels 
    int *xmax; // a ny * nz  array of int pointers to start and end of data
    float* rdata; // store real data;

public:
    VolTable();
    ~VolTable();
    void setVolTable(EMData *data_in,int dcx=0,int dcy=0,int dcz=0, int ri = 0);
    void setTableFromMRC(char* fspec,int ri=0);
    void setSize(int x, int y, int z); //sets object size.
    float setRowAndPixel(int ri=0,int dcx=0,int dcy=0,int dcz=0);
    EMData *project3d(float alt,float az,float phi);
    inline int  getXSize() { return nx; }
    inline int  getYSize() { return ny; }
    inline int  getZSize() { return nz; }
    inline int  getCXSize() { return cx; }
    inline int  getCYSize() { return cy; }
    inline int  getCZSize() { return cz; }
    inline float getRadius(){ return r_;}
    inline int getNoOfRow(){ return nrow;}
    inline float* getData(){ return rdata;}
    void zero();	// zero all elements;
    // inline int* getPterAt(int n);
    inline int validXYZ(int x, int y, int z);
    inline int validRow(int n);

};

inline int VolTable::validXYZ(int x, int y, int z)
{
    if (y>=ny || y<0 || z>=nz || z<0 || x<xmax[(y+z*ny)*5+0] || x>xmax[(y+z*ny)*5+1])
	return 0;
    return 1;
}
inline int VolTable::validRow(int n)
{
    if(n<0 || n>nrow)
	return 0;
    return 1;
}
    
//inline int* VolTable::getPterAt(int n)
//{
//    if(!validRow(n))
//    {
//	return 0;
//    }
//    return  xmax[n];
//}

#endif
