#include <cstdio>

class EMVtk {
public:
    EMVtk(const char* filename);
    EMVtk(FILE* in);
    ~EMVtk();
    
    int init();
    int read_data(float** p_data);
    int get_nx() const { return nx; }
    int get_ny() const { return ny; }
    int get_nz() const { return nz; }

private:    
    enum VtkType { VTK_ASCII, VTK_BINARY, VTK_UNKNOWN };
    enum DataType { UNSIGNED_SHORT, FLOAT, DATA_UNKNOWN };
    
    const char* fname;
    FILE* in;
    DataType datatype;
    VtkType filetype;
    int nx;
    int ny;
    int nz;
    float originx;
    float originy;
    float originz;
    float spacingx;
    float spacingy;
    float spacingz;
};
