#include "qdialog.h"
#include "qlineedit.h"

class OneLiner : public QDialog {
	Q_OBJECT

	
public:
	QLineEdit *edit;

	OneLiner( const char *prompt, const char *dflt, QWidget *parent=NULL, const char *name=NULL );

//	static void getOneLine(QCString *ret, const char *prompt, const char *dflt,QWidget *parent = NULL);
	static QString getOneLine(const char *prompt, const char *dflt,QWidget *parent = NULL);

};

