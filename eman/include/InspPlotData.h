/**********************************************************************

	--- Qt Architect generated file ---

	File: InspPlotData.h
	Last generated: Thu Apr 25 00:40:18 2002

	DO NOT EDIT!!!  This file will be automatically
	regenerated by qtarch.  All changes will be lost.

 *********************************************************************/

#ifndef InspPlotData_included
#define InspPlotData_included

#include <qwidget.h>
#include "qwidgetstack.h"
#include <qpushbutton.h>
#include <qlistbox.h>
#include <qtabbar.h>
#include <qlineedit.h>

class InspPlotData : public QWidget
{
    Q_OBJECT

public:

    InspPlotData(QWidget *parent = NULL, const char *name = NULL);

    virtual ~InspPlotData();

    protected slots:

    virtual void newPlotTab(int) =0;
    virtual void newLegend(bool) =0;
    virtual void newPlotList(int) =0;
    virtual void newPlotName() =0;

    protected:

    QListBox *plotlist;
    QLineEdit *plotname;
    QTabBar *plottab;
    QPushButton *legend;
    QWidgetStack *stack;
};

#endif // InspPlotData_included
