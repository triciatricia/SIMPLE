#ifndef emobject_h_
#define emobject_h_

#include "EMData.h"

/** EMObject is a wrapper class for types including int, float,
 * double, etc as defined in ObjectType. Each type is typically used 
 * as follows ('int' is the example):
 *
 *    int a = 12;
 *    EMObject o(a);
 *    EMObject o2 = a; // implicit converter from int to EMObject. 
 *    int a1 = o;      // implicit converter from EMObject to int.
 * 
 * Backport from EMAN2 for new HDF I/O	--Grant Tang (gtang@bcm.edu)
 */
class EMObject
{
public:
	enum ObjectType {
		INT,
		FLOAT,
		DOUBLE,
		STRING,
		EMDATA,
		XYDATA,
		FLOATARRAY,
		STRINGARRAY,
		UNKNOWN
	};

public:
	EMObject():type(UNKNOWN)
	{
		n = 0;
		f = 0;
		d = 0;
		emdata = 0;
		xydata = 0;
	}

	EMObject(int num):n(num), emdata(0), xydata(0), type(INT)
	{
	}
	EMObject(float ff):f(ff), emdata(0), xydata(0), type(FLOAT)
	{
	}
	EMObject(double dd):d(dd), emdata(0), xydata(0), type(DOUBLE)
	{
	}
	EMObject(const char *s): n(0), emdata(0), xydata(0), str(string(s)), type(STRING)
	{
	}
	EMObject(const string & s):n(0), emdata(0), xydata(0), str(s), type(STRING)
	{
	}
	EMObject(EMData * em):n(0), emdata(em), xydata(0), type(EMDATA)
	{
	}
	EMObject(XYData * xy):n(0),  emdata(0), xydata(xy),type(XYDATA)
	{
	}
	EMObject(const vector < float >&v)
		:n(0), emdata(0), xydata(0), farray(v),type(FLOATARRAY)
	{
	}

	EMObject(const vector <string>& sarray)
		:n(0),emdata(0),xydata(0),strarray(sarray),type(STRINGARRAY)
	{
	}
	
	~EMObject() {
	}

	operator  int () const;
	operator  float () const;
	operator  double () const;
	operator  const char *() const;
	operator  EMData *() const;
	operator  XYData *() const;

	operator vector < float > () const;
	operator vector<string> () const;
	
	bool is_null() const;
	string to_str() const;
	ObjectType get_type() const;
	static const char *get_object_type_name(ObjectType t);

	friend bool operator==(const EMObject &e1, const EMObject & e2);
	friend bool operator!=(const EMObject &e1, const EMObject & e2);
	
private:
	union
	{
		int n;
		float f;
		double d;
	};

	EMData *emdata;
	XYData *xydata;
	string str;
	vector < float >farray;
	vector < string> strarray;
	ObjectType type;
};

bool operator==(const EMObject &e1, const EMObject & e2);
bool operator!=(const EMObject &e1, const EMObject & e2);

#endif	//emobject_h_	