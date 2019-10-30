import logging
import numpy as np
import scipy.special

from .external import Model, ModelIwls, InputDataGLM
from .processModel import ProcessModel

logger = logging.getLogger(__name__)


class ModelIwlsNb(ModelIwls, Model, ProcessModel):

    compute_mu: bool
    compute_r: bool

    def __init__(
            self,
            input_data: InputDataGLM,
            model_vars,
            compute_mu,
            compute_r,
            dtype,
    ):
        self.compute_mu = compute_mu
        self.compute_r = compute_r

        super(Model, self).__init__(
            input_data=input_data
        )
        ModelIwls.__init__(
            self=self,
            model_vars=model_vars
        )

    @property
    def fim_weight(self):
        """

        :return: observations x features
        """
        return - self.location * self.scale / (self.scale + self.location)

    @property
    def ybar(self) -> np.ndarray:
        """

        :return: observations x features
        """
        return np.asarray(self.x - self.location) / self.location

    def fim_weight_j(self, j):
        """

        :return: observations x features
        """
        return - self.location_j(j=j) * self.scale_j(j=j) / (self.scale_j(j=j) + self.location_j(j=j))

    def ybar_j(self, j) -> np.ndarray:
        """

        :return: observations x features
        """
        return np.asarray(self.x[:, [j]] - self.location_j(j=j)) / self.location_j(j=j)

    @property
    def jac_weight_b(self):
        """

        :return: observations x features
        """
        scale = self.scale
        loc = self.location
        scale_plus_x = np.asarray(scale + self.x)
        r_plus_mu = scale + loc

        # Define graphs for individual terms of constant term of hessian:
        const1 = scipy.special.digamma(scale_plus_x) - scipy.special.digamma(scale)
        const2 = - scale_plus_x / r_plus_mu
        const3 = np.log(scale) + np.ones_like(scale) - np.log(r_plus_mu)
        return scale * (const1 + const2 + const3)

    def jac_weight_b_j(self, j):
        """

        :return: observations x features
        """
        scale = self.scale_j(j=j)
        loc = self.location_j(j=j)
        scale_plus_x = np.asarray(scale + self.x[:, [j]])
        r_plus_mu = scale + loc

        # Define graphs for individual terms of constant term of hessian:
        const1 = scipy.special.digamma(scale_plus_x) - scipy.special.digamma(scale)
        const2 = - scale_plus_x / r_plus_mu
        const3 = np.log(scale) + np.ones_like(scale) - np.log(r_plus_mu)
        return scale * (const1 + const2 + const3)

    @property
    def ll(self):
        scale = self.scale
        loc = self.location
        log_r_plus_mu = np.log(scale + loc)
        if isinstance(self.x, np.ndarray):
            ll = scipy.special.gammaln(scale + self.x) - \
                 scipy.special.gammaln(self.x + np.ones_like(scale)) - \
                 scipy.special.gammaln(scale) + \
                 self.x * (self.eta_loc - log_r_plus_mu) + \
                 np.multiply(scale, self.eta_scale - log_r_plus_mu)
        else:
            ll = scipy.special.gammaln(np.asarray(scale + self.x)) - \
                scipy.special.gammaln(self.x + np.ones_like(scale)) - \
                scipy.special.gammaln(scale) + \
                np.asarray(self.x.multiply(self.eta_loc - log_r_plus_mu) +
                           np.multiply(scale, self.eta_scale - log_r_plus_mu))
        return self.np_clip_param(np.asarray(ll), "ll")

    def ll_j(self, j):
        scale = self.scale_j(j=j)
        loc = self.location_j(j=j)
        log_r_plus_mu = np.log(scale + loc)
        if isinstance(self.x, np.ndarray):
            ll = scipy.special.gammaln(scale + self.x[:, [j]]) - \
                 scipy.special.gammaln(self.x + np.ones_like(scale)) - \
                 scipy.special.gammaln(scale) + \
                 self.x[:, [j]] * (self.eta_loc_j(j=j) - log_r_plus_mu) + \
                 np.multiply(scale, self.eta_scale_j(j=j) - log_r_plus_mu)
        else:
            ll = scipy.special.gammaln(np.asarray(scale + self.x[:, j])) - \
                 scipy.special.gammaln(self.x + np.ones_like(scale)) - \
                 scipy.special.gammaln(scale) + \
                 np.asarray(self.x[:, j].multiply(self.eta_loc_j(j=j) - log_r_plus_mu) +
                            np.multiply(scale, self.eta_scale_j(j=j) - log_r_plus_mu))
        return self.np_clip_param(np.asarray(ll), "ll")
