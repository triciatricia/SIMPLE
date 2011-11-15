PROG =	dummy

SRCS =	ecuyer_cote_mod.f90 random_beta_mod.f90 random_binomial_mod.f90 \
	random_chisq_mod.f90 random_exponential_mod.f90 random_f_mod.f90 \
	random_gamma_mod.f90 random_multinomial_mod.f90 \
	random_multivariate_normal_mod.f90 random_nc_chisq_mod.f90 \
	random_nc_f_mod.f90 random_negative_binomial_mod.f90 \
	random_normal_mod.f90 random_permutation_mod.f90 \
	random_poisson_mod.f90 random_standard_exponential_mod.f90 \
	random_standard_gamma_mod.f90 random_standard_normal_mod.f90 \
	random_standard_uniform_mod.f90 random_uniform_integer_mod.f90 \
	random_uniform_mod.f90 user_set_generator.f90

OBJS =	ecuyer_cote_mod.o random_beta_mod.o random_binomial_mod.o \
	random_chisq_mod.o random_exponential_mod.o random_f_mod.o \
	random_gamma_mod.o random_multinomial_mod.o \
	random_multivariate_normal_mod.o random_nc_chisq_mod.o \
	random_nc_f_mod.o random_negative_binomial_mod.o random_normal_mod.o \
	random_permutation_mod.o random_poisson_mod.o \
	random_standard_exponential_mod.o random_standard_gamma_mod.o \
	random_standard_normal_mod.o random_standard_uniform_mod.o \
	random_uniform_integer_mod.o random_uniform_mod.o user_set_generator.o

LIBS =	

CC = cc
CFLAGS = -O
FC = f77
FFLAGS = -O 
F90 = f95
F90FLAGS = -O -std
LDFLAGS = 

all: $(PROG)

$(PROG): $(OBJS)
	$(F90) $(LDFLAGS) -o $@ $(OBJS) $(LIBS)

clean:
	rm -f $(PROG) $(OBJS) *.mod

.SUFFIXES: $(SUFFIXES) .f90

.f90.o:
	$(F90) $(F90FLAGS) -c $<

random_beta_mod.o: random_standard_uniform_mod.o
random_binomial_mod.o: random_standard_uniform_mod.o
random_chisq_mod.o: random_standard_gamma_mod.o
random_exponential_mod.o: random_standard_exponential_mod.o
random_f_mod.o: random_standard_gamma_mod.o
random_gamma_mod.o: random_standard_gamma_mod.o
random_multinomial_mod.o: random_binomial_mod.o
random_multivariate_normal_mod.o: random_standard_normal_mod.o
random_nc_chisq_mod.o: random_standard_gamma_mod.o \
	random_standard_normal_mod.o
random_nc_f_mod.o: random_standard_gamma_mod.o random_standard_normal_mod.o
random_negative_binomial_mod.o: random_poisson_mod.o \
	random_standard_gamma_mod.o
random_normal_mod.o: random_standard_normal_mod.o
random_permutation_mod.o: random_uniform_integer_mod.o
random_poisson_mod.o: random_standard_exponential_mod.o \
	random_standard_normal_mod.o random_standard_uniform_mod.o
random_standard_exponential_mod.o: random_standard_uniform_mod.o
random_standard_gamma_mod.o: random_standard_exponential_mod.o \
	random_standard_normal_mod.o random_standard_uniform_mod.o
random_standard_normal_mod.o: random_standard_uniform_mod.o
random_standard_uniform_mod.o: ecuyer_cote_mod.o
random_uniform_integer_mod.o: ecuyer_cote_mod.o
random_uniform_mod.o: random_standard_uniform_mod.o
usr_set_generator.o: ecuyer_cote_mod.o
