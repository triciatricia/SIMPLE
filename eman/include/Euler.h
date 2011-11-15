#ifndef EULERINC
#define EULERINC

#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <cctype>
// #include "util.h"
#include <vector>
using std::vector;

class Vect;
class Euler;
//class Quaternion;


// int MAXEL[] = { 1 , 2 ,5,6,7 };

class Euler{

public:

// that means SPIN axis variables: closely related to QUATernionic variables
enum EulerType { EMAN,IMAGIC,SPIN,QUAT,MATRIX,SGIROT,SPIDER,MRC };

//      CONSTRUCTORS
// Euler(float a1, float a2, float a3, float a4=0, int typ_=1);  // An all-purpose one?
Euler();
Euler(float a1, float a2, float a3);// EMAN by default
Euler(float a1, float a2, float a3, int typ); // EMAN, IMAGIC or SPIDER
Euler(float e1, float e2, float e3, float e0, int typ); // QUATERNIONS, SPIN axis, or SGIROT
Euler(float *m); // matrix form
~Euler();
void init();

//		FUNCTION DECLARATIONS
void rectify();
void setAngle(float a1, float a2, float a3, int typ = EMAN);  //  EMAN, IMAGIC or SPIDER setAngle			
void setAngle(float e1, float e2, float e3, float e0, int typ); // quaternion, spin, and SGIROT setAngle
void setAngle(float *m); // matrix setAngle
void setTyp(int i);

void increment(float delAlt, float delAz, float delPhi); // increment an Euler in place
float diff(Euler* ang, bool nophi=true);	// find angle between two direction vectors (defined by alt,az, phi has no effect)

Euler inverse();       // takes the inverse of an euler
void fromLeft(Euler leftEuler); // rotates a given rotation  on the left
void fromLeft(float alt, float az, float phi); // rotates a given rotation  on the left
void fromLeftold(Euler bc); // rotates a given rotation  on the left; don't use this
Euler EulerMult(Euler bc) ;  // returns the value of the given rotation above

Euler operator*(Euler ab );
Euler operator/(Euler ab) ;
int operator!=(Euler ab);

int getMaxSymEl(); // gets the order of the group
char* getSym();	// return the symmetry string
void setSym(char *symmetry);// initialize symcounter to zero,
void resetSym();	// initializes symcounter_ without returning 1st element
Euler FirstSym();	// initializes symcounter_, symoperation_m MaxSymEl_
			// 	unless told otherwise
Euler NextSym();
Euler SymN(int n);	// returns the n'th symmetric element
int valid();

vector< Euler*> asymmetricUnit(float angle_step, int mode=0, int with_mirror=0); // return the complete list of orientations in an asymmetric unit

// we need as many ways as possible to read the data

void fromMRC(float theta, float phi, float omega);	//set from MRC angles

float thetaMRC() const;
float phiMRC() const;
float omegaMRC() const;
		
float alt() const;
float az() const;
float phi() const;

float alpha() const;  // IMAGIC lingo
float beta() const;
float gamma() const;

float phiSpider() const;    // SPIDER lingo
float thetaSpider() const;
float gammaSpider() const;

float e0() const;      // QUATernion lingo
float e1() const;
float e2() const;
float e3() const;

float Q() const;      // SPIN axis lingo
float n1() const;
float n2() const;
float n3() const;

float Qsgi() const;      //SGIROT lingo
float n1sgi() const;
float n2sgi() const;
float n3sgi() const;

float *mat(); // get out the 3 by 3 matrix; 
void print(char *id=NULL, FILE* out=stdout);
void printMatrix(char *id=NULL, FILE* out=stdout);

///////////////*******************************//////////////////////////
//////// the following 5 functions are added by Xiangan Liu (02/20/2004)
///////////////*******************************//////////////////////////

Vect GetXCoef();      //the first  line of the transform matrix
Vect GetYCoef();      //the second line of the transform matrix
Vect GetZCoef();      //the third  line of the transform matrix
Vect GetNormal();  // get Z' axis coordinates in XYZ system
Vect TransformXYZtoXYZprime ( Vect &v ); //transform a vector from XYZ system to X'Y'Z' system


void setAngleFromMRC(float alt_mrc, float az_mrc, float phi_mrc); //input mrc euler angle, directly give eman euler angles
void convertToMRCAngle(); //convert an eman euler to mrc euler angle directly
// return euler angles of MRC converted from eman convention, before using them, need to call convetTOMRCAngle()
float alt_MRC();
float az_MRC();
float phi_MRC();

///////////////*******************************//////////////////////////

//float operator[];

private:
int typ_;                  // The representation of the orientation that the user is employing
float alt_ , az_ , phi_ ;  // EMAN and internal variables
float alt_mrc, az_mrc, phi_mrc; // mrc euler angle, before using them, need to call convertToMRCAngle()
float m_[9];

char sym[8];
int nsym;		// number of symmetric elements
int csym;		// current symmetric element to return

// float alpha, beta, gamma; // IMAGIC variables
// float n1, n2, n3, Q;   // spin variables
// float e0, e1, e2, e3; // S4 or quaternionic variables

}; // ends declaration of class Euler

float *matmulmat(float *mleft, float *mright); // multiply 3 by 3 matrices

#endif
