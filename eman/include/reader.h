/**
 * Reading routines for volumetric data
 *
 * Author: Tao Ju
 * Date: 02/16/2005
 */


#ifndef READER_H
#define READER_H

#include <cstdio>
#include <cstdlib>
#include "EMData.h"
#include "volume.h"

class VolumeReader
{
public:
	VolumeReader ( ){} ;

	/* Read volume from input */
	virtual Volume* getVolume( ) = 0 ;

	/* Get resolution */
	virtual void getSpacing( float& ax, float& ay, float& az ) = 0 ;


	void flipBits32 ( void *x )
	{
		unsigned char *temp = (unsigned char *)x;
		unsigned char swap;
		
		swap = temp [ 0 ];
		temp [ 0 ] = temp [ 3 ];
		temp [ 3 ] = swap;

		swap = temp [ 1 ];
		temp [ 1 ] = temp [ 2 ];
		temp [ 2 ] = swap;
	}


};

class EmanMRCReader : public VolumeReader
{
	EMData* model ; 

public:
	/* Initializer */
	EmanMRCReader( char* fname )
	{
		model = new EMData ;
		if ( model->readImage( fname, -1 ) )
		{
			printf("Error reading input %s.\n", fname);
			exit(1);
		}
	}

	/* Read volume */
	Volume* getVolume( )
	{
		int dimx = model->xSize() ;
		int dimy = model->ySize() ;
		int dimz = model->zSize() ;

		Volume* vol = new Volume( dimx, dimy, dimz ) ;
		for ( int i = 0 ; i < dimz ; i ++ )
			for ( int j = 0 ; j < dimy ; j ++ )
				for ( int k = 0 ; k < dimx ; k ++ )
				{
					float d = model->valueAt( i, j, k ) ;
					
					vol->setDataAt( i, j, k, d ) ;
				}
		return vol ;
	}

	/* Get resolution */
	void getSpacing( float& ax, float& ay, float& az )
	{
		ax = 1 ;
		ay = 1 ;
		az = 1 ;
	}


private:

	int totx, toty, totz ;
	int offx, offy, offz ;
	int dimx, dimy, dimz ;

	float angsx, angsy, angsz ;
	float anglex, angley, anglez ;
	float dmin, dmax, dmean, drms ;
	
	int mode ;

	char mrcfile[1024] ;
};

class MRCReader : public VolumeReader
{
public:
	/* Initializer */
	MRCReader( char* fname )
	{
		sprintf( mrcfile, "%s", fname ) ;

		FILE* fin = fopen( fname, "rb" ) ;

		// Parse header
		fread( &totx, sizeof( int ), 1, fin ) ;
		fread( &toty, sizeof( int ), 1, fin ) ;
		fread( &totz, sizeof( int ), 1, fin ) ;

		fread( &mode, sizeof( int ), 1, fin ) ;

		fread( &offx, sizeof( int ), 1, fin ) ;
		fread( &offy, sizeof( int ), 1, fin ) ;
		fread( &offz, sizeof( int ), 1, fin ) ;
		
		fread( &dimx, sizeof( int ), 1, fin ) ;
		fread( &dimy, sizeof( int ), 1, fin ) ;
		fread( &dimz, sizeof( int ), 1, fin ) ;
		dimx ++ ;
		dimy ++ ;
		dimz ++ ;

		fread( &angsx, sizeof( float ), 1, fin ) ;
		fread( &angsy, sizeof( float ), 1, fin ) ;
		fread( &angsz, sizeof( float ), 1, fin ) ;

		fread( &anglex, sizeof( float ), 1, fin ) ;
		fread( &angley, sizeof( float ), 1, fin ) ;
		fread( &anglez, sizeof( float ), 1, fin ) ;

		fseek( fin, 12, SEEK_CUR ) ;

		fread( &dmin, sizeof( float ), 1, fin ) ;
		fread( &dmax, sizeof( float ), 1, fin ) ;
		fread( &dmean, sizeof( float ), 1, fin ) ;

		fseek( fin, 4 * 32, SEEK_CUR ) ;

		fread( &drms, sizeof( float ), 1, fin ) ;
		fclose( fin ) ;

		dimx = totx ;
		dimy = toty ;
		dimz = totz ;

		printf("Dimension: %d %d %d\n", dimx, dimy, dimz ) ;
		printf("Mode: %d\n", mode) ;
		printf("Density: from %f to %f, mean at %f, rms at %f\n", dmin, dmax, dmean, drms ) ;
		printf("Cell size: %f %f %f\n", angsx / (dimx-1), angsy / (dimy-1), angsz / (dimz-1) ) ;
		printf("Cell angles: %f %f %f\n", anglex, angley, anglez ) ;

		if ( mode > 2 )
		{
			printf("Complex mode not supported.\n") ;
			exit(0) ;
		}

		/* Hacking code 
		fseek( fin, 0, SEEK_END ) ;
		long len = ftell( fin ) ;
		len -= 1024 ;

		dimen = 1 ;
		while ( dimen * dimen * dimen < len / 4 )
		{
			dimen ++ ;
		}
		printf("Size: %d\n", dimen) ;
		*/
	}

	/* Read volume */
	Volume* getVolume( )
	{
		FILE* fin = fopen( mrcfile, "rb" ) ;
		fseek( fin, 1024, SEEK_SET ) ;

		char chard ;
		short shortd ;
		float floatd ;
		double d ;

		
		Volume* vol = new Volume( dimx, dimy, dimz ) ;
		for ( int i = 0 ; i < dimz ; i ++ )
			for ( int j = 0 ; j < dimy ; j ++ )
				for ( int k = 0 ; k < dimx ; k ++ )
				{
					switch ( mode )
					{
					case 0: 
						fread( &chard, sizeof( char ), 1, fin ) ;
						d = (double) chard ;
						break ;
					case 1:
						fread( &shortd, sizeof( short ), 1, fin ) ;
						d = (double) shortd ;
						break ;
					case 2:
						fread( &floatd, sizeof( float ), 1, fin ) ;
						d = (double) floatd ;
						break ;
					}
					
					vol->setDataAt( k, j, i, d ) ;
				}
		fclose( fin ) ;

		return vol ;
	}

	/* Get resolution */
	void getSpacing( float& ax, float& ay, float& az )
	{
		ax = angsx / (dimx - 1);
		ay = angsy / (dimy - 1) ;
		az = angsz / (dimz - 1) ;
	}


private:

	int totx, toty, totz ;
	int offx, offy, offz ;
	int dimx, dimy, dimz ;

	float angsx, angsy, angsz ;
	float anglex, angley, anglez ;
	float dmin, dmax, dmean, drms ;
	
	int mode ;

	char mrcfile[1024] ;
};

class InvMRCReader : public VolumeReader
{
public:
	/* Initializer */
	InvMRCReader( char* fname )
	{
		sprintf( mrcfile, "%s", fname ) ;

		FILE* fin = fopen( fname, "rb" ) ;

		// Parse header
		ifread( &totx, sizeof( int ), 1, fin ) ;
		ifread( &toty, sizeof( int ), 1, fin ) ;
		ifread( &totz, sizeof( int ), 1, fin ) ;


		ifread( &mode, sizeof( int ), 1, fin ) ;

		ifread( &offx, sizeof( int ), 1, fin ) ;
		ifread( &offy, sizeof( int ), 1, fin ) ;
		ifread( &offz, sizeof( int ), 1, fin ) ;
		printf("%d %d %d\n", offx, offy, offz) ;
		
		ifread( &dimx, sizeof( int ), 1, fin ) ;
		ifread( &dimy, sizeof( int ), 1, fin ) ;
		ifread( &dimz, sizeof( int ), 1, fin ) ;

		ifread( &angsx, sizeof( float ), 1, fin ) ;
		ifread( &angsy, sizeof( float ), 1, fin ) ;
		ifread( &angsz, sizeof( float ), 1, fin ) ;

		ifread( &anglex, sizeof( float ), 1, fin ) ;
		ifread( &angley, sizeof( float ), 1, fin ) ;
		ifread( &anglez, sizeof( float ), 1, fin ) ;

		fseek( fin, 12, SEEK_CUR ) ;

		ifread( &dmin, sizeof( float ), 1, fin ) ;
		ifread( &dmax, sizeof( float ), 1, fin ) ;
		ifread( &dmean, sizeof( float ), 1, fin ) ;

		fseek( fin, 4 * 32, SEEK_CUR ) ;

		ifread( &drms, sizeof( float ), 1, fin ) ;
		fclose( fin ) ;

		dimx = totx ;
		dimy = toty ;
		dimz = totz ;
		printf("Dimension: %d %d %d\n", dimx, dimy, dimz ) ;
		printf("Mode: %d\n", mode) ;
		printf("Density: from %f to %f, mean at %f, rms at %f\n", dmin, dmax, dmean, drms ) ;
		printf("Cell size: %f %f %f\n", angsx / (dimx-1), angsy / (dimy-1), angsz / (dimz-1) ) ;
		printf("Cell angles: %f %f %f\n", anglex, angley, anglez ) ;

		if ( mode > 2 )
		{
			printf("Complex mode not supported.\n") ;
			// exit(0) ;
		}

		/* Hacking code 
		fseek( fin, 0, SEEK_END ) ;
		long len = ftell( fin ) ;
		len -= 1024 ;

		dimen = 1 ;
		while ( dimen * dimen * dimen < len / 4 )
		{
			dimen ++ ;
		}
		printf("Size: %d\n", dimen) ;
		*/
	}

	/* Read volume */
	Volume* getVolume( )
	{
		FILE* fin = fopen( mrcfile, "rb" ) ;
		fseek( fin, 1024, SEEK_SET ) ;

		char chard ;
		short shortd ;
		float floatd ;
		double d ;

		
		Volume* vol = new Volume( dimx, dimy, dimz ) ;
		for ( int i = 0 ; i < dimz ; i ++ )
			for ( int j = 0 ; j < dimy ; j ++ )
				for ( int k = 0 ; k < dimx ; k ++ )
				{
					switch ( mode )
					{
					case 0: 
						fread( &chard, sizeof( char ), 1, fin ) ;
						d = (double) chard ;
						break ;
					case 1:
						fread( &shortd, sizeof( short ), 1, fin ) ;
						d = (double) shortd ;
						break ;
					default:
						ifread( &floatd, sizeof( float ), 1, fin ) ;
						d = (double) floatd ;
						break ;
					}

//					printf("%g\n", d) ;exit(0) ;
				
					vol->setDataAt( k, j, i, d ) ;
				}
		fclose( fin ) ;

		return vol ;
	}

	void ifread( void * d, size_t s1, size_t s2, FILE* f )
	{
		fread( d, s1, s2, f ) ;
		flipBits32( d ) ;
	}

	/* Get resolution */
	void getSpacing( float& ax, float& ay, float& az )
	{
		ax = angsx / (dimx - 1);
		ay = angsy / (dimy - 1) ;
		az = angsz / (dimz - 1) ;
	}


private:

	int totx, toty, totz ;
	int offx, offy, offz ;
	int dimx, dimy, dimz ;

	float angsx, angsy, angsz ;
	float anglex, angley, anglez ;
	float dmin, dmax, dmean, drms ;
	
	int mode ;

	char mrcfile[1024] ;
};

class MRCReaderPicker
{
public:
	MRCReaderPicker(){} ;

	static VolumeReader* pick( char* fname )
	{
		return new EmanMRCReader( fname ) ;

		FILE* fin = fopen( fname, "rb" ) ;
		if ( fin == NULL )
		{
			printf("Error reading MRC file %s.\n", fname) ;
			exit(0) ;
		}
		int totx, toty, totz ;

		// Parse header
		fread( &totx, sizeof( int ), 1, fin ) ;
		fread( &toty, sizeof( int ), 1, fin ) ;
		fread( &totz, sizeof( int ), 1, fin ) ;

		fclose( fin ) ;

		if ( totx <= 0 || totx > 1024 )
		{
			printf("Calling inverse MRCreader.\n") ;
			return new InvMRCReader( fname ) ;
		}
		else
		{
			printf("Calling MRCreader.\n") ;
			return new MRCReader( fname ) ;
		}
	}
};

class HackMRCReader : public VolumeReader
{
public:
	/* Initializer */
	HackMRCReader( char* fname )
	{
		sprintf( mrcfile, "%s", fname ) ;

		FILE* fin = fopen( fname, "rb" ) ;


		fseek( fin, 0, SEEK_END ) ;
		long len = ftell( fin ) ;
		len -= 1024 ;

		dimen = 1 ;
		while ( dimen * dimen * dimen < len / 4 )
		{
			dimen ++ ;
		}
		printf("Volume Size: %d\n", dimen) ;

		fclose( fin ) ;
	}

	/* Read volume */
	Volume* getVolume( )
	{
		FILE* fin = fopen( mrcfile, "rb" ) ;
		fseek( fin, 1024, SEEK_SET ) ;
		
		Volume* vol = new Volume( dimen, dimen, dimen ) ;
		float d ;
		for ( int i = 0 ; i < dimen ; i ++ )
			for ( int j = 0 ; j < dimen ; j ++ )
				for ( int k = 0 ; k < dimen ; k ++ )
				{
					fread( &d, sizeof( float ), 1, fin ) ;
					flipBits32( &d ) ;
					// printf("%g\n", d) ;exit(0) ;
					vol->setDataAt( k, j, i, d ) ;
				}
		fclose( fin ) ;

		return vol ;
	}

	/* Get resolution */
	void getSpacing( float& ax, float& ay, float& az )
	{
		ax = 1 ;
		ay = 1 ;
		az = 1 ;
	}


private:

	int dimen ;
	char mrcfile[1024] ;
};


class CylinderVolumeGenerator : public VolumeReader
{
public:
	/* Initializer */
	CylinderVolumeGenerator( int dim, double rad )
	{
		size = dim ;
		radius = rad ;
	};

	Volume* getVolume()
	{
		Volume* vol = new Volume( size, size, size ) ;
		int thick = size / 6 ;

		double cent = (size - 1) / 2.0 ;
		double r2 = radius * radius ;
		for ( int x = 0 ; x < size ; x ++ )
			for ( int y = 0 ; y < size ; y ++ )
				for ( int z = 0 ; z < size ; z ++ )
				{
					double dis = sqrt( ( z - cent ) * ( z - cent ) + ( x - cent ) * ( x - cent ) );
					
					if ( fabs( y - cent ) > thick )
					{
						vol->setDataAt( x, y, z, - ( fabs( y - cent ) - thick ) ) ;
					}
					else
					{
						vol->setDataAt( x, y, z, radius - dis ) ;
					}

					// double dis = ( z - cent ) * ( z - cent ) + ( x - cent ) * ( x - cent );
					// vol->setDataAt( x, y, z, 10 - 10 * dis / r2 ) ;
				};

		return vol ;
	};

	/* Get resolution */
	void getSpacing( float& ax, float& ay, float& az )
	{
		ax = 1 ;
		ay = 1 ;
		az = 1 ;
	}


private:

	int size ;
	double radius ;
};


class SheetVolumeGenerator : public VolumeReader
{
public:
	/* Initializer */
	SheetVolumeGenerator( int dim, double hit )
	{
		size = dim ;
		height = hit ;
	};

	Volume* getVolume()
	{
		Volume* vol = new Volume( size, size, size ) ;

		double cent = (size - 1) / 2.0 ;
		for ( int x = 0 ; x < size ; x ++ )
			for ( int y = 0 ; y < size ; y ++ )
				for ( int z = 0 ; z < size ; z ++ )
				{
					double dis = fabs( z - cent );
					vol->setDataAt( x, y, z, 10 - 10 * dis / height ) ;

					// double dis = ( z - cent ) * ( z - cent ) + ( x - cent ) * ( x - cent );
					// vol->setDataAt( x, y, z, 10 - 10 * dis / r2 ) ;
				};

		return vol ;
	};

	/* Get resolution */
	void getSpacing( float& ax, float& ay, float& az )
	{
		ax = 1 ;
		ay = 1 ;
		az = 1 ;
	}


private:

	int size ;
	double height ;
};




class SphereVolumeGenerator : public VolumeReader
{
public:
	/* Initializer */
	SphereVolumeGenerator( int dim, double ratiox, double ratioy, double ratioz )
	{
		size = dim ;
		rx = ratiox ;
		ry = ratioy ;
		rz = ratioz ;
	};

	Volume* getVolume()
	{
		Volume* vol = new Volume( size, size, size ) ;

		double dis = ( size - 1 ) * ( size - 1 ) / 4 ;

		for ( int x = 0 ; x < size ; x ++ )
			for ( int y = 0 ; y < size ; y ++ )
				for ( int z = 0 ; z < size ; z ++ )
				{
					double d = rx * ( x - ( size - 1 ) / 2) * ( x - ( size - 1 ) / 2) + 
						ry * ( y - ( size - 1 ) / 2) * ( y - ( size - 1 ) / 2) + 
						rz * ( z - ( size - 1 ) / 2) * ( z - ( size - 1 ) / 2) ;
					vol->setDataAt( x, y, z, 10 - 10 * sqrt(d) / sqrt(dis) ) ;
					// vol->setDataAt( x, y, z, 10 - 10 * (x + y) / size ) ;
				};

		return vol ;
	};

	/* Get resolution */
	void getSpacing( float& ax, float& ay, float& az )
	{
		ax = 1 ;
		ay = 1 ;
		az = 1 ;
	}


private:

	int size, rx, ry, rz ;
};








#endif
