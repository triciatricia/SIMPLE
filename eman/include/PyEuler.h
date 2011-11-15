#ifndef _pyeuler_h_
#define _pyeuler_h_

#include "PyList.h"
#include "Euler.h"

class PyEuler : public Euler {
public:
    PyEuler();
    PyEuler(float a1, float a2, float a3);
    PyEuler(float a1, float a2, float a3, int type);
    PyEuler(float a1, float a2, float a3, float a0, int type);
    PyEuler(PyList m);
    ~PyEuler();

    python::tuple getByType(EulerType type);
    void setByType(python::tuple value, EulerType type);
    
    friend PyEuler operator*(const PyEuler& lhs, const PyEuler& rhs);
    friend PyEuler operator/(const PyEuler& lhs, const PyEuler& rhs) ;
    friend int operator!=(const PyEuler& lhs, const PyEuler& rhs);
    friend int operator==(const PyEuler& lhs, const PyEuler& rhs);
    
};




#endif

