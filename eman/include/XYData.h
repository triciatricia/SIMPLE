// XYData 1/23/00  Steve Ludtke
// This is a simple class for handling 1d data files (2 column)
// data may be evenly or unevenly spaced, ordered or unordered
// note, data is ALWAYS sorted by increasing X

#ifndef XYDH
#define XYDH



#include <cstdlib>
#include <cstdio>
#include <cmath>

int flcmp(const void *a, const void *b);

class XYData {

private:
float *D;	// interleaved x,y data
int N,Na;	// number of elements, and amount of allocated space
float ylim[2];	// ymin and ymax
float xs;	// mean x spacing

public:
XYData();
~XYData();

int readFile(const char *fsp);
int writeFile(const char *fsp);
void update();

inline float x(int n);			// nth value in the array
inline float y(int n);
inline int n();
float yatx(float x);	// interpolated value of Y at X
inline float miny();
inline float maxy();
inline int validx(float x);

void setN(int n);		// set number of data points
inline float *getData();			// call update() after changing
float correlation(XYData* xy, float minx, float maxx);	// compute correlation of this XYData to another XYData object
void logy();	// set y = log10(y)
};

inline int XYData::validx(float x) { if (x<D[0]||x>D[(N-1)*2]) return 0; return 1; }
inline int XYData:: n() { return N; }
inline float XYData:: x(int n) { if (n<0||n>=N) return 0; return D[n*2]; }
inline float XYData:: y(int n) { if (n<0||n>=N) return 0; return D[n*2+1]; }
inline float XYData:: miny() { return ylim[0]; }
inline float XYData:: maxy() { return ylim[1]; }
inline float *XYData:: getData() { return D; }

#endif
