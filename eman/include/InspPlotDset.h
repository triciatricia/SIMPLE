/**********************************************************************

	--- Qt Architect generated file ---

	File: InspPlotDset.h
	Last generated: Tue Nov 9 22:07:32 1999

 *********************************************************************/

#ifndef InspPlotDset_included
#define InspPlotDset_included

#include "inspPlotDsetBase.h"
#include "Inspector.h"
#include "DataSet.h"
#include "Plot.h"

class InspPlotDset : public inspPlotDsetBase, public Inspector<Plot>
{
    Q_OBJECT
    
public:

    InspPlotDset(
        QWidget *parent = NULL,
        const char *name = NULL );

    virtual ~InspPlotDset();
    //    virtual void displayPlotData();
    virtual void refresh();
};
#endif // InspPlotDset_included
