import numpy as np
from scipy.special import comb

def draw_bezier(x, y, ax, points, already_drawn=False, draw_color="black"):
    """
    Draws a single Bézier curve using matplotlib,
    with control points given by (x[i], y[i]).
    
    Parameters:
    -----------
    x, y          : list or ndarray
                    coordinates of Bézier control points (same length)
    ax            : matplotlib Axes object
                    (e.g., obtained by fig, ax = plt.subplots())
    points        : int
                    number of "u" points (uniformly sampled in [0,1])
    already_drawn : bool
                    determines rendering style – editable or finalized
    """

    data_len = len(x)

    points2draw = np.linspace(0, 1, points)
    
    # 1. Prepare control point list as [(x0, y0), (x1, y1), ...]
    control_points = [(x[i], y[i]) for i in range(data_len)]
    
    # 2. Compute curve coordinates for each u in points2draw
    #    using the de Casteljau matrix-based algorithm
    x_forplot, y_forplot = de_casteljau_2d(control_points, points2draw)

    # 3. Draw the curve
    if not already_drawn:
        ax.plot(x_forplot, y_forplot, color="crimson", linewidth=2)

        # 4. Draw control points to allow interactive editing
        ax.scatter(x, y, color="green", s=7)

        for i, (x_i, y_i) in enumerate(zip(x, y)):
            ax.text(x_i, y_i + 10, str(i+1), color="black", fontsize=8, ha='center', fontweight='bold')
        return x_forplot, y_forplot
    else:
        ax.plot(x_forplot, y_forplot, color=draw_color, linewidth=2)

def de_casteljau_2d(control_points, t_values):
    """
    Returns 2D Bézier curve coordinates at given t values.

    Parameters:
    ---------   
    control_points : array_like of shape (n+1, 2)
        Control points, where n is the degree of the curve.
        Each element is (x_i, y_i).
    t_values : array_like, shape (m,)
        Parameter values t in range [0, 1] for which curve points are computed.

    Returns:
    -------
    x_forplot : ndarray, shape (m,)
        x-coordinates of points on the Bézier curve.
    y_forplot : ndarray, shape (m,)
        y-coordinates of points on the Bézier curve.
    """

    # Convert list/tuple to NumPy arrays
    cp = np.array(control_points, dtype=float)
    t = np.array(t_values, dtype=float).reshape(-1, 1)  # Wymuszamy kształt (m,1)

    # Separate x and y coordinates of control points
    x_cp = cp[:, 0]  # (n+1,)
    y_cp = cp[:, 1]  # (n+1,)

    # Degree of the curve (n = number of points - 1)
    n = len(cp) - 1

    # Compute binomial coefficients: [C(n,0), C(n,1), ..., C(n,n)]
    binomial_coeffs = comb(n, np.arange(n+1))

    # Compute Bernstein basis functions for each k in [0, n]
    #   B_k^n(t) = C(n,k) * (1 - t)^(n-k) * (t)^k
    # We want the result as a matrix basis (m, n+1),
    # where basis[i, k] = B_k^n(t[i]).
    basis_list = []
    for k in range(n+1):
        # C(n,k) * (1-t)^(n-k) * t^k
        b_k_t = binomial_coeffs[k] * (1 - t)**(n - k) * (t**k)
        basis_list.append(b_k_t)

    # Stack list of (m,1) arrays into a (m, n+1) matrix
    basis = np.hstack(basis_list)

    # Matrix multiplication – compute curve coordinates
    # x_forplot[i] = \sum_k basis[i, k] * x_cp[k]
    # y_forplot[i] = \sum_k basis[i, k] * y_cp[k]
    x_forplot = basis.dot(x_cp)
    y_forplot = basis.dot(y_cp)

    return x_forplot, y_forplot
