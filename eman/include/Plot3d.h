#ifndef PLOTH
#define PLOTH
#include <qobject.h>
#include <qpainter.h>
//#include "Axes2d.h"
#include "DataSet.h"
#include "misc.h"

class Axes3d;

class Plot3d : public QObject {
    Q_OBJECT

DataSet *data;
int *cols;
int ncol;
char *Label;

protected:
QFont *lfont;
QFontMetrics *lmet;

public:
Plot();
~Plot();

void setCols(int *c,int n);
void setCols(int c1,int c2,int c3,int c4);


virtual void setData(DataSet *data);
DataSet *getData();
int *getCols();
int getNCols();
void setLabel(char *label,float *mx);
char *label();
virtual void render(int list,float *mx);
virtual f3Rect getLimits();

signals:
	void changed();

private slots:
	virtual void dataChanged();

};

inline void Plot::setLabel(char *label) { Label=(char *)realloc(Label,strlen(label)+1); strcpy(Label,label); }
inline char *Plot::label() { return Label; }
inline DataSet *Plot::getData() { return data; }
inline int *Plot::getCols() { return cols; }
inline int Plot::getNCols() { return ncol; }
#endif
