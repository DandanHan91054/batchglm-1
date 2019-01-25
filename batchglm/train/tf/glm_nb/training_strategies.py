from enum import Enum

class TrainingStrategies(Enum):

    AUTO = None
    DEFAULT = [
        {
            "convergence_criteria": "all_converged_ll",
            "stopping_criteria": 1e-8,
            "use_batching": False,
            "optim_algo": "nr_tr",
        },
    ]
    INEXACT = [
        {
            "convergence_criteria": "all_converged_ll",
            "stopping_criteria": 1e-4,
            "use_batching": False,
            "optim_algo": "nr_tr",
        },
    ]
    EXACT = [
        {
            "convergence_criteria": "all_converged_ll",
            "stopping_criteria": 1e-8,
            "use_batching": False,
            "optim_algo": "nr_tr",
        },
    ]