#ifndef VECT_QUATER_H
#define VECT_QUATER_H

// by Wen Jiang, June 2000

#include "Euler.h"
#include "util.h"

//#ifndef PI
//#define PI 3.14159265358979
//#endif


class Quater {
public:
	float	nx, ny, nz, Q;
	Quater();
	Quater(Euler& e); 
	Quater(float x, float y, float z, float q);
	void fromEuler(Euler& e);
	Euler toEuler();
	void print(char* id=NULL, FILE* out=stdout);
};
		
class Vect {
private:
	float	x, y, z;
public:
	Vect();
	Vect(float xx, float yy, float zz);
	void normalize();
	Vect rotate(float m[9]);	// assume m[9] array
	Vect rotate(float m[3][3]);	// assume m[3][3] array
	Vect rotate(Euler *ang);
	Vect rotate(Euler& ang);
	Vect rotate(float alt, float az, float phi);
	Vect rotate(Quater *q);
	Vect rotate(Quater& q);
	Vect rotate(Vect& p, float q);
	Vect rotate(float nx, float ny, float nz, float q);
	Vect cross(Vect& p);
	Vect CrossP(Vect& p);   //( same function as the cross() above, but different implementation) added by Xiangan Liu 
	Quater getQuater();
	inline float X();
	inline float Y();
	inline float Z();
	inline float Alt();
	inline float Az();
	void setX(float xx);
	void setY(float yy);
	void setZ(float zz);
	void setXYZ(float xx, float yy, float zz);
	float inner(Vect& p);
	float angle(Vect& p, Vect y = Vect());
	float length();
	Euler euler();	// Euler angle needed for (0,0,1) be rotated to this
	Euler eulerTo(Vect& p);
	Euler eulerTo(float x, float y, float z);
	bool isNeighbor(Vect* p);	//26 neighbor connection
	bool isNeighbor(Vect& p);	//26 neighbor connection
	void print(char* id=NULL, FILE* out=stdout);
	Vect operator * (float r);
	Vect operator / (float r);
	Vect operator + (float r);
	Vect operator + (const Vect& r);
	Vect operator - (float r);
	Vect operator - (const Vect& r);
	bool operator == (const Vect& p);
};

inline float Vect::X()
{
	return x;
}

inline float Vect::Y()
{
	return y;
}

inline float Vect::Z()
{
	return z;
}

inline float Vect::Alt()
{
	return euler().alt();
}

inline float Vect::Az()
{
	return euler().az();
}

typedef Vect Point;

/*************************************************
**
** not really needed for transformation right now
** just leave it here in case future needs
**
**************************************************

class Transform3D {
private:	
	float m[16];
public:
	Transform3D();
	Transform3D(Euler& euler);
	Transform3D(Vect& vect);
	Transform3D(Euler& euler, Vect& vect);	// translate then rotate
	Transform3D(const float mat[16]);
	void setUnit();
	void setMatrix(const float mat[16]);	
	void setRotation(Euler& euler);
	void setTranslation(Vect& vect);
	Euler getRotation();
	Vect getTranslation();
	const float *mat();
	Transform3D inverse();
	Transform3D inverseRotation();
	void print(char* id=NULL, FILE* out=stdout);
	Transform3D operator*(Transform3D& tf);
	void operator=(Transform3D& tf);
};		
*/
Quater euler2quater (Euler& ang);
Quater euler2quater (float alt, float az, float phi);
Euler quater2euler(float nx, float ny, float nz, float Q);
Euler quater2euler(Quater& quater);
Euler quater2euler(Vect& p, float q);


#endif
