#include <qgl.h>

#define D3_ACT_ROTATE	1		// these 4 are for display only
#define D3_ACT_LEGEND	2		// move legend
#define D3_ACT_ZOOM		4		// user zoom in on drag, rescale on click

#define D3_OPT_FLOOR	(1<<0)
#define D3_OPT_WALLS	(1<<1)
#define D3_OPT_TITLE	(1<<2)
#define D3_OPT_AUTOSCALE	(1<<3)
#define D3_OPT_ANIMZOOM	(1<<4)	// unimplimented
#define D3_OPT_SHOWZ0	(1<<5)	// Always show the x axis
#define D3_OPT_LEGEND	(1<<6)	// display legend

#define D3_OPT_AXIS		(1<<0)
#define D3_OPT_TIC		(1<<1)
#define D3_OPT_GRID		(1<<2)	// unimplimented
#define D3_OPT_LOG		(1<<3)	// unimplimented
#define D3_OPT_SCALE	(1<<4)
#define	D3_OPT_CSCA		(1<<5)
#define D3_OPT_LABEL	(1<<6)

#define D3_OPT_ASDIS	(1<<22)	// INTERNAL USE ONLY!	(disabled autoscale)
#define D3_OPT_XCH		(1<<23)	// INTERNAL USE ONLY!	(crosshair)
#define D3_OPT_YCH		(1<<24)
#define D3_OPT_XRA		(1<<25) // INTERNAL USE ONLY!  (range)
#define D3_OPT_YRA		(1<<26)
#define D3_OPT_TXT		(1<<27)	// INTERNAL USE ONLY!  (position display)
#define D3_CLRINT		((1<<23)-1)	// for clearing internal flags

class Axes3d : public QGLWidget {
	Q_OBJECT

unsigned char *data;
f3Point dorigin,dsize,dlimit;
f3Point aorigin,asize,alimit;
int needupd;

unsigned char *data;

public:

Axes3d( QWidget *parent, const char *name ):QGLWidget(parent,name);
~Axes3d();

void setData(unsigned char *d,int x,int y,int z);
float xdtor(float x);
float ydtor(float y);
float zdtor(float z);
float xrtod(float x);
float yrtod(float y);
float zrtod(float z);

public slots:

void setThr(float val);	

protected:

void initializeGL();

void resizeGL( int w, int h );

void paintGL();

};
