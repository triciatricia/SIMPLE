// This is just like the qt QDict class, but it contains actual values
// (like floats and ints) instead of pointers to values
// Haven't tested, may have problems with doubles or other >4 byte values

template<class type> class QDictV : public QGDict
{
public:
    QDictV(int size=17,bool cs=TRUE,bool ck=TRUE) : QGDict(size,cs,ck,0) {}
    QDictV( const QDictT<type> &d ) : QGDict(d) {}
   ~QDictV()                            { clear(); }
    QDictV<type> &operator=(const QDictV<type> &d)
                        { return (QDictV<type>&)QGDict::operator=(d); }
    uint  count()   const               { return QGDict::count(); }
    uint  size()    const               { return QGDict::size(); }
    bool  isEmpty() const               { return QGDict::count() == 0; }
    void  insert( const char *k, const type d )
                                        { QGDict::look(k,(GCI)d,1); }
    void  replace( const char *k, const type d )
                                        { QGDict::look(k,(GCI)d,2); }
    bool  remove( const char *k )       { return QGDict::remove(k); }
    type  take( const char *k )         { return (type)QGDict::take(k); }
    void  clear()                       { QGDict::clear(); }
    type  find( const char *k ) const
                    { return (type)((QGDict*)this)->QGDict::look(k,0,0); }
    type  operator[]( const char *k ) const
                    { return (type)((QGDict*)this)->QGDict::look(k,0,0); }
    void  statistics() const            { QGDict::statistics(); }
private:
    void  deleteItem( GCI d )   { if ( del_item ) delete (type)d; }
};
