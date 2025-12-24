---
sidebar_position: 3
title: Action-Perception Loop
description: Explore the feedback cycle at the heart of embodied intelligence
---

# Action-Perception Loop

## Key Concepts

- **Action-Perception Loop**: Continuous cycle where actions produce sensory feedback that informs next actions
- **Closed-Loop Control**: Control with feedback (vs open-loop: no feedback)
- **Reactive Control**: Immediate response to sensory input
- **Model-Based Control**: Use internal model to predict outcomes
- **Sensorimotor Contingencies**: Learned associations between actions and sensory changes

---

## Introduction

Unlike disembodied AI (process input → produce output), Physical AI exists in a continuous **action-perception loop**: robots act on the world, perceive the consequences, and adjust their actions accordingly. This closed-loop nature is fundamental to embodied intelligence—it enables adaptation, learning, and robust interaction with unpredictable environments.

This chapter explores how the action-perception loop shapes control strategies, learning, and the very notion of intelligence in physical systems.

---

## The Closed-Loop Nature of Physical Intelligence

### Open-Loop vs Closed-Loop

**Open-Loop Control** (no feedback):
- Execute pre-planned action sequence
- No adjustment based on outcomes
- Fast, simple
- Fragile (fails if environment differs from expectation)

**Example**: Robot arm follows trajectory to grasp object
- **Failure mode**: If object moved slightly, grasp misses (no correction)

---

**Closed-Loop Control** (with feedback):
- Continuously sense state
- Adjust actions based on sensory feedback
- Robust to disturbances
- Slower (sensing, computation overhead)

**Example**: Robot arm uses vision to track object, adjusts trajectory in real-time
- **Success**: Even if object moves, robot compensates

---

### Why Embodied Systems Require Closed-Loop

**Physical World is Unpredictable**:
- Objects shift position
- Surfaces have variable friction
- Humans walk into workspace
- Sensors are noisy

**Implication**: Pre-planned actions (open-loop) fail. Feedback (closed-loop) is essential for robustness.

---

## The Action-Perception Cycle

### The Loop

```
1. Perception: Sense current state (vision, touch, proprioception)
    ↓
2. Decision: Compute desired action (planning, control policy)
    ↓
3. Action: Execute motor commands (move joints)
    ↓
4. World Changes: Robot body and environment respond
    ↓
5. Perception: Sense new state → repeat
```

**Key Properties**:
- **Continuous**: No fixed start/end (loop runs at 10-1000 Hz)
- **Coupled**: Perception depends on action (where you look matters), action depends on perception
- **Emergent**: Intelligence emerges from loop dynamics, not individual steps

---

## Reactive Control

### Definition

**Reactive Control**: Generate actions directly from sensory input, no internal model or planning.

**Characteristics**:
- Fast (millisecond responses)
- Local reasoning (only current percept)
- No memory of past states
- Simple mappings (sensor → action)

---

### Examples

**1. Obstacle Avoidance (Potential Fields)**
- **Perception**: Laser scan detects obstacle at distance d
- **Action**: Steer away with force ∝ 1/d²
- **Loop**: Continuously sense obstacle distance, adjust steering

**2. Grasping Reflex**
- **Perception**: Touch sensor detects contact
- **Action**: Close gripper
- **Loop**: Adjust grip force based on tactile feedback (if slipping, increase force)

**3. Balance Reflexes (Humanoids)**
- **Perception**: IMU detects tilt
- **Action**: Shift CoM to counteract (ankle strategy, hip strategy)
- **Loop**: Real-time balance adjustments (200 Hz update)

---

### Strengths and Limitations

**Strengths**:
- Fast response (no planning overhead)
- Handles dynamic environments (reacts to changes instantly)
- Simple implementation

**Limitations**:
- No foresight (can't plan multi-step tasks)
- Local minima (gets stuck when reactive heuristic fails)
- No learning (fixed mapping)

---

## Model-Based Control

### Definition

**Model-Based Control**: Use internal model of robot and environment to predict outcomes, plan actions.

**Components**:
- **Forward Model**: Predict next state given current state and action
- **Inverse Model**: Compute action needed to reach desired state

---

### How Models Enable Prediction

**Forward Model** Example:
- **Input**: Current arm pose, motor command "extend elbow 10°"
- **Output**: Predicted arm pose after action
- **Use**: Simulate action before executing (mental imagery)

**Inverse Model** Example:
- **Input**: Current hand position, desired hand position
- **Output**: Joint angles needed to reach desired position
- **Use**: Inverse kinematics for reaching

---

### Model Predictive Control (MPC)

**Approach**:
1. **Predict**: Use forward model to simulate future trajectories (next N timesteps)
2. **Optimize**: Choose action sequence that minimizes cost (reach goal, avoid obstacles)
3. **Execute**: Apply first action
4. **Re-plan**: Sense new state, repeat (receding horizon)

**Advantages**:
- Global reasoning (considers future consequences)
- Optimal within horizon
- Handles constraints (joint limits, collisions)

**Challenges**:
- Computationally expensive (optimization every timestep)
- Requires accurate model (mismatch → poor performance)

**Example**: Bipedal walking MPC
- **Horizon**: Next 10 steps (1 second)
- **Predict**: CoM trajectory for candidate foot placements
- **Optimize**: Choose placements that maintain balance, progress toward goal
- **Re-plan**: Every 50ms based on current state

---

## Learning Sensorimotor Contingencies

### What are Sensorimotor Contingencies?

**Definition**: Learned associations between actions and resulting sensory changes.

**Example**:
- **Action**: Move eye to the right
- **Sensory Change**: Visual scene shifts left
- **Contingency**: "When I move eye right, world appears to move left"

**Significance**: These learned mappings constitute understanding of how the body interacts with the world.

---

### Learning the Action-Perception Loop

**Approach**: Robot explores environment, learns predictive models.

**Self-Supervised Learning**:
1. **Collect Data**: Execute random actions, observe outcomes
2. **Learn Forward Model**: Train neural network to predict sensory feedback given action
3. **Use Model**: For planning (simulate actions), anomaly detection (unexpected feedback)

**Example**: Robot learns to predict tactile feedback when grasping
- **Training**: Grasp many objects, record finger contact patterns
- **Model**: Neural network predicts contact pattern given grasp pose
- **Application**: Plan grasps that maximize contact area (stable grasp)

---

### Affordance Learning through Interaction

**Affordances**: Action possibilities offered by environment

**Learning Process**:
1. **Interact**: Robot pushes, grasps, pokes objects
2. **Observe**: Which actions succeeded? (object moved, was grasped, etc.)
3. **Learn**: Associate object properties (shape, size) with action outcomes

**Example**: Learn "graspability"
- **Observation**: Cylindrical objects with handles afford grasping at handle
- **Generalization**: New object with handle → likely graspable there

---

## Feedback at Multiple Timescales

### Fast Reflexes (1-10 ms)

**Purpose**: Safety, stabilization

**Examples**:
- Collision detection → emergency stop
- Joint torque limit → reduce motor command

**Control**: Hard-coded, low-level (firmware, hardware safety circuits)

---

### Reactive Control (10-100 ms)

**Purpose**: Real-time adaptation, disturbance rejection

**Examples**:
- Balance recovery (humanoid pushed)
- Grasp force adjustment (object slipping)

**Control**: Feedback loops (PID, impedance control), reactive policies

---

### Deliberative Planning (100 ms - seconds)

**Purpose**: Task execution, goal achievement

**Examples**:
- Motion planning (compute collision-free path)
- Task re-planning (object moved, switch grasp strategy)

**Control**: Optimization (MPC, trajectory optimization), learned policies

---

### Long-Term Learning (hours - days)

**Purpose**: Skill acquisition, adaptation to environment

**Examples**:
- Learn object properties from repeated interactions
- Calibrate sensors (vision-proprioception alignment)

**Control**: Offline learning (batch updates to models, policies)

---

## How Embodiment Shapes the Control Problem

### Active Perception

**Insight**: Perception is not passive—actions shape what is perceived.

**Example**: Robot moves head to see occluded object
- **Action influences perception**: Changing viewpoint reveals hidden information
- **Perception guides action**: Visual feedback indicates where to look next

**Implication**: Planning must consider both task goals (reach object) and perceptual goals (observe object)

---

### Morphological Computation

**Insight**: Body structure performs computation (reduces control burden).

**Example**: Passive dynamic walker (robot with no motors)
- **Body structure** (leg length, mass distribution, joint stiffness) encodes walking dynamics
- **Control**: Minimal (just trigger step, gravity does rest)

**Implication**: Well-designed bodies simplify control—action-perception loop exploits physical properties.

---

### Situatedness

**Insight**: Intelligence is context-dependent—what works depends on environment.

**Example**: Grasping strategy for fragile vs rigid objects
- **Fragile**: Gentle grip, tactile feedback to avoid crushing
- **Rigid**: Firm grip, less sensitivity needed

**Implication**: Control policies must adapt to context (learned or parameterized)

---

## Combining Reactive and Model-Based Control

### Hybrid Architectures

**Approach**: Use both reactive and model-based control together.

**Layer 1 (Reactive)**: Fast reflexes, safety, stabilization
**Layer 2 (Model-Based)**: Planning, optimization, goal achievement

**Example: Humanoid Manipulation**
- **Model-Based (Motion Layer)**: Plan arm trajectory to grasp
- **Reactive (Joint Layer)**: PID tracks trajectory, impedance control handles contact

**Benefit**: Robustness (reactive handles unexpected) + optimality (model-based plans globally)

---

## Challenges

### Model Inaccuracy

**Problem**: Forward models are never perfect (friction, contact, deformation are hard to model)

**Solution**:
- **Robust control**: Design controllers that tolerate model errors
- **Adaptive models**: Update model online from data
- **Model-free learning**: Learn policies directly, bypass explicit model

---

### Sensor Latency

**Problem**: Sensing, computation, actuation take time (10-50ms delay)

**Solution**:
- **Predictive control**: Predict future state, act on prediction
- **State estimation**: Kalman filter fuses delayed measurements
- **Fast control loops**: Minimize latency (dedicated hardware)

---

### Exploration vs Exploitation

**Problem**: Learning requires exploration (try new actions), but task execution requires exploitation (use best-known actions)

**Solution**:
- **Curriculum learning**: Safe exploration in easy scenarios, transfer to hard
- **Sim-to-real**: Explore in simulation, deploy in real world
- **Active learning**: Strategically explore uncertain regions

---

## Summary

The action-perception loop is central to embodied intelligence:

- **Closed-loop control**: Continuous feedback enables robustness to unpredictability
- **Reactive control**: Fast, local adjustments (potential fields, reflexes)
- **Model-based control**: Global planning using forward models (MPC, trajectory optimization)
- **Sensorimotor contingencies**: Learned mappings between actions and sensory changes
- **Multiple timescales**: Fast reflexes, reactive control, deliberative planning, long-term learning
- **Embodiment shapes control**: Active perception, morphological computation, situatedness

Effective Physical AI systems combine reactive and model-based strategies, leverage embodiment, and continuously learn from interaction—closing the loop between perception and action at multiple timescales.

---

## Related Topics

- **[Control Hierarchies](./control-hierarchies)** - How the action-perception loop operates at multiple control levels
- **[Sensorimotor Integration](../../module-2-embodied/sensorimotor-integration)** - Neural mechanisms underlying the action-perception loop
- **[Physical Interaction Learning](../../module-2-embodied/physical-interaction-learning)** - Learning through the action-perception loop
