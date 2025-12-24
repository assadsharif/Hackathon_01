---
sidebar_position: 2
title: Control Hierarchies
description: Understand layered control architectures for complex robots
---

# Control Hierarchies

## Key Concepts

- **Hierarchical Control**: Multi-level control architecture (task → motion → joint levels)
- **Task-Level Control**: High-level goal specification (pick up cup, walk forward)
- **Motion-Level Control**: Trajectory generation and coordination
- **Joint-Level Control**: Low-level motor commands (torque, position)
- **Whole-Body Control**: Coordinating all robot DOFs simultaneously

---

## Introduction

Complex robots like humanoids have 30+ joints, multiple sensors, and must perform intricate tasks (walk while carrying object, maintain balance during manipulation). Managing this complexity requires **hierarchical control**—organizing control into layers, each operating at different timescales and abstraction levels.

This chapter explores how control hierarchies enable humanoids to plan tasks, coordinate motion, and execute precise joint commands.

---

## Why Hierarchical Control?

### The Complexity Problem

**Challenge**: Directly mapping high-level goals ("pick up cup") to motor commands is intractable.

**Example**:
- User wants robot to "fetch cup from table"
- This requires: navigate to table, reach for cup, grasp, lift, carry
- Each subtask involves 10-30 joints, coordination, collision avoidance

**Solution**: Break problem into levels of abstraction.

---

## The Three-Layer Architecture

### 1. Task Level (High-Level Planning)

**What**: Goal specification, sequencing

**Abstraction**: Symbolic reasoning about objects, actions, goals

**Examples**:
- "Grasp cup, then pour into bowl"
- "Walk to door, open it, pass through"

**Output**: Task plan (sequence of actions)

**Timescale**: Seconds to minutes

**Methods**:
- Task planning (PDDL planners, behavior trees)
- Learning (LLM-based task decomposition, reinforcement learning)

---

### 2. Motion Level (Trajectory Generation)

**What**: Translate task-level actions into continuous motion

**Abstraction**: Trajectories in joint space or Cartesian space

**Examples**:
- Given "grasp cup," compute arm trajectory to approach, finger closure
- Given "walk forward," generate foot placements, CoM trajectory

**Output**: Desired trajectories (position, velocity, acceleration over time)

**Timescale**: 0.1-1 second (re-plan dynamically)

**Methods**:
- Motion planning (RRT, trajectory optimization)
- Model Predictive Control (MPC)
- Learned motion primitives

---

### 3. Joint Level (Low-Level Control)

**What**: Track desired trajectories with motor commands

**Abstraction**: Control individual actuators (motors, hydraulics)

**Examples**:
- PID control to track joint angle setpoint
- Torque control for force regulation

**Output**: Motor commands (voltage, current, torque)

**Timescale**: 1-10 milliseconds (real-time feedback loop)

**Methods**:
- PID (Proportional-Integral-Derivative) control
- Impedance control (regulate stiffness, damping)
- Adaptive control (adjust to parameter changes)

---

## Information Flow

### Top-Down (Command)
```
Task Level: "Grasp cup"
    ↓
Motion Level: "Move arm to pre-grasp pose, close gripper"
    ↓
Joint Level: "Track desired joint angles θ₁(t), θ₂(t), ... θ₇(t)"
```

### Bottom-Up (Feedback)
```
Joint Level: "Current joint state, torque measurements"
    ↓
Motion Level: "Collision detected, object slipped"
    ↓
Task Level: "Grasp failed, retry or abort"
```

**Key Insight**: Each level operates independently but communicates through interfaces—enables modularity, fault isolation.

---

## Whole-Body Control for Humanoids

### The Challenge

**Problem**: Humanoids have many DOFs (30+), multiple objectives (balance, reach, avoid obstacles), limited actuation.

**Example**: Robot walks while manipulating object
- **Legs**: Maintain balance, generate locomotion
- **Arms**: Reach and manipulate object
- **Torso**: Counterbalance arm motion to avoid tipping

**Goal**: Coordinate all joints to satisfy multiple objectives simultaneously.

---

### Whole-Body Control Formulation

**Approach**: Optimization-based control

**Variables**: Joint accelerations q̈

**Objective**: Minimize weighted sum of task errors

**Constraints**:
- Dynamics (equations of motion)
- Joint limits
- Contact forces (feet on ground)

**Example Formulation**:
```
minimize: w₁·||CoM_acceleration - desired_CoM|| + w₂·||hand_position - desired_hand|| + w₃·||joint_torques||²

subject to:
  - Robot dynamics
  - Feet remain in contact with ground
  - Joint limits
```

**Output**: Joint torques that achieve multiple objectives while respecting constraints

---

## Task Prioritization

### The Prioritization Problem

**Challenge**: Multiple objectives may conflict (can't satisfy all perfectly).

**Example**:
- **High priority**: Maintain balance (avoid falling)
- **Medium priority**: Reach target (manipulation task)
- **Low priority**: Minimize energy

**Solution**: Priority hierarchy—satisfy high-priority tasks first, use remaining DOFs for lower priorities.

---

### Null-Space Projection

**Concept**: Redundant robots have more DOFs than needed for primary task—use extra DOFs for secondary tasks.

**Example**: 7-DOF arm grasping object
- **Primary**: End-effector reaches grasp pose (6 DOF constraint)
- **Null-space** (1 DOF remaining): Optimize elbow position to avoid obstacle

**Method**: Project secondary task into null-space of primary task (secondary task doesn't interfere with primary)

---

### Prioritized Control

**Levels**:
1. **Priority 1** (critical): Balance, contact stability
2. **Priority 2** (functional): Task objectives (reach, grasp)
3. **Priority 3** (optimization): Energy, comfort, singularity avoidance

**Execution**: Solve for Priority 1 first, then Priority 2 within null-space, then Priority 3.

---

## Feedback at Each Level

### Task-Level Feedback

**Sensors**: Vision (object detected?), touch (contact made?), task completion metrics

**Decisions**:
- Task success/failure
- Re-plan if environment changes
- Switch to backup strategy

**Example**: Vision detects cup moved → re-plan grasp approach

---

### Motion-Level Feedback

**Sensors**: Joint encoders (position), IMU (body orientation), force sensors

**Decisions**:
- Re-plan trajectory if collision detected
- Adjust motion to maintain balance
- Compensate for disturbances (push recovery)

**Example**: Unexpected push → MPC re-computes CoM trajectory to prevent fall

---

### Joint-Level Feedback

**Sensors**: Joint encoders (position, velocity), current sensors (motor torque)

**Decisions**:
- Adjust motor commands to track desired trajectory
- Detect saturation (joint limit reached)
- Safety monitoring (excessive torque → emergency stop)

**Example**: PID controller adjusts motor voltage to minimize tracking error

---

## Real-World Control Architecture: Case Study (Atlas)

**Boston Dynamics Atlas** uses hierarchical control:

### Task Layer
- Behavior finite state machine (walk, stand, manipulate)
- Transition logic (if balance lost → recovery mode)

### Motion Layer
- **Locomotion**: MPC re-plans foot placements every 50ms
- **Manipulation**: Trajectory optimization for arm motion
- **Whole-body**: Quadratic program (QP) solver coordinates all joints

### Joint Layer
- Custom motor controllers (1kHz update rate)
- Torque control with gravity compensation
- Force feedback for contact detection

**Result**: Dynamic walking, running, jumping, manipulation—all coordinated through hierarchy.

---

## Challenges in Hierarchical Control

### 1. Inter-Level Communication

**Problem**: Information loss between levels (task planner doesn't see low-level dynamics)

**Solution**: Feedback channels, task monitoring, re-planning triggers

---

### 2. Computational Load

**Problem**: High-frequency control (1kHz joint-level) + expensive optimization (MPC, QP)

**Solution**:
- Dedicated hardware (real-time CPUs, GPUs)
- Approximate solvers (warm-start, early termination)
- Hierarchy itself (simple control at high frequency, complex at low frequency)

---

### 3. Modeling Errors

**Problem**: Controllers assume model accuracy (dynamics, contact), but real robots differ

**Solution**:
- Adaptive control (update model online)
- Robust control (account for uncertainty)
- Learning (adjust controller from data)

---

## Learning in Control Hierarchies

### Task-Level Learning

**Approach**: Learn task decomposition, action sequencing

**Methods**: Reinforcement learning, LLM-based planning

**Example**: Learn "to pour, first grasp, then tilt at 30° while monitoring flow"

---

### Motion-Level Learning

**Approach**: Learn motion primitives, trajectory distributions

**Methods**: Imitation learning, RL in simulation

**Example**: Learn diverse grasping motions from human demonstrations

---

### Joint-Level Learning

**Approach**: Learn low-level policies that compensate for modeling errors

**Methods**: Model-based RL, adaptive control

**Example**: Learn torque corrections to handle unknown object mass

---

## Summary

Hierarchical control manages complexity in humanoid robots:

- **Three layers**: Task (goal sequencing), motion (trajectory generation), joint (motor commands)
- **Whole-body control**: Optimize all DOFs simultaneously to satisfy multiple objectives
- **Task prioritization**: Critical tasks (balance) take precedence, secondary tasks use remaining DOFs
- **Feedback at all levels**: Task success monitoring, motion re-planning, joint tracking
- **Real-world systems** (Atlas): Combine optimization-based whole-body control with fast joint-level feedback

Hierarchical organization enables modularity, fault tolerance, and scalability—essential for complex robots operating in unstructured environments.

---

## Related Topics

- **[Motion Planning](./motion-planning)** - Generating trajectories at the motion level
- **[Action-Perception Loop](./action-perception-loop)** - Feedback integration across control levels
- **[Bipedal Locomotion](../../module-3-humanoid/bipedal-locomotion)** - Whole-body control for walking
