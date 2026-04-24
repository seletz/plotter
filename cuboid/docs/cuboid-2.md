# CUBOID

An infinite 3D lattice of cubes, drawn from inside. The viewer stands in the gap between cubes at a three-way junction corner; the scene recedes to three vanishing points. Every face-to-face adjacency between neighboring cubes is crossed by a random cluster of cylindrical connections. Output is a single-layer black-ink plot on A1 paper.


## Geometry

The lattice consists of axis-aligned unit cubes on a regular 3D grid. Cube side is 1.0; gap between cubes is 0.2, one-fifth of the cube side. The grid period is therefore 1.2 in each axis. The lattice is conceptually infinite and culled to what's visible.


## Viewpoint

The camera sits at (0.6, 0.6, 0.6), the center of a three-way gap intersection. This places the viewer symmetrically among the eight immediately surrounding cubes, with nearest cube corners roughly 0.1 units away — close enough to feel enclosed, far enough not to clip.

The camera pitches up slightly. The resulting framing uses asymmetric three-point perspective: left vanishing point near the canvas left edge, right vanishing point at roughly three-quarters of canvas width, horizon above midline, and a distant vertical vanishing point well above the canvas. The viewer feels small; the structure looms overhead and recedes into the left.


## Connections

Every face-to-face adjacency between neighboring cubes carries cylindrical connections spanning the gap. Each face-pair hosts 3, 5, or 7 cylinders — odd numbers, chosen per face-pair. Cylinder diameter is 0.04, one-fifth of the gap width and identical for every cylinder. Axes align with the face normal.

Cylinder origins on the face plane are placed by random sampling under two constraints: a minimum distance between origins, so cylinders don't clump; and a margin from the face boundary, so cylinder silhouettes don't visually collide with the cube wireframe. When the sampler can't place the requested count within these constraints, it takes whatever it got — occasional face-pairs carry 4 or 6 cylinders rather than the nominal odd count.

Sampling is deterministic. A master seed combined with a canonical face-pair identifier produces a per-face-pair RNG state, so the composition is reproducible across studio preview and plotter batch, and across runs. Changing the master seed rerolls the whole lattice.


## Culling

The visible scene is a cube-only frontier. Cubes are culled by distance and frustum; cylinders render only when both of their endpoint cubes survive culling. At the edge of the visible region, cubes exist but cylinders pointing into the void are omitted rather than truncated — the lattice terminates crisply.


## Medium

The drawing is made on a pen plotter (iDraw H A1). The physical medium is pen strokes on paper — only straight line segments exist in output. Curves are polyline approximations; cylinders are rendered as prisms of 8 or 16 sides. Hidden-line removal is true: occluded portions of edges are cut from the output, not painted over. The final artifact is a single-layer black-ink drawing on DIN A1 paper in landscape orientation.
