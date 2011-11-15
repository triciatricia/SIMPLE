#ifndef _quaternion__h__
#define _quaternion__h__

#include "Euler.h"
#include "Vect.h"

class Quaternion {
public:
#ifdef APPLE
	/*This is a dummy boolean variable to work around the compilation failure on Mac OS X.*/
	bool dummy_;
#endif
	double w, x, y, z;
	float  m_f[9];
	double m[9];

	Quaternion();
	Quaternion(const Quaternion& Q);
	Quaternion(double w1, double x1, double y1, double z1);
	Quaternion(const Euler& Eu);
	Quaternion(double alt, double az, double phi);
	Quaternion(float  mat[9]);
	Quaternion(double mat[9]);

	void   setQuaternion(const Quaternion& Q);
	void   setQuaternion(double w1, double x1, double y1, double z1);
	void   setQuaternion(Euler& Eu);
	void   setQuaternion(double alt, double az, double phi);
	void   setQuaternion(float  mat[9]);
	void   setQuaternion(double mat[9]);
	void   setQuaternionAngleAxis(double theta, double nx, double ny, double nz); //set this quaternion by rotatation angle and axis
	void   setQuaternionAxisUP();
	void   setQuaternionFlip();
	void   setQuaternionRotation(int i, double theta);

	double  getAngle(const Quaternion& Q);
	double  dotQuaternion(const Quaternion& Q1);
	void   multQuaternion(const Quaternion& Q1);
	void   invMultQuaternion(const Quaternion& Q1); //inverse multiply, Q1*this, NOT this*Q1
	double  dotQuaternion(double w1, double x1, double y1, double z1);
	void   multQuaternion(double w1, double x1, double y1, double z1);
	void   invMultQuaternion(double w1, double x1, double y1, double z1); //inverse multiply, inputQ*this, NOT this*inputQ
	Quaternion matrixToQuaternion(double mat[9]);  //the input matrix has to be orthoganal and transfer from X'Y'Z'/intrinsic system to XYZ/world system
	void   calMatrix();
	double *getMatrix();
	Euler  getEuler();
	Quaternion getQuaternion();
	void   getAngleAxis(double* theta, double* nx, double* ny, double* nz); //return rotatation angle and axis
	void   getAngleAxisUp(double* theta, double* nx, double* ny, double* nz); //keep rotation axis up, angle 0 --> 2pi, since Q and -Q are the same rotation
	Vect   GetXCoef();      //the first  column of the transform matrix
	Vect   GetYCoef();      //the second column of the transform matrix
	Vect   GetZCoef();      //the third  column of the transform matrix
	Vect   GetNormal();  // get Z' axis coordinates in XYZ system
	Vect   MatrixTransform(Vect &v ); //do forward transform by matrix multiply Ax
	Vect   InverseMatrixTransform(Vect &v ); //do inverse (transpose matrix) transform by matrix multiply A~1x or ATx
	Vect   Transform(Vect &v ); //do forward transform by quaternion multiply qXq~1
	Vect   InverseTransform(Vect &v ); //do inverse transform by quaternion multiply q~1Xq

	double  genUniformQuaternion(double s, double theta1, double theta2); //return w to check maximum axes deviation
	int    genUniformQuaternionInARange(double s, double theta1, double theta2, double cosRange); //cosRange instead of Rang; in range return 1, ortherwise return 0

	void   slerp(Quaternion* from, Quaternion* to, double t, Quaternion* res);

	void   threeFoldAxes(Vect *axis);
	void   generateIcosSymRotations(Quaternion *Q); //generate the symmetric rotaions from rotation relationships
	void   getIcosSymRotations(Quaternion *Q); //get the symmetric rotaions, read from numerical value
	void   generateIcosSymQuaternions(Quaternion *Q); //output the symmetric quaternion

	int    isItInAsym(); //check if it is in an asymmetric unit
	Quaternion  getAsymQuaternion(); //return a symmetric quaternion which is located in the asymmetric unit
	void   convertToAsym(); //convert this quaternion to asymmetric unit

	Quaternion operator + (const Quaternion& Q);
	Quaternion operator - (const Quaternion& Q);
	Quaternion operator * (const Quaternion& Q);
	Quaternion operator / (const Quaternion& Q);
//	double      operator < (const Quaternion& Q);
	Quaternion operator ^ (double t);
	Quaternion operator ~ ();  //return the conjugate or inverse
	Quaternion&   operator  = (const Quaternion& Q);
	Quaternion&   operator += (const Quaternion& Q);
	Quaternion&   operator -= (const Quaternion& Q);
	Quaternion&   operator *= (const Quaternion& Q);
	Quaternion&   operator /= (const Quaternion& Q);
	Quaternion&   operator ^= (double t);


private:
	int     matrixCalculated;     //a flag to mark if the matrix need to be calculated
	float   tmpM_f[9];
	double  tmpM[9];
	float  *transposeMatrix(float *matPtr);
	double *transposeMatrix(double *matPtr);
	float  *cpDoubleMatrixToFloat();

};


#endif
