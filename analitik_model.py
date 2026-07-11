# -*- coding: utf-8 -*-
"""
Ag/MoS2/p-Si/Al MIS Schottky diyot - analitik karanlık I-V modeli
Termiyonik emisyon (TE) + seri direnc (Lambert-W cozumu) + MoS2 arayuzey
tabakasinin tunelleme zayiflatmasi.

MIS teorisi: I = A A* T^2 exp(-sqrt(chi_t)*delta) exp(-q phi_b / kT)
                 * [exp(q(V - I Rs)/(n k T)) - 1]
  chi_t : ortalama tunel bariyeri (eV), delta : MoS2 kalinligi (Angstrom)
  (Card & Rhoderick 1971 yaklasimi; alpha ~ 1 eV^-1/2 A^-1 varsayimi)

Cikti: tez-simulasyon/analitik_iv.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import lambertw

# --- sabitler ---
q = 1.602176634e-19      # C
kB = 8.617333262e-5      # eV/K
T = 300.0                # K
kT = kB * T              # eV

# --- cihaz parametreleri (parametreler.md ile tutarli) ---
A_star = 32.0            # A cm^-2 K^-2  (p-Si, desik)
area = 7.85e-3           # cm^2 (1 mm cap)
phi_b0 = 0.70            # eV, Ag/p-Si efektif bariyer (pinning'li gercekci deger)
n_ideal = 1.8            # idealite faktoru (arayuzey tabakali diyotlarda tipik 1.5-3)
Rs = 100.0               # ohm, seri direnc
chi_t = 0.3              # eV, MoS2 uzerinden ortalama tunel bariyeri (belirsiz parametre)

def dark_iv(V, phi_b, n, Rs, delta_nm=0.0, chi_t=chi_t):
    """TE + Rs (Lambert-W) + tunelleme zayiflatmasi. V: dizi [V], donus I [A]."""
    delta_A = delta_nm * 10.0
    I0 = area * A_star * T**2 * np.exp(-np.sqrt(chi_t) * delta_A) \
         * np.exp(-phi_b / kT)
    nkT = n * kT  # eV
    # I = I0 [exp((V - I Rs)/nkT) - 1]  ->  Lambert-W kapali cozum
    x = (I0 * Rs / nkT) * np.exp((V + I0 * Rs) / nkT)
    I = (nkT / Rs) * np.real(lambertw(x)) - I0
    return I

V = np.linspace(-2.0, 1.0, 601)

fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))

# (a) bariyer yuksekligi etkisi
ax = axes[0]
for phi in [0.60, 0.70, 0.80, 0.91]:
    I = dark_iv(V, phi, n_ideal, Rs, delta_nm=2.0)
    ax.semilogy(V, np.abs(I) + 1e-15, label=f"$\\phi_b$ = {phi:.2f} eV")
ax.set_title("(a) Bariyer yuksekligi etkisi\n(MoS2 = 2 nm, n = 1.8)")
ax.legend()

# (b) MoS2 kalinlik etkisi - TUNEL-MIS REJIMI (yalnizca <~3 nm gecerli!)
# Daha kalin MoS2'de yapi heteroekleme donusur; orada analitik TE+tunel modeli
# COKER -> sayisal simulator (SCAPS/Lumerical) gerekir. Tezin sim. gerekcesi bu.
ax = axes[1]
for d in [0, 0.65, 1.3, 2.0, 3.0]:   # 0.65 nm = 1 tek-katman MoS2
    I = dark_iv(V, phi_b0, n_ideal, Rs, delta_nm=d)
    lbl = "MoS2 yok" if d == 0 else f"MoS2 = {d:g} nm"
    ax.semilogy(V, np.abs(I) + 1e-15, label=lbl)
ax.set_title("(b) Ultra ince MoS2: tunel-MIS rejimi\n($\\phi_b$ = 0.70 eV, $\\chi_t$ = 0.3 eV)")
ax.legend()

# (c) idealite faktoru etkisi
ax = axes[2]
for n in [1.0, 1.5, 2.0, 3.0]:
    I = dark_iv(V, phi_b0, n, Rs, delta_nm=2.0)
    ax.semilogy(V, np.abs(I) + 1e-15, label=f"n = {n:.1f}")
ax.set_title("(c) Idealite faktoru etkisi\n($\\phi_b$ = 0.70 eV, MoS2 = 2 nm)")
ax.legend()

for ax in axes:
    ax.set_xlabel("Gerilim (V)")
    ax.set_ylabel("|I| (A)")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(1e-13, 1e-1)

fig.suptitle("Ag/MoS2/p-Si/Al diyot - analitik karanlik I-V (TE + Rs + tunelleme), 300 K",
             y=1.02)
fig.tight_layout()
out = "analitik_iv.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print("kaydedildi:", out)

# hizli sayisal ozet (tunel-MIS rejimi)
for d in [0, 0.65, 2.0, 3.0]:
    I05 = dark_iv(np.array([0.5]), phi_b0, n_ideal, Rs, delta_nm=d)[0]
    Im2 = dark_iv(np.array([-2.0]), phi_b0, n_ideal, Rs, delta_nm=d)[0]
    print(f"MoS2 {d:>4} nm:  I(+0.5V) = {I05:.3e} A,  I(-2V) = {Im2:.3e} A, "
          f"dogrultma orani ~ {abs(I05/Im2):.1e}")
print("\nNOT: >~3 nm MoS2'de tasima tunelleme degil heteroeklem/surklenme-difuzyon")
print("rejimindedir; analitik model gecersizlesir -> SCAPS/sayisal simulasyon sarti.")
