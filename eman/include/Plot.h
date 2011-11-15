#ifndef PLOTH
#define PLOTH
#include <qobject.h>
#include <qpainter.h>
//#include "Axes2d.h"
#include "DataSet.h"
#include "misc.h"

#define PLOT_SELECTED	(1<<30)		// selected flag, not used yet

class Axes2d;

class Plot : public QObject {
    Q_OBJECT

DataSet *data;
QString Label;

protected:
QFont *lfont;
QFontMetrics *lmet;
QArray<int> cols;
int flags;	// lower 24 bits of flags are different for each plot, top 8 reserved

public:
Plot();
~Plot();

void setCols(int *c,int n);
void setCols(int c1,int c2=1,int c3=1,int c4=1,int c5=1,int c6=1,int c7=1);

virtual void setData(DataSet *data);
DataSet *getData();
QArray<int> getCols();
void setFlags(int f);
int getFlags();
void setLabel(const QString &nl);
QString getLabel();
virtual void display(QPainter *qp,Axes2d *axis,int x0,int y0,int x1,int y1);
virtual int legend(QPainter *qp,Axes2d *axis,int x,int y);
virtual fRect getLimits();

signals:
	void changed();

   public slots://private before
	virtual void dataChanged();

};

inline void Plot::setFlags(int f) { flags=f; }
inline int Plot::getFlags() { return flags; }
inline void Plot::setLabel(const QString &lab) { Label=lab; }
inline QString Plot::getLabel() { return Label; }
inline DataSet *Plot::getData() { return data; }
inline QArray<int> Plot::getCols() { return cols; }
#endif
