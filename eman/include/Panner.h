#include <qwidget.h>

#ifndef PANNER_H
#define PANNER_H

class Panner:public QWidget {
    Q_OBJECT


virtual void mousePressEvent ( QMouseEvent * );
virtual void mouseMoveEvent ( QMouseEvent * );
virtual void mouseReleaseEvent ( QMouseEvent * );
virtual void paintEvent ( QPaintEvent * pe );

float X[4],Y[4];	// min, max, width(0-1), cur
int busy;
int pressed;

public:
Panner( QWidget *parent = NULL, const char *name = NULL);
~Panner();


float xVal();
float yVal();
void validate();

signals:
void newValue(float x,float y);

public slots:
void setHandleSize(float x,float y);
void setXRange(float min,float max);
void setYRange(float min,float max);
void setValue(float x, float y);
void setXValue(float x);
void setYValue(float y);

};

inline float Panner::xVal() { return X[3]; }
inline float Panner::yVal() { return Y[3]; }

#endif