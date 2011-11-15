#ifndef InspAxis_included
#define InspAxis_included

#include "inspAxisBase.h"
#include "Axes2d.h"
#include "Inspector.h"

class InspAxis : public inspAxisBase, public Inspector<Axes2d>
{
    Q_OBJECT

	int axis;

public:

    InspAxis
    (
        QWidget* parent = NULL,
        const char* name = NULL
    );

    virtual ~InspAxis();
	virtual void refresh();
	virtual void setAxis(int a) { axis=a; }	// 0 -> x, 1 -> y

protected slots:
    virtual void newCBTitle(bool);
    virtual void newMajGrid(bool b);
    virtual void newMaj();
    virtual void newMajTick(bool b);
    virtual void newMax();
    virtual void newAxisColor();
    virtual void newMin();
    virtual void newCBLog(bool);
    virtual void newTFont();
    virtual void newAuto(bool);
    virtual void newAFont();
    virtual void newCBAxis(bool);
    virtual void newMinor(int);
    virtual void newMinGrid(bool b);
    virtual void newTitle();

};
#endif // InspAxis_included
