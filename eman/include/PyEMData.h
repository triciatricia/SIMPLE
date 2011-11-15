#ifndef _pyemdata_h_
#define _pyemdata_h_

#include "PyList.h"
#include "EMData.h"
#include "EMTypes.h"
#include "crossCommonLine.h"
#include <boost/python.hpp>

class PyEuler;

class PyEMData : public EMData {
public:
    PyEMData();
    ~PyEMData();

    python::tuple py_MinLoc();
    python::tuple py_MaxLoc();
    
    int display();
    
    PyArray get_num_array();
    void set_num_array(PyArray& num_array);
    
    int readImage(const char* filename, int n = -1, int nodata = 0, ImageType img_type = IMAGE_ANY);
    
    int writeImage(const char* filename, int n = -1, ImageType imagetype = IMAGE_ANY,
		   int nolock = 0, int swap = 0, int mode = MODE_float);
    
    void py_calcHist(PyList hist_list, int n, float hmin = 0,
		     float hmax = 0, int add = 0);

    python::tuple py_transAlign(EMData* with, int useparent, int intonly, int maxshift);
    
    void py_calcRCF(EMData* with, PyList sum_list, int NS);
    void py_applyRadFn(int n, float x0, float dx, PyList y_list, int interp = 1);
    void py_addRadNoise(int n, float x0, float dx, PyList y_list, int interp);	   
    
    python::tuple py_normalizeTo(EMData* noisy, int keepzero = 0, int invert = 0);	
    
    python::tuple py_leastSquareNormalizeTo(EMData* to, float low_thresh = FLT_MIN, 
					    float high_thresh = FLT_MAX);

    void py_calcRadDist(int n, float x0, float dx, PyList y_list);
    void py_calcRadDist(int n, float x0, float dx, PyList y_list, float acen, float amwid);

    void py_calcAzDist(int n, float a0, float da, PyList data_list,
		       float rmin, float rmax);
    python::tuple py_get_bounding_box(float thresh);	 
    python::tuple py_lcmp(EMData* noisy, int keepzero = 0, int invert = 0);	 

    void py_makeAverage(PyList in, EMData* sigma = 0, int ignore0 = 0);
    void py_makeAverageIter(PyList in);
    
    void py_makeAverageWT(PyList in, EMData* curves, XYData* sf);
    void py_makeAverageCTFCW(PyList in, XYData* sf, PyList SNR_list = PyList(0));
    
    void py_makeAverageCTFC(PyList in, float filtr);
    void py_makeAverageCTFCWauto(PyList in, const char *outfile = 0);
    
    void py_makeMedian(PyList in);
    void py_interpFT3d(float x, float y, float z, PyList ret_list, int mode);

    python::tuple py_normSlice(EMData* slice, float alt, float az, float phi);
    
    PyList py_ctfCurve(int type, XYData* sf);
    PyList py_fsc(EMData* with);
	PyList py_MaxLocs(int n);

    PyList py_getCTF();
    void py_setCTF(PyList ctf);
	void py_setSFFile(const char* filename);

	float py_fscmp(EMData* with, PyList snr = PyList(0));

    PyEMData* py_matchFilter(EMData* to);
	
    PyEMData* py_doFFT();

    PyEMData* py_copy(int withfft = 0, int withparent =1);
    PyEMData* py_copyHead();
    
    PyEMData* py_clip(int x0, int y0, int w, int h);
    PyEMData* py_clip(int x0, int y0, int z0, int w, int h, int d);
    PyEMData* py_Parent();
    PyEuler* py_getEuler(); 

    PyEMData* py_doIFT();
    PyEMData* py_doRadon();
    PyEMData* py_vertACF(int maxdy);

    PyEMData* py_convolute(EMData* with);
    PyEMData* py_calcCCF(EMData* with, int tocorner = 0, EMData* filter = NULL);
    PyEMData* py_calcFLCF(EMData* with, int r);
    PyEMData* py_calcCCFX(EMData* with, int y0 = 0, int y1 = -1, int nosum = 0);
    PyEMData* py_calcMCF(EMData* with, int tocorner=0, EMData* filter = NULL);
    PyEMData* py_littleBigDot(EMData* with, int sigma = 0);
    
    PyEMData* py_RTFAlignRadon(EMData* with, int maxshift = -1,
			       EMData* thisf = NULL,
			       EMData* radonwith = NULL,
			       EMData* radonthis = NULL,
			       EMData* radonthisf = NULL);

    PyEMData* py_RTAlignRadon(EMData* with, int maxshift = -1,
			      EMData* radonwith = NULL,
			      EMData* radonthis = NULL);

    PyEMData* py_RTFAlignSlow(EMData* with,
			      EMData* flip = NULL,
			      int maxshift = -1);

    PyEMData* py_RTFAlignSlowest(EMData* with,
				 EMData* flip = NULL,
				 int maxshift = -1);

    PyEMData* py_RTFAlignBest(EMData* with = NULL,
			      EMData* flip = NULL,
			      int maxshift = -1, float *snr=NULL);

    PyEMData* py_RTFAlign(EMData* with = NULL,
			  EMData* flip = NULL,
			  int usedot = 1, int maxshift = -1);

    PyEMData* py_RFAlign(EMData* with,
			 EMData* flip = NULL,
			 int imask = 0);
    
    PyEMData* py_RTAlign(EMData* with, int usedot = 0, int maxshift = 0);

    PyEMData* py_RTAlignBest(EMData* with, int maxshift = 0, float *snr=NULL);

    PyEMData* py_makeRFP(int premasked = 0, int unwrap = 1);
    PyEMData* py_unwrap(int r1 = -1, int r2 = -1, int xs = -1,
			int dx = 0, int dy = 0, int do360 = 0);
    
				
    PyEMData* py_project3d(float alt, float az,  float phi, 
			   int mode,  float thr = 1.0, float ri = 0);
    PyEMData* py_fftSlice(float alt, float az, float phi, int mode = 5);

    PyEMData* py_iftSlice();
    PyEMData* py_row(int n);
    PyEMData* py_col(int n);
    PyEMData* py_mxMult(EMData* second);

    
    PyEMData& operator+=(float n);
    PyEMData& operator-=(float n);
    PyEMData& operator*=(float n);
    PyEMData& operator/=(float n);
    
    PyEMData& operator+=(const PyEMData& em);
    PyEMData& operator-=(const PyEMData& em);
    PyEMData& operator*=(const PyEMData& em);
    PyEMData& operator/=(const PyEMData& em);

    friend PyEMData& operator+(const PyEMData& em, float n);
    friend PyEMData& operator-(const PyEMData& em, float n);
    friend PyEMData& operator*(const PyEMData& em, float n);
    friend PyEMData& operator/(const PyEMData& em, float n);
    
    friend PyEMData& operator+(float n, const PyEMData& em);
    friend PyEMData& operator-(float n, const PyEMData& em);
    friend PyEMData& operator*(float n, const PyEMData& em);
    friend PyEMData& operator/(float n, const PyEMData& em);
    
    friend PyEMData& operator+(const PyEMData& a, const PyEMData& b);
    friend PyEMData& operator-(const PyEMData& a, const PyEMData& b);
    friend PyEMData& operator*(const PyEMData& a, const PyEMData& b);
    friend PyEMData& operator/(const PyEMData& a, const PyEMData& b);

private:
    enum EMOper { EM_ADD, EM_SUB, EM_MUL, EM_DIV };
    
    void apply_obj(const PyEMData& other, EMOper op);
    PyEMData* my_copy() const;
    python::tuple get_loc(int ismax);
};

python::tuple fileCount(const char* filename);
PyList py_readImages(const char *filespec, int n0, int n1, int nodata=0);
PyList py_readImagesExt(const char *filespec, const char *ext, int n0,
			int n1, int nodata=0);

#endif
