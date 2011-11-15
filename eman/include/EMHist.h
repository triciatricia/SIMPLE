#ifndef EMHISTH
#define EMHISTH

#include <ctime>

struct EMHist {
long id;
int ppid;
int type;
time_t etime;
time_t fintime;
char *file;
char *info;
char *command;
char *tstr;
char *rtstr;
char *dir;

EMHist(char *parse=NULL);
~EMHist();

void parse(const char *parse);
void setDir(const char *dir);
void setFinTime(time_t tm);
char *getDir();

private:
char *Command();
};


#endif
