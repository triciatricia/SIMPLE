#include <qlistbox.h>

class ColorListItem : public QListBoxItem {
private:
QColor color;

public:
ColorListItem( const char *s, QColor col ): QListBoxItem() 
	{ setText( s ); color=col; }

void setColor(QColor col);
QColor getColor();

protected:
	virtual void paint( QPainter * );
	virtual int height( const QListBox * ) const;
	virtual int width( const QListBox * ) const;

};

inline void ColorListItem::setColor(QColor col) { color=col; }
inline QColor ColorListItem::getColor() { return color; }
