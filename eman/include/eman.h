// globals for queues and data i/o
extern FILE *rtcom,*bgcom;		// fifos for reading commands from external programs
extern struct DATAOUT *share;	// shared memory segment for output to ext pgm
extern int bgpid;
extern List *dlist;

