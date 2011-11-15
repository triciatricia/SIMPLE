#ifndef _pylist_h_
#define _pylist_h_

#include <boost/python.hpp>
#include <boost/python/to_python_converter.hpp>
#include <boost/python/detail/api_placeholder.hpp>

#include <vector>
using std::vector;

class List;
namespace python = boost::python;
typedef python::list PyList;
typedef python::numeric::array PyArray;

void list2array(const PyList& l, int* array);
void list2array(const PyList& l, float* array);
void list2array(const PyList& l, const char** array);
void array2list(const int* array, PyList& l, int nitems = 0);
void array2list(const float* array, PyList& l, int nitems = 0);


class Float {
public:
    Float(float v = 0) {
        val = v;
    }
   
    Float(const Float& other) {
	val = other.val;
    }

    float val;
};

template <class T>
struct vector_to_python : python::to_python_converter<vector<T>, vector_to_python<T> >
{
    static PyObject* convert(vector<T> const& v)
    {
	python::list result;

	for (size_t i = 0; i < v.size(); i++) {
	    result.append(v[i]);
	}

	return python::incref(python::list(result).ptr());
    }
};

    
template <class T>
struct vector_from_python
{
    vector_from_python()
    {
	python::converter::registry::push_back(&convertible, &construct,
					       python::type_id<vector<T> >());
    }
    
    static void* convertible(PyObject* obj_ptr)
    {
	if (!(PyList_Check(obj_ptr) || PyTuple_Check(obj_ptr)
	      || PyIter_Check(obj_ptr)  || PyRange_Check(obj_ptr))) {
	    return 0;
	}
	
	return obj_ptr;
    }

    
    static void construct(PyObject* obj_ptr,
			  python::converter::rvalue_from_python_stage1_data* data)
    {
	void* storage = ((python::converter::rvalue_from_python_storage<vector<T> >*) data)->storage.bytes;
	new (storage) vector<T>();

	data->convertible = storage;

	vector<T>& result = *((vector<T>*) storage);
	
	python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
	
	while(1) {
	    python::handle<> py_elem_hdl(python::allow_null(PyIter_Next(obj_iter.get())));
	    if (PyErr_Occurred()) {
		python::throw_error_already_set();
	    }
	    
	    if (!py_elem_hdl.get()) {
		break;
	    }
	    
	    python::object py_elem_obj(py_elem_hdl);
	    python::extract<T> elem_proxy(py_elem_obj);
	    result.push_back(elem_proxy());
	}
    }
};
    

#endif
