#ifndef D2Inspector_included
#define D2Inspector_included

#include "d2InspectorBase.h"
#include "Inspector.h"

class Axes2d;

class D2Inspector : public d2InspectorBase
{
    Q_OBJECT
    Inspector<Axes2d> *insp[4];
    int ci;
    Axes2d *target;

public:

    D2Inspector(QWidget* parent = NULL,const char* name = NULL);

    virtual ~D2Inspector();
    virtual void setTarget(Axes2d *t);
	
protected slots:

   virtual void tabSel();
   virtual void refresh() { insp[ci]->refresh(); }
	
//	virtual void focusInEvent ( QFocusEvent *e ) { insp[ci]->update(); }
//	virtual void enterEvent ( QEvent *e ) { insp[ci]->update(); }
};
#endif // D2Inspector_included
