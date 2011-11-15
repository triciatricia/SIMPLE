#ifndef FENTH
#define FENTH

#include <qstrlist.h>
#include <qwidget.h>
#include <qscrollview.h>
#include <qmessagebox.h>
#include <qlabel.h>
#include <qpushbutton.h>
#include <qlineedit.h>
#include <qcombobox.h>

class FEntry : public QObject {
	Q_OBJECT

int type;
QString text;
QString help;
QString label;
QLabel *wlabel;
QWidget *wentry;
QPushButton *whelpbut;
float min,max;
int textw;

public:
enum { F_NONE,F_TEXT,F_STRING,F_FLOAT,F_INT,F_LIST,F_BUTTON };

FEntry(int type,char *lab,char *range,char *txt, char *help,
	QScrollView *parent,int x,int y);
~FEntry();

const char *getlabel();
int intValue();
float floatValue();
const char *strValue();
int height();
int width();

signals:
	void newValue();

public slots:
	void changed();
	void dohelp();
	void setIntValue(int v);
	void setFloatValue(float v);
	void setStringValue(char *v);

};

inline const char *FEntry::getlabel() { return (char *)label.data(); }

#endif
