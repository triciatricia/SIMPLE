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
/* Generated on Wed Jul 27 06:17:28 EDT 2011 */

#include "codelet-rdft.h"

#ifdef HAVE_FMA

/* Generated by: ../../../genfft/gen_hc2c.native -fma -reorder-insns -schedule-for-pipeline -compact -variables 4 -pipeline-latency 4 -n 16 -dit -name hc2cf_16 -include hc2cf.h */

/*
 * This function contains 174 FP additions, 100 FP multiplications,
 * (or, 104 additions, 30 multiplications, 70 fused multiply/add),
 * 97 stack variables, 3 constants, and 64 memory accesses
 */
#include "hc2cf.h"

static void hc2cf_16(R *Rp, R *Ip, R *Rm, R *Im, const R *W, stride rs, INT mb, INT me, INT ms)
{
     DK(KP923879532, +0.923879532511286756128183189396788286822416626);
     DK(KP414213562, +0.414213562373095048801688724209698078569671875);
     DK(KP707106781, +0.707106781186547524400844362104849039284835938);
     {
	  INT m;
	  for (m = mb, W = W + ((mb - 1) * 30); m < me; m = m + 1, Rp = Rp + ms, Ip = Ip + ms, Rm = Rm - ms, Im = Im - ms, W = W + 30, MAKE_VOLATILE_STRIDE(rs)) {
	       E T3G, T3F;
	       {
		    E T3z, T3o, T8, T1I, T2p, T35, T2r, T1s, T2w, T36, T2k, T1F, T3k, T1N, T3A;
		    E Tl, T1T, T2V, T1U, Tz, T29, T30, T2c, T11, TB, TE, T2h, T31, T2a, T1e;
		    E TC, T1X, TH, TK, TG, TD, TJ;
		    {
			 E Ta, Td, Tb, T1J, Tg, Tj, Tf, Tc, Ti;
			 {
			      E T1h, T1k, T1n, T2l, T1i, T1q, T1m, T1j, T1p;
			      {
				   E T1, T3n, T3, T6, T2, T5;
				   T1 = Rp[0];
				   T3n = Rm[0];
				   T3 = Rp[WS(rs, 4)];
				   T6 = Rm[WS(rs, 4)];
				   T2 = W[14];
				   T5 = W[15];
				   {
					E T3l, T4, T1g, T3m, T7;
					T1h = Ip[WS(rs, 7)];
					T1k = Im[WS(rs, 7)];
					T3l = T2 * T6;
					T4 = T2 * T3;
					T1g = W[28];
					T1n = Ip[WS(rs, 3)];
					T3m = FNMS(T5, T3, T3l);
					T7 = FMA(T5, T6, T4);
					T2l = T1g * T1k;
					T1i = T1g * T1h;
					T3z = T3n - T3m;
					T3o = T3m + T3n;
					T8 = T1 + T7;
					T1I = T1 - T7;
					T1q = Im[WS(rs, 3)];
					T1m = W[12];
				   }
				   T1j = W[29];
				   T1p = W[13];
			      }
			      {
				   E T1u, T1x, T1v, T2s, T1A, T1D, T1z, T1w, T1C;
				   {
					E T2m, T1l, T2o, T1r, T2n, T1o, T1t;
					T1u = Ip[WS(rs, 1)];
					T2n = T1m * T1q;
					T1o = T1m * T1n;
					T2m = FNMS(T1j, T1h, T2l);
					T1l = FMA(T1j, T1k, T1i);
					T2o = FNMS(T1p, T1n, T2n);
					T1r = FMA(T1p, T1q, T1o);
					T1x = Im[WS(rs, 1)];
					T1t = W[4];
					T2p = T2m - T2o;
					T35 = T2m + T2o;
					T2r = T1l - T1r;
					T1s = T1l + T1r;
					T1v = T1t * T1u;
					T2s = T1t * T1x;
				   }
				   T1A = Ip[WS(rs, 5)];
				   T1D = Im[WS(rs, 5)];
				   T1z = W[20];
				   T1w = W[5];
				   T1C = W[21];
				   {
					E T2t, T1y, T2v, T1E, T2u, T1B, T9;
					Ta = Rp[WS(rs, 2)];
					T2u = T1z * T1D;
					T1B = T1z * T1A;
					T2t = FNMS(T1w, T1u, T2s);
					T1y = FMA(T1w, T1x, T1v);
					T2v = FNMS(T1C, T1A, T2u);
					T1E = FMA(T1C, T1D, T1B);
					Td = Rm[WS(rs, 2)];
					T9 = W[6];
					T2w = T2t - T2v;
					T36 = T2t + T2v;
					T2k = T1E - T1y;
					T1F = T1y + T1E;
					Tb = T9 * Ta;
					T1J = T9 * Td;
				   }
				   Tg = Rp[WS(rs, 6)];
				   Tj = Rm[WS(rs, 6)];
				   Tf = W[22];
				   Tc = W[7];
				   Ti = W[23];
			      }
			 }
			 {
			      E TQ, TT, TR, T25, TW, TZ, TV, TS, TY;
			      {
				   E To, Tr, Tp, T1P, Tu, Tx, Tt, Tq, Tw;
				   {
					E T1K, Te, T1M, Tk, T1L, Th, Tn;
					To = Rp[WS(rs, 1)];
					T1L = Tf * Tj;
					Th = Tf * Tg;
					T1K = FNMS(Tc, Ta, T1J);
					Te = FMA(Tc, Td, Tb);
					T1M = FNMS(Ti, Tg, T1L);
					Tk = FMA(Ti, Tj, Th);
					Tr = Rm[WS(rs, 1)];
					Tn = W[2];
					T3k = T1K + T1M;
					T1N = T1K - T1M;
					T3A = Te - Tk;
					Tl = Te + Tk;
					Tp = Tn * To;
					T1P = Tn * Tr;
				   }
				   Tu = Rp[WS(rs, 5)];
				   Tx = Rm[WS(rs, 5)];
				   Tt = W[18];
				   Tq = W[3];
				   Tw = W[19];
				   {
					E T1Q, Ts, T1S, Ty, T1R, Tv, TP;
					TQ = Ip[0];
					T1R = Tt * Tx;
					Tv = Tt * Tu;
					T1Q = FNMS(Tq, To, T1P);
					Ts = FMA(Tq, Tr, Tp);
					T1S = FNMS(Tw, Tu, T1R);
					Ty = FMA(Tw, Tx, Tv);
					TT = Im[0];
					TP = W[0];
					T1T = T1Q - T1S;
					T2V = T1Q + T1S;
					T1U = Ts - Ty;
					Tz = Ts + Ty;
					TR = TP * TQ;
					T25 = TP * TT;
				   }
				   TW = Ip[WS(rs, 4)];
				   TZ = Im[WS(rs, 4)];
				   TV = W[16];
				   TS = W[1];
				   TY = W[17];
			      }
			      {
				   E T13, T16, T14, T2d, T19, T1c, T18, T15, T1b;
				   {
					E T26, TU, T28, T10, T27, TX, T12;
					T13 = Ip[WS(rs, 2)];
					T27 = TV * TZ;
					TX = TV * TW;
					T26 = FNMS(TS, TQ, T25);
					TU = FMA(TS, TT, TR);
					T28 = FNMS(TY, TW, T27);
					T10 = FMA(TY, TZ, TX);
					T16 = Im[WS(rs, 2)];
					T12 = W[8];
					T29 = T26 - T28;
					T30 = T26 + T28;
					T2c = TU - T10;
					T11 = TU + T10;
					T14 = T12 * T13;
					T2d = T12 * T16;
				   }
				   T19 = Ip[WS(rs, 6)];
				   T1c = Im[WS(rs, 6)];
				   T18 = W[24];
				   T15 = W[9];
				   T1b = W[25];
				   {
					E T2e, T17, T2g, T1d, T2f, T1a, TA;
					TB = Rp[WS(rs, 7)];
					T2f = T18 * T1c;
					T1a = T18 * T19;
					T2e = FNMS(T15, T13, T2d);
					T17 = FMA(T15, T16, T14);
					T2g = FNMS(T1b, T19, T2f);
					T1d = FMA(T1b, T1c, T1a);
					TE = Rm[WS(rs, 7)];
					TA = W[26];
					T2h = T2e - T2g;
					T31 = T2e + T2g;
					T2a = T17 - T1d;
					T1e = T17 + T1d;
					TC = TA * TB;
					T1X = TA * TE;
				   }
				   TH = Rp[WS(rs, 3)];
				   TK = Rm[WS(rs, 3)];
				   TG = W[10];
				   TD = W[27];
				   TJ = W[11];
			      }
			 }
		    }
		    {
			 E T2U, T3u, T2Z, T21, T1W, T34, T2X, T3f, T32, T3t, T1H, T3q, T3e, TO, T3g;
			 E T37, T3r, T3s, T3h, T3i;
			 {
			      E Tm, T1Y, TF, T20, TL, T3p, T1Z, TI;
			      T2U = T8 - Tl;
			      Tm = T8 + Tl;
			      T1Z = TG * TK;
			      TI = TG * TH;
			      T1Y = FNMS(TD, TB, T1X);
			      TF = FMA(TD, TE, TC);
			      T20 = FNMS(TJ, TH, T1Z);
			      TL = FMA(TJ, TK, TI);
			      T3p = T3k + T3o;
			      T3u = T3o - T3k;
			      {
				   E T1f, TM, T1G, T3j, T2W, TN;
				   T2Z = T11 - T1e;
				   T1f = T11 + T1e;
				   T21 = T1Y - T20;
				   T2W = T1Y + T20;
				   T1W = TF - TL;
				   TM = TF + TL;
				   T1G = T1s + T1F;
				   T34 = T1s - T1F;
				   T2X = T2V - T2W;
				   T3j = T2V + T2W;
				   T3f = T30 + T31;
				   T32 = T30 - T31;
				   T3t = TM - Tz;
				   TN = Tz + TM;
				   T3r = T1G - T1f;
				   T1H = T1f + T1G;
				   T3s = T3p - T3j;
				   T3q = T3j + T3p;
				   T3e = Tm - TN;
				   TO = Tm + TN;
				   T3g = T35 + T36;
				   T37 = T35 - T36;
			      }
			 }
			 Im[WS(rs, 3)] = T3r - T3s;
			 Ip[WS(rs, 4)] = T3r + T3s;
			 Rp[0] = TO + T1H;
			 Rm[WS(rs, 7)] = TO - T1H;
			 T3h = T3f - T3g;
			 T3i = T3f + T3g;
			 {
			      E T3a, T2Y, T3x, T3v, T3b, T33;
			      Ip[0] = T3i + T3q;
			      Im[WS(rs, 7)] = T3i - T3q;
			      Rp[WS(rs, 4)] = T3e + T3h;
			      Rm[WS(rs, 3)] = T3e - T3h;
			      T3a = T2U - T2X;
			      T2Y = T2U + T2X;
			      T3x = T3u - T3t;
			      T3v = T3t + T3u;
			      T3b = T32 - T2Z;
			      T33 = T2Z + T32;
			      {
				   E T2E, T1O, T3B, T3H, T2x, T2q, T3C, T23, T2S, T2O, T2K, T2J, T3I, T2H, T2B;
				   E T2j;
				   {
					E T2F, T1V, T22, T2G, T3c, T38;
					T2E = T1I + T1N;
					T1O = T1I - T1N;
					T3B = T3z - T3A;
					T3H = T3A + T3z;
					T3c = T34 + T37;
					T38 = T34 - T37;
					T2F = T1U + T1T;
					T1V = T1T - T1U;
					{
					     E T3d, T3w, T3y, T39;
					     T3d = T3b - T3c;
					     T3w = T3b + T3c;
					     T3y = T38 - T33;
					     T39 = T33 + T38;
					     Rp[WS(rs, 6)] = FMA(KP707106781, T3d, T3a);
					     Rm[WS(rs, 1)] = FNMS(KP707106781, T3d, T3a);
					     Ip[WS(rs, 2)] = FMA(KP707106781, T3w, T3v);
					     Im[WS(rs, 5)] = FMS(KP707106781, T3w, T3v);
					     Ip[WS(rs, 6)] = FMA(KP707106781, T3y, T3x);
					     Im[WS(rs, 1)] = FMS(KP707106781, T3y, T3x);
					     Rp[WS(rs, 2)] = FMA(KP707106781, T39, T2Y);
					     Rm[WS(rs, 5)] = FNMS(KP707106781, T39, T2Y);
					     T22 = T1W + T21;
					     T2G = T1W - T21;
					}
					{
					     E T2M, T2N, T2b, T2i;
					     T2x = T2r - T2w;
					     T2M = T2r + T2w;
					     T2N = T2p + T2k;
					     T2q = T2k - T2p;
					     T3C = T1V + T22;
					     T23 = T1V - T22;
					     T2S = FMA(KP414213562, T2M, T2N);
					     T2O = FNMS(KP414213562, T2N, T2M);
					     T2K = T29 - T2a;
					     T2b = T29 + T2a;
					     T2i = T2c - T2h;
					     T2J = T2c + T2h;
					     T3I = T2G - T2F;
					     T2H = T2F + T2G;
					     T2B = FNMS(KP414213562, T2b, T2i);
					     T2j = FMA(KP414213562, T2i, T2b);
					}
				   }
				   {
					E T2R, T2L, T3L, T3M;
					{
					     E T2A, T24, T2C, T2y, T3J, T3K, T2D, T2z;
					     T2A = FNMS(KP707106781, T23, T1O);
					     T24 = FMA(KP707106781, T23, T1O);
					     T2R = FNMS(KP414213562, T2J, T2K);
					     T2L = FMA(KP414213562, T2K, T2J);
					     T2C = FNMS(KP414213562, T2q, T2x);
					     T2y = FMA(KP414213562, T2x, T2q);
					     T3J = FMA(KP707106781, T3I, T3H);
					     T3L = FNMS(KP707106781, T3I, T3H);
					     T3K = T2C - T2B;
					     T2D = T2B + T2C;
					     T3M = T2y - T2j;
					     T2z = T2j + T2y;
					     Ip[WS(rs, 3)] = FMA(KP923879532, T3K, T3J);
					     Im[WS(rs, 4)] = FMS(KP923879532, T3K, T3J);
					     Rp[WS(rs, 3)] = FMA(KP923879532, T2z, T24);
					     Rm[WS(rs, 4)] = FNMS(KP923879532, T2z, T24);
					     Rm[0] = FMA(KP923879532, T2D, T2A);
					     Rp[WS(rs, 7)] = FNMS(KP923879532, T2D, T2A);
					}
					{
					     E T2Q, T3D, T3E, T2T, T2I, T2P;
					     T2Q = FNMS(KP707106781, T2H, T2E);
					     T2I = FMA(KP707106781, T2H, T2E);
					     T2P = T2L + T2O;
					     T3G = T2O - T2L;
					     T3F = FNMS(KP707106781, T3C, T3B);
					     T3D = FMA(KP707106781, T3C, T3B);
					     Ip[WS(rs, 7)] = FMA(KP923879532, T3M, T3L);
					     Im[0] = FMS(KP923879532, T3M, T3L);
					     Rp[WS(rs, 1)] = FMA(KP923879532, T2P, T2I);
					     Rm[WS(rs, 6)] = FNMS(KP923879532, T2P, T2I);
					     T3E = T2R + T2S;
					     T2T = T2R - T2S;
					     Ip[WS(rs, 1)] = FMA(KP923879532, T3E, T3D);
					     Im[WS(rs, 6)] = FMS(KP923879532, T3E, T3D);
					     Rp[WS(rs, 5)] = FMA(KP923879532, T2T, T2Q);
					     Rm[WS(rs, 2)] = FNMS(KP923879532, T2T, T2Q);
					}
				   }
			      }
			 }
		    }
	       }
	       Ip[WS(rs, 5)] = FMA(KP923879532, T3G, T3F);
	       Im[WS(rs, 2)] = FMS(KP923879532, T3G, T3F);
	  }
     }
}

static const tw_instr twinstr[] = {
     {TW_FULL, 1, 16},
     {TW_NEXT, 1, 0}
};

static const hc2c_desc desc = { 16, "hc2cf_16", twinstr, &GENUS, {104, 30, 70, 0} };

void X(codelet_hc2cf_16) (planner *p) {
     X(khc2c_register) (p, hc2cf_16, &desc, HC2C_VIA_RDFT);
}
#else				/* HAVE_FMA */

/* Generated by: ../../../genfft/gen_hc2c.native -compact -variables 4 -pipeline-latency 4 -n 16 -dit -name hc2cf_16 -include hc2cf.h */

/*
 * This function contains 174 FP additions, 84 FP multiplications,
 * (or, 136 additions, 46 multiplications, 38 fused multiply/add),
 * 52 stack variables, 3 constants, and 64 memory accesses
 */
#include "hc2cf.h"

static void hc2cf_16(R *Rp, R *Ip, R *Rm, R *Im, const R *W, stride rs, INT mb, INT me, INT ms)
{
     DK(KP382683432, +0.382683432365089771728459984030398866761344562);
     DK(KP923879532, +0.923879532511286756128183189396788286822416626);
     DK(KP707106781, +0.707106781186547524400844362104849039284835938);
     {
	  INT m;
	  for (m = mb, W = W + ((mb - 1) * 30); m < me; m = m + 1, Rp = Rp + ms, Ip = Ip + ms, Rm = Rm - ms, Im = Im - ms, W = W + 30, MAKE_VOLATILE_STRIDE(rs)) {
	       E T7, T37, T1t, T2U, Ti, T38, T1w, T2R, Tu, T2s, T1C, T2c, TF, T2t, T1H;
	       E T2d, T1f, T1q, T2B, T2C, T2D, T2E, T1Z, T2j, T24, T2k, TS, T13, T2w, T2x;
	       E T2y, T2z, T1O, T2g, T1T, T2h;
	       {
		    E T1, T2T, T6, T2S;
		    T1 = Rp[0];
		    T2T = Rm[0];
		    {
			 E T3, T5, T2, T4;
			 T3 = Rp[WS(rs, 4)];
			 T5 = Rm[WS(rs, 4)];
			 T2 = W[14];
			 T4 = W[15];
			 T6 = FMA(T2, T3, T4 * T5);
			 T2S = FNMS(T4, T3, T2 * T5);
		    }
		    T7 = T1 + T6;
		    T37 = T2T - T2S;
		    T1t = T1 - T6;
		    T2U = T2S + T2T;
	       }
	       {
		    E Tc, T1u, Th, T1v;
		    {
			 E T9, Tb, T8, Ta;
			 T9 = Rp[WS(rs, 2)];
			 Tb = Rm[WS(rs, 2)];
			 T8 = W[6];
			 Ta = W[7];
			 Tc = FMA(T8, T9, Ta * Tb);
			 T1u = FNMS(Ta, T9, T8 * Tb);
		    }
		    {
			 E Te, Tg, Td, Tf;
			 Te = Rp[WS(rs, 6)];
			 Tg = Rm[WS(rs, 6)];
			 Td = W[22];
			 Tf = W[23];
			 Th = FMA(Td, Te, Tf * Tg);
			 T1v = FNMS(Tf, Te, Td * Tg);
		    }
		    Ti = Tc + Th;
		    T38 = Tc - Th;
		    T1w = T1u - T1v;
		    T2R = T1u + T1v;
	       }
	       {
		    E To, T1y, Tt, T1z, T1A, T1B;
		    {
			 E Tl, Tn, Tk, Tm;
			 Tl = Rp[WS(rs, 1)];
			 Tn = Rm[WS(rs, 1)];
			 Tk = W[2];
			 Tm = W[3];
			 To = FMA(Tk, Tl, Tm * Tn);
			 T1y = FNMS(Tm, Tl, Tk * Tn);
		    }
		    {
			 E Tq, Ts, Tp, Tr;
			 Tq = Rp[WS(rs, 5)];
			 Ts = Rm[WS(rs, 5)];
			 Tp = W[18];
			 Tr = W[19];
			 Tt = FMA(Tp, Tq, Tr * Ts);
			 T1z = FNMS(Tr, Tq, Tp * Ts);
		    }
		    Tu = To + Tt;
		    T2s = T1y + T1z;
		    T1A = T1y - T1z;
		    T1B = To - Tt;
		    T1C = T1A - T1B;
		    T2c = T1B + T1A;
	       }
	       {
		    E Tz, T1E, TE, T1F, T1D, T1G;
		    {
			 E Tw, Ty, Tv, Tx;
			 Tw = Rp[WS(rs, 7)];
			 Ty = Rm[WS(rs, 7)];
			 Tv = W[26];
			 Tx = W[27];
			 Tz = FMA(Tv, Tw, Tx * Ty);
			 T1E = FNMS(Tx, Tw, Tv * Ty);
		    }
		    {
			 E TB, TD, TA, TC;
			 TB = Rp[WS(rs, 3)];
			 TD = Rm[WS(rs, 3)];
			 TA = W[10];
			 TC = W[11];
			 TE = FMA(TA, TB, TC * TD);
			 T1F = FNMS(TC, TB, TA * TD);
		    }
		    TF = Tz + TE;
		    T2t = T1E + T1F;
		    T1D = Tz - TE;
		    T1G = T1E - T1F;
		    T1H = T1D + T1G;
		    T2d = T1D - T1G;
	       }
	       {
		    E T19, T20, T1p, T1X, T1e, T21, T1k, T1W;
		    {
			 E T16, T18, T15, T17;
			 T16 = Ip[WS(rs, 7)];
			 T18 = Im[WS(rs, 7)];
			 T15 = W[28];
			 T17 = W[29];
			 T19 = FMA(T15, T16, T17 * T18);
			 T20 = FNMS(T17, T16, T15 * T18);
		    }
		    {
			 E T1m, T1o, T1l, T1n;
			 T1m = Ip[WS(rs, 5)];
			 T1o = Im[WS(rs, 5)];
			 T1l = W[20];
			 T1n = W[21];
			 T1p = FMA(T1l, T1m, T1n * T1o);
			 T1X = FNMS(T1n, T1m, T1l * T1o);
		    }
		    {
			 E T1b, T1d, T1a, T1c;
			 T1b = Ip[WS(rs, 3)];
			 T1d = Im[WS(rs, 3)];
			 T1a = W[12];
			 T1c = W[13];
			 T1e = FMA(T1a, T1b, T1c * T1d);
			 T21 = FNMS(T1c, T1b, T1a * T1d);
		    }
		    {
			 E T1h, T1j, T1g, T1i;
			 T1h = Ip[WS(rs, 1)];
			 T1j = Im[WS(rs, 1)];
			 T1g = W[4];
			 T1i = W[5];
			 T1k = FMA(T1g, T1h, T1i * T1j);
			 T1W = FNMS(T1i, T1h, T1g * T1j);
		    }
		    T1f = T19 + T1e;
		    T1q = T1k + T1p;
		    T2B = T1f - T1q;
		    T2C = T20 + T21;
		    T2D = T1W + T1X;
		    T2E = T2C - T2D;
		    {
			 E T1V, T1Y, T22, T23;
			 T1V = T19 - T1e;
			 T1Y = T1W - T1X;
			 T1Z = T1V - T1Y;
			 T2j = T1V + T1Y;
			 T22 = T20 - T21;
			 T23 = T1k - T1p;
			 T24 = T22 + T23;
			 T2k = T22 - T23;
		    }
	       }
	       {
		    E TM, T1K, T12, T1R, TR, T1L, TX, T1Q;
		    {
			 E TJ, TL, TI, TK;
			 TJ = Ip[0];
			 TL = Im[0];
			 TI = W[0];
			 TK = W[1];
			 TM = FMA(TI, TJ, TK * TL);
			 T1K = FNMS(TK, TJ, TI * TL);
		    }
		    {
			 E TZ, T11, TY, T10;
			 TZ = Ip[WS(rs, 6)];
			 T11 = Im[WS(rs, 6)];
			 TY = W[24];
			 T10 = W[25];
			 T12 = FMA(TY, TZ, T10 * T11);
			 T1R = FNMS(T10, TZ, TY * T11);
		    }
		    {
			 E TO, TQ, TN, TP;
			 TO = Ip[WS(rs, 4)];
			 TQ = Im[WS(rs, 4)];
			 TN = W[16];
			 TP = W[17];
			 TR = FMA(TN, TO, TP * TQ);
			 T1L = FNMS(TP, TO, TN * TQ);
		    }
		    {
			 E TU, TW, TT, TV;
			 TU = Ip[WS(rs, 2)];
			 TW = Im[WS(rs, 2)];
			 TT = W[8];
			 TV = W[9];
			 TX = FMA(TT, TU, TV * TW);
			 T1Q = FNMS(TV, TU, TT * TW);
		    }
		    TS = TM + TR;
		    T13 = TX + T12;
		    T2w = TS - T13;
		    T2x = T1K + T1L;
		    T2y = T1Q + T1R;
		    T2z = T2x - T2y;
		    {
			 E T1M, T1N, T1P, T1S;
			 T1M = T1K - T1L;
			 T1N = TX - T12;
			 T1O = T1M + T1N;
			 T2g = T1M - T1N;
			 T1P = TM - TR;
			 T1S = T1Q - T1R;
			 T1T = T1P - T1S;
			 T2h = T1P + T1S;
		    }
	       }
	       {
		    E T1J, T27, T3g, T3i, T26, T3h, T2a, T3d;
		    {
			 E T1x, T1I, T3e, T3f;
			 T1x = T1t - T1w;
			 T1I = KP707106781 * (T1C - T1H);
			 T1J = T1x + T1I;
			 T27 = T1x - T1I;
			 T3e = KP707106781 * (T2d - T2c);
			 T3f = T38 + T37;
			 T3g = T3e + T3f;
			 T3i = T3f - T3e;
		    }
		    {
			 E T1U, T25, T28, T29;
			 T1U = FMA(KP923879532, T1O, KP382683432 * T1T);
			 T25 = FNMS(KP923879532, T24, KP382683432 * T1Z);
			 T26 = T1U + T25;
			 T3h = T25 - T1U;
			 T28 = FNMS(KP923879532, T1T, KP382683432 * T1O);
			 T29 = FMA(KP382683432, T24, KP923879532 * T1Z);
			 T2a = T28 - T29;
			 T3d = T28 + T29;
		    }
		    Rm[WS(rs, 4)] = T1J - T26;
		    Im[WS(rs, 4)] = T3d - T3g;
		    Rp[WS(rs, 3)] = T1J + T26;
		    Ip[WS(rs, 3)] = T3d + T3g;
		    Rm[0] = T27 - T2a;
		    Im[0] = T3h - T3i;
		    Rp[WS(rs, 7)] = T27 + T2a;
		    Ip[WS(rs, 7)] = T3h + T3i;
	       }
	       {
		    E T2v, T2H, T32, T34, T2G, T33, T2K, T2Z;
		    {
			 E T2r, T2u, T30, T31;
			 T2r = T7 - Ti;
			 T2u = T2s - T2t;
			 T2v = T2r + T2u;
			 T2H = T2r - T2u;
			 T30 = TF - Tu;
			 T31 = T2U - T2R;
			 T32 = T30 + T31;
			 T34 = T31 - T30;
		    }
		    {
			 E T2A, T2F, T2I, T2J;
			 T2A = T2w + T2z;
			 T2F = T2B - T2E;
			 T2G = KP707106781 * (T2A + T2F);
			 T33 = KP707106781 * (T2F - T2A);
			 T2I = T2z - T2w;
			 T2J = T2B + T2E;
			 T2K = KP707106781 * (T2I - T2J);
			 T2Z = KP707106781 * (T2I + T2J);
		    }
		    Rm[WS(rs, 5)] = T2v - T2G;
		    Im[WS(rs, 5)] = T2Z - T32;
		    Rp[WS(rs, 2)] = T2v + T2G;
		    Ip[WS(rs, 2)] = T2Z + T32;
		    Rm[WS(rs, 1)] = T2H - T2K;
		    Im[WS(rs, 1)] = T33 - T34;
		    Rp[WS(rs, 6)] = T2H + T2K;
		    Ip[WS(rs, 6)] = T33 + T34;
	       }
	       {
		    E T2f, T2n, T3a, T3c, T2m, T3b, T2q, T35;
		    {
			 E T2b, T2e, T36, T39;
			 T2b = T1t + T1w;
			 T2e = KP707106781 * (T2c + T2d);
			 T2f = T2b + T2e;
			 T2n = T2b - T2e;
			 T36 = KP707106781 * (T1C + T1H);
			 T39 = T37 - T38;
			 T3a = T36 + T39;
			 T3c = T39 - T36;
		    }
		    {
			 E T2i, T2l, T2o, T2p;
			 T2i = FMA(KP382683432, T2g, KP923879532 * T2h);
			 T2l = FNMS(KP382683432, T2k, KP923879532 * T2j);
			 T2m = T2i + T2l;
			 T3b = T2l - T2i;
			 T2o = FNMS(KP382683432, T2h, KP923879532 * T2g);
			 T2p = FMA(KP923879532, T2k, KP382683432 * T2j);
			 T2q = T2o - T2p;
			 T35 = T2o + T2p;
		    }
		    Rm[WS(rs, 6)] = T2f - T2m;
		    Im[WS(rs, 6)] = T35 - T3a;
		    Rp[WS(rs, 1)] = T2f + T2m;
		    Ip[WS(rs, 1)] = T35 + T3a;
		    Rm[WS(rs, 2)] = T2n - T2q;
		    Im[WS(rs, 2)] = T3b - T3c;
		    Rp[WS(rs, 5)] = T2n + T2q;
		    Ip[WS(rs, 5)] = T3b + T3c;
	       }
	       {
		    E TH, T2L, T2W, T2Y, T1s, T2X, T2O, T2P;
		    {
			 E Tj, TG, T2Q, T2V;
			 Tj = T7 + Ti;
			 TG = Tu + TF;
			 TH = Tj + TG;
			 T2L = Tj - TG;
			 T2Q = T2s + T2t;
			 T2V = T2R + T2U;
			 T2W = T2Q + T2V;
			 T2Y = T2V - T2Q;
		    }
		    {
			 E T14, T1r, T2M, T2N;
			 T14 = TS + T13;
			 T1r = T1f + T1q;
			 T1s = T14 + T1r;
			 T2X = T1r - T14;
			 T2M = T2x + T2y;
			 T2N = T2C + T2D;
			 T2O = T2M - T2N;
			 T2P = T2M + T2N;
		    }
		    Rm[WS(rs, 7)] = TH - T1s;
		    Im[WS(rs, 7)] = T2P - T2W;
		    Rp[0] = TH + T1s;
		    Ip[0] = T2P + T2W;
		    Rm[WS(rs, 3)] = T2L - T2O;
		    Im[WS(rs, 3)] = T2X - T2Y;
		    Rp[WS(rs, 4)] = T2L + T2O;
		    Ip[WS(rs, 4)] = T2X + T2Y;
	       }
	  }
     }
}

static const tw_instr twinstr[] = {
     {TW_FULL, 1, 16},
     {TW_NEXT, 1, 0}
};

static const hc2c_desc desc = { 16, "hc2cf_16", twinstr, &GENUS, {136, 46, 38, 0} };

void X(codelet_hc2cf_16) (planner *p) {
     X(khc2c_register) (p, hc2cf_16, &desc, HC2C_VIA_RDFT);
}
#endif				/* HAVE_FMA */
