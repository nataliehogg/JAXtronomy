__author__ = ["sibirrer", "nataliehogg"]

from jax import grad, numpy as np # NH: does PEP8 have something to say about the phrasing of imports?

from lenstronomy.LensModel.Profiles.base_profile import LensProfileBase # NH: leave this import alone? it's not jax-dependent

__all__ = ["SIS"]


class SIS(LensProfileBase):
    """This class contains the function and the derivatives of the Singular Isothermal
    Sphere.

    .. math::
        \\kappa(x, y) = \\frac{1}{2} \\left(\\frac{\\theta_{E}}{\\sqrt{x^2 + y^2}} \\right)

    with :math:`\\theta_{E}` is the Einstein radius,
    """

    param_names = ["theta_E", "center_x", "center_y"]
    lower_limit_default = {"theta_E": 0, "center_x": -100, "center_y": -100}
    upper_limit_default = {"theta_E": 100, "center_x": 100, "center_y": 100}

    def function(self, x, y, theta_E, center_x=0, center_y=0):
        x_shift = x - center_x
        y_shift = y - center_y
        f_ = theta_E * jnp.sqrt(x_shift * x_shift + y_shift * y_shift)
        return f_

    def derivatives(self, x, y, theta_E, center_x=0, center_y=0):
        """Returns df/dx and df/dy of the function."""

        # NH: something I'm concerned about is the fact that, while concise, this obscures the actual calculation

        f_x, f_y = grad(self.function, argnums=(0, 1))(x, y, theta_E, center_x, center_y)

        return f_x, f_y

    def hessian(self, x, y, theta_E, center_x=0, center_y=0):
        """Returns Hessian matrix of function d^2f/dx^2, d^2/dxdy, d^2/dydx,
        d^f/dy^2."""

        f_x, f_y = jacfwd(jacrev(self.function, argnums=(0,1)), argnums=(0,1))(x, y, theta_E, center_x, center_y)

        f_xx = f_x[0]
        f_xy = f_x[1]
        f_yx = f_y[0]
        f_yy = f_y[1] # NH: to me this is ugly, to be improved

        return f_xx, f_xy, f_xy, f_yy

    @staticmethod
    def rho2theta(rho0):
        """Converts 3d density into 2d projected density parameter :param rho0:

        :return:
        """
        theta_E = np.pi * 2 * rho0
        return theta_E

    @staticmethod
    def theta2rho(theta_E):
        """Converts projected density parameter (in units of deflection) into 3d density
        parameter :param theta_E: Einstein radius :return:"""
        fac1 = np.pi * 2
        rho0 = theta_E / fac1
        return rho0

    @staticmethod
    def mass_3d(r, rho0):
        """Mass enclosed a 3d sphere or radius r :param r: radius in angular units
        :param rho0: density at angle=1 :return: mass in angular units."""
        mass_3d = 4 * np.pi * rho0 * r
        return mass_3d

    def mass_3d_lens(self, r, theta_E):
        """Mass enclosed a 3d sphere or radius r given a lens parameterization with
        angular units.

        :param r: radius in angular units
        :param theta_E: Einstein radius
        :return: mass in angular units
        """
        rho0 = self.theta2rho(theta_E)
        return self.mass_3d(r, rho0)

    @staticmethod
    def mass_2d(r, rho0):
        """Mass enclosed projected 2d sphere of radius r :param r:

        :param rho0:
        :return:
        """
        alpha = 2 * rho0 * np.pi**2
        mass_2d = alpha * r
        return mass_2d

    def mass_2d_lens(self, r, theta_E):
        """

        :param r: radius
        :param theta_E: Einstein radius
        :return: mass within a radius in projection
        """
        rho0 = self.theta2rho(theta_E)
        return self.mass_2d(r, rho0)

    def grav_pot(self, x, y, rho0, center_x=0, center_y=0):
        """Gravitational potential (modulo 4 pi G and rho0 in appropriate units) :param
        x:

        :param y:
        :param rho0:
        :param center_x:
        :param center_y:
        :return:
        """
        x_ = x - center_x
        y_ = y - center_y
        r = np.sqrt(x_**2 + y_**2)
        mass_3d = self.mass_3d(r, rho0)
        pot = mass_3d / r
        return pot

    @staticmethod
    def density(r, rho0):
        """Computes the density :param r: radius in angles :param rho0: density at
        angle=1 :return: density at r."""
        rho = rho0 / r**2
        return rho

    def density_lens(self, r, theta_E):
        """Computes the density at 3d radius r given lens model parameterization. The
        integral in projected in units of angles (i.e. arc seconds) results in the
        convergence quantity.

        :param r: 3d radius
        :param theta_E: Einstein radius
        :return: density(r)
        """
        rho0 = self.theta2rho(theta_E)
        return self.density(r, rho0)

    @staticmethod
    def density_2d(x, y, rho0, center_x=0, center_y=0):
        """Projected density :param x:

        :param y:
        :param rho0:
        :param center_x:
        :param center_y:
        :return:
        """
        x_ = x - center_x
        y_ = y - center_y
        r = np.sqrt(x_**2 + y_**2)
        sigma = np.pi * rho0 / r
        return sigma
