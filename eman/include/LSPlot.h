#ifndef LSPLOTH
#define LSPLOTH
#include <math.h>
#include <qpainter.h>
#include "Axes2d.h"
#include "DataSet.h"
#include "Plot.h"

#define LS_LINE	1
#define LS_SYM	2
#define LS_XERROR 4		// x error bars
#define LS_YERROR 8		// y error bars
#define LS_VECXY 16		// x-y vectors, cannot be used with error bars
#define LS_VECRT 32		// r-theta vectors, see above
#define LS_HSV 64		// point by point coloration, hsv colorspace
#define LS_RGB 128		// point by point coloration, rgb colorspace

#define LS_VECERR	(LS_XERROR|LS_YERROR|LS_VECXY|LS_VECRT)
#define LS_COLOR	(LS_HSV|LS_RGB)

#define SYM_POINT	0
#define SYM_X		1
#define SYM_PLUS	2
#define SYM_CIRCLE	3
#define SYM_BOX		4
#define SYM_DIAM	5
#define SYM_STAR	6
#define SYM_FBOX	7
#define SYM_FDIAM	8
#define COL_WHITE       0
#define COL_BLACK       1
#define COL_RED         2
#define COL_DARKRED     3  
#define COL_GREEN       4
#define COL_DARKGREEN   5
#define COL_BLUE        6
#define COL_DARKBLUEE   7
#define COL_CYAN        8
#define COL_DARKCYAN    9
#define COL_YELLOW      10
#define COL_DARKYELLOW  11
#define COL_GRAY        12
#define COL_DARKGRAY    13
#define COL_LIGHTGRAY   16
#define COL_MAGENTA     14
#define COL_DARKMAGENTA 15

class LSPlot:public Plot {
    Q_OBJECT

short sym;
short symsize;
short linewid,linesty;
QPen pen;
QBrush brush;
QColor color;
void drawsym(QPainter *qp,int x,int y);

public:
LSPlot();
~LSPlot();

void setSym(int s,short size);
short getSym();
short getSymS();
void setLine(int ls=-1,int width=-1);
short getLW();
short getLS();
void setColor(int r,int g,int b);
void setHSVColor(int h, int s, int v);
void setColor(QColor *qc);
QColor getColor();
virtual void display(QPainter *qp,Axes2d *axis,int x0,int y0,int x1,int y1);
virtual int legend(QPainter *qp,Axes2d *axis,int x,int y);

};

inline short LSPlot::getLW() { return linewid; }
inline short LSPlot::getLS() { return linesty; }
inline short LSPlot::getSym() { return sym; }
inline short LSPlot::getSymS() { return symsize; }
inline QColor LSPlot::getColor() { return color; }
inline void LSPlot::setSym(int s,short size) { if(s >=0) sym=s; if(size>=0)symsize= (size+1)*OVERSMP; }

#endif
