#ifndef MISCI
#define MISCI

#ifndef PI
#define PI (3.141592654)
#endif

class fRect { 
float x[2],y[2]; 

public:
fRect() { x[0]=y[0]=0; x[1]=y[1]=1.0; }
fRect(float X0,float Y0,float X1,float Y1) { setRect(X0,Y0,X1,Y1); }
fRect(const fRect &r) { setRect(r.x[0],r.y[0],r.x[1],r.y[1]); }

inline float x0() { return x[0]; }
inline float x1() { return x[1]; }
inline float y0() { return y[0]; }
inline float y1() { return y[1]; }
inline float xw() { return x[1]-x[0]; }
inline float yw() { return y[1]-y[0]; }
inline void setx0(float px) { if (px>x[1]) { x[0]=x[1]; x[1]=px; } else x[0]=px; }
inline void sety0(float py) { if (py>y[1]) { y[0]=y[1]; y[1]=py; } else y[0]=py; }
inline void setx1(float px) { if (px<x[0]) { x[1]=x[0]; x[0]=px; } else x[1]=px; }
inline void sety1(float py) { if (py<y[0]) { y[1]=y[0]; y[0]=py; } else y[1]=py; }
inline void setxw(float w) { if (w<0) { x[1]=x[0]; x[0]=x[1]+w; } else x[1]=x[0]+w; }
inline void setyw(float w) { if (w<0) { y[1]=y[0]; y[0]=y[1]+w; } else y[1]=y[0]+w; }
inline void setRect(float X0,float Y0,float X1,float Y1) { 
	if (X1<X0) { x[0]=X1; x[1]=X0; } else { x[0]=X0; x[1]=X1; }
	if (Y1<Y0) { y[0]=Y1; y[1]=Y0; } else { y[0]=Y0; y[1]=Y1; }
}

};

struct fPoint { float x,y; };

struct f3Rect { float min[3],max[3]; };
struct f3Point { float x,y,z; };

inline int rnd(float v) { return (int)v; }
#endif
