
#include <qscrollview.h>
#include <qfont.h>
#include "ImageMxCon.h"
#include "EMData.h"
#include <qfiledialog.h>
#include <qpixmap.h>

#ifndef UBUNTU
	#include <qlist.h>
#endif //UBUNTU


// like QPoint, but can handle big numbers
class BPoint {
int X,Y;

public:
BPoint() { X=Y=0; }
BPoint( int x,int y) { X=x; Y=y; }

int x() { return X; }
int y() { return Y; }
void setX(int x) { X=x; }
void setY(int y) { Y=y; }
};



class ImageMx : public QScrollView {

Q_OBJECT

QList<EMData> data;
QList<BPoint> loc;

QFont *labelfont;

QPixmap qpm;

int autodel,label;
float cont,brite,scale;
int invert,mode;
int mdx,mdy,mim;
int orx,ory;

ImageMx *split;

ImageMxCon *imc;

virtual void viewportMousePressEvent(QMouseEvent *);
virtual void viewportMouseReleaseEvent(QMouseEvent *);
virtual void viewportMouseMoveEvent(QMouseEvent *);

public:
ImageMx(QWidget* parent=NULL,const char* name=NULL);
ImageMx(const ImageMx& img) {}
~ImageMx();

virtual void drawContentsOffset ( QPainter * p, int offsetx, int offsety, int clipx, int clipy, int clipw, int cliph );
virtual void resizeEvent ( QResizeEvent * );
virtual void closeEvent ( QCloseEvent * e );
void replaceData(int n,EMData *d);
void addData(EMData *d,int n=-1);
void removeData(EMData *d);
void removeData(int n);
void clearData();
void buildMx();
void makeVisible(int i);
void setAutoDelete(int i);		// If set, the EMData objects will be deleted when this window closes

inline float pxtodx(int px,int mim);
inline float pytody(int py,int mim);

signals:
void	mousePress(QMouseEvent *,int n,int ix, int iy);
void	mouseRelease(QMouseEvent *,int n,int ix, int iy);
void	mouseMove(QMouseEvent *,int n,int ix, int iy);
void	probe(unsigned char *mx,int sub,int x,int y,float val,int but);
void    imsChanged(QList<EMData> *im);

public slots:
void setBC(float b,float c);
void setInvert(int i);
void setLabel(int i);
void setLabel2(int i);
void setScale(float s);
void saveImage();
void saveFile();
void notVisible();
void setMode(int m);
void setReadOnly(int ro);
void print();
};

inline float ImageMx::pxtodx(int px,int mim) {
return ((px-loc.at(mim)->x()-1)/scale+.5);
}

inline float ImageMx::pytody(int py,int mim) {
return ((data.at(mim)->ySize()*scale-(py-loc.at(mim)->y()))/scale)+.5;
}


inline void ImageMx::setAutoDelete(int i) { if (i) data.setAutoDelete(TRUE); else data.setAutoDelete(FALSE); autodel=i; }
