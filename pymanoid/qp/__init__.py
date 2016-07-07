#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Stephane Caron <stephane.caron@normalesup.org>
#
# This file is part of pymanoid.
#
# pymanoid is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pymanoid is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# pymanoid. If not, see <http://www.gnu.org/licenses/>.


from numpy import dot


solve_qp = None

try:  # CVXOPT
    from backend_cvxopt import solve_qp as cvxopt_solve_qp
    solve_qp = cvxopt_solve_qp
except ImportError:
    def cvxopt_solve_qp(*args, **kwargs):
        raise ImportError("CVXOPT not found")

try:  # Gurobi
    from backend_gurobi import solve_qp as gurobi_solve_qp
    if solve_qp is not None:
        solve_qp = gurobi_solve_qp
except ImportError:
    def gurobi_solve_qp(*args, **kwargs):
        raise ImportError("Gurobi not found")


try:  # qpOASES
    from backend_qpoases import solve_qp as qpoases_solve_qp
    if solve_qp is not None:
        solve_qp = qpoases_solve_qp
except ImportError:
    def qpoases_solve_qp(*args, **kwargs):
        raise ImportError("qpOASES not found")


def solve_relaxed_qp(P, q, G, h, A, b, tol=None, OVER_WEIGHT=100000.):
    """
    Solve a relaxed version of the Quadratic Program:

        min_x   x.T * P * x + 2 * q.T * x

         s.t.   G * x <= h
                A * x == b

    The relaxed problem is defined by

        min_x   c1(x, P, q) + OVER_WEIGHT * c2(x, A, b)
         s.t.   G * x <= h

    where c1(x, P, q) is the initial cost, OVER_WEIGHT is a very high weight and

        c1(x, P, q) = x.T * P * x + 2 * q.T * x
        c2(x, A, b) = |A * x - b|^2

    If ``tol`` is not None, the solution will only be returned if the relative
    variation between A * x and b is less than ``tol``.
    """
    P2 = P + OVER_WEIGHT * dot(A.T, A)
    q2 = q + OVER_WEIGHT * dot(-b.T, A)
    x = solve_qp(P2, q2, G, h)
    if tol is not None:
        def sq(v):
            return dot(v, v)
        if sq(dot(A, x) - b) / sq(b) > tol * tol:
            return None
    return x


__all__ = [
    'cvxopt_solve_qp',
    'gurobi_solve_qp',
    'qpoases_solve_qp',
]