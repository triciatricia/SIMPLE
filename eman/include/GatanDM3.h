#ifndef __gatandm3_h__
#define __gatandm3_h__

#include <cstdio>
#include <map>
#include <vector>
#include <cstring>

#ifdef DEBUG_DM3
#include <cassert>
#else
#undef assert
#define assert(expr) (void (0))
#endif

using std::vector;

namespace Gatan {
    
    enum Endian {
	BigEndian = 0,
	LittleEndian = 1,
	UnknownEndian = 2
    };

    enum DataFormat {
	TAG_DATA,
	NON_TAG
    };
    
    void swap2(void* data, int nitems);
    void swap4(void* data, int nitems);
    void swap8(void* data, int nitems);
    
    
    void becomeplatformendian(short* data, DataFormat f);
    void becomeplatformendian(unsigned short* data, DataFormat f);
    void becomeplatformendian(int* data, DataFormat f);
    void becomeplatformendian(unsigned int* data, DataFormat f);
    void becomeplatformendian(unsigned long* data, DataFormat f);
    void becomeplatformendian(float* data, DataFormat f);
    void becomeplatformendian(double* data, DataFormat f);

    
    class Util {
    public:	
	static bool is_valid_order(DataFormat f);
	static Endian image_endian;
	static Endian system_endian;
	
    private:
	Util();
	
    };
    
    class StrCmp
    {
    public:
	bool operator()(const char* s1, const char* s2) const
	{
	    return std::strcmp(s1, s2) < 0;
	}
    };

    class TagTable {
    public:
	static TagTable* get_instance();
	static void clear();
	
	void add(const char* name, const char* value);
	void add_data(char* data);	
	
	
	const char* get_string(const char* name);
	int get_int(const char* name);
	float get_float(const char* name);
	double get_double(const char* name);

	int get_x() const;
	int get_y() const;
	int get_z() const;
	int get_datatype() const;
	char* get_data() const;
	
	void dump() const;
	
    private:
	static TagTable* instance;
	std::map<const char*, const char*, StrCmp> tags;
	
	int img_index;
	vector<int> x_list;
	vector<int> y_list;
	vector<int> z_list;
	vector<int> datatype_list;
	vector<char*> data_list;
	
	TagTable();
	~TagTable();
	void set_thumb_index(int i);
    };
    
    class TagData {
     public:
	enum Type {
	    SHORT   = 2,
	    LONG    = 3,
	    USHORT  = 4,
	    ULONG   = 5,
	    FLOAT   = 6,
	    DOUBLE  = 7,
	    BOOLEAN = 8,
	    CHAR    = 9,
	    OCTET   = 10,
	    STRUCT  = 15,
	    STRING  = 18,
	    ARRAY   = 20
	};
	
   
	TagData(FILE* data_file, const char* tagname);
	~TagData();

	int read(bool nodata=false);
		
    private:
	FILE* in;
	int tag_type;
	const char* name;
	
	int typesize() const;
	int typesize(int type) const;

	int read_any(bool nodata=false);
	
	vector<int> read_array_types();
	int read_array_data(vector<int> item_types, bool nodata=false);
	vector<int> read_struct_types();
	const char* read_native(bool is_value_stored);
	const char* read_string(int size);
	
    };

    
    class TagGroup {
    public:
	TagGroup(FILE* data_file, const char* groupname);
	~TagGroup();
	
	int read(bool nodata=false); // return 0 if OK; -1 if any error;	
	const char* get_name() const;
	int get_entry_id();
	
    private:
	FILE* in;
	const char* name;
	int entry_id;
    };

    
    class TagEntry {
    public:
	enum EntryType {
	    GROUP_TAG = 20,
	    DATA_TAG = 21
	};
	    
	TagEntry( FILE* data_file, TagGroup* parent_group);
	~TagEntry();
	
	int read(bool nodata=false);
	
    private:
	FILE* in;
	char* name;
	TagGroup* parent_group;
    };

    
    class DataType {
    public:
	enum Type {
	    NULL_DATA,
	    SIGNED_INT16_DATA,
	    REAL4_DATA,
	    COMPLEX8_DATA,
	    OBSELETE_DATA,
	    PACKED_DATA,
	    UNSIGNED_INT8_DATA,
	    SIGNED_INT32_DATA,
	    RGB_DATA,
	    SIGNED_INT8_DATA,
	    UNSIGNED_INT16_DATA,
	    UNSIGNED_INT32_DATA,
	    REAL8_DATA,
	    COMPLEX16_DATA,
	    BINARY_DATA,
	    RGB_UINT8_0_DATA,
	    RGB_UINT8_1_DATA,
	    RGB_UINT16_DATA,
	    RGB_FLOAT32_DATA,
	    RGB_FLOAT64_DATA,
	    RGBA_UINT8_0_DATA,
	    RGBA_UINT8_1_DATA,
	    RGBA_UINT8_2_DATA,
	    RGBA_UINT8_3_DATA,
	    RGBA_UINT16_DATA,
	    RGBA_FLOAT32_DATA,
	    RGBA_FLOAT64_DATA,
	    POINT2_SINT16_0_DATA,
	    POINT2_SINT16_1_DATA,
	    POINT2_SINT32_0_DATA,
	    POINT2_FLOAT32_0_DATA,
	    RECT_SINT16_1_DATA,
	    RECT_SINT32_1_DATA,
	    RECT_FLOAT32_1_DATA,
	    RECT_FLOAT32_0_DATA,
	    SIGNED_INT64_DATA,
	    UNSIGNED_INT64_DATA,
	    LAST_DATA
	};

    };


    class DM3Reader {
    public:
	DM3Reader(FILE* file);
	DM3Reader(const char* filename);
	~DM3Reader();

	int init();
	int read(bool nodata=false);
	
	int read_data(float** p_data);

	int get_nx() const;
	int get_ny() const;
	int get_nz() const;

	int get_exposure_num() const;
	int get_data_type() const;
	int get_camera_x() const;
	int get_camera_y() const;
	const char* get_frame_type() const;

	int get_binning_x() const;
	int get_binning_y() const;
	
	float get_zoom_factor() const;
	double get_exposure_time() const;  
	bool get_anti_blooming() const;
	double get_magnification() const;
	
    private:
	const char* filename;
	FILE* in;
	TagGroup* root_group;
	
	int nx;
	int ny;
	int nz;
	int exp_num;
	int data_type;
	int camera_x;
	int camera_y;
	const char* frame_type;
	int binning_x;
	int binning_y;
	float zoom;
	double exp_time;
	bool anti_blooming;
	double mag;

	void init_vars();
    };
    
    const char* to_str(Endian byteorder);
    const char* to_str(TagData::Type type);
    const char* to_str(TagEntry::EntryType type);
    const char* to_str(DataType::Type type);
}

#endif
