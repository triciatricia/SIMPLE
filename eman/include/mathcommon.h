int yylex();

struct Term {
	short type;
	union {
		double value;
		double *var;
		Term *exp1;
		double (*fn1)(double val);
		double (*fn2)(double val,double val2);
		double (*fn)(int n,double *vals);
	};
	union {
		double value2;
		Term *exp2;
	};
	Term *exp3;
};

struct M_OPS {
	char name[10];
	short nparm;
	union {
	double (*fn1)(double parm);
	double (*fn2)(double parm1,double parm2);
	double (*fnn)(int n,double *parm);
	};
};
