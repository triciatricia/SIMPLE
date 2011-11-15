#ifndef IMAGEH
#define IMAGEH

#include <stdio.h>
#include <qwidget.h>
#include <qpixmap.h>
#include <qpainter.h>
#include <qcolor.h>
#include <qfont.h> 
#include <qdict.h>
#include <qintdict.h>
#include "EMData.h"
#include "Euler.h"
#include "ImageMxCon.h"
#include <qfiledialog.h>
#include <qspinbox.h>

#ifndef UBUNTU
	#include <qfontmet.h>
	#include <qlist.h>
#endif	//UBUNTU	

struct ImShape {
    enum { NONE, LINE, BOX, DOTBOX, CIRCLE, TEXT, CENELLIPSE, FILL_CIRCLE, HELIXBOX };
    int type;
    float x0,y0,x1,y1;			// origin & width,height
    float r;
    float sel0,sel1;
    union { int user; float userf; };	// misc use for flags, etc.
    union { int user2; float userf2; };	// misc use for flags, etc.
    QColor color;
    QString text;
    short lw;

    ImShape() { text=""; type=NONE; x0=y0=x1=y1=0; r=50; color=QColor(0,0,0); lw=1;}
    ~ImShape() { }

};

class Image:public QWidget {
    Q_OBJECT

protected:
    QPainter *qp;
    QPaintDevice *qpd;
    QPixmap *qpm;

    EMData *datar;
    EMData *dcopy;
    EMData *data;
    EMData *slicea;
    Euler angle;

    ImageMxCon *imc;
    //   QSpinBox   *spinbox;
    

    QString mtstr;
    QString imagefile;

    int mdx,mdy;
    int needupd;
    int mode,invert,showfft;
    float cont,brite,hmin,hmax;
//	float hist[256];	// histogram of current image used for b/c adjustement

    int originx,originy;
    float scale;

    QList<ImShape> shapes;

public:

    float lscale;		// DO NOT MODIFY EXTERNALLY

    ImShape select;

    Image( QWidget *parent=0, const char *name=0 );
    Image(const Image& img) {}
    ~Image();

    void setData(EMData *d);
    EMData *getData();
    QPixmap *getQPixmap();

    void setNullString(char *str);
    void setFileName(char* str);

    int addShape(ImShape *s,int n=-1);
    void delShape(int n);
    void clearShapes();
    ImShape *shapeAt(int n);
    int nShapes();
    void hilight(int i);

    float pxtodx(int);
    float pytody(int);
    int dxtopx(int);
    int dytopy(int);
    float getOriginx();
    float getOriginy();
    void helixUpdate(int);
    float get128();	// returns the float value displayed as a middle grey value

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
    virtual void print(QPaintDevice *dev);

    signals:
    void	resized(int neww, int newh);
    void	keyPress(QKeyEvent *);
    void	mousePress(QMouseEvent *);
    void	mouseMove(QMouseEvent *);	// Only events not intercepted by the image object, usu with lbm
    void	mouseRelease(QMouseEvent *);
	void	mouseMoveAll(QMouseEvent *);	// ALL mousemove events. Any slots must be very fast
    void	moved(int xo,int yo);
    void	changed();
    void	imChanged(EMData *data);
    void	probe(unsigned char *mx,int na,int x,int y,float val,int but);

public slots:
    void	imageChanged();
    void	setMode(int val);
    void	setCont(float val);
    void	setBrite(float val);
    void	setBC(float b, float c);
    void	setScale(float sca);
    void	setOrigin(int x,int y);
    void	setInvert(int);
    void	setFFT(int);
    void	saveImage();
    void	notVisible();
    void	doPrint();
    void	changeslice(int val);
    void	reload();
};


inline EMData *Image::getData() { return datar; }
inline QPixmap *Image::getQPixmap() { return qpm; }
inline void Image::setMode(int val) { mode=val; needupd=1; update(); }
inline void Image::setCont(float val) { cont=val; needupd=1; update(); }
inline void Image::setBrite(float val) { brite=val; needupd=1; update(); }
inline void Image::setNullString(char *str) { mtstr=str; update(); }
inline void Image::setFileName(char *str){ imagefile=str;}
inline int Image::nShapes() { return shapes.count(); }
inline float Image::getOriginx() { return originx; }
inline float Image::getOriginy() { return originy; }
#endif
