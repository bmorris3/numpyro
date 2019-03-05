# Code modified from scipy.distributions._distn_infrastucture.py
#
# Copyright (c) 2001, 2002 Enthought, Inc.
# All rights reserved.
#
# Copyright (c) 2003-2019 SciPy Developers.
# All rights reserved.

import scipy.stats as sp
from jax import lax
from jax.random import _is_prng_key
from jax.numpy.lax_numpy import _promote_args
import jax.numpy as np


class jax_continuous(sp.rv_continuous):
    def rvs(self, *args, **kwargs):
        rng = kwargs.pop('random_state')
        if rng is None:
            rng = self.random_state
        # assert that rng is PRNGKey and not mtrand.RandomState object from numpy.
        assert _is_prng_key(rng)
        args = list(args)
        # If 'size' is not in kwargs, then it is either the last element of args
        # or it will take default value (which is None).
        # Note: self.numargs is the number of shape parameters.
        size = kwargs.pop('size', args.pop() if len(args) > (self.numargs + 2) else None)
        args, loc, scale = self._parse_args(*args, **kwargs)
        # FIXME(fehiepsi): Using _promote_args_like requires calling `super(jax_continuous, self).rvs` but
        # it will call `self._rvs` (which is written using JAX and requires JAX random state).
        loc, scale, *args = _promote_args("rvs", loc, scale, *args)
        if not size:
            shapes = [np.shape(arg) for arg in args] + [np.shape(loc), np.shape(scale)]
            size = lax.broadcast_shapes(*shapes)
        self._random_state = rng
        self._size = size
        vals = self._rvs(*args)
        return vals * scale + loc

    def logpdf(self, x, *args, **kwargs):
        args, loc, scale = self._parse_args(*args, **kwargs)
        loc, scale, *args = _promote_args(self.logpdf, loc, scale, *args)
        x = (x - loc) / scale
        return self._logpdf(x, *args) - np.log(scale)
