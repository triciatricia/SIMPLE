#include <qgl.h>
#include "Plot3d.h"


class IsoPlot : public Plot3d {
	Q_OBJECT

unsigned char *cdata;
float min,max;
int nx,ny,nz;
int thr;
int needupd;
int mode;

enum { MODE_POINT, MODE_MESH, MODE_SURF };

unsigned char *data;

// an array of vertex data for current thr
// contains some padding, size is nx*ny*nz*3
// values represent fractional crossing position at current threshold
// or zero if no crossing
unsigned char *vertex;	

public:

IsoPlot();
~IsoPlot();

void setData(float *d,int x,int y,int z);
virtual void render(int list,float *mx);
virtual f3Rect getLimits();

public slots:

void setThr(float val);	
void setMode(int m);
};
