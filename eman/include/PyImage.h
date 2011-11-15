#ifndef _h_pyimage_h__
#define _h_pyimage_h__

#include "config.h"
#ifdef GUI

#include <qwidget.h>
#include "Image.h"
#include "ImageMx.h"

class QApplication;
class PyEMData;

class PyQApplication
{
public:
    PyQApplication();
    PyQApplication(int i);
    ~PyQApplication();
    
    int exec();
    
private:
    QApplication* app;
};

class PyQWidget : public QWidget {
public:
    PyQWidget(PyQWidget* parent = 0, const char* name = 0);
    PyQWidget(const PyQWidget& qw);
    ~PyQWidget();
};


class PyImage : public Image {
public:
    PyImage(PyQWidget* parent = 0, const char* name = 0);
    PyImage(const PyImage& img);
    ~PyImage();

    //PyEMData* py_getData();
};

class PyImageMx : public ImageMx {
public:
    PyImageMx(PyQWidget* parent = 0, const char* name = 0);
    PyImageMx(const PyImageMx& img);
    ~PyImageMx();
};

#endif

#endif
