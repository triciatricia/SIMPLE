#ifndef __pyemdatawrap_h__
#define __pyemdatawrap_h__

#include "PyEMDataWrap.h"
#include "PyEMData.h"
#include "PyEuler.h"
#include "PyVect.h"
#include "PyPickle.h"
#include <boost/python.hpp>
#include <boost/python/to_python_converter.hpp>

namespace python = boost::python;

void export_EMData();
void export_EMData2(python::class_<EMData>& EMData_class, python::class_<PyEMData, python::bases<EMData> >& PyEMData_class);
void export_EMData3(python::class_<EMData>& EMData_class, python::class_<PyEMData, python::bases<EMData> >& PyEMData_class);
void export_EMData4(python::class_<EMData>& EMData_class, python::class_<PyEMData, python::bases<EMData> >& PyEMData_class);

#endif
