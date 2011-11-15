#ifndef _pyvect_h_
#define _pyvect_h_

#include "Vect.h"

class PyVect : public Vect {
public:
    PyVect();
    PyVect(float xx, float yy, float zz);

    friend PyVect operator * (const PyVect& lhs, float rhs);
    friend PyVect operator / (const PyVect& lhs, float rhs);
    friend PyVect operator + (const PyVect& lhs, float rhs);
    friend PyVect operator + (const PyVect& lhs, const PyVect& rhs);
    friend PyVect operator - (const PyVect& lhs, float rhs);
    friend PyVect operator - (const PyVect& lhs, const PyVect& rhs);
    friend int operator == (const PyVect& lhs, const PyVect& rhs);
};

#endif
