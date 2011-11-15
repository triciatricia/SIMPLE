#ifndef LISTH
#define LISTH


class List 
{
private:
	void **items;
	int n,na;

public:
	List();
	~List();
	//void insertIntAt(int i,int n);
	//void addInt(int i);
	//int replaceIntAt(int n, int i);
	//int intAt(int n);
	void insertObjectAt(void *obj,int n);
	void swap(int index1,int index2);
	void addObject(void *obj);
	void removeObject(void *obj);
	void *removeObjectAt(int n);
	void *objectAt(int n);
	void *replaceObjectAt(int n, void *nw);
	void *replaceObject(void *obj, void *n);
	void addObjects(List *list);
	void removeObjects(List *list);
	int count();
	int indexOf(void *obj);
	void empty();
};


//inline void List::insertIntAt(int i,int n) { insertObjectAt((void *)i,n); }
//inline void List::addInt(int i) { addObject((void *)i); }
//inline int List::replaceIntAt(int n,int i) { return (int)replaceObjectAt(n,(void *)i); } 
//inline int List::intAt(int i) { return (int)objectAt(i); }
#endif
