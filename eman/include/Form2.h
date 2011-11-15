#ifndef FORMH
#define FORMH

#include <qobject.h>
#include <qdict.h>
#include "FEntry.h"
#include <qscrollview.h>
#include <qfile.h>
#include <qcstring.h>

class Form : public QScrollView {
    Q_OBJECT

QDict<FEntry> entry;
int busy;

public:

Form(QWidget* parent = NULL,const char* name = NULL);
~Form();

void parseFile(char *file);
void parseStr(char *str);

FEntry *getItem(char *label);

void dumpValToFile(char *fsp);
void readValFromFile(char *fsp);

void setBusy(int b) { busy=b; }

static QCString *valFromFile(char *file,char *key);

signals:
	void changed(const char *label);

public slots:
	void change();
	void change(int v);
	void change(const QString &);
};

#endif
