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
        return np.multiply(
            self.location,
            np.divide(self.scale, self.scale + self.location)
        )

    @property
    def ybar(self) -> np.ndarray:
        """

        :return: observations x features
        """
        return (self.x - self.location) / self.location

    @property
    def ll(self):
        log_r_plus_mu = np.log(self.scale + self.location)
        ll = scipy.special.gammaln(self.scale + self.x) - \
            scipy.special.gammaln(self.x + np.ones_like(self.x)) - \
            scipy.special.gammaln(self.scale) + \
            np.multiply(self.x, self.eta_loc - log_r_plus_mu) + \
            np.multiply(self.scale, self.eta_scale - log_r_plus_mu)
        return self.np_clip_param(ll, "ll")
