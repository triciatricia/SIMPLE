/*******************************************************************************
********************************************************************************
*                   rawiv.h:  header for Rawiv data format                     *
********************************************************************************
*                                                                              *
* official definition at http://www.ticam.utexas.edu/~shrew/formats/rawiv.html *	
*                            Wen Jiang   2003-12-8                             *
*                                                                              *
********************************************************************************
*******************************************************************************/


#ifndef RAWIV_H
#define RAWIV_H


/* Everything is in big-endian. Big endian is the byte order on Sun, SGI, IBM 
   architectures. Intel's byte order is little endian.
*/
 
/*******************************************************************************
Protected Data Structures
*******************************************************************************/
struct rawivH
{
	float			minX;		/* co-ordinates of the 1st voxel */
	float			minY;                
	float			minZ;                
	float			maxX;		/* co-ordinates of the 1st voxel */
	float			maxY;                
	float			maxZ;     
	
	unsigned int	 numVerts;	/* number of vertices in the grid = dimX * dimY * dimZ */
	unsigned int	 numCells;	/* number of cells in the grid = (dimX - 1) * (dimY - 1) * (dimZ - 1) */
	
	unsigned int	 dimX;		/* number of vertices in x direction */
	unsigned int	 dimY;		/* number of vertices in y direction */
	unsigned int	 dimZ;		/* number of vertices in z direction */
	
	float			originX;
	float			originY;
	float			originZ;
		          
	float			spanX;		/* spacing between one vertex and the next along X axis */
	float			spanY;		/* spacing between one vertex and the next along Y axis */
	float			spanZ;		/* spacing between one vertex and the next along Z axis */
};

/* 
Next follows the actual data in the raw format. 

A rawiv file is created by concatenating a raw file to a file containing the rawiv header. 
The suffix on the name of a rawiv file .rawiv 

The raw portion of the rawiv file is in binary big-Endian format used to represent 3D volumetric data 
of scalar fields defined on a regular grid. It is simply a sequence of values. These values can be 
floats, unsigned shorts, or unsigned chars. 

The data is listed with the x co-ordinate varying fastest, and z varying slowest. 

So, in C++ syntax a reader would contain the following code snippet: 

for (int z=0; z < dimZ; z++)
        for (int y=0; y < dimY; y++)
                for (int x=0; x < dimX; x++)
                {
                        //read data here
                }

*/
		
#endif
