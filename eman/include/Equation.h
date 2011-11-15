#ifndef EQNH
#define EQNH

#include <stdlib.h>
#include <qobject.h>
#include <qdict.h>

#ifndef UBUNTU
	#include <qlist.h>
#endif	//UBUNTU

#include "mathcommon.h"

class Equation : public QObject {
    Q_OBJECT

Term *tree;
//Term *tlist;
//int nterm,nterma;

Term *newTerm();
double evalTerm(Term *term);

static M_OPS *oplist;
static int nops,nopsa;
QDict<double> varlist;
QString eqn;

public:
Equation();
~Equation();
static void init();
int parseToken();

// This sets the current equation
int parseEqn(QString s);
QString getEqn();	// returns the current equation

double eval();
void freeTree(Term *term);

void setVar(char *name,double val,bool quiet=FALSE);		// sets value of variable
double getVar(char *name);				// gets value of variable or NaN if unset
double *getVarP(char *name);			// gets pointer to variable, created if unset
										// useful for speed for multiple updates
										// but prevents any auto-update

static void addop1(char *name,double (*fn)(double parm));
static void addop2(char *name,double (*fn)(double parm1,double parm2));
static void addopn(char *name,double (*fn)(int n,double *parm));

signals:
	void	changed();

private slots:

};

inline QString Equation::getEqn() { return eqn; }

inline Term *Equation::newTerm() { return (Term *)malloc(sizeof(Term)); }

/*inline Term *Equation::newTerm() { 
	nterm++; 
	if (nterm==nterma) { 
		nterma+=nterma/2; 
		tlist=(Term *)realloc(tlist,nterma*sizeof(Term)); 
	}
	return &tlist[nterm-1]; 
}*/

#endif
