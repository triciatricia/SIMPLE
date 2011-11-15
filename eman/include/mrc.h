/******************************************************************************
*******************************************************************************
*                   mrc.h:  header for mrc.c                                  *
*******************************************************************************
*                                                                             *
*     updated to MRC Image2000 format which is compatible with CCP4 format    *	
*                            Wen Jiang   2003-2-24                            *
*                                                                             *
*******************************************************************************
*                            Steve Hardt                                      *
*                            East Campus                                      *
*                            3 Ames St                                        *
*                            Cambridge, MA 02139                              *
*                            (617)225-6368                                    *
*                            hardts@athena.mit.edu                            *
*                                                                             *
*                            August 24, 1992                                  *
*******************************************************************************
* Some code from mrc.h and mrc.c was taken from xvmrc.h and xvmrc.c which     *
* were written by                                                             *
*                            Man Wei Tam                                      *
*                            72 Trafalgar Rd, Wallasey,                       *
*                            Merseyside, England,                             *
*                            UK, L44OEB                                       *
*******************************************************************************
******************************************************************************/


#ifndef MRCP_H
#define MRCP_H

/* for MRC header */
#define MRC_LABEL_SIZE      80   
#define MRC_USER            25
#define MRC_NUM_LABELS      10

/*  The different modes supported by the MRC format. Values used by IMOD */
#define MODE_char           0
#define MODE_short          1
#define MODE_float          2
#define MODE_short_COMPLEX  3  
#define MODE_float_COMPLEX  4
#define MODE_ushort			6		//non-standard
#define MODE_uchar3			16		//unsigned char * 3, for rgb data, non-standard
/* All modes before MODE_short_COMPLEX must be real, all those after it must be complex. */


/*******************************************************************************
Protected Data Structures
*******************************************************************************/
struct mrcH
{
    int         nx;                 /* Number of columns -      */
                                    /* Fastest changing in map. */
    int         ny;

    int         nz;                 /* Number of sections -     */
                                    /* slowest changing in map. */

    int         mode;               /* See modes above. */

    int         nxstart;            /* No. of first column in map, default 0.*/
    int         nystart;            /* No. of first row in map, default 0.*/
    int         nzstart;            /* No. of first section in map,default 0.*/

    int         mx;                 /* Number of intervals along X. */
    int         my;                 /* Number of intervals along Y. */
    int         mz;                 /* Number of intervals along Z. */

    float       xlen;               /* Cell dimensions (Angstroms). */
    float       ylen;               /* Cell dimensions (Angstroms). */
    float       zlen;               /* Cell dimensions (Angstroms). */

    float       alpha;              /* Cell angles (Degrees). */
    float       beta;               /* Cell angles (Degrees). */
    float       gamma;              /* Cell angles (Degrees). */

    int         mapc;               /* Which axis corresponds to Columns.  */
                                    /* (1,2,3 for X,Y,Z.                   */
    int         mapr;               /* Which axis corresponds to Rows.     */
                                    /* (1,2,3 for X,Y,Z.                   */
    int         maps;               /* Which axis corresponds to Sections. */
                                    /* (1,2,3 for X,Y,Z.                   */

    float       amin;               /* Minimum density value. */
    float       amax;               /* Maximum density value. */
    float       amean;              /* Mean density value.    */

    int         ispg;               /* Space group number (0 for images). */

    int         nsymbt;             /* Number of chars used for storing   */
                                    /* symmetry operators. */


    int         user[MRC_USER];  
	
    float       xorigin;            /* X origin. */
    float       yorigin;            /* Y origin. */
    float       zorigin;            /* Y origin. */

    char        map[4];				/* constant string "MAP "  */
    int         machinestamp;	    /* machine stamp in CCP4 convention: big endian=0x11110000 little endian=0x4444000 */
                                    /* The specification is ambiguous, so we are writing 0x11111111 and 0x44444444 */

    float       rms;                /* 	rms deviation of map from mean density */

    int         nlabl;              /* Number of labels being used. */
                                    /* 10 text labels of 80 characters each. */
    char        labels[MRC_NUM_LABELS][MRC_LABEL_SIZE];
    
};
#endif
