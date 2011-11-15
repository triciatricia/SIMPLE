#ifndef InspPlot_included
#define InspPlot_included

#include "inspPlotBase.h"
#include "Axes2d.h"
#include "Inspector.h"

class InspPlot : public inspPlotBase, public Inspector<Axes2d>
{
    Q_OBJECT

	Inspector<Plot> *insp[3];
	int ci;
	Plot *target2;

public:

    InspPlot(QWidget* parent = NULL,const char* name = NULL);

    virtual ~InspPlot();
	virtual void refresh();

protected slots:

    virtual void newPlotTab();
    virtual void newLegend(bool);
    virtual void newPlotList(int);
    virtual void newPlotName();
};
#endif // InspPlot_included
