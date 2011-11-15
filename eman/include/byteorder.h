/**
 * $Id: byteorder.h,v 1.5 2008/05/15 23:57:44 gtang Exp $
 */

#ifndef eman__byteorder_h__
#define eman__byteorder_h__ 1

#include <cstddef>

/** ByteOrder defines functions to work on big/little endian byte orders.
 *
 * The byte order is the order in which bytes are stored to
 * create larger data types such as the int and long values.
 * Different kinds of computers use different byte order conventions.
 * 
 * There are 2 major byte orders: big-endian and little-endian.
 *
 * big-endian (like SGI) store the most significant bytes (i.e. the
 * bytes that hold the largest part of the value) first. little-endian
 * (like x86) store the most significant byte last. 
 *
 * The machine byte order is the byte order used on the current machine.
 *
 * ByteOrder class defines functions for
 *    checking running-machine byte-order,
 *    checking data byte-order,
 *    convert data from one byte-order to another byte-order.
 */
class ByteOrder
{
public:
    static bool is_machine_big_endian();
    
    /** given a small floating number, return whether the number
	 * is in big endian or not. If a number is smaller than 65535,
	 * it is defined as a "small" number here.
	 */
	static bool is_float_big_endian(float small_number);

    /** given a pointer to a reasonable small integer number,
     * return whether the number is big endian or not.
     * For a n-bit integer, the number should < (2 ^ (n/2)).
     * e.g., for 'int', number should < 65535;
     * for 'short', number should < 255.
     */
    template <class T> static bool is_data_big_endian(T * small_num_addr)
    {
	if (!small_num_addr) {
	    return false;
	}

	bool data_big_endian = false;
	size_t typesize = sizeof(T);
	char *d = (char *) small_num_addr;

	if (is_machine_big_endian()) {
	    data_big_endian = false;
	    for (size_t i = typesize / 2; i < typesize; i++) {
		if (d[i] != 0) {
		    data_big_endian = true;
		    break;
		}
	    }
	}
	else {
	    data_big_endian = true;
	    for (size_t j = 0; j < typesize / 2; j++) {
		if (d[j] != 0) {
		    data_big_endian = false;
		    break;
		}
	    }
	}

	return data_big_endian;
    }

    /** convert data from machine byte order to big endian order.
     * 'n' is the number of elements of type T.
     */
    template <class T> static void become_big_endian(T * data, size_t n = 1) {
	if (!is_machine_big_endian()) {
	    swap_bytes<T>(data, n);
	}
    }

    /** convert data from machine byte order to little endian order.
     * 'n' is the number of elements of type T.
     */
    template <class T> static void become_little_endian(T * data, size_t n = 1) {
	if (is_machine_big_endian()) {
	    swap_bytes<T>(data, n);
	}
    }

    /** swap the byte order of data with 'n' T-type elements.
     */
    template <class T> static void swap_bytes(T * data, size_t n = 1) {
	unsigned char s;
	size_t p = sizeof(T);
	char *d = (char *) data;

	if (p > 1) {
	    for (size_t i = 0; i < n; i++, d += p) {
		for (size_t j = 0; j < p / 2; j++) {
		    s = d[j];
		    d[j] = d[p - 1 - j];
		    d[p - 1 - j] = s;
		}
	    }
	}
    }

private:
    static bool is_machine_endian_checked;
    static bool machine_big_endian;
};


#endif
