#ifndef CCMLPARM
#define CCMLPARM
#include <list>
#include <string.h>
#include "XYData.h"
#include "Quaternion.h"
#include "Euler.h"

#ifndef PI
#define PI 3.141592653589
#endif
#ifndef twoPI
#define twoPI 6.2831853072
#endif

#ifndef MAX_EXTR_NUM //define maximum number of extral initial parameters/configurations
#define MAX_EXTR_NUM 100
#endif

using namespace std;

class EMData;

class ccmlParm { //used for (internal) pass parameters
  private:
	float  __tmpCx, __tmpCy;
	float  __tmpAlt, __tmpAz, __tmpPhi;
	double __tmpQw, __tmpQx, __tmpQy, __tmpQz;
	Quaternion __tmpQ;

   public:
   	float  pftStepSize;
	int    searchMode, scalingMode, residualMode, weightMode;
	int    numOfRefImages;
	int    thisRawImageSN;
//	char   rawImageIniParmFN[500];
	char   *rawImageFN;
	char   *refImagesFN;
	char   *rawImageIniParmFN;
	int rawImagePhaseCorrected;
	int    rMask, rMask1;
	string sym;
	string refEulerConvention;

 	float  extrCx[MAX_EXTR_NUM], extrCy[MAX_EXTR_NUM];
	float  extrAlt[MAX_EXTR_NUM], extrAz[MAX_EXTR_NUM], extrPhi[MAX_EXTR_NUM];
	double extrQw[MAX_EXTR_NUM], extrQx[MAX_EXTR_NUM], extrQy[MAX_EXTR_NUM], extrQz[MAX_EXTR_NUM];
	Quaternion extrQ[MAX_EXTR_NUM];
 	float  extrResidual[MAX_EXTR_NUM];
	int totalExtrNum;

	float  refCx, refCy;
	float  refAlt, refAz, refPhi;
	double refQw, refQx, refQy, refQz;
	Quaternion refQ;


	float  iniCx, iniCy;
	float  iniAlt, iniAz, iniPhi;
	double iniQw, iniQx, iniQy, iniQz;
	Quaternion iniQ;
	float  residual;

	int iniParmsGiven;

	float  orientationSearchRange, centerSearchRange;
	XYData *scateringFactor;
	EMData *rawImage;
	vector< EMData* > refImages;

	int    FFTOverSampleScale;
	float  deltaR, RMin, RMax;


	float  stepX, stepY;  //step sizes on x, y directions
	int    numOfStartConfigurations;
	int    numOfRandomJump;
	int    numOfFastShrink;
	int    maxNumOfIteration;
	int    maxNumOfRun;

	double zScoreCriterion;
	double residualCriterion;
	double solutionCenterDiffCriterion;
	double solutionOrientationDiffCriterion;

	int    numRef, numAmpWeight;
	int    numPoints, numSym, totalNumPoints;

	//temporarily pass parameters
	float  cx, cy;
	float  alt, az, phi;

	EMData *xFFT, *yFFT, *xxFFT, *yyFFT, *xyFFT;
	EMData *thisRaw, *thisFFT, *refFFT, **refsFFT;
	Euler  *refEuler, *refsEuler;
	float  *amplitude1, *amplitude2, *phase1, *phase1Shift, *phase2;
	float  *weightAmpRawNoScale, *weightAmpRefsNoScale,*weightSNRNoScale;
	float  *weightAmpRaw, *weightAmpRef, *weightAmpRefs, *weightSNR, *weightSNRSqrt;
	float  *theta; //the common line's angle in raw image (2D FFT image)
	int    *ignoreThisSym; //some symmetric orientation could have the same orientation as one of the reference image
	float  df; //defocus---relative to the current defocus
	//all the following parameters meam how much the distorted/raw image is distorted/shifted from the undistorted/corrected image
	// frawimg(x,y)=fcorrectedimg(x+dx,y+dy)
	// frawimg(x,y)=scalingFuctionf(scale,scaleE,scaleTheta)*fcorrectedimg(x,y)
	float scale;		//this for overall scaling
	float scaleE, scaleTheta;   //eccentricity e=sqrt(1-b^2/a^2)=c/a, if it is circle, e=0
					//counterclockwise from +x axis.

	int    overAllScaleChanged;

	int    totalPFTPoints; //PFT matrix step
	float  *thisPFT, *refsPFT; //PFT matrix pointers

	int    totalIgnoredCommonLines;
	int    verbose;  //screen print out control

	ccmlParm() {  //the structure is treated as a special class, the initial values are assigned by this constructor
		pftStepSize = 0.1;
		//input parameters
		//mode selecton
		searchMode = 0;
		scalingMode = 0;
		residualMode = 0;
		weightMode = 0;

		//initial parameters
		//rawImageIniParmFN[0] = '\0';
                refEulerConvention = "eman";
		sym = "icos";
                
		rawImagePhaseCorrected = 0;
		thisRawImageSN = 0; numOfRefImages = 1;
		iniCx  = 0;   iniCy = 0;
		iniAlt = 0;   iniAz = 0;   iniPhi = 0;
		iniQw  = 0;   iniQx = 0;   iniQy  = 0;   iniQz = 0;
		residual = 999.99;
		iniParmsGiven = 1;
		totalExtrNum = 0;
		orientationSearchRange = 36.0;
		centerSearchRange = 25.0;

		//common line parameters
		deltaR = 1.0;
		RMin=5;
		RMax = 35;
		FFTOverSampleScale=1;

		//control parameters of minimization
		numOfStartConfigurations = 10;
		numOfRandomJump = 50;
		numOfFastShrink = 150;
		maxNumOfIteration = 1000;
		maxNumOfRun = 5;
		zScoreCriterion = 3.5;
		residualCriterion = -1.0;
		solutionCenterDiffCriterion = -1.0;
		solutionOrientationDiffCriterion = -1.0;

		numAmpWeight = 1;
		overAllScaleChanged = 1;
		scale = 1.0; scaleE = 0; scaleTheta = 0;

		totalIgnoredCommonLines = 0;
		verbose = 0;  //no screen print out
	}


	void getParmsFromRandom() {  // generate a random orientation and set center to image center
		float ran();
		__tmpCx = rawImage->xSize()/2;  __tmpCy = rawImage->ySize()/2;
		__tmpQ.genUniformQuaternion(ran(), ran()*twoPI, ran()*twoPI);
		__tmpAlt = __tmpQ.getEuler().alt();
		__tmpAz  = __tmpQ.getEuler().az();
		__tmpPhi = __tmpQ.getEuler().phi();
		__tmpQw  = __tmpQ.w; __tmpQx = __tmpQ.x; __tmpQy = __tmpQ.y; __tmpQz = __tmpQ.z;
	}

	void getParmsFromInputs(float iCx, float iCy, Quaternion& iQ) {
		__tmpCx = iCx;  __tmpCy = iCy;
		__tmpQ.setQuaternion(iQ);
		__tmpAlt = __tmpQ.getEuler().alt();
		__tmpAz  = __tmpQ.getEuler().az();
		__tmpPhi = __tmpQ.getEuler().phi();
		__tmpQw  = __tmpQ.w; __tmpQx = __tmpQ.x; __tmpQy = __tmpQ.y; __tmpQz = __tmpQ.z;
	}

	void getParmsFromParticle() {
		rawImage->readImage(rawImageFN, thisRawImageSN, 1); //read raw image header to find center / orientation
		__tmpCx = rawImage->get_center_x();
		__tmpCy = rawImage->get_center_y();
		if (__tmpCx >= rawImage->xSize()) __tmpCx = rawImage->xSize()/2;
		if (__tmpCy >= rawImage->ySize()) __tmpCy = rawImage->ySize()/2;
		__tmpAlt = rawImage->alt();
		__tmpAz  = rawImage->az();
		__tmpPhi = rawImage->phi();
		if (refEulerConvention == "mrc") { //if the particle's orientation is not represented by eman convention, do this convert
			Euler eu;
			eu.setAngleFromMRC(__tmpAlt, __tmpAz, __tmpPhi);
			__tmpAlt = eu.alt();
			__tmpAz  = eu.az();
			__tmpPhi = eu.phi();
		}

		__tmpQ.setQuaternion(__tmpAlt, __tmpAz, __tmpPhi);
		__tmpQw  = __tmpQ.w; __tmpQx = __tmpQ.x; __tmpQy = __tmpQ.y; __tmpQz = __tmpQ.z;
		if (verbose > 0) printf("Read Input Center and Euler angles :: %5d  %7.1f  %7.1f  %7.1f %7.3f %7.3f \n", thisRawImageSN, __tmpCx, __tmpCy, __tmpAlt, __tmpAz, __tmpPhi);
	}


	void getParmsFromIniParmFile() {  //read orientation and center from file
		int rawImgSN;
		char tmp[1001];
		float alt, az, phi, cx, cy;
		FILE *fp;

		if (rawImageIniParmFN[0]=='\0') {
				if (verbose > 0) fprintf(stderr, "ERROR:  file name of the initial center and oriention was not given\n");
				exit(0);
		}

		fp = fopen(rawImageIniParmFN, "r");
		for(;;) {
			int s = fscanf(fp, "%d %f %f %f %f %f\n",&rawImgSN, &__tmpCx, &__tmpCy, &__tmpAlt, &__tmpAz, &__tmpPhi, &residual); //return # of variables which has been read
			fgets(tmp, 1000, fp); //read the rest of the line
			if (s == EOF) {
				if (verbose > 0) fprintf(stderr, "ERROR:  Did not find initial center and oriention of image #%d in file \"%s\"!\n",thisRawImageSN,rawImageIniParmFN);
				if (verbose > 0) fprintf(stderr, "************  The initial is set to random values  ******************\n");
				exit(0);
			}
			if (s != 6) continue; //if read less than 6 variables, continue
			if (rawImgSN != thisRawImageSN) continue;

			__tmpAlt = __tmpAlt/180.0*PI; __tmpAz = __tmpAz/180.0*PI; __tmpPhi = __tmpPhi/180.0*PI;
			if (refEulerConvention == "mrc") { //if the read in euler angle is not eman convention, do this convert
				Euler eu;
				eu.setAngleFromMRC(__tmpAlt, __tmpAz, __tmpPhi);
				__tmpAlt = eu.alt();
				__tmpAz  = eu.az();
				__tmpPhi = eu.phi();
			}
			__tmpQ.setQuaternion(__tmpAlt, __tmpAz, __tmpPhi);
			__tmpQw = __tmpQ.w; __tmpQx = __tmpQ.x; __tmpQy = __tmpQ.y; __tmpQz = __tmpQ.z;

			if (verbose > 0) printf("Readin Center and Euler angles :: %5d  %7.1f  %7.1f  %7.1f %7.3f %7.3f \n", thisRawImageSN, __tmpCx, __tmpCy, __tmpAlt, __tmpAz, __tmpPhi);
			break;
		}


		//read the extra initial parameters
		int i=0;
		totalExtrNum = 0;
		for(;;) {
			int s = fscanf(fp, "%d %f %f %f %f %f\n",&rawImgSN, &extrCx[i], &extrCy[i], &extrAlt[i], &extrAz[i], &extrPhi[i], &extrResidual[i]); //return # of variables which has been read
			fgets(tmp, 1000, fp); //read the rest of the line
			if (s == EOF) break;
			if (s != 6) continue; //if read less than 6 variables, continue
			if (rawImgSN != thisRawImageSN) continue;

			extrAlt[i] = extrAlt[i]/180.0*PI; extrAz[i] = extrAz[i]/180.0*PI; extrPhi[i] = extrPhi[i]/180.0*PI;
			if (refEulerConvention.compare("mrc")==0) { //if the read in euler angle is not eman convention, do this convert
				Euler eu;
				eu.setAngleFromMRC(extrAlt[i], extrAz[i], extrPhi[i]);
				extrAlt[i] = eu.alt();
				extrAz[i]  = eu.az();
				extrPhi[i] = eu.phi();
			}
			extrQ[i].setQuaternion(extrAlt[i], extrAz[i], extrPhi[i]);
			extrQw[i] = extrQ[i].w; extrQx[i] = extrQ[i].x; extrQy[i] = extrQ[i].y; extrQz[i] = extrQ[i].z;
			i++; totalExtrNum = i;//count the number of extral parameters
		}
		if ((verbose > 0)&&(totalExtrNum>0)) printf("Readin [%d] extral Center and Euler angles\n",totalExtrNum);

	}

	void copyTmpParmsToIni() {
		iniCx = __tmpCx; iniCy = __tmpCy;
		iniAlt = __tmpAlt; iniAz  = __tmpAz; iniPhi = __tmpPhi;
		iniQ  = __tmpQ; iniQw = __tmpQw; iniQx = __tmpQx; iniQy = __tmpQy; iniQz = __tmpQz;
	}

	void copyTmpParmsToRef() {
		refCx = __tmpCx; refCy = __tmpCy;
		refAlt = __tmpAlt; refAz  = __tmpAz; refPhi = __tmpPhi;
		refQ  = __tmpQ; refQw = __tmpQw; refQx = __tmpQx; refQy = __tmpQy; refQz = __tmpQz;
	}


	void setRefCenterAndOrientationFromRandom() {  // generate a random orientation and set center to image center
                getParmsFromRandom();
                copyTmpParmsToRef();
	}

	void setRefCenterAndOrientationFromInput(float iCx, float iCy, Quaternion& iQ) {
                getParmsFromInputs(iCx, iCy, iQ);
                copyTmpParmsToRef();
	}

	void setRefCenterAndOrientationFromIniParmFile() {  //if given file, read from file, otherwise generate a random orientation and set center to image center
                getParmsFromIniParmFile();
                copyTmpParmsToRef();
                iniParmsGiven = 1;
	}

	void setRefCenterAndOrientationFromParticle() {
                getParmsFromParticle();
                copyTmpParmsToRef();
                iniParmsGiven = 1;
	}
        
	void setRefCenterAndOrientationFromInitializedParms() {
		refCx = iniCx; refCy = iniCy;
		refAlt = iniAlt; refAz  = iniAz; refPhi = iniPhi;
		refQ  = iniQ; refQw = iniQw; refQx = iniQx; refQy = iniQy; refQz = iniQz;
	}

	void initializeCenterAndOrientationFromRandom() {  // generate a random orientation and set center to image center
                getParmsFromRandom();
                copyTmpParmsToIni();
                iniParmsGiven = 0;
	}

	void initializeCenterAndOrientationFromInput(float iCx, float iCy, Quaternion& iQ) {
                getParmsFromInputs(iCx, iCy, iQ);
                copyTmpParmsToIni();
	}

	void initializeCenterAndOrientationFromIniParmFile() {  //if given file, read from file, otherwise generate a random orientation and set center to image center
                getParmsFromIniParmFile();
                copyTmpParmsToIni();
	}

	void initializeCenterAndOrientationFromParticle() {
                getParmsFromParticle();
                copyTmpParmsToIni();
	}

	void initializeCenterAndOrientationFromSetRefParms() {
		iniCx = refCx; iniCy = refCy;
		iniAlt = refAlt; iniAz  = refAz; iniPhi = refPhi;
		iniQ  = refQ; iniQw = refQw; iniQx = refQx; iniQy = refQy; iniQz = refQz;
	}

        
        
};


class ccmlOutputParm {
  private:
	float  __tmpCx, __tmpCy;
	float  __tmpAlt, __tmpAz, __tmpPhi;
	double __tmpQw, __tmpQx, __tmpQy, __tmpQz;
	Quaternion __tmpQ;
	int diffCalculated;  //set a flag to format the output

   public:
	float asymAlt, asymAz, asymPhi;
	Quaternion asymQ;

	int rawImageSN;

	float cx, cy; //center X, Y
	float alt, az, phi;   //euler angle
	double qw, qx, qy, qz; //quaternion
	Quaternion q;

	float  iniCx, iniCy;
	float  iniAlt, iniAz, iniPhi;
	double iniQw, iniQx, iniQy, iniQz;
	Quaternion iniQ;

	float  refCx, refCy;
	float  refAlt, refAz, refPhi;
	double refQw, refQx, refQy, refQz;
	Quaternion refQ;

	float centerDiff, maxAxisDiff,orientationDiff, maxEulerAngleDiff;

	int   numOfRun;
	float residual;
	float zScore;
	float zScoreCriterion;
	float sigma;
	int   passAllCriteria;
	int   totalIgnoredCommonLines;
	int   verbose;



	ccmlOutputParm() {  //the structure is treated as a special class, the initial values are assigned by this constructor
		cx  = 0;  cy  = 0;
		alt = 0;  az  = 0;  phi = 0;
		qw = 1; qx = 0; qy = 0; qz = 0;
		centerDiff = 99.99; maxAxisDiff = 999.99; orientationDiff = 999.99; maxEulerAngleDiff = 999.99;
		numOfRun = 0;
		residual = 99999.99;
		diffCalculated = 0;
		zScore = 0;
		passAllCriteria = 0;
		totalIgnoredCommonLines = 0;
		verbose = 0;
		zScoreCriterion = 3.5;

	}

	void copyIniParm(ccmlParm* parm) {
		iniCx  = parm->iniCx;   iniCy = parm->iniCy;
		iniAlt = parm ->iniAlt; iniAz = parm ->iniAz; iniPhi = parm ->iniPhi;
		iniQ   = parm->iniQ;    iniQw = parm->iniQw;  iniQx  = parm->iniQx;   iniQy = parm->iniQy; iniQz = parm->iniQz;
	}

	void copyRefParm(ccmlParm* parm) {
		refCx  = parm->refCx;   refCy = parm->refCy;
		refAlt = parm ->refAlt; refAz = parm ->refAz; refPhi = parm ->refPhi;
		refQ   = parm->refQ;    refQw = parm->refQw;  refQx  = parm->refQx;   refQy = parm->refQy; refQz = parm->refQz;

	}

	void setRefCenterAndOrientation(float rCx, float rCy, Quaternion& rQ) {
		refCx = rCx;  refCy = rCy;
		refQ.setQuaternion(rQ);
		refAlt = refQ.getEuler().alt();
		refAz  = refQ.getEuler().az();
		refPhi = refQ.getEuler().phi();
		refQw  = refQ.w; refQx = refQ.x; refQy = refQ.y; refQz = refQ.z;
	}

	void setCalculatedCenterAndOrientation(float cCx, float cCy, Quaternion& cQ) {
		cx = cCx;  cy = cCy;
		q.setQuaternion(cQ);
		alt = q.getEuler().alt();
		az  = q.getEuler().az();
		phi = q.getEuler().phi();
		qw  = q.w; qx = q.x; qy = q.y; qz = q.z;
	}

	void convertCalculatedOrientationToAsymmetricUnit() {
		int success = convertToAsymmetricUnit(alt, az, phi);
		if(success) {
			alt = asymAlt; az = asymAz; phi = asymPhi;
			q = asymQ;
			qw = asymQ.w; qx = asymQ.x; qy = asymQ.y; qz = asymQ.z;
		}
	}

	void convertRefOrientationToAsymmetricUnit() {
		int success = convertToAsymmetricUnit(refAlt, refAz, refPhi);
		if(success) {
			refAlt = asymAlt; refAz = asymAz; refPhi = asymPhi;
			refQ = asymQ;
			refQw = asymQ.w; refQx = asymQ.x; refQy = asymQ.y; refQz = asymQ.z;
		}
	}

	void convertIniOrientationToAsymmetricUnit() {
		int success = convertToAsymmetricUnit(iniAlt, iniAz, iniPhi);
		if(success) {
			iniAlt = asymAlt; iniAz = asymAz; iniPhi = asymPhi;
			iniQ = asymQ;
			iniQw = asymQ.w; iniQx = asymQ.x; iniQy = asymQ.y; iniQz = asymQ.z;
		}
	}

	int isItInAsym(float altTmp, float azTmp) {
		float asyCenter = 1.5*PI;
		if((azTmp > asyCenter + 0.2*PI) || (azTmp < asyCenter - 0.2*PI)) return 0;

		double a, b, c;
		double nx = sin(azTmp)*sin(altTmp);
		double ny = cos(azTmp)*sin(altTmp);
		double nz = cos(altTmp);

		if((asyCenter - 0.5*PI) < 0.0001) {
			//bottom  line/plane a=-1.61803398875 b=0 c=1 d=0
			a=-1.61803398875; b=0; c=1;
			if((a*nx + b*ny + c*nz) < 0) return  0; //it should be 0, but for error reason, make it to -0.01
		}

		if((asyCenter - 1.5*PI) < 0.0001) {
			a = 0.68819096023515636; b = 0.5; c = 0.52573111211999457;
			if((a*nx + b*ny + c*nz) < 0) return  0; //it should be 0, but for error reason, make it to -0.01

			a = 0.68819096023515636; b =-0.5; c = 0.52573111211999457;
			if((a*nx + b*ny + c*nz) < 0) return  0; //it should be 0, but for error reason, make it to -0.01
		}

		if(azTmp >= asyCenter) return 1;
		else return 2;

	}


	int convertToAsymmetricUnit(float altTmp, float azTmp, float phiTmp) {
		Quaternion Qt[60];
		Quaternion tmpQuaternion(altTmp, azTmp, phiTmp);
		tmpQuaternion.generateIcosSymQuaternions(Qt); //convert asymmetric unit


		int returnValue = 0;

		asymAlt = 0; asymAz  = 0; asymPhi = 0; //initial the Euler angles
		for(int i=0; i<60; i++) {
			Euler tmpEuler = Qt[i].getEuler();  //this one could bring error, getEuler can give 1 degree error
			asymAlt = tmpEuler.alt();
			asymAz  = tmpEuler.az();
			asymPhi = tmpEuler.phi();

			returnValue = isItInAsym(asymAlt, asymAz);
			//printf("Alt %7.2f  %7.2f  %7.2f  ==> %d\n", asymAlt * 180.0 / PI, asymAz * 180.0 / PI, asymPhi * 180.0 / PI, returnValue);
			if(returnValue > 0) { //the definition of asymmetric unit in EMAN
				asymQ = Qt[i];
				return returnValue;
			}
		}

		Euler tmpEuler = Qt[0].getEuler();
		asymAlt = tmpEuler.alt();
		asymAz  = tmpEuler.az();
		asymPhi = tmpEuler.phi();
		asymQ = Qt[0];
		return returnValue; //not find any symmetric Euler angles in the Aysmmetric unit, it frequently happens when alt close to 0
	}

	void calculateDifferenceWithIniParm() {
		convertIniOrientationToAsymmetricUnit();
		calculateDifference(iniCx, iniCy, iniQ);
	}

	void calculateDifferenceWithRefParm() {
		convertRefOrientationToAsymmetricUnit();
		calculateDifference(refCx, refCy, refQ);
	}

	void calculateDifference(float cmpCX, float cmpCY, Quaternion& cmpQ) {
		Euler cmpEuler = cmpQ.getEuler();
		float cmpAlt = cmpEuler.alt();
		float cmpAz  = cmpEuler.az();
		float cmpPhi = cmpEuler.phi();


		Quaternion Qt[60], QDiff;
		q.generateIcosSymQuaternions(Qt); //convert asymmetric unit

		float QthetaDiff;
		float dx, dy, dz, dxyzMax;
		int symSN=0;

		orientationDiff = 20*PI;
		for(int i=0; i<60; i++) {
			double tmpdotvalue = fabs((cmpQ.dotQuaternion(Qt[i]))); if(tmpdotvalue > 1) tmpdotvalue = 1;
			QthetaDiff = 2*acos(tmpdotvalue);
			if(orientationDiff > QthetaDiff) {
				orientationDiff = QthetaDiff;


				QDiff = Qt[i]/cmpQ;
				dx = QDiff.getMatrix()[0]; if(dx>1) dx = 1;
				dy = QDiff.getMatrix()[4]; if(dy>1) dy = 1;
				dz = QDiff.getMatrix()[8]; if(dz>1) dz = 1;

				dx = acos(dx);
				dy = acos(dy);
				dz = acos(dz);

				if(dx > dy) dxyzMax = dx; else dxyzMax =dy;
				if(dxyzMax < dz) dxyzMax = dz;

				maxAxisDiff = dxyzMax;

				symSN=i;
			}
		}



		float tmpAlt, tmpAz, tmpPhi;
		Euler thisEuler = Qt[symSN].getEuler();
		tmpAlt = thisEuler.alt();
		tmpAz  = thisEuler.az();
		tmpPhi = thisEuler.phi();

		float eulerAngle;
		eulerAngle = fabs(tmpAlt-cmpAlt); if(eulerAngle > PI) eulerAngle = twoPI - eulerAngle;
		maxEulerAngleDiff = eulerAngle;

		eulerAngle = fabs(tmpAz-cmpAz);   if(eulerAngle > PI) eulerAngle = twoPI - eulerAngle;
		if(maxEulerAngleDiff < eulerAngle) maxEulerAngleDiff = eulerAngle;

		eulerAngle = fabs(tmpPhi-cmpPhi); if(eulerAngle > PI) eulerAngle = twoPI - eulerAngle;
		if(maxEulerAngleDiff < eulerAngle) maxEulerAngleDiff = eulerAngle;


		centerDiff = sqrt((cx-cmpCX)*(cx-cmpCX) + (cy-cmpCY)*(cy-cmpCY));


		diffCalculated = 1;

		if(verbose > 4)  {
			printf("Axes, Quaternion and Euler angle difference  ::  %10.2f, %10.2f, %10.2f, %10.2f, %10.2f\n", dx*180./PI, dy*180./PI, dz*180./PI, orientationDiff*180./PI, maxEulerAngleDiff*180./PI);
			double angle, nx, ny, nz;
			QDiff.getAngleAxis(&angle, &nx, &ny, &nz);
			printf("Rotate back Q [roation angle, axes]  ::  %7.2f  %7.3f %7.3f %7.3f\n",  angle*180/PI, nx, ny, nz);
		}
	}


	void outputResult(char *outputFileName) {
		char OKorXX[3];

		if (passAllCriteria) strcpy(OKorXX, "OK");
		else strcpy(OKorXX, "XX");

		FILE *fp = fopen(outputFileName, "a");
		fprintf(fp, "%6d %7.2f%7.2f%7.2f%7.2f%7.2f   %7.5f%7.3f%7.2f%8.2f%5d%7s   ", rawImageSN, cx, cy, alt*180./PI, az*180./PI, phi*180./PI, residual, sigma, zScore, zScoreCriterion, numOfRun, OKorXX);
		if(diffCalculated) {
			fprintf(fp, "%7.2f%7.2f  %7.2f%7.2f%7.2f %7.2f %7.2f :%7.2f\n", refCx, refCy, refAlt*180./PI, refAz*180./PI, refPhi*180./PI, centerDiff, orientationDiff*180./PI,maxEulerAngleDiff*180./PI);
		} else {
			fprintf(fp, "\n");
		}
		fclose(fp);
	}

};



class configParm {
	public:
	float wAnc, xAnc, yAnc, zAnc;
	float cxAnc, cyAnc;
	float residualAnc;
	float w, x, y, z;
	float cx, cy;
	float vx, vy;
	Quaternion vq;
	float zScore;
	float zScoreCriterion;
	float sigma;
	float residual;
	int   passAllCriteria;
	int   numOfFail;
	list< configParm > *confListPtr;

	configParm() {
		wAnc = 1; xAnc = 0; yAnc = 0; zAnc = 0;
		cxAnc = 0; cyAnc = 0;
		residualAnc = 99999.9;

		vx=10; vy=10;
		vq.setQuaternion(cos(5.0/180.0*3.14),0.0,0.0,sin(5.0/180.0*3.14)); //rotate along Z 10 degree

		w = 1; x = 0; y = 0; z = 0;
		cx = 0; cy = 0;
		zScore = 0;
		zScoreCriterion=0;
		sigma = 1.0;
		residual = 99999.9;
		passAllCriteria = 0;
		numOfFail=0;
		confListPtr = NULL;
	}

	configParm(float w0, float x0, float y0, float z0, float cx0, float cy0, float residual0, list< configParm >  *confListPtr0) {
		wAnc = w0; xAnc = x0; yAnc = y0; zAnc = z0;
		cxAnc = cx0; cyAnc = cy0;
		residualAnc = residual0;
		
                vx=10; vy=10;
		vq.setQuaternion(cos(5.0/180.0*3.14),0.0,0.0,sin(5.0/180.0*3.14)); //rotate along Z 10 degree
						
		w = w0; x = x0; y = y0; z = z0;
		cx = cx0; cy = cy0;
		residual = residual0;
		confListPtr = confListPtr0;
	}


	void setConfigParm(float w0, float x0, float y0, float z0, float cx0, float cy0, float residual0, list< configParm >  *confListPtr0) {
		w = w0; x = x0; y = y0; z = z0;
		cx = cx0; cy = cy0;
		residual = residual0;
		confListPtr = confListPtr0;
	}

	void setAncestorConfigParm(float w0, float x0, float y0, float z0, float cx0, float cy0, float residual0) {
		wAnc = w0; xAnc = x0; yAnc = y0; zAnc = z0;
		cxAnc = cx0; cyAnc = cy0;
		residualAnc = residual0;
	}

	void setSpeed(float vx0, float vy0, Quaternion vq0) {
		vx = vx0; vy =  vy0;
		vq.setQuaternion(vq0);
	}

	void setAncestorConfigParm(const configParm& conf0) {
		wAnc = conf0.wAnc; xAnc = conf0.xAnc; yAnc = conf0.yAnc; zAnc = conf0.zAnc;
		cxAnc = conf0.cxAnc; cyAnc = conf0.cyAnc;
		residualAnc = conf0.residualAnc;
	}

	void copyToAncestorConfigParm() {
		wAnc = w; xAnc = x; yAnc = y; zAnc = z;
		cxAnc = cx; cyAnc = cy;
		residualAnc = residual;
	}

	void copyFromAncestorConfigParm() {
		w = wAnc; x = xAnc; y = yAnc; z = zAnc;
		cx = cxAnc; cy = cyAnc;
		residual = residualAnc;
	}

	void setResidual(float residual0) {
		residual = residual0;
	}


	int operator<(const configParm& b) const {
//	printf("< called ");
		if (this->residual < b.residual) return 1;
		return 0;
	}

	float distFromthisQtoAllRefQ() {
//		if (confListPtr == NULL) return 99999.9;
		float avgDist = 0;
		int count = 0;
		Quaternion Q[60];
		thisQ.setQuaternion(w, x, y, z);
		thisQ.generateIcosSymQuaternions(Q);
		list<configParm>::iterator iter, iterEnd=confListPtr->end();
		for(int i=0; i<5; i++) iterEnd--;
		for(iter=confListPtr->begin(); iter!=iterEnd; iter++) {
			refQ.setQuaternion((*iter).w, (*iter).x, (*iter).y, (*iter).z);
			float shortestDist = 100000.0;
			for(int i=0; i<60; i++) {
//				float theta = 2*acos(fabs(Q[i].dotQuaternion(refQ)));  //range from 0-->PI/2
				float theta = Q[i].getAngle(refQ);  //range from 0-->PI/2
				if (shortestDist > theta) shortestDist = theta;
//				printf("%7.2f ",theta*180/PI);
			}
//		printf("dist :: %f\n", shortestDist);
			avgDist += shortestDist;
			count++;
		}
		avgDist /=count;
//		printf("#, count :: %f, %d", avgDist, count); exit(0);
		return avgDist; //range from 0-->PI
	}

	configParm bestDistQ(float *bestD) {
//		if (confListPtr == NULL) return NULL;
		float bestDist=10000.0;
		Quaternion Q[60];
		list<configParm>::iterator iter, iter1, bestIter, iterEnd=confListPtr->end();
		for(int i=0; i<5; i++) iterEnd--;
		for(iter=confListPtr->begin(); iter!=iterEnd; iter++) {
			thisQ.setQuaternion((*iter).w, (*iter).x, (*iter).y, (*iter).z);
			thisQ.generateIcosSymQuaternions(Q);
			float avgDist = 0;
			int count = 0;
			for(iter1=confListPtr->begin(); iter1!=iterEnd; iter1++) {
				refQ.setQuaternion((*iter1).w, (*iter1).x, (*iter1).y, (*iter1).z);
				float shortestDist = 100000.0;
				for(int i=0; i<60; i++) {
//					float theta = 2*acos(fabs(Q[i].dotQuaternion(refQ)));  //range from 0-->PI/2
					float theta = Q[i].getAngle(refQ);  //range from 0-->PI/2
					if (shortestDist > theta) shortestDist = theta;
				}
				avgDist += shortestDist;
				count++;
			}
			avgDist /=count;
			if(bestDist > avgDist) {
				bestDist = avgDist;
				bestIter = iter;
			}
		}

		*bestD = bestDist;
		return *bestIter;
	}


	private:
	Quaternion thisQ, refQ;
};

#endif

