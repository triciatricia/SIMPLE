#ifndef __emtypes_h__
#define __emtypes_h__

enum MapInfoType {
    NORMAL,
    ICOS2F_FIRST_OCTANT,
    ICOS2F_FULL,
    ICOS2F_HALF,
    ICOS3F_HALF,
    ICOS3F_FULL,
    ICOS5F_HALF,
    ICOS5F_FULL
};

struct CTFParam {
    float defocus;
    float bfactor;
    float amplitude;
    float ampcont;
    float noise1;
    float noise2;
    float noise3;
    float noise4;
    float voltage;
    float cs;
    float apix;
};

enum ImageType {
    IMAGE_MRC = 0,
    IMAGE_SPIDER = 1,
    IMAGE_IMAGIC = 2,
    IMAGE_PGM = 4,
    IMAGE_LST = 5,
    IMAGE_PIF = 6,
    IMAGE_DM3 = 7,
    IMAGE_TIF = 8,
    IMAGE_VTK = 9,
    IMAGE_HDF = 10,
    IMAGE_PNG = 11,
    IMAGE_EM = 12,
    IMAGE_SAL,    
    IMAGE_ICOS,
    IMAGE_IMAGIC3D,
    IMAGE_EMIM,
    IMAGE_SINGLE_SPIDER,
    IMAGE_GATAN,
    IMAGE_AMIRA,
    IMAGE_XPLOR,
    IMAGE_SPIDER_SWAP,
    IMAGE_DF3,
    IMAGE_ANY
};



#endif
