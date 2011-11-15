#ifndef _EM_ICOS_H_
#define _EM_ICOS_H_

#include <cstdio>

class EMIcos {
public:
    EMIcos(const char* filename);
    ~EMIcos();

    bool is_right_order() const;
    bool is_valid_header() const;
    int get_nx() const;
    int get_ny() const;
    int get_nz() const;
    const char* get_title() const;
    
private:
    struct icosH* header;
    FILE* in;
    bool is_zipped;
    bool right_order;
    bool valid_header;
};

#endif








