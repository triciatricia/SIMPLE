#ifndef VALSH
#define VALSH

#include "QLineEdit2.h"
#include <qslider.h>

class ValSlider : public QWidget
{
    Q_OBJECT
private:
	float value,min,max;
	int tsize,twidth,active;
	char *vname;
	QSlider		*slider;
	QLineEdit2	*line;

public:
	ValSlider( QWidget *parent=0, const char *name=0 );
	~ValSlider();
	float		Value();
	void		setTSize(int);
	void 		setVarName(char *name);
protected:
	void        resizeEvent( QResizeEvent * );
public:
signals:
	void		newValue(float);
	void		newVarVal(char *name,float val);
public slots:
	void        sliderchange();
	void		textchange();
	void		setValue(float);
	void		setValueQ(float);
	void		setMin(float);
	void		setMax(float);
};

inline float ValSlider::Value() { return value; }

#endif
