#ifndef Inspector_included
#define Inspector_included

#include "qwidget.h"

template<class type> class Inspector
{

protected:
type *target;

public:

Inspector() { target = NULL; }

virtual ~Inspector() {}

virtual type *getTarget() { return target; }
virtual void setTarget(type *t) { target=t; refresh(); }
virtual void refresh() {}

};
#endif
