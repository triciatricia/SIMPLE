#ifndef AXES2DH
#define AXES2DH

#include <stdio.h>
#include <qwidget.h>
#include <qpixmap.h>
#include <qfont.h> 
#include <qdict.h>
#include <qintdict.h>
#include <qprinter.h>

#ifndef UBUNTU
	#include <qlist.h>
	#include <qfontmet.h>
#endif	//UBUNTU

#include "Plot.h"
#include "misc.h"
#include <math.h>
//#include "D2Inspector.h"

#define OVERSMP 10

//class Plot;

// These are actions which can be attached to mouse clicks, etc...
#define D2_ACT_XVALUE	1		// these 4 are for display only
#define D2_ACT_XRANGE	2		// clicks and drags are reported
#define D2_ACT_YVALUE	4		// regardless
#define D2_ACT_YRANGE	8
#define D2_ACT_MPOS		16		// mouse position display
#define D2_ACT_ZOOM		64		// user zoom in on drag, rescale on click
#define D2_ACT_YLOG		128		// toggle log y on mousedown
#define D2_ACT_LEGEND	256		// move legend
#define D2_ACT_INSPECT	512		// display inspector

// Options for the whole plot region
#define D2_OPT_FRAME	(1<<0)
#define D2_OPT_LR		(1<<1)
#define D2_OPT_TITLE	(1<<2)
#define D2_OPT_AUTOSCALE	(1<<3)
#define D2_OPT_ANIMZOOM	(1<<4)	// unimplimented
#define D2_OPT_SHOWY0	(1<<5)	// Always show the x axis
#define D2_OPT_LEGEND	(1<<6)	// display legend
#define D2_OPT_LBOX		(1<<7)	// box around legend (unimplimented)

// Options for each axis
#define D2_OPT_AXIS		(1<<0)
#define D2_OPT_TIC		(1<<1)
#define D2_OPT_GRID		(1<<2)	// unimplimented
#define D2_OPT_GRIDM	(1<<3)	// unimplimented
#define D2_OPT_LOG		(1<<4)	// unimplimented for X
#define D2_OPT_SCALE	(1<<5)
#define	D2_OPT_CSCA		(1<<6)
#define D2_OPT_LABEL	(1<<7)

// Internal flags
#define D2_OPT_ASDIS	(1<<22)	// INTERNAL USE ONLY!	(disabled autoscale)
#define D2_OPT_XCH		(1<<23)	// INTERNAL USE ONLY!	(crosshair)
#define D2_OPT_YCH		(1<<24)
#define D2_OPT_XRA		(1<<25) // INTERNAL USE ONLY!  (range)
#define D2_OPT_YRA		(1<<26)
#define D2_OPT_TXT		(1<<27)	// INTERNAL USE ONLY!  (position display)
#define D2_CLRINT		(0x003fffff)	// for clearing internal flags
class D2Inspector;
class Axes2d:public QWidget {
    Q_OBJECT

int options,xopt,yopt;
fPoint dorigin,dsize,dlimit;
fPoint aorigin,asize,alimit;
fPoint ticspace;
fPoint sel[2];
int legx,legy;
QFont *tfont,*lfont,*sfont;
QFontMetrics *tmet,*lmet,*smet;
QString xlabel,ylabel,title;
char *(*labfn)(float val,int isy);
int minor[2];
int axislw,framelw;
QIntDict<int> actions;
QList<Plot> *plots;
QPainter *qp;
QPrinter *qpd;
QPixmap *qpm;
QColor textcolor;
QColor axiscolor;
QColor framecolor;
QColor mousecolor;
int needupd;
D2Inspector *inspect;

QString fileToSave;

void ytic(float x,float y,float min);		// draws tic marks
void xtic(float x, float y, float min); 
public:

			
Axes2d( QWidget *parent=0, const char *name=0 );
~Axes2d();

// state can use LeftButton, RightButton, MidButton, ShiftButton, ControlButton, AltButton
void setAction(int state,int action);	// state is QMouseEvent state(), actions above
void setOptions(int opt,int xo,int yo);
inline void setFlags(int opt) { setOptions(options|opt,xopt,yopt); }
inline void setXFlags(int xo) { setOptions(options,xopt|xo,yopt); }
inline void setYFlags(int yo) { setOptions(options,xopt,yopt|yo); }
inline void resetFlags(int opt) { setOptions(options&(~opt),xopt,yopt); }
inline void resetXFlags(int xo) { setOptions(options,xopt&(~xo),yopt); }
inline void resetYFlags(int yo) { setOptions(options,xopt,yopt&(~yo)); }
int getOptions();
int getXOpt();
int getYOpt();

int needUpd();
void addPlot(Plot *plot);
void removePlot(Plot *plot);
void noPlots();
int nPlots();
Plot *plotAt(int n);
void setFonts(char *fontname,int titlesize,int labelsize,int scalesize);
void setTFont(QFont &f);
void setLFont(QFont &f);
void setSFont(QFont &f);
QFont getTFont();
QFont getLFont();
QFont getSFont();
inline void setAxisLW(int w) { axislw=w; needupd=1; }
inline void setFrameLW(int w) { framelw=w; needupd=1; }
inline int getAxisLW() { return axislw; }
inline int getFrameLW() { return framelw; }
void setTextColor(QColor &color);
void setAxisColor(QColor &color);
void setFrameColor(QColor &color);
void setMouseColor(QColor &color);
inline void setMinorX(int m) { minor[0]=m; needupd=1; }
inline void setMinorY(int m) { minor[1]=m; needupd=1; }
inline int getMinorX() { return minor[0]; }
inline int getMinorY() { return minor[1]; }
void rescale();
void setlabfn(char *labfn(float val,int isy));
inline void setXTicspace(float x) { ticspace.x=x; needupd=1; }
inline void setYTicspace(float y) { ticspace.y=y; needupd=1; }
inline float getXTicspace() { return(ticspace.x); }
inline float getYTicspace() { return(ticspace.y); }
void setXLabel(QString);
void setYLabel(QString);
void setTitle(QString);
float xdtor(float x);
float xdtor2(float x);
float xrtod(float x);
float ydtor(float y);
float ydtor2(float y);
float yrtod(float y);
void sanity();
inline fRect getLimits() { return fRect(dorigin.x,dorigin.y,dlimit.x,dlimit.y); }

inline QColor getTextColor() { return textcolor; }
inline QColor getAxisColor() { return axiscolor; }
inline QColor getFrameColor() { return framecolor; }
inline QColor getMouseColor() { return mousecolor; }
inline QString getTitle() { return title; }
inline QString getXLabel() { return xlabel; }
inline QString getYLabel() { return ylabel; }

virtual int inside(float x,float y);
virtual void paintEvent( QPaintEvent *qp );
virtual void mousePressEvent(QMouseEvent *);
virtual void mouseReleaseEvent(QMouseEvent *);
virtual void mouseDoubleClickEvent(QMouseEvent *e);
virtual void mouseMoveEvent(QMouseEvent *);
virtual void mouseEnter(int);
virtual void mouseLeave(int);
virtual void keyPressEvent(QKeyEvent *);
virtual void keyReleaseEvent(QKeyEvent *);
virtual void resizeEvent ( QResizeEvent * );
virtual void print(QPrinter *dev);
virtual void savePNG(QString &fts);

signals:
		// ANY change will be reported
	void	newLimits(float x0,float y0,float x1,float y1);
		// only changes requiring redraws are reported
	void	changed();
		// x and y are in data space, use xdtor and ydtor to convert
	void	mouseDown(int state,float x,float y);
	void	mouseDrag(int state,float x0,float y0,float x1,float y1);
	void	mouseUp(int state,float x0,float y0,float x1,float y1);

public slots:
	void	plotChanged();
	void	setLimits(fRect v);
};

inline int Axes2d::nPlots() { return plots->count(); }

inline Plot *Axes2d::plotAt(int n) { return plots->at(n); }

inline float Axes2d::xdtor(float x) {
    float r;
        if (xopt&D2_OPT_LOG)
		r=(log10(x)-dorigin.x)/dsize.x*asize.x+aorigin.x;
	else
	    {
		r=(x-dorigin.x)/dsize.x;
		r=r*asize.x+aorigin.x;
	    }
	    
	//	    if (r<aorigin.x) r=aorigin.x;
	//	    if (r>alimit.x) r=alimit.x;
	//	r = height()-r;  
	return r; 
}

inline float Axes2d::xdtor2(float x) { 
	float r;
	if (xopt&D2_OPT_LOG)
		r=(log10(x)-dorigin.x)/dsize.x*asize.x+aorigin.x;
	else
	    {
		r=(x-dorigin.x)/dsize.x;
		r=r*asize.x+aorigin.x;
	    }
	
	//	if (r<aorigin.x) r=aorigin.x;
	//	if (r>alimit.x) r=alimit.x;
	//	r = height()-r;
	return r*OVERSMP;
}

inline float Axes2d::xrtod(float x) {
    //    x= height()-x;
    // printf("width: %8.3f\n", width());
    if (xopt&D2_OPT_LOG)
    {
	    // printf("got here \n");
	    // printf("xrtod was call, x: %8.3f, aorigin.x = %8.3f\n",x, aorigin.x);
	    
	    // float n = (x-aorigin.x)/asize.x*dsize.x+dorigin.x;
	    
	    // printf("n = %8.3f, xrtod: %8.3f\n",n,pow(10.0, n));
	return pow(10.0F,((x-aorigin.x)/asize.x*dsize.x+dorigin.x));
    }
    else
        return (x-aorigin.x)/asize.x*dsize.x+dorigin.x;
}

inline void Axes2d::setlabfn(char *lab(float, int)) { labfn=lab; }
inline int Axes2d::getOptions() { return options; }
inline int Axes2d::getXOpt() { return xopt; }
inline int Axes2d::getYOpt() { return yopt; }
inline QFont Axes2d::getTFont() { return *tfont; }
inline QFont Axes2d::getLFont() { return *lfont; }
inline QFont Axes2d::getSFont() { return *sfont; }
inline void Axes2d::setTextColor(QColor &color) { textcolor=color; needupd=1; }
inline void Axes2d::setAxisColor(QColor &color) { axiscolor=color; needupd=1; }
inline void Axes2d::setFrameColor(QColor &color) { framecolor=color; needupd=1; }
inline void Axes2d::setMouseColor(QColor &color) { mousecolor=color; needupd=1; }

inline int Axes2d::needUpd() { return needupd; }
#endif
