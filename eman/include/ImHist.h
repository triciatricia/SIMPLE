#ifndef IMHISTH
#define IMHISTH

#include <stdio.h>
#include <qwidget.h>
#include <qpixmap.h>
#include <qpainter.h>

#ifndef UBUNTU
	#include <qlist.h>
#endif	//UBUNTU

#include "EMData.h"

class ImHist:public QWidget {
	Q_OBJECT
	
	QPainter *qp;
	QPixmap *qpm;
	
	float mind,maxd;
	float range0,range1;
	float sel,peak,mean;
	int stat;
	float sigma;
	QString misc;

public:
	ImHist( QWidget *parent=0, const char *name=0 );
	~ImHist();
	
	virtual void paintEvent( QPaintEvent *qp );
	virtual void mousePressEvent(QMouseEvent *);
	virtual void mouseReleaseEvent(QMouseEvent *);
	virtual void mouseMoveEvent(QMouseEvent *);
	virtual void resizeEvent ( QResizeEvent * );

signals:
	
	
public slots:
	void setData(EMData *d);
	void setData(QList<EMData> *im,int n);
	void setMinMax(float min,float max);
	void setSel(float x);
	void setMiscText(QString s);
};
#endif
