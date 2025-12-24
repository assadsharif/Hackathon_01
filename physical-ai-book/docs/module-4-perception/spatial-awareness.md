---
sidebar_position: 2
title: Spatial Awareness
description: Learn how robots build 3D representations of their environment
---

# Spatial Awareness

## Key Concepts

- **SLAM (Simultaneous Localization and Mapping)**: Building a map while tracking robot position
- **Occupancy Grid**: 3D space represented as occupied/free cells
- **Point Cloud**: Set of 3D points representing surfaces
- **Depth Perception**: Estimating distance to objects
- **Spatial Representation**: How environment geometry is encoded

---

## Introduction

Spatial awareness is a robot's understanding of 3D space—where obstacles are, what surfaces exist, how rooms connect. For navigation and manipulation, robots must build and maintain representations of their environment.

---

## Depth Perception Methods

### Stereo Vision
**Principle**: Two cameras, like human eyes, compute depth from disparity (pixel offset between images)

**Pros**: Passive (no active illumination), rich depth maps
**Cons**: Fails in textureless regions, computationally expensive

### Structured Light (RGB-D Cameras)
**Principle**: Project known pattern (IR dots), measure deformation to infer depth

**Examples**: Microsoft Kinect, Intel RealSense

**Pros**: Dense depth maps, works indoors
**Cons**: Limited range (~5m), fails in sunlight (IR interference)

### LIDAR (Light Detection and Ranging)
**Principle**: Laser scans, measure time-of-flight for distance

**Pros**: Long range (100m+), accurate, works in various lighting
**Cons**: Expensive, sparse (point cloud, not dense image)

### Monocular Depth Estimation (Learning-Based)
**Principle**: Single camera, neural network predicts depth from visual cues (perspective, occlusion, size)

**Pros**: Cheap (one camera), increasingly capable with deep learning
**Cons**: Scale ambiguity (can't distinguish large-far from small-close without context)

---

## Spatial Representations

### Occupancy Grids
**Structure**: 3D voxel grid, each cell marked occupied/free/unknown

**Use Cases**: Navigation, collision avoidance

**Pros**: Simple, fast collision checks
**Cons**: Memory intensive for large spaces, fixed resolution

### Point Clouds
**Structure**: Set of 3D points (x, y, z), often with color/intensity

**Use Cases**: 3D reconstruction, object recognition

**Pros**: Flexible resolution, captures surface detail
**Cons**: Large data size, harder to use for planning

### Mesh Representations
**Structure**: Triangulated surfaces connecting points

**Use Cases**: Realistic rendering, physics simulation

**Pros**: Compact, supports textures
**Cons**: Requires post-processing (meshing point clouds)

### Semantic Maps
**Structure**: Spatial map annotated with object labels (table, chair, door)

**Use Cases**: Task planning (find table to place object)

**Pros**: High-level reasoning
**Cons**: Requires object recognition

---

## SLAM (Simultaneous Localization and Mapping)

### The SLAM Problem

**Challenge**: Build a map of an unknown environment while simultaneously tracking robot position within that map.

**Chicken-and-egg**: Need map to localize, need localization to build map.

**Solution**: Iteratively update both (map and pose) based on sensor measurements.

### SLAM Approaches

**Visual SLAM** (ORB-SLAM, LSD-SLAM):
- Use camera images
- Track visual features (corners, edges)
- Build sparse 3D map of features

**Lidar SLAM** (Google Cartographer, Hector SLAM):
- Use 2D/3D lidar scans
- Match scans to map, update pose
- Build occupancy grid or point cloud

**RGB-D SLAM** (KinectFusion):
- Fuse depth images into 3D volumetric representation
- Dense reconstruction

**Learning-Based**: Neural networks predict camera motion and depth (emerging area)

---

## Egocentric vs Allocentric Representations

### Egocentric (Body-Centered)
**Definition**: Spatial information relative to robot's current position/orientation

**Example**: "Object is 2m ahead, 1m to my left"

**Pros**: Directly usable for action (reach forward)
**Cons**: Unstable (changes as robot moves)

### Allocentric (World-Centered)
**Definition**: Spatial information in global coordinate frame

**Example**: "Object is at (5, 3, 1) in room coordinates"

**Pros**: Stable across robot motion, shareable between robots
**Cons**: Requires localization (know where robot is in global frame)

**Hybrid Approach**: Maintain both—allocentric map for planning, egocentric for control.

---

## Practical Applications

### Indoor Navigation
1. **SLAM**: Build occupancy grid of rooms/hallways
2. **Localization**: Track robot position in map
3. **Path Planning**: A* or RRT search from current position to goal
4. **Obstacle Avoidance**: Update local map with new obstacles, replan dynamically

### Object Placement
1. **Scene Reconstruction**: RGB-D camera builds point cloud of table surface
2. **Plane Detection**: Segment flat surfaces
3. **Grasp Planning**: Identify collision-free placement pose
4. **Execution**: Place object while monitoring contact

---

## Challenges

### Dynamic Environments
**Problem**: SLAM assumes static world; moving people/objects violate assumption

**Solutions**: Detect and filter moving objects, update map dynamically

### Loop Closure
**Problem**: After long exploration, robot returns to starting area—must recognize it's the same place

**Solutions**: Visual place recognition, graph optimization to correct accumulated drift

### Scale
**Problem**: Large environments (buildings, outdoor areas) require huge maps

**Solutions**: Hierarchical maps (rooms → floors → buildings), map compression

---

## Summary

Spatial awareness enables robots to understand 3D geometry:

- **Depth perception**: Stereo, RGB-D, LIDAR, monocular learning-based methods
- **Representations**: Occupancy grids (navigation), point clouds (reconstruction), semantic maps (task planning)
- **SLAM**: Simultaneously build map and track position
- **Egocentric vs allocentric**: Body-centered for action, world-centered for stable representation

Robust spatial awareness is foundational for navigation, manipulation, and interaction in 3D environments.

---

## Related Topics

- **[Multimodal Sensing](./multimodal-sensing)** - Combining vision, touch, proprioception for robust perception
- **[Object Recognition](./object-recognition)** - Recognizing what objects are in 3D space
- **[Module 5: Motion Planning](../../module-5-control/motion-planning)** - Using spatial maps for navigation
