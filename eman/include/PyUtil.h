#ifndef _py_util_h_
#define _py_util_h_

#include "PyList.h"

void py_save_data(PyList x_list, PyList y_list, int n, const char* fsp);
void py_save_data(float x0, float dx, PyList y_list, int n, const char* fsp);
void py_lsqfit(int n, PyList dx_list, PyList dy_list, Float m, Float b,
	       int ign0 = 1);
float py_interpolate(float xl, int n, PyList x_list, PyList y_list);
void py_appinit(PyList argv);
int  py_LOGbegin(PyList argv, int ppid = 0);
void py_roteulertb(Float alt, Float az, Float phi, float dx, float dy);


#endif
