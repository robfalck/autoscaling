# Autoscaling API Version 1.0

An API for automated scaling of dynamically-constrained optimization problems in Dymos.

As of Version 1.0, the API supports the use of two automatic scaling techniques---isoscaling (IS) and projected jacobian rows normalization (PJRN)---for scaling the discretized aspects of small dynamically-constrained optimization problems in Dymos. The API also facilitates the implementation of custom automatic scaling techniques through inheritance from an AutoScaler base class.

**For various algorithm implementation details and basic usage tutorials, please see the Autoscaling API Tutorial LaTeX file located in the docs folder.** A similar tutorial on general scaling principles can be found on GitHub at https://github.com/hweyandtnasa/scaling-tutorial. (Note that these documents will be added to and improved over time, so check for new versions from time to time!)
