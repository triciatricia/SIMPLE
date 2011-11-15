#ifndef _EMem_h__
#define _EMem_h__

#include <cstdio>

struct EMHeader {
    char machine; // 0=OS-8, 1=VAX; 2=Convex; 3=SGI; 5=Mac; 6=PC
    char is_new_ver;  //OS-9 only
    char not_used1;
    char data_type; // 1=byte, 2=short; 4=int; 5=float; 8=complex; 9=double
    int nx;
    int ny;
    int nz;
    char comment[80];
    int parameters[40];
    char username[20];
    char date[8];
    char userdata[228];
};


class EMem {
public:
    enum DataType { UNKNOWN_TYPE, CHAR=1, SHORT=2, INT=4, FLOAT=5, COMPLEX=8, DOUBLE=9 };
    enum MachineType { EM_OS8=0, EM_VAX=1, EM_CONVEX=2, EM_SGI=3, EM_MAC=5,EM_PC=6, EM_UNKNOWN_MACHINE };

public:
    EMem(const char* filename);
    ~EMem();

    int read_data(float** p_data, int img_index, bool is_3d=false);
    bool is_complex_mode() const;
    static bool is_valid(const char* filename);

    int get_nx() const;
    int get_ny() const;
    int get_nz() const;

    static int get_machine_type();
    
private:
    FILE* in;
    EMHeader header;
    int mode_size;
    DataType mode;
    bool right_order;
    bool valid_header;
    
    static int get_mode_size(char data_type);
};
  

#endif
