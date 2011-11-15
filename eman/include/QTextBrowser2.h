#include <qtextbrowser.h>
#include "QLineEdit2.h"

#ifdef UBUNTU
	#include <qptrstack.h>
#else	//UBUNTU
	#include <qstack.h>
#endif	//UBUNTU

class MyQTextBrowser : public QTextBrowser {
        Q_OBJECT
public:
        MyQTextBrowser( QWidget *parent=0, const char *name=0 ) :
	    QTextBrowser(parent, name) {}
    
       ~MyQTextBrowser() {}

public slots:
       void setSource(const QString& name);
};


class QTextBrowser2:public QWidget {
	Q_OBJECT

	MyQTextBrowser *browser;
	QLineEdit2 *qle;
	QStack<QString> history;
	QString home;
	
public:
	QTextBrowser2( QWidget *parent=0, const char *name=0 );
	~QTextBrowser2();

	virtual void setSource(const QString& name);
	virtual void setLSource(const QString& name);
	virtual void keyReleaseEvent ( QKeyEvent *e );
	virtual void setHome(QString str);

public slots:
	void gotoTop();
	void goBack();
	void newAddr();
	void bChanged();
};
