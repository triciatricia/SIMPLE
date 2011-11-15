#ifndef __pypickle_h_
#define __pypickle_h_

#include <boost/python.hpp>

class Euler;
class EMData;
class Vect;
class Quater;
class Cylinder;
class ObjectStat;

namespace python = boost::python;

class Euler_pickle_suite : public python::pickle_suite {
public:
    static python::tuple getinitargs(Euler& e);
};

class EMData_pickle_suite : public python::pickle_suite {
public:
    static python::tuple getinitargs(EMData& em);
    static python::tuple getstate(python::object em);
    static void setstate(python::object em, python::tuple state);
    static bool getstate_manages_dict();
};

class Quater_pickle_suite : public python::pickle_suite {
public:
    static python::tuple getinitargs(Quater& q);
};

class Vect_pickle_suite : public python::pickle_suite {
public:
    static python::tuple getinitargs(Vect& v);
};

class Cylinder_pickle_suite : public python::pickle_suite {
public:
    static python::tuple getinitargs(Cylinder& c);
};


class ObjectStat_pickle_suite : public python::pickle_suite {
public:
    static python::tuple getinitargs(ObjectStat& o);
    static python::tuple getstate(python::object o);
    static void setstate(python::object o, python::tuple state);
    static bool getstate_manages_dict();
};

#if 0

class HHH;
class Helix;

class Helix_pickle_suite : public python::pickle_suite {
public:
    static python::tuple getinitargs(Helix& h);
    static python::tuple getstate(python::object h);
    static void setstate(python::object h, python::tuple state);
    static bool getstate_manages_dict();
};

class HHH_pickle_suite : public python::pickle_suite {
public:
    static python::tuple getinitargs(HHH& h);
    static python::tuple getstate(python::object h);
    static void setstate(python::object h, python::tuple state);
    static bool getstate_manages_dict();
};
#endif

#endif
