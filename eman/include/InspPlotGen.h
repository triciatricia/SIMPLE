#ifndef InspPlotGen_included
#define InspPlotGen_included

#include "inspPlotGenBase.h"
#include "Inspector.h"
#include "Plot.h"

class InspPlotGen : public inspPlotGenBase, public Inspector<Plot>
{
    Q_OBJECT

public:

    InspPlotGen(
        QWidget *parent = NULL,
        const char *name = NULL );

    virtual ~InspPlotGen();
};
#endif // InspPlotGen_included
