#ifndef COLH
#define COLH

#include "Equation.h"
#include <qobject.h>
#include <qvaluelist.h>

#define COL_DATA	1
#define COL_EQN		2
#define COL_RANGE	3
#define COL_REPCYC	4
#define COL_STRINGS	5

class DataSet;

class Column : public QObject{
    Q_OBJECT


float *data;
int n,nrep,ncyc,eqch,cid;
char type;
float min,max;
//QString ceqn;		//now stored in Equation object
Equation *eqn;
DataSet *parent;
QString title;
QValueList<QString> symbols;

public:
Column(int CID=0);
~Column();
void setRange(float min,float max,int n);
void setRepCyc(float min,float max,int nr,int nc,int n);
void setData(float *dat=NULL,int n=-1);
void setData(int n,float f);
void setData(int n,QString s);
void setEqn(const char *eqn,int n,DataSet *par);
void setSize(int n);
int getSize();
float dataAt(int n);
void updateEqn();
float getMin();
float getMax();
QString getEqn();
void setType(int t,int n);

float *getData();	// DANGEROUS! not for normal use
double *dependsOn(int n);
void eqChangedQ();	// a quiet version of the eqChanged slot

signals:
	void changed(int cid);		//column id used for DataSet

public slots:
	void eqChanged();
	void setVar(char *var,double val,bool quiet=0);
};

// This is called when the equation requires an update, but parents should not be notified
inline void Column::eqChangedQ() { 
if (type==COL_EQN) eqch=1;
}

inline int Column::getSize() { return n; }

inline float *Column::getData() { 
	if (type==COL_EQN && eqch) { updateEqn(); eqch=0; }
	return data; 
}

inline QString Column::getEqn() { 
	if (type==COL_EQN) return eqn->getEqn();
	return NULL;
}
#endif
