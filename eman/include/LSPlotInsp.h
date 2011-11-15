#ifndef LSPlotInsp_included
#define LSPlotInsp_included

#include "lsPlotInspBase.h"
#include "Inspector.h"
#include "Plot.h"
#include "LSPlot.h"

class LSPlotInsp : public lsPlotInspBase, public Inspector<Plot>
{
    Q_OBJECT

public:

    LSPlotInsp(QWidget *parent = NULL,const char *name = NULL );

    virtual ~LSPlotInsp();
	virtual void refresh();

    public slots:

    virtual void setLS(int);
    virtual void setSym(int);
    virtual void setVec(int);
    virtual void lineTog(bool);
    virtual void symTog(bool);
    virtual void setCol();
    virtual void setSSz(int);
    virtual void setCMode(int);
    virtual void setLW(int);
    virtual void colEnable();
    //    virtual void setConstCol(int);
    virtual void newConstColor();
};
#endif // LSPlotInsp_included
