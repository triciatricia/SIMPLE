#ifndef QLED2
#define QLED2

#ifdef UBUNTU
	#include <qlineedit.h>
#else	//UBUNTU
	#include <qlined.h>
#endif	//UBUNTU

class QLineEdit2:public QLineEdit {
	Q_OBJECT

protected:
	virtual void focusOutEvent ( QFocusEvent *fe );

public:
	QLineEdit2( QWidget * parent, const char * name=0 );
	QLineEdit2( const QString &s, QWidget * parent, const char * name=0 );

signals:
	void lostFocus2();

};

#endif
