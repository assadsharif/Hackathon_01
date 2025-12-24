---
sidebar_position: 1
title: Simulation vs. Reality
description: Understand the tradeoffs between simulated and real-world robot learning
---

# Simulation vs. Reality

## Key Concepts

- **Sim-to-Real Gap**: Discrepancy between simulated and real-world robot behavior
- **Physics Simulation**: Virtual environment modeling robot dynamics, contacts, sensors
- **Sample Efficiency**: Amount of data needed to learn a skill
- **Reality Gap**: Differences in physics, sensors, actuation between simulation and reality
- **Deployment**: Transferring learned policies from simulation to real robots

---

## Introduction

Training robots in the real world is expensive, time-consuming, and risky (robots can break, humans can get hurt). **Simulation** offers a solution: train robots in virtual environments where failures are free, time can be accelerated, and variations can be systematically explored. However, simulations are imperfect—the **sim-to-real gap** means policies that work perfectly in simulation often fail on real robots.

This chapter explores the tradeoffs between simulation and reality, and when each is appropriate for robot learning.

---

## Why Use Simulation?

### 1. Safety

**Real World**: Robot failures can cause damage, injury
- Humanoid falling during learning → $100K+ repair
- Grasping errors → broken objects, gripper damage

**Simulation**: Failures are free
- Reset to initial state instantly
- No physical consequences

**Use Case**: Learning risky behaviors (dynamic locomotion, aggressive manipulation)

---

### 2. Speed

**Real World**: Learning happens in real-time
- 1 hour of training = 1 hour elapsed
- Slow reset (human must intervene)

**Simulation**: Accelerate time
- Simulate 1000 hours in 1 hour (1000x speedup)
- Instant reset (no human intervention)

**Use Case**: Reinforcement learning (requires millions of samples)

---

### 3. Scalability

**Real World**: Limited to physical robot count
- 1 robot → 1 trajectory at a time
- Expensive to scale ($50K-$1M per robot)

**Simulation**: Parallelize across GPUs
- 1000 virtual robots → 1000 parallel trajectories
- Marginal cost near zero

**Use Case**: Large-scale data collection (vision datasets, grasping datasets)

---

### 4. Systematic Exploration

**Real World**: Environment is fixed
- Hard to vary object properties, lighting, surfaces
- Can't control all variables

**Simulation**: Full control
- Systematically vary friction, mass, shape
- Test edge cases (low-friction surfaces, heavy objects)

**Use Case**: Robustness testing, understanding failure modes

---

## Why Use Real World?

### 1. Reality is the Ground Truth

**Simulation**: Approximation of reality
- Physics engines simplify contact, friction, deformation
- Sensor models are idealized

**Real World**: No approximation
- True physics, sensor noise, actuation limits

**Implication**: Policies that work in real world are guaranteed to work in deployment

---

### 2. Unmodeled Phenomena

**Hard to Simulate**:
- **Soft object deformation**: Grasping cloth, foam, food
- **Fluid dynamics**: Pouring, stirring, washing
- **Complex contacts**: Multi-contact manipulation, friction
- **Sensor artifacts**: Motion blur, lens distortion, tactile sensor hysteresis

**Real World**: Captures all phenomena automatically

**Use Case**: Tasks involving complex physics (deformable manipulation, fluid handling)

---

### 3. Deployment Environment

**Simulation**: Controlled, idealized
- Perfect lighting, clean surfaces
- No unexpected objects or people

**Real World**: Messy, unpredictable
- Variable lighting, clutter, distractions
- Humans in the loop

**Implication**: Real-world training exposes robot to deployment conditions

---

## The Sim-to-Real Gap

### Sources of Discrepancy

**1. Physics Modeling Errors**
- **Contact**: Simulation uses simplified contact models (penalty-based, impulse-based)
- **Friction**: Friction cones are approximations
- **Compliance**: Real actuators have elasticity (joint stiffness varies with load)

**Example**: Simulated robot walks perfectly, real robot's feet slip (friction mismatch)

---

**2. Sensor Modeling Errors**
- **Vision**: Simulated cameras lack motion blur, rolling shutter, auto-exposure
- **Depth**: Simulated depth is perfect, real RGB-D has noise, missing data (reflective/transparent surfaces)
- **Tactile**: Hard to model sensor dynamics (hysteresis, drift)

**Example**: Vision policy works with perfect sim images, fails with real camera artifacts

---

**3. Actuation Modeling Errors**
- **Motor dynamics**: Simulated motors respond instantly, real motors have delays, backlash
- **Torque limits**: Simulated limits are hard constraints, real motors have soft limits (current spikes)

**Example**: Simulation achieves aggressive trajectory, real robot saturates actuators

---

**4. Unmodeled Delays**
- **Computation**: Simulation assumes zero latency, real systems have 10-50ms delay (sensing → actuation)
- **Communication**: Real robots have network delays (wireless control)

**Example**: Simulated feedback control is tight, real control oscillates due to latency

---

## When to Use Simulation vs Real World

### Decision Framework

| **Factor** | **Prefer Simulation** | **Prefer Real World** |
|------------|----------------------|----------------------|
| **Sample Efficiency** | Low (RL, need millions of samples) | High (few demos, imitation learning) |
| **Physics Complexity** | Simple (rigid objects, basic contact) | Complex (deformables, fluids, multi-contact) |
| **Risk** | High (dynamic locomotion, aggressive manipulation) | Low (slow, safe tasks) |
| **Deployment Environment** | Known, controlled | Unstructured, variable |
| **Budget** | Limited (simulation is cheap) | Sufficient (real robots available) |
| **Task** | Requires exploration (RL, randomized search) | Requires precision (calibration, fine manipulation) |

---

### Hybrid Approach (Common in Practice)

**Strategy**: Pre-train in simulation, fine-tune in real world

**Example Workflow**:
1. **Simulation**: Learn locomotion policy (1M steps, 10 GPU-hours)
2. **Transfer**: Deploy to real robot
3. **Real-World Fine-Tuning**: Adapt to real physics (1K steps, 1 hour)

**Benefit**: Leverage speed of simulation + accuracy of real world

---

## Case Studies

### 1. OpenAI Dactyl (Rubik's Cube Manipulation)

**Task**: Humanoid hand solves Rubik's cube

**Approach**:
- **Simulation**: RL in MuJoCo simulator (100 years simulated experience)
- **Domain Randomization**: Vary cube size, friction, hand dynamics
- **Transfer**: Deploy to real Shadow Hand

**Result**: Successful cube solving in real world (50 consecutive solves)

**Key Insight**: Aggressive randomization compensates for sim-to-real gap

---

### 2. Boston Dynamics (Atlas Parkour)

**Task**: Humanoid navigates obstacle course (jumps, balancing)

**Approach**:
- **Simulation**: Model-based trajectory optimization in custom simulator
- **Real-World Testing**: Extensive iteration on real robot
- **Controller Robustness**: QP whole-body controller handles model mismatch

**Result**: Dynamic parkour in real world

**Key Insight**: Simulation for trajectory design, real-world for validation and tuning

---

### 3. Google Robot Grasping (Everyday Objects)

**Task**: Grasp diverse objects in cluttered bins

**Approach**:
- **Real-World Data**: 800K grasps collected with robot farm (14 robots, several months)
- **No Simulation**: Train vision-based grasping policy directly from real data

**Result**: 96% grasp success on novel objects

**Key Insight**: For vision-based tasks with simple physics (grasping rigid objects), real-world data can be sample-efficient enough to avoid simulation

---

## Simulation Tools for Physical AI

### Physics Engines

**MuJoCo** (Multi-Joint dynamics with Contact)
- Fast, differentiable physics
- Used for RL, trajectory optimization
- Good for: Locomotion, manipulation

**PyBullet**
- Open-source, Python API
- Real-time simulation
- Good for: Research prototyping, education

**Isaac Gym** (NVIDIA)
- GPU-accelerated, thousands of parallel envs
- Tensor-based API (PyTorch integration)
- Good for: Large-scale RL

**Gazebo**
- ROS-integrated, realistic sensors
- Good for: Full-system testing, autonomous navigation

---

### Rendering Engines (for Vision)

**Blender**
- Photorealistic rendering
- Good for: Generating synthetic vision datasets

**UnrealEngine / Unity**
- Game engines, real-time rendering
- Good for: Interactive sim-to-real (visual domain randomization)

---

## Limitations of Simulation

### 1. Accuracy-Speed Tradeoff

**Accurate Simulation** (e.g., FEM for soft bodies): Slow (minutes per second)
**Fast Simulation** (e.g., rigid body): Inaccurate for complex tasks

**Implication**: Can't have both—must choose based on task

---

### 2. Unknown Unknowns

**Problem**: You don't know what you don't know
- Simulation omits phenomena you didn't think to model
- Real world surprises with edge cases

**Example**: Dust on gripper fingers reduces friction → grasps fail (not modeled in sim)

---

### 3. Validation Challenge

**Problem**: How do you know simulation is accurate?
- Requires real-world validation (defeats purpose of sim-only training)
- Model parameters are hard to measure (friction coefficients, joint stiffness)

**Solution**: Sim-to-real methods (domain randomization, system ID) address this

---

## Summary

Simulation and real-world training each have distinct advantages:

- **Simulation advantages**: Safety, speed (1000x), scalability (1000s of robots), systematic exploration
- **Real-world advantages**: Ground truth physics, unmodeled phenomena (deformables, fluids), deployment conditions
- **Sim-to-real gap**: Physics, sensor, actuation, delay discrepancies
- **Decision framework**: Consider sample efficiency, physics complexity, risk, budget
- **Hybrid approach**: Pre-train in sim, fine-tune in real (common in practice)
- **Simulation tools**: MuJoCo, PyBullet, Isaac Gym, Gazebo for physics; Blender, Unity for vision

Effective Physical AI development strategically combines simulation (for efficient exploration) and real-world testing (for validation and adaptation).

---

## Related Topics

- **[Transfer Learning](./transfer-learning)** - Techniques for bridging the sim-to-real gap
- **[Reinforcement Learning](./reinforcement-learning)** - Learning methods that leverage simulation
- **[Physical Interaction Learning](../../module-2-embodied/physical-interaction-learning)** - Real-world learning through interaction
