#ifndef CYLINDER_H
#define CYLINDER_H

// by Wen Jiang, June 2000

#include <ctime>
#include "EMData.h"
#include "Vect.h"
#include <cstring>
#include <vector>

using namespace std;

class Cylinder {
	Point	cen;
	Vect	axis;
	float	radius, length;	// in Angstrom
	float	weight;
	int startid, endid;
	string label;
	
	public:
	Cylinder();
	Cylinder(const Point& center, const Vect& axisdir, float len = 5.4, float r = 2.5, float w = 0.9);
	Point	Center();
	Vect	Axis();
	Quater	QuaterForAxis();
	float	Xc();
	float	Yc();
	float	Zc();
	float	Alt();
	float	Az();
	float	Radius();
	float	Length();
	float	Weight();
	int 	StartID();
	int		EndID();
	string	Label();
	void	print(int id = -1, FILE *out = stdout);
	void	toInventor(FILE *out = stdout, int id = 0, int indent = 1, bool with_head = false);
	void	toDejaVu(FILE *out = stdout, int id = 0);
	void	toCosec(FILE *out = stdout, int id = 0);
    //void	setCenter(const Point& center);
	void	setCenter(float x, float y, float z);
	void	setAxis(const Vect& axisdir);
	void	setAxis(Euler& axisdir);
	void	setAxis(Euler* axisdir);
	void	setRadius(float r);
	void	setLength(float l);
	void	setWeight(float w);
	void 	setStartID(int i);
	void	setEndID(int i);
	void	setLabel(const string& l);
	float	PlaneAngleDiff(Cylinder * next);// dihedral angle of planes formed by the two axes and center connection vector
	float	AxisAngleDiff(Cylinder * next);	// difference in orientation (axises)
	float	Angle2Vect(Vect& v);	// difference in orientation axis of this and the direction vector 
	float	Angle2Point(Point& p);	// difference in orientation between line passing both P and this center and axis of this 
	float	Angle2Center(Cylinder * next);	// difference in orientation between line passing both centers and axis of this
	float	NormDistance(Cylinder * next); // shortest distance of the two axes 
	float	CenterDistance(Cylinder * next); // distance of the center of next cylinder to the center of this
	float	Distance2Point(float x, float y, float z); // distance of the Point to the center of this cylinder
	bool 	if_merge(Cylinder * next, float da_limit = 30. * PI / 180., float distance_limit = 3.2); // if next is ok to merge with this
	bool 	merge(Cylinder * next);	// actually merge both into this
	void	mirror();	// mirror the cylinders
	void	Transform(Quater& rot, Vect& trans, Vect& center);	// transform: rotate then translate
	void	Transform(Euler& rot, Vect& trans, Vect& center);	// transform: rotate then translate
};

class CylLenComp {	// sort criteria : increasing order
	public:
	int	operator()( Cylinder *cyl1,  Cylinder *cyl2) const {
		return (cyl1->Length()) > (cyl2->Length());
	} 
};

class CylWeightComp {	// sort criteria : increasing order
	public:
	int	operator()( Cylinder *cyl1,  Cylinder *cyl2) const {
		return (cyl1->Weight()) > (cyl2->Weight());
	} 
};

class Cylinders {
private:
	vector < Cylinder* > cyls;
public:
	int size();
	Cylinders copy();
	Cylinders subset(int* list, int n);
	bool add(Cylinder * cyl);
	bool ReadListfile(const char * in = "-");
	bool ReadListfile(FILE * in = stdin);
	bool WriteListfile(FILE * out = stdout);
	bool WriteListfile(const char * out = "-");
	bool ReadInventor(FILE * in = stdin);
	bool ReadInventor(const char * in = "-");
	bool WriteInventor(FILE * out = stdout);
	bool WriteInventor(const char * out = "-");
	bool WriteVRML(FILE *out = stdout);
	bool WriteVRML(const char *out = "-");
	bool ReadDejaVu(FILE * in=stdin);
	bool ReadDejaVu(const char * in="-");	
	bool WriteDejaVu(FILE * out=stdout, const char * mol = "0dum", const char * note = "dummy protein", const char * pdb = "0dum.pdb");
	bool WriteDejaVu(const char * out="-", const char * mol = "0dum", const char * note = "dummy protein", const char * pdb = "0dum.pdb");
	bool ReadCosec(FILE * in=stdin);
	bool ReadCosec(const char * in="-");	
	bool WriteCosec(FILE * out=stdout, const char *prog="helixhunter", const char *pdbid="0dum", const char *header="dummy protein", const char *compnd="dummy protein", const char *source="nowhere", const char *author="");
	bool WriteCosec(const char *out="-", const char *prog="helixhunter", const char *pdbid="0dum", const char *header="dummy protein", const char *compnd="dummy protein", const char *source="nowhere", const char *author="");
	bool SortLength();
	bool SortWeight();
	float OrientationDiff(Cylinders& comp, bool ignoredir=true, bool uselengthweight=true);	// average individual cylinders angle diff
	void mirror();
	void Transform(Quater& rot, Vect& trans, Vect& center);	// transform: rotate then translate
	void Transform(Euler& rot, Vect& trans, Vect& center);	// transform: rotate then translate
	void print();
	Cylinder * operator[](int i){return cyls[i];}; 
};

inline float radprofile(float r, int type = 0);
EMData *modelHelix(EMData *in, float alt, float az, int type = 0, float len = 10.8, int x0 = -1, int y0 = -1, int z0 = -1, bool reset = true);
void	threshHold(EMData*map, float thresh);

void	jacobi(float nu[][3], float d[], float v[][3]);
void	eigsrt(float d[], float v[][3]);
void	AspectRatio(float evalue[3], float ratio[3]);

class ObjectStat {
public:
	float   xc, yc, zc;
	Vect	axis;
	float	mass, volume, len, rad;
	float 	aspectratio[3];
	float	moments[3][3], eigenvalue[3], eigenvector[3][3];
	void	SetObject(EMData *map, const vector < Point * > &obj);
	void	SetObject(EMData *map);
	void	EigenSortTo(ObjectStat *obj);
	void	FitEllipsoid(bool sort = true);
	void	Norm();
	void	ComputeLongAxis();
	Euler	rotationFromOrigin();	// the rotation needed from orientation origin (longest axis-x, shortest axis-z)
	void	print();
};

// definitons for output format for use in IRIS Explorer module
struct Match { 
    float    qx;        //quaternion 
    float    qy;        //quaternion 
    float    qz;        //quaternion 
    float    qa;        //quaternion 

    float    tx;        //translation 
    float    ty;        //translation 
    float    tz;        //translation 
  
    float    c;         //coefficient 
    float    len;       //helix length 
};
  
typedef Match Helix;

struct FHH { 
    char	version[32];     //set to "#helixhunter V1 binary\n" for helixhunter output helices
							//		 "#foldhunter V1 binary\n" for foldhunter output matches	
    long    n;              //number of foldhunter matches or helices 

    char    fileRef[512]; 
    char    fileProbe[512]; 
    char    fileCoeff[512]; 

    float    apix;       //reference resolution 
    float    rox;       //relative origin of reference 
    float    roy;       //relative origin of reference 
    float    roz;       //relative origin of reference 

    float    pcx;       //probe center 
    float    pcy;       //probe center 
    float    pcz;       //probe center 		
}; 

typedef FHH HHH;

#endif
