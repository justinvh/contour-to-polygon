# Problem:

You form a contour from a raster and now you want to form a bounding
polygon mesh that the contour encloses.

# Solution:

1. Walk the contour
2. Map occupied cells as 4-edges in a new coordinate system
3. Walk the edges and follow CW winding order rules
4. Polygon is generated

# Assumptions

1. The contour doesn't extrapolate positions. This means positions
   monotonically increase or decrease in x and/or y.
