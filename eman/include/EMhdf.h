#ifndef _emhdf_h_
#define _emhdf_h_

#include "config.h"
#ifdef HDF5

#define H5_USE_16_API

#include <hdf5.h>
#include "EMTypes.h"
#include <vector>

using std::vector;

class EMhdf {
public:
    enum DataType { INT, FLOAT, STRING };
    
public:
    EMhdf(const char* hdf_filename, const char* rw_mode="rw");
    ~EMhdf();

    static int is_valid(const char* filename);
    
    int read_data(int dataset_id, float** p_data);
    int write_data(int dataset_id, float* data, int ndim, int* dims);
    
    int read_int_attr(int dataset_id, const char* attr_name);
    float read_float_attr(int dataset_id, const char* attr_name);
    const char* read_string_attr(int dataset_id, const char* attr_name);
    void read_array_attr(int dataset_id, const char* attr_name, void* value);

    int read_global_int_attr(const char* attr_name);
    float read_global_float_attr(const char* attr_name);
    
    int read_ctfit(int dataset_id, CTFParam* value);
    int* read_dims(int dataset_id, int* p_ndim);
    int read_euler_attr(int dataset_id, const char* attr_name);
    int read_mapinfo_attr(int dataset_id, const char* attr_name);

    int write_int_attr(int dataset_id, const char* attr_name, int value);
    int write_float_attr(int dataset_id, const char* attr_name, float value);
    int write_string_attr(int dataset_id, const char* attr_name, const char* value);
    int write_array_attr(int dataset_id, const char* attr_name, int nitems, void* data, DataType type);
    int write_global_int_attr(const char* attr_name, int value);
    int write_ctfit(int dataset_id, CTFParam* value);
    int write_euler_attr(int dataset_id, const char* attr_name, int value);
    int write_mapinfo_attr(int dataset_id, const char* attr_name, int value);
    
    int delete_attr(int dataset_id, const char* attr_name);
    
    int get_num_dataset();
    vector<int> get_dataset_ids();
    
private:
    enum Nametype { ROOT_GROUP, CTFIT, NUMDATASET, COMPOUND_DATA_MAGIC };
    
private:
    hid_t file;
    hid_t group;
    hid_t cur_dataset;
    int cur_dataset_id;
    
    herr_t (*old_func)(void*);
    void *old_client_data;

    static hid_t euler_type;
    static hid_t mapinfo_type;

    vector<int> dataset_ids;
    
    void hdf_err_off();
    void hdf_err_on();

    int delete_attr(const char* attr_name);
    
    void set_dataset(int dataset_id);      
    int create_compound_attr(int dataset_id, const char* attr_name);        
    void close_dataset(hid_t dataset);    
    static const char* get_item_name(Nametype type);
    void increase_num_dataset();
    
    static void create_enum_types();
    const char* get_compound_name(int id, const char* name);

    float read_float_attr(const char* attr_name);
    int write_int_attr(const char* attr_name, int value);
    int write_float_attr(const char* attr_name, float value);

    friend herr_t file_info(hid_t loc_id, const char *name, void *opdata);
};

herr_t file_info(hid_t loc_id, const char *name, void *opdata);

#endif
#endif
