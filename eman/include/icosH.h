/******************************************************************************
*******************************************************************************
*                   icos.h:  header for Brandeis format used in 			  *
*							 Hong's icosahedral reconstruction                *
*******************************************************************************
*                            Wen Jiang                                 		  *
*                            Baylor College of Medicine                       *             
*                            wjiang@tiger.bcm.tmc.edu                         *
*                                                                             *
*                            May 2, 2001                                  	  *
*******************************************************************************
******************************************************************************/


#ifndef ICOSFILE_H
#define ICOSFILE_H

/*******************************************************************************
Data Structure
*******************************************************************************/
struct icosH
{
	int			stamp;				/* = 72 */
    char        title[72];			/* title of the map */
	int			stamp1;				/* = 72 */
	int			stamp2;				/* = 20 */
    int       	nx;                 /* number of rows */
    int       	ny;                 /* number of columnss */
    int       	nz;                 /* number of sections */
	float		min;				/* minimum density value */
	float		max;				/* maximal density value */
    int			stamp3;				/* = 20 */
};

/******************************************************************************
*	the rest are the data in the following format:
*  
*	for each row:
*		int nx*sizeof(float), nx*float, int nx*sizeof(float)
*	
*	then just ny*nz rows stacked	
*******************************************************************************/			
#endif
