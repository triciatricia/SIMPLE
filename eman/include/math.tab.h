#ifndef BISON_MATH_TAB_H
# define BISON_MATH_TAB_H

#ifndef YYSTYPE
typedef union { Term *value; } yystype;
# define YYSTYPE yystype
# define YYSTYPE_IS_TRIVIAL 1
#endif
# define	E_ERROR	257
# define	E_VAR	258
# define	E_FN	259
# define	E_FN2	260
# define	E_FNN	261
# define	E_NUMBER	262
# define	E_UMINUS	263


extern YYSTYPE mathlval;

#endif /* not BISON_MATH_TAB_H */
