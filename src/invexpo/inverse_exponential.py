from scipy.optimize import root_scalar, minimize
from scipy import integrate 
from scipy.stats import uniform
import numpy as np

from .exceptions import ArgumentError, NotFittedError

class InverseExponential:
    def __init__(self) -> None:
        self.__param_a: float = 0.001
        self.__fitted: bool = False
    
    def fit(self, data: list[float], maxiter: int = 1000) -> None:
        if len(data) < 1:
            raise ArgumentError("Need more than one sample to fit data.")

        self.__data: list[float] = data.copy()
        self.__lower_bound: float = min(data)
        self.__upper_bound: float = max(data)
        if self.__upper_bound == self.__lower_bound:
            raise ArgumentError("Lower bound and upper bound must be different.")

        self.__range: float = self.__upper_bound - self.__lower_bound

        self.__find_root_of_likelihood(maxiter)
        self.__fitted = True

    def get_parameter(self) -> float:
        return self.__param_a

    # create a theoretical distribution
    def create(self, a: float, lower_bound: float, upper_bound) -> None:
        if lower_bound >= upper_bound:
            raise ArgumentError("Lower bound must be less than upper bound.")

        self.__param_a = a
        self.__lower_bound = lower_bound
        self.__upper_bound = upper_bound
        self.__range = upper_bound - lower_bound
        self.__fitted = True

    def pdf(self, x: float) -> float:
        if not self.__fitted:
            raise NotFittedError("pdf")

        _a: float = self.__param_a
        _numerator: float = _a * np.exp(_a * (x - self.__lower_bound))
        _denominator: float = np.exp(_a * self.__range) - 1

        return _numerator / _denominator

    def cdf(self, x: float) -> float:
        if not self.__fitted:
            raise NotFittedError("cdf")

        if x <= self.__lower_bound:
            return 0.0

        if x >= self.__upper_bound:
            return 1.0

        return integrate.quad(self.pdf, self.__lower_bound, x)[0]

    def ppf(self, p: float) -> float:
        if not self.__fitted:
            raise NotFittedError("ppf")

        if p < 0.0 or p > 1.0:
            raise ArgumentError("p must be 0.0 <= p <= 1.0")

        return self.__find_ppf(p)

    def icdf(self, p: float) -> float:
        return self.ppf(p)

    def integrate(self, lower_bound: float, upper_bound: float) -> float:
        if lower_bound >= upper_bound:
            raise ArgumentError("lower_bound must be less than upper_bound.")

        return integrate.quad(self.pdf, lower_bound, upper_bound)[0]

    def rvs(self, size = 1) -> list[float]:
        if size < 1:
            raise ArgumentError("size must be >= 1.")

        _uniform_dist = uniform()

        samples: list[float] = []
        for i in range(size):
            # sometimes the icdf is slightly inaccurate and generates values outside the bounds
            # so we repeatedly sample until we obtain valid values
            while True:
                _u: float = _uniform_dist.rvs()
                _sample = self.ppf(_u)
                if _sample >= self.__lower_bound and _sample <= self.__upper_bound:
                    samples.append(_sample)
                    break

        return samples

    def moment(self, n: int) -> float:
        if not self.__fitted:
            raise NotFittedError("moment")

        return integrate.quad(lambda x: pow(x, n) * self.pdf(x), self.__lower_bound, self.__upper_bound)[0]

    def median(self) -> float:
        if not self.__fitted:
            raise NotFittedError("median")

        return self.icdf(0.5)

    def mean(self) -> float:
        return self.moment(1)

    def var(self) -> float:
        return self.moment(2) - self.moment(1)**2

    def std(self) -> float:
        return np.sqrt(self.var())

    def sf(self, x: float) -> float:
        raise NotImplementedError()

    def isf(self, p: float) -> float:
        raise NotImplementedError()

    def __log_likelihood(self, _a: float) -> float:
        _sum: float = 0.0
        for _x in self.__data:
            _sum += (_x - self.__lower_bound)
        _n: int = len(self.__data)

        return _n/_a + _sum - (self.__range * _n * np.exp(self.__range * _a))/(np.exp(self.__range * _a) - 1.0)

    def __find_root_of_likelihood(self, maxiter: int) -> None:
        result = root_scalar(self.__log_likelihood, method = 'newton', x0 = 0.01, maxiter = maxiter)
        if not result.converged:
            raise Exception("Optimizer could not converge. Try increasing maxiter?")
        self.__param_a = result.root

    def __find_ppf(self, p: float) -> float:
        # start the initial guess in the middle of the range
        x0: float = (self.__lower_bound + self.__upper_bound) / 2.0
        result = minimize(lambda x: (self.cdf(x) - p)**2, x0 = [x0])
        if not result.success:
            raise Exception("ppf optimizer was not successful in finding an appropriate value.")

        return result.x[0]
