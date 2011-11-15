#ifndef _EM_PIF_H_
#define _EM_PIF_H_

#include "pif.h"
#include <cstdio>


class EMPif {
public:
    EMPif(const char* filename);
    ~EMPif();

    int read_data(int which_img, float** p_data, bool is_3d);
    void dump() const;
    
    bool is_complex_mode() const {
	if (pfh.mode == PIF_SHORT_COMPLEX ||
	    pfh.mode == PIF_FLOAT_INT_COMPLEX ||
	    pfh.mode == PIF_FLOAT_COMPLEX ||
	    pfh.mode == PIF_SHORT_FLOAT_COMPLEX) {
	    return true;
	}
	return false;	
    }
    
    bool is_valid_mode() const {
	if (mode_size > 0) {
	    return true;
	}
	return false;
    }
    
    bool is_right_order() const {
	return right_order;
    }
    
    bool is_valid_header() const {
	return valid_header;
    }
    
    int get_nx() const {
	return pfh.nx;
    }
    
    int get_ny() const {
	return pfh.ny;
    }
    
    int get_nz() const {
	return pfh.nz;
    }

    int get_nimg() const {
	return pfh.nimg;
    }
    
    int get_mode() const {
	return pfh.mode;
    }
    
    int get_mode_nbytes() const {
	return mode_size;
    }


private:
    PifFileHeader pfh;
    FILE* in;
    bool is_zipped;
    int  mode_size;
    bool right_order;
    bool valid_header;
    float real_scale_factor;
};

#endif
