# Inverse Exponential Distribution
This is a custom probability density function I created to solve a particular problem I had at work, however it could also be useful to others.

This distribution aims to fit exponentially *ascending* data on an interval [a, b]. That is, it's not bound to zero like the regular exponential distribution and can be defined for any interval.

With this module, I aim to mimic the `scipy` API it has for its distributions (although not *everything* is implemented.)

## Dependencies
This module uses [scipy](https://github.com/scipy/scipy/blob/main/LICENSE.txt) which (at the time of writing) is licensed under BSD-3.

## Warnings
* When fitting your data, the lower and upper bounds are determined by the min/max of the data; this will severely impact the results if you have very low/high extremes. It's recommended to treat your data and ensure the sample you're fitting is a "natural"-looking exponentially ascending shape.

* Drawing samples (with `rvs()`) is very slow when exceeding ~1000 samples. It's currently using optimization and numerical integration to evaluate the inverse CDF each time you want to draw a sample. In the future this may be improved if required.

## Example Data
To see an example of what type of data this distribution fits, see the image below.

TODO:

## Mathematical Details
If you're interested in the actual derivation, see the [whitepaper](whitepaper.pdf) in this repo.

## Installation
TODO:

## API
TODO:
