#ifndef InspArea_included
#define InspArea_included

#include "inspAreaBase.h"
#include "Axes2d.h"
#include "Inspector.h"

class InspArea : public inspAreaBase, public Inspector<Axes2d>
{
    Q_OBJECT

public:

InspArea(QWidget* parent = NULL,const char* name = NULL);

virtual ~InspArea();

virtual void refresh();

protected slots:
virtual void newCBTitle(bool);
virtual void newAxLW(int);
virtual void newCBLBox(bool);
virtual void newXTitle();
virtual void newShowY0(bool);
virtual void newCBLR(bool);
virtual void newYTitle();
virtual void newFrameLw(int);
virtual void newAnimZ(bool);
virtual void newCBXAX(bool);
virtual void newCBYAX(bool);
virtual void newCBLegend(bool);
virtual void newTFont();
virtual void newFrameColor();
virtual void newAxColor();
virtual void newCBYTitle(bool);
virtual void newLFont();
virtual void newCBFrame(bool);
virtual void newCBXTitle(bool);
virtual void newTitle();
virtual void savepng();
virtual void print();
 
};
#endif // InspArea_included
