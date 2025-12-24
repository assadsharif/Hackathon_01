---
sidebar_position: 1
title: Motion Planning
description: Learn how robots plan collision-free paths and trajectories
---

# Motion Planning

## Key Concepts

- **Motion Planning**: Computing collision-free paths from start to goal configuration
- **Configuration Space (C-space)**: Space of all possible robot poses
- **Sampling-Based Planning**: Randomly explore C-space (RRT, PRM algorithms)
- **Optimization-Based Planning**: Find optimal trajectories subject to constraints
- **Reactive vs Deliberative**: Fast local adjustments vs global path planning

---

## Introduction

Motion planning is the computational problem of finding a collision-free path from a robot's current configuration to a desired goal. For a humanoid picking up an object, this means planning arm trajectories that avoid hitting obstacles, respect joint limits, and smoothly reach the target grasp pose.

This chapter covers fundamental planning approaches, from classical graph search to modern sampling-based and optimization methods.

---

## The Motion Planning Problem

### Problem Definition

**Given**:
- Robot's current configuration (joint angles, position)
- Goal configuration or task specification
- Geometric model of environment (obstacles, surfaces)
- Robot's kinematic/dynamic constraints

**Find**: Collision-free path (sequence of configurations) connecting start to goal

**Constraints**:
- Joint limits (each joint has min/max angle)
- Collision avoidance (robot body must not intersect obstacles)
- Dynamics (acceleration, velocity limits)
- Task constraints (gripper orientation for grasping)

---

## Configuration Space (C-space)

### What is C-space?

**Definition**: The space of all possible robot configurations.

**Example**:
- 2-DOF robot arm: C-space is 2D (two joint angles)
- 7-DOF arm: C-space is 7D
- Humanoid (30 DOF): C-space is 30D

### Why C-space Matters

**Workspace** (physical 3D world):
- Complex obstacle geometry
- Difficult to reason about robot body collisions

**C-space** (configuration coordinates):
- Obstacles become regions in C-space (C-obstacles)
- Robot is a point
- Path planning becomes finding collision-free path for a point

**Challenge**: C-space grows exponentially with DOF (curse of dimensionality)

---

## Planning Approaches

### 1. Grid-Based Search (A*, Dijkstra)

**Approach**: Discretize C-space into grid, search for path using graph algorithms.

**Pros**: Complete (finds solution if exists), optimal path
**Cons**: Exponential memory/time for high-DOF robots (infeasible for humanoids)

**Use Case**: Low-DOF systems (2-3 DOF), mobile robot navigation (2D)

---

### 2. Sampling-Based Planning

**Core Idea**: Randomly sample configurations, build connectivity graph, search graph for path.

#### Probabilistic Roadmap (PRM)

**Algorithm**:
1. Sample random configurations in C-space
2. Check each for collision
3. Connect nearby collision-free samples with edges (if local path is collision-free)
4. Result: Roadmap graph
5. Query: Connect start/goal to roadmap, search graph

**Pros**: Multi-query (reuse roadmap), probabilistically complete
**Cons**: Requires pre-computation, struggles in narrow passages

#### Rapidly-Exploring Random Tree (RRT)

**Algorithm**:
1. Grow tree from start configuration
2. Repeatedly:
   - Sample random configuration
   - Extend tree toward sample
   - Add new node if edge is collision-free
3. Stop when tree reaches goal region

**Pros**: Single-query, fast, handles high-DOF, good exploration
**Cons**: Paths are jerky (not smooth), not optimal

**Variants**:
- **RRT\***: Asymptotically optimal (rewires tree to minimize cost)
- **RRT-Connect**: Grow trees from both start and goal, connect when they meet

---

### 3. Optimization-Based Planning

**Approach**: Formulate planning as optimization problem, minimize cost function subject to constraints.

**Example: Trajectory Optimization**

**Variables**: Trajectory (sequence of robot states over time)

**Objective**: Minimize energy, time, or smoothness

**Constraints**:
- Collision avoidance (distance to obstacles > threshold)
- Dynamics (acceleration limits)
- Boundary conditions (start/goal states)

**Methods**:
- **CHOMP** (Covariant Hamiltonian Optimization for Motion Planning): Gradient-based, smooth trajectories
- **TrajOpt**: Sequential convex optimization
- **iLQR** (iterative Linear Quadratic Regulator): Dynamic trajectory optimization

**Pros**: Smooth, optimal, can incorporate dynamics
**Cons**: Requires good initialization (often from RRT), can get stuck in local minima

---

## Path vs Trajectory

### Path
**Definition**: Geometric sequence of configurations (no timing)

**Example**: [q₀, q₁, q₂, ..., qₙ] where each qᵢ is a configuration

**Output of**: RRT, PRM, A*

### Trajectory
**Definition**: Path with timing (velocity, acceleration profiles)

**Example**: q(t) for t ∈ [0, T], with q̇(t) and q̈(t) specified

**Output of**: Trajectory optimization, time parameterization of path

**Why it matters**: Robots need trajectories (not just paths) for execution—must know velocities to control motors.

---

## Reactive vs Deliberative Control

### Deliberative Planning
**Approach**: Plan complete path before execution

**Characteristics**:
- Global reasoning (considers entire environment)
- Offline or slow online computation
- Assumes static environment

**Example**: RRT plans arm motion before robot starts moving

### Reactive Control
**Approach**: Generate motion in real-time based on current sensor feedback

**Characteristics**:
- Fast, no planning
- Local reasoning (only nearby obstacles)
- Handles dynamic environments

**Methods**:
- **Potential Fields**: Attractive force toward goal, repulsive from obstacles
- **Dynamic Window Approach**: Select velocity from dynamically feasible set that maximizes progress toward goal

**Limitation**: Can get stuck in local minima (no global plan)

### Hybrid Approach (Modern Standard)
**Combine**:
- Deliberative: Plan global path
- Reactive: Adjust locally to avoid unexpected obstacles, disturbances

**Example**: Humanoid plans arm trajectory (deliberative), but adjusts in real-time if human walks into workspace (reactive).

---

## Planning for Manipulation

### Task-Specific Constraints

**Grasping**: Gripper must approach object from specific direction, orientation

**Placement**: Object must be placed stably on surface

**Two-Handed Tasks**: Both arms must coordinate (relative pose constraints)

### Inverse Kinematics (IK)

**Problem**: Given desired end-effector pose (x, y, z, orientation), find joint angles

**Challenges**:
- Multiple solutions (redundant arms have infinite solutions)
- No solution (pose unreachable)

**Use in Planning**: Sample end-effector goals, use IK to get configurations, plan in joint space

---

## Handling Uncertainty

### Probabilistic Planning

**Challenge**: Robot doesn't know exact configuration (noisy sensors), or environment is uncertain

**Approach**: Plan in belief space (probability distributions over states)

**Example**: Grasp planning when object pose is uncertain—plan robust grasps that work across range of poses

### Contingency Planning

**Approach**: Plan multiple branches—if action fails, execute backup plan

**Example**: If grasp fails (no contact detected), retry with different approach angle

---

## Computational Considerations

### Real-Time Requirements

**Manipulation**: 0.1-1 second planning time acceptable (pick-and-place)

**Dynamic Locomotion**: Millisecond updates (MPC re-plans every 10-50ms)

**Solution**:
- Fast planners (RRT-Connect)
- Warm-start (reuse previous solution)
- Hardware acceleration (GPU parallelization)

### Dimensionality Challenge

**High-DOF Humanoids** (30+ joints):
- Full-body motion planning is hard
- Decomposition: Plan for subsystems (legs, arms separately)
- Prioritization: Plan end-effector path, then inverse kinematics for joints

---

## Practical Planning Pipeline

1. **Task Specification**: User/high-level planner specifies goal (grasp object)
2. **Inverse Kinematics**: Compute goal configuration(s)
3. **Collision-Free Path**: RRT plans joint-space path
4. **Trajectory Optimization**: Smooth path into trajectory with velocity/acceleration limits
5. **Execution**: Low-level controller tracks trajectory
6. **Reactive Adjustment**: Monitor for obstacles, adjust locally if needed

---

## Summary

Motion planning enables robots to navigate complex environments:

- **C-space**: Abstracts planning to finding collision-free path for a point in configuration space
- **Sampling-based methods** (RRT, PRM): Handle high-DOF robots, fast, probabilistically complete
- **Optimization-based**: Smooth, optimal trajectories (CHOMP, TrajOpt)
- **Path vs trajectory**: Paths are geometric, trajectories include timing
- **Reactive vs deliberative**: Global planning + local reactive adjustments
- **Manipulation challenges**: IK, task constraints, coordination

Modern humanoid systems combine deliberative global planning with reactive local adjustments, enabling robust operation in dynamic, uncertain environments.

---

## Related Topics

- **[Control Hierarchies](./control-hierarchies)** - How motion plans are executed through layered control
- **[Spatial Awareness](../../module-4-perception/spatial-awareness)** - Building environment models for planning
- **[Action-Perception Loop](./action-perception-loop)** - Integrating planning with real-time feedback
