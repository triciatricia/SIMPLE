#ifndef MINIIMAGEH
#define MINIIMAGEH

#include <stdio.h>
#include <qwidget.h>
#include <qpainter.h>
#include <qcolor.h>

#ifndef UBUNTU
	#include <qlist.h>
#endif	//UBUNTU

#include "EMData.h"

class MiniImage:public QWidget {
    Q_OBJECT
	
	QPainter *qp;
	unsigned char *data;
	int nx,ny;

public:
MiniImage( QWidget *parent=0, const char *name=0 );
~MiniImage();

virtual void paintEvent( QPaintEvent *qp );

signals:

public slots:
void setData(unsigned char *data,int nx,int ny);
};


#endif
