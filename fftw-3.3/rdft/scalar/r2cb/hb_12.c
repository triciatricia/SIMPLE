/*
 * Copyright (c) 2003, 2007-11 Matteo Frigo
 * Copyright (c) 2003, 2007-11 Massachusetts Institute of Technology
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */

/* This file was automatically generated --- DO NOT EDIT */
/* Generated on Wed Jul 27 06:18:38 EDT 2011 */

#include "codelet-rdft.h"

#ifdef HAVE_FMA

/* Generated by: ../../../genfft/gen_hc2hc.native -fma -reorder-insns -schedule-for-pipeline -compact -variables 4 -pipeline-latency 4 -sign 1 -n 12 -dif -name hb_12 -include hb.h */

/*
 * This function contains 118 FP additions, 68 FP multiplications,
 * (or, 72 additions, 22 multiplications, 46 fused multiply/add),
 * 64 stack variables, 2 constants, and 48 memory accesses
 */
#include "hb.h"

static void hb_12(R *cr, R *ci, const R *W, stride rs, INT mb, INT me, INT ms)
{
     DK(KP866025403, +0.866025403784438646763723170752936183471402627);
     DK(KP500000000, +0.500000000000000000000000000000000000000000000);
     {
	  INT m;
	  for (m = mb, W = W + ((mb - 1) * 22); m < me; m = m + 1, cr = cr + ms, ci = ci - ms, W = W + 22, MAKE_VOLATILE_STRIDE(rs)) {
	       E T1U, T1X, T1W, T1Y, T1V;
	       {
		    E T18, T20, T2a, T1s, T21, T1b, T29, T1p, TO, T11, To, Tb, Tg, T23, T1f;
		    E Ty, Tl, Tt, T1z, T2d, T1i, T24, T1w, T2c;
		    {
			 E T5, TN, Ta, TI;
			 {
			      E T1, TE, TM, T6, TJ, T1o, T4, T17, TH, TK, T7, T8;
			      T1 = cr[0];
			      TE = ci[WS(rs, 11)];
			      TM = cr[WS(rs, 6)];
			      T6 = ci[WS(rs, 5)];
			      {
				   E T2, T3, TF, TG;
				   T2 = cr[WS(rs, 4)];
				   T3 = ci[WS(rs, 3)];
				   TF = ci[WS(rs, 7)];
				   TG = cr[WS(rs, 8)];
				   TJ = ci[WS(rs, 9)];
				   T1o = T2 - T3;
				   T4 = T2 + T3;
				   T17 = TF + TG;
				   TH = TF - TG;
				   TK = cr[WS(rs, 10)];
				   T7 = ci[WS(rs, 1)];
				   T8 = cr[WS(rs, 2)];
			      }
			      {
				   E T1a, T1r, T1q, T19, TL, T9, T16, T1n;
				   T5 = T1 + T4;
				   T16 = FNMS(KP500000000, T4, T1);
				   T1a = TJ + TK;
				   TL = TJ - TK;
				   T1r = T7 - T8;
				   T9 = T7 + T8;
				   T18 = FNMS(KP866025403, T17, T16);
				   T20 = FMA(KP866025403, T17, T16);
				   T1q = FMA(KP500000000, TL, TM);
				   TN = TL - TM;
				   Ta = T6 + T9;
				   T19 = FNMS(KP500000000, T9, T6);
				   T1n = FNMS(KP500000000, TH, TE);
				   TI = TE + TH;
				   T2a = FMA(KP866025403, T1r, T1q);
				   T1s = FNMS(KP866025403, T1r, T1q);
				   T21 = FNMS(KP866025403, T1a, T19);
				   T1b = FMA(KP866025403, T1a, T19);
				   T29 = FNMS(KP866025403, T1o, T1n);
				   T1p = FMA(KP866025403, T1o, T1n);
			      }
			 }
			 {
			      E Tc, Tp, Tx, Th, Tu, Tf, T1v, Ts, T1e, Tv, Ti, Tj;
			      Tc = cr[WS(rs, 3)];
			      TO = TI - TN;
			      T11 = TI + TN;
			      Tp = ci[WS(rs, 8)];
			      To = T5 - Ta;
			      Tb = T5 + Ta;
			      Tx = cr[WS(rs, 9)];
			      Th = ci[WS(rs, 2)];
			      {
				   E Td, Te, Tq, Tr;
				   Td = ci[WS(rs, 4)];
				   Te = ci[0];
				   Tq = cr[WS(rs, 7)];
				   Tr = cr[WS(rs, 11)];
				   Tu = ci[WS(rs, 10)];
				   Tf = Td + Te;
				   T1v = Td - Te;
				   Ts = Tq + Tr;
				   T1e = Tq - Tr;
				   Tv = ci[WS(rs, 6)];
				   Ti = cr[WS(rs, 1)];
				   Tj = cr[WS(rs, 5)];
			      }
			      {
				   E T1h, T1y, T1x, T1g, Tw, Tk, T1d, T1u;
				   T1d = FNMS(KP500000000, Tf, Tc);
				   Tg = Tc + Tf;
				   Tw = Tu + Tv;
				   T1h = Tv - Tu;
				   Tk = Ti + Tj;
				   T1y = Ti - Tj;
				   T23 = FNMS(KP866025403, T1e, T1d);
				   T1f = FMA(KP866025403, T1e, T1d);
				   Ty = Tw - Tx;
				   T1x = FMA(KP500000000, Tw, Tx);
				   T1g = FNMS(KP500000000, Tk, Th);
				   Tl = Th + Tk;
				   Tt = Tp - Ts;
				   T1u = FMA(KP500000000, Ts, Tp);
				   T1z = FNMS(KP866025403, T1y, T1x);
				   T2d = FMA(KP866025403, T1y, T1x);
				   T1i = FMA(KP866025403, T1h, T1g);
				   T24 = FNMS(KP866025403, T1h, T1g);
				   T1w = FMA(KP866025403, T1v, T1u);
				   T2c = FNMS(KP866025403, T1v, T1u);
			      }
			 }
		    }
		    {
			 E TY, T13, TX, T10;
			 {
			      E Tn, T12, TC, Tm, TD, TS, TA, Tz;
			      Tn = W[16];
			      T12 = Tt + Ty;
			      Tz = Tt - Ty;
			      TC = W[17];
			      Tm = Tg + Tl;
			      TD = Tg - Tl;
			      TS = To + Tz;
			      TA = To - Tz;
			      {
				   E TV, TU, TW, TT;
				   {
					E TQ, TR, TP, TB;
					TV = TO - TD;
					TP = TD + TO;
					cr[0] = Tb + Tm;
					TB = Tn * TA;
					TQ = Tn * TP;
					TR = W[4];
					cr[WS(rs, 9)] = FNMS(TC, TP, TB);
					TU = W[5];
					ci[WS(rs, 9)] = FMA(TC, TA, TQ);
					TW = TR * TV;
					TT = TR * TS;
				   }
				   ci[WS(rs, 3)] = FMA(TU, TS, TW);
				   cr[WS(rs, 3)] = FNMS(TU, TV, TT);
				   TY = Tb - Tm;
				   T13 = T11 - T12;
				   TX = W[10];
				   T10 = W[11];
				   ci[0] = T11 + T12;
			      }
			 }
			 {
			      E T1K, T1Q, T1P, T1L, T2o, T2u, T2t, T2p;
			      {
				   E T1E, T1D, T1H, T1F, T1G, T1t, T1k, T1A;
				   {
					E T1c, TZ, T14, T1j;
					T1K = T18 - T1b;
					T1c = T18 + T1b;
					TZ = TX * TY;
					T14 = T10 * TY;
					T1j = T1f + T1i;
					T1Q = T1f - T1i;
					T1P = T1p + T1s;
					T1t = T1p - T1s;
					cr[WS(rs, 6)] = FNMS(T10, T13, TZ);
					ci[WS(rs, 6)] = FMA(TX, T13, T14);
					T1E = T1c + T1j;
					T1k = T1c - T1j;
					T1A = T1w - T1z;
					T1L = T1w + T1z;
				   }
				   {
					E T15, T1m, T1B, T1l, T1C;
					T15 = W[18];
					T1m = W[19];
					T1D = W[6];
					T1H = T1t + T1A;
					T1B = T1t - T1A;
					T1l = T15 * T1k;
					T1C = T1m * T1k;
					T1F = T1D * T1E;
					T1G = W[7];
					cr[WS(rs, 10)] = FNMS(T1m, T1B, T1l);
					ci[WS(rs, 10)] = FMA(T15, T1B, T1C);
				   }
				   {
					E T26, T2i, T2l, T2f, T1Z, T28;
					{
					     E T22, T1I, T25, T2b, T2e;
					     T22 = T20 + T21;
					     T2o = T20 - T21;
					     cr[WS(rs, 4)] = FNMS(T1G, T1H, T1F);
					     T1I = T1G * T1E;
					     T2u = T23 - T24;
					     T25 = T23 + T24;
					     T2b = T29 - T2a;
					     T2t = T29 + T2a;
					     T2p = T2c + T2d;
					     T2e = T2c - T2d;
					     ci[WS(rs, 4)] = FMA(T1D, T1H, T1I);
					     T26 = T22 - T25;
					     T2i = T22 + T25;
					     T2l = T2b + T2e;
					     T2f = T2b - T2e;
					}
					T1Z = W[2];
					T28 = W[3];
					{
					     E T2h, T2k, T27, T2g, T2j, T2m;
					     T2h = W[14];
					     T2k = W[15];
					     T27 = T1Z * T26;
					     T2g = T28 * T26;
					     T2j = T2h * T2i;
					     T2m = T2k * T2i;
					     cr[WS(rs, 2)] = FNMS(T28, T2f, T27);
					     ci[WS(rs, 2)] = FMA(T1Z, T2f, T2g);
					     cr[WS(rs, 8)] = FNMS(T2k, T2l, T2j);
					     ci[WS(rs, 8)] = FMA(T2h, T2l, T2m);
					}
				   }
			      }
			      {
				   E T2y, T2B, T2A, T2C, T2z;
				   {
					E T2n, T2q, T2v, T2s, T2r, T2x, T2w;
					T2n = W[8];
					T2y = T2o + T2p;
					T2q = T2o - T2p;
					T2B = T2t - T2u;
					T2v = T2t + T2u;
					T2s = W[9];
					T2r = T2n * T2q;
					T2x = W[20];
					T2w = T2n * T2v;
					T2A = W[21];
					cr[WS(rs, 5)] = FNMS(T2s, T2v, T2r);
					T2C = T2x * T2B;
					T2z = T2x * T2y;
					ci[WS(rs, 5)] = FMA(T2s, T2q, T2w);
				   }
				   ci[WS(rs, 11)] = FMA(T2A, T2y, T2C);
				   cr[WS(rs, 11)] = FNMS(T2A, T2B, T2z);
				   {
					E T1J, T1M, T1R, T1O, T1N, T1T, T1S;
					T1J = W[0];
					T1U = T1K + T1L;
					T1M = T1K - T1L;
					T1X = T1P - T1Q;
					T1R = T1P + T1Q;
					T1O = W[1];
					T1N = T1J * T1M;
					T1T = W[12];
					T1S = T1J * T1R;
					T1W = W[13];
					cr[WS(rs, 1)] = FNMS(T1O, T1R, T1N);
					T1Y = T1T * T1X;
					T1V = T1T * T1U;
					ci[WS(rs, 1)] = FMA(T1O, T1M, T1S);
				   }
			      }
			 }
		    }
	       }
	       ci[WS(rs, 7)] = FMA(T1W, T1U, T1Y);
	       cr[WS(rs, 7)] = FNMS(T1W, T1X, T1V);
	  }
     }
}

static const tw_instr twinstr[] = {
     {TW_FULL, 1, 12},
     {TW_NEXT, 1, 0}
};

static const hc2hc_desc desc = { 12, "hb_12", twinstr, &GENUS, {72, 22, 46, 0} };

void X(codelet_hb_12) (planner *p) {
     X(khc2hc_register) (p, hb_12, &desc);
}
#else				/* HAVE_FMA */

/* Generated by: ../../../genfft/gen_hc2hc.native -compact -variables 4 -pipeline-latency 4 -sign 1 -n 12 -dif -name hb_12 -include hb.h */

/*
 * This function contains 118 FP additions, 60 FP multiplications,
 * (or, 88 additions, 30 multiplications, 30 fused multiply/add),
 * 39 stack variables, 2 constants, and 48 memory accesses
 */
#include "hb.h"

static void hb_12(R *cr, R *ci, const R *W, stride rs, INT mb, INT me, INT ms)
{
     DK(KP500000000, +0.500000000000000000000000000000000000000000000);
     DK(KP866025403, +0.866025403784438646763723170752936183471402627);
     {
	  INT m;
	  for (m = mb, W = W + ((mb - 1) * 22); m < me; m = m + 1, cr = cr + ms, ci = ci - ms, W = W + 22, MAKE_VOLATILE_STRIDE(rs)) {
	       E T5, TH, T12, T1M, T1i, T1U, Tg, Tt, T19, T1X, T1p, T1P, Ta, TM, T15;
	       E T1N, T1l, T1V, Tl, Ty, T1c, T1Y, T1s, T1Q;
	       {
		    E T1, TD, T4, T1g, TG, T11, T10, T1h;
		    T1 = cr[0];
		    TD = ci[WS(rs, 11)];
		    {
			 E T2, T3, TE, TF;
			 T2 = cr[WS(rs, 4)];
			 T3 = ci[WS(rs, 3)];
			 T4 = T2 + T3;
			 T1g = KP866025403 * (T2 - T3);
			 TE = ci[WS(rs, 7)];
			 TF = cr[WS(rs, 8)];
			 TG = TE - TF;
			 T11 = KP866025403 * (TE + TF);
		    }
		    T5 = T1 + T4;
		    TH = TD + TG;
		    T10 = FNMS(KP500000000, T4, T1);
		    T12 = T10 - T11;
		    T1M = T10 + T11;
		    T1h = FNMS(KP500000000, TG, TD);
		    T1i = T1g + T1h;
		    T1U = T1h - T1g;
	       }
	       {
		    E Tc, Tp, Tf, T17, Ts, T1o, T18, T1n;
		    Tc = cr[WS(rs, 3)];
		    Tp = ci[WS(rs, 8)];
		    {
			 E Td, Te, Tq, Tr;
			 Td = ci[WS(rs, 4)];
			 Te = ci[0];
			 Tf = Td + Te;
			 T17 = KP866025403 * (Td - Te);
			 Tq = cr[WS(rs, 7)];
			 Tr = cr[WS(rs, 11)];
			 Ts = Tq + Tr;
			 T1o = KP866025403 * (Tq - Tr);
		    }
		    Tg = Tc + Tf;
		    Tt = Tp - Ts;
		    T18 = FMA(KP500000000, Ts, Tp);
		    T19 = T17 + T18;
		    T1X = T18 - T17;
		    T1n = FNMS(KP500000000, Tf, Tc);
		    T1p = T1n + T1o;
		    T1P = T1n - T1o;
	       }
	       {
		    E T6, TL, T9, T1j, TK, T14, T13, T1k;
		    T6 = ci[WS(rs, 5)];
		    TL = cr[WS(rs, 6)];
		    {
			 E T7, T8, TI, TJ;
			 T7 = ci[WS(rs, 1)];
			 T8 = cr[WS(rs, 2)];
			 T9 = T7 + T8;
			 T1j = KP866025403 * (T7 - T8);
			 TI = ci[WS(rs, 9)];
			 TJ = cr[WS(rs, 10)];
			 TK = TI - TJ;
			 T14 = KP866025403 * (TI + TJ);
		    }
		    Ta = T6 + T9;
		    TM = TK - TL;
		    T13 = FNMS(KP500000000, T9, T6);
		    T15 = T13 + T14;
		    T1N = T13 - T14;
		    T1k = FMA(KP500000000, TK, TL);
		    T1l = T1j - T1k;
		    T1V = T1j + T1k;
	       }
	       {
		    E Th, Tx, Tk, T1a, Tw, T1r, T1b, T1q;
		    Th = ci[WS(rs, 2)];
		    Tx = cr[WS(rs, 9)];
		    {
			 E Ti, Tj, Tu, Tv;
			 Ti = cr[WS(rs, 1)];
			 Tj = cr[WS(rs, 5)];
			 Tk = Ti + Tj;
			 T1a = KP866025403 * (Ti - Tj);
			 Tu = ci[WS(rs, 10)];
			 Tv = ci[WS(rs, 6)];
			 Tw = Tu + Tv;
			 T1r = KP866025403 * (Tv - Tu);
		    }
		    Tl = Th + Tk;
		    Ty = Tw - Tx;
		    T1b = FMA(KP500000000, Tw, Tx);
		    T1c = T1a - T1b;
		    T1Y = T1a + T1b;
		    T1q = FNMS(KP500000000, Tk, Th);
		    T1s = T1q + T1r;
		    T1Q = T1q - T1r;
	       }
	       {
		    E Tb, Tm, TU, TW, TX, TY, TT, TV;
		    Tb = T5 + Ta;
		    Tm = Tg + Tl;
		    TU = Tb - Tm;
		    TW = TH + TM;
		    TX = Tt + Ty;
		    TY = TW - TX;
		    cr[0] = Tb + Tm;
		    ci[0] = TW + TX;
		    TT = W[10];
		    TV = W[11];
		    cr[WS(rs, 6)] = FNMS(TV, TY, TT * TU);
		    ci[WS(rs, 6)] = FMA(TV, TU, TT * TY);
	       }
	       {
		    E TA, TQ, TO, TS;
		    {
			 E To, Tz, TC, TN;
			 To = T5 - Ta;
			 Tz = Tt - Ty;
			 TA = To - Tz;
			 TQ = To + Tz;
			 TC = Tg - Tl;
			 TN = TH - TM;
			 TO = TC + TN;
			 TS = TN - TC;
		    }
		    {
			 E Tn, TB, TP, TR;
			 Tn = W[16];
			 TB = W[17];
			 cr[WS(rs, 9)] = FNMS(TB, TO, Tn * TA);
			 ci[WS(rs, 9)] = FMA(Tn, TO, TB * TA);
			 TP = W[4];
			 TR = W[5];
			 cr[WS(rs, 3)] = FNMS(TR, TS, TP * TQ);
			 ci[WS(rs, 3)] = FMA(TP, TS, TR * TQ);
		    }
	       }
	       {
		    E T28, T2e, T2c, T2g;
		    {
			 E T26, T27, T2a, T2b;
			 T26 = T1M - T1N;
			 T27 = T1X + T1Y;
			 T28 = T26 - T27;
			 T2e = T26 + T27;
			 T2a = T1U + T1V;
			 T2b = T1P - T1Q;
			 T2c = T2a + T2b;
			 T2g = T2a - T2b;
		    }
		    {
			 E T25, T29, T2d, T2f;
			 T25 = W[8];
			 T29 = W[9];
			 cr[WS(rs, 5)] = FNMS(T29, T2c, T25 * T28);
			 ci[WS(rs, 5)] = FMA(T25, T2c, T29 * T28);
			 T2d = W[20];
			 T2f = W[21];
			 cr[WS(rs, 11)] = FNMS(T2f, T2g, T2d * T2e);
			 ci[WS(rs, 11)] = FMA(T2d, T2g, T2f * T2e);
		    }
	       }
	       {
		    E T1S, T22, T20, T24;
		    {
			 E T1O, T1R, T1W, T1Z;
			 T1O = T1M + T1N;
			 T1R = T1P + T1Q;
			 T1S = T1O - T1R;
			 T22 = T1O + T1R;
			 T1W = T1U - T1V;
			 T1Z = T1X - T1Y;
			 T20 = T1W - T1Z;
			 T24 = T1W + T1Z;
		    }
		    {
			 E T1L, T1T, T21, T23;
			 T1L = W[2];
			 T1T = W[3];
			 cr[WS(rs, 2)] = FNMS(T1T, T20, T1L * T1S);
			 ci[WS(rs, 2)] = FMA(T1T, T1S, T1L * T20);
			 T21 = W[14];
			 T23 = W[15];
			 cr[WS(rs, 8)] = FNMS(T23, T24, T21 * T22);
			 ci[WS(rs, 8)] = FMA(T23, T22, T21 * T24);
		    }
	       }
	       {
		    E T1C, T1I, T1G, T1K;
		    {
			 E T1A, T1B, T1E, T1F;
			 T1A = T12 + T15;
			 T1B = T1p + T1s;
			 T1C = T1A - T1B;
			 T1I = T1A + T1B;
			 T1E = T1i + T1l;
			 T1F = T19 + T1c;
			 T1G = T1E - T1F;
			 T1K = T1E + T1F;
		    }
		    {
			 E T1z, T1D, T1H, T1J;
			 T1z = W[18];
			 T1D = W[19];
			 cr[WS(rs, 10)] = FNMS(T1D, T1G, T1z * T1C);
			 ci[WS(rs, 10)] = FMA(T1D, T1C, T1z * T1G);
			 T1H = W[6];
			 T1J = W[7];
			 cr[WS(rs, 4)] = FNMS(T1J, T1K, T1H * T1I);
			 ci[WS(rs, 4)] = FMA(T1J, T1I, T1H * T1K);
		    }
	       }
	       {
		    E T1e, T1w, T1u, T1y;
		    {
			 E T16, T1d, T1m, T1t;
			 T16 = T12 - T15;
			 T1d = T19 - T1c;
			 T1e = T16 - T1d;
			 T1w = T16 + T1d;
			 T1m = T1i - T1l;
			 T1t = T1p - T1s;
			 T1u = T1m + T1t;
			 T1y = T1m - T1t;
		    }
		    {
			 E TZ, T1f, T1v, T1x;
			 TZ = W[0];
			 T1f = W[1];
			 cr[WS(rs, 1)] = FNMS(T1f, T1u, TZ * T1e);
			 ci[WS(rs, 1)] = FMA(TZ, T1u, T1f * T1e);
			 T1v = W[12];
			 T1x = W[13];
			 cr[WS(rs, 7)] = FNMS(T1x, T1y, T1v * T1w);
			 ci[WS(rs, 7)] = FMA(T1v, T1y, T1x * T1w);
		    }
	       }
	  }
     }
}

static const tw_instr twinstr[] = {
     {TW_FULL, 1, 12},
     {TW_NEXT, 1, 0}
};

static const hc2hc_desc desc = { 12, "hb_12", twinstr, &GENUS, {88, 30, 30, 0} };

void X(codelet_hb_12) (planner *p) {
     X(khc2hc_register) (p, hb_12, &desc);
}
#endif				/* HAVE_FMA */
