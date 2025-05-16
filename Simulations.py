import numpy as np
from scipy.optimize import minimize_scalar, root_scalar
import matplotlib.pyplot as plt

# Parameters
mu = 5.0   # service rate (cars/sec)
C = 110    # total cycle time (seconds)

# Arrival rates (cars/sec)
lambda_N = 0.438
lambda_S = 0.382
lambda_E = 0.619
lambda_W = 0.521

def scenario_a():
    lambda_NS = (lambda_N + lambda_S) / 2
    lambda_EW = (lambda_E + lambda_W) / 2

    def total_wait_time(G_NS):
        G_EW = C - 8 - G_NS
        if G_NS <= 0 or G_EW <= 0:
            return np.inf
        denom_NS = mu * G_NS - lambda_NS * C
        denom_EW = mu * G_EW - lambda_EW * C
        if denom_NS <= 0 or denom_EW <= 0:
            return np.inf
        return C / denom_NS + C / denom_EW

    result = minimize_scalar(total_wait_time, bounds=(1, C - 9), method='bounded')
    G_NS_star = result.x
    G_EW_star = C - 8 - G_NS_star

    print("Scenario (a): Paired Directions")
    print(f"  Optimal G_NS = {G_NS_star:.2f} sec")
    print(f"  Optimal G_EW = {G_EW_star:.2f} sec")
    print(f"  Min Total Wait Time: {result.fun:.2f} sec\n")

    # Graphical validation
    G_vals = np.linspace(1, C - 9, 500)
    W_vals = [total_wait_time(G) for G in G_vals]

    plt.figure(figsize=(10, 6))
    plt.plot(G_vals, W_vals, label='Total Wait Time $W(G_{NS})$', linewidth=2)
    plt.axvline(G_NS_star, color='red', linestyle='--', label=f'Optimal $G_{{NS}}$ = {G_NS_star:.2f} sec')
    plt.title('Scenario (a): Total Wait Time vs $G_{NS}$')
    plt.xlabel('$G_{NS}$ (Green time for North-South) [sec]')
    plt.ylabel('Total Wait Time [sec]')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def scenario_b():
    lambdas = np.array([lambda_N, lambda_E, lambda_S, lambda_W])
    total_lambda = np.sum(lambdas)

    def constraint(gamma):
        if gamma <= 0:
            return 1e6
        sqrt_term = np.sqrt(mu * C / gamma)
        Gs = (lambdas * C + sqrt_term) / mu
        return np.sum(Gs) - (C - 16)

    sol = root_scalar(constraint, bracket=[1e-6, 1e6], method='brentq')

    if not sol.converged:
        print("Scenario (b): Root finding did not converge.\n")
        return

    gamma_solution = sol.root
    sqrt_term = np.sqrt(mu * C / gamma_solution)
    Gs = (lambdas * C + sqrt_term) / mu

    print("Scenario (b): Independent Directions")
    directions = ['N', 'E', 'S', 'W']
    for d, g in zip(directions, Gs):
        print(f"  Optimal G_{d} = {g:.2f} sec")
    print(f"  Total Green Time: {np.sum(Gs):.2f} sec")
    print(f"  Gamma (Lagrange Multiplier) = {gamma_solution:.6f}\n")

    # Graphical validation of constraint residual
    gamma_vals = np.logspace(-3, 3, 500)
    constraint_vals = [constraint(g) for g in gamma_vals]

    plt.figure(figsize=(10, 6))
    plt.plot(gamma_vals, constraint_vals, label='Constraint Residual', linewidth=2)
    plt.axhline(0, color='red', linestyle='--', label='Target: 0')
    plt.xscale('log')
    plt.xlabel('Gamma (Lagrange Multiplier)')
    plt.ylabel('Constraint Residual')
    plt.title('Scenario (b): Constraint Satisfaction vs Gamma')
    plt.grid(True, which='both')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    scenario_a()
    scenario_b()
