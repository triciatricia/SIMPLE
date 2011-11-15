#ifndef ImageMxCon_included
#define ImageMxCon_included

#include "ImageMxConData.h"
#include "MiniImage.h"
#include "EMData.h"

#ifndef UBUNTU
	#include <qlist.h>
#endif	//UBUNTU

class ImageMxCon : public ImageMxConData
{
    Q_OBJECT

public:

    ImageMxCon(QWidget* parent = NULL,const char* name = NULL);

    virtual ~ImageMxCon();

	void setup(float b,float c, int inv, int lab,int mode=0);

	EMData *data;		// used only by histogram, and not guarenteed to be coorrect
	QList<EMData> *datal;
	bool histvis;
	int subim;
	int mdx,mdy;

signals:
	void setBC(float B,float C);
	void invToggle(int toggle);
	void fftToggle(int toggle);
	void labToggle(int toggle);
	void lab2Toggle(int toggle);
	void setScale(float scale);
	void saveImage();
	void saveFile();
	void newMode(int);
	void print();

public slots:
	void imageChanged(EMData *im);
	void imagesChanged(QList<EMData> *im);
	void imageMinMax(float min,float max);
	void doProbe(unsigned char *mx,int subim,int x,int y,float val,int but);
	void newBC(float B);
	void newInv(bool t);
	void newFFT(bool t);
	void newHist(bool t);
	void newLab(bool l);
	void newLab2(bool l);
	void newPoint(int x,int y);
	void newScale();
	void doSaveFile();
	void doSaveView();
	void setModeApp();
	void setModeProbe();
	void setModeDel();
	void setModeMove();
	void setModeSplit();
	void doPrint();
};
#endif // ImageMxCon_included
