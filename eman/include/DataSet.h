#ifndef DATAH
#define DATAH

#include "Column.h"
#include <qobject.h>

#define DSB_VARSET	1

class DataSet : public QObject {
    Q_OBJECT

Column **data;
int nx,ny;
int busyflag;

public:
DataSet();
~DataSet();

QString title;

void setRC(int nx,int ny);
Column *getColumn(int n);

float dataAt(int x,int y);

void setXYfn(float minx, float maxx, int n, char *fofx);
void setXYdata(float minx, float maxx, int n);
void setXYdata(float *xdat, float *ydat, int n);
void setXYparmfn(int n, char *fxofrow, char *fyofrow);

void setXYZdata(float *xdat, float *ydat, float *zdat, int n);
void setXYZparmfn(int n,char *fxofrow, char *fyofrow, char *fzofrow);
void setXYZmxdata(float xmin, float xmax, int nx, float ymin,float ymax, int ny, float *zdata);
void setXYZmxfn(float xmin, float xmax, int nx, float ymin,float ymax, int ny, char *fofxy);

int readFile(const char *file);
int readFile(const char *file,char sep,int reclines=1,int skiplines=0);
int writeFile(const char *file);

int cols();
int rows();

signals:
	void	changed();

public slots:
	void	colChanged(int cid);
	void 	setVar(char *name,float val,bool quiet=0);
};

inline int DataSet::cols() { return nx; }
inline int DataSet::rows() { return ny; }
inline Column *DataSet::getColumn(int n) { if (n<0||n>=nx) return NULL; return data[n]; }
#endif
