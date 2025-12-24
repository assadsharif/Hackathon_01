---
sidebar_position: 2
title: Transfer Learning
description: Learn techniques for bridging the sim-to-real gap
---

# Transfer Learning

## Key Concepts

- **Domain Adaptation**: Techniques to transfer knowledge from source domain (sim) to target domain (real)
- **Domain Randomization**: Randomize simulation parameters to span real-world variations
- **System Identification**: Estimate real robot parameters to improve sim accuracy
- **Fine-Tuning**: Adapt sim-trained policies using limited real-world data
- **Sim-to-Real Transfer**: Successfully deploying simulation-trained policies on real robots

---

## Introduction

The sim-to-real gap creates a **domain shift**: policies optimized for simulation may fail catastrophically on real robots. **Transfer learning** addresses this through techniques that either (1) make simulation more realistic, (2) make policies robust to domain differences, or (3) adapt policies using limited real-world data.

This chapter covers practical methods for successful sim-to-real transfer in Physical AI.

---

## The Transfer Learning Problem

### Source vs Target Domain

**Source Domain** (Simulation):
- Abundant data (millions of samples)
- Fast, safe, scalable
- Imperfect physics, sensors, dynamics

**Target Domain** (Real World):
- Limited data (hundreds to thousands of samples)
- Slow, risky, expensive
- True physics

**Goal**: Use source domain to learn policy that performs well in target domain

---

### What Transfers and What Doesn't

**Transfers Well**:
- High-level strategies (where to grasp, when to step)
- Relative spatial relationships (object proximity, collision avoidance)
- Task structure (sequence of actions)

**Transfers Poorly**:
- Low-level control gains (PID parameters)
- Exact timing (due to latency differences)
- Fine force control (friction, compliance mismatch)

**Implication**: Design policies that rely on transferable features, not brittle low-level details

---

## Domain Randomization

### Core Idea

**Problem**: Simulation has fixed parameters (friction = 0.5), real world has variable parameters (friction ∈ [0.3, 0.7])

**Solution**: Train in simulation with randomized parameters—policy learns to be robust to variations

**Hypothesis**: If randomization spans real-world variations, policy will transfer

---

### What to Randomize

**1. Physics Parameters**
- **Friction**: Contact friction coefficients
- **Mass**: Object masses, link masses
- **Damping**: Joint damping, air resistance
- **Restitution**: Bounciness of collisions

**Example**: For grasping, randomize object mass (0.1-1.0 kg), friction (0.2-0.8)

---

**2. Visual Appearance**
- **Lighting**: Direction, intensity, color temperature
- **Textures**: Object textures, floor patterns
- **Camera**: Noise, exposure, white balance
- **Backgrounds**: Randomize scene clutter

**Example**: For vision-based grasping, randomize lighting and object textures so policy learns shape, not appearance

---

**3. Dynamics**
- **Motor gains**: Vary PID gains around nominal values
- **Delays**: Add random latencies (10-30ms)
- **Noise**: Add noise to sensor readings

**Example**: For locomotion, randomize joint damping and motor time constants

---

**4. Environment**
- **Obstacles**: Random positions, sizes
- **Surfaces**: Vary terrain slope, roughness
- **Distractors**: Add irrelevant objects

**Example**: For navigation, randomize obstacle layouts

---

### Automatic Domain Randomization (ADR)

**Motivation**: Hand-tuning randomization ranges is tedious—can we automate it?

**Approach**:
1. Start with narrow randomization ranges
2. Train policy
3. If policy performs well, widen ranges (increase difficulty)
4. If policy fails, narrow ranges
5. Repeat until convergence

**Example (OpenAI, 2020)**:
- Dexterous manipulation: ADR automatically tuned 100+ randomization parameters
- Result: Robust policies that transferred to real robot hand

---

## System Identification (Sys-ID)

### Core Idea

**Problem**: We don't know true parameters of real robot (friction, inertias, motor constants)

**Solution**: Estimate parameters from real robot data, use in simulation

---

### Process

1. **Collect Real-World Data**: Execute known trajectories, record state/action/next-state
2. **Parameter Estimation**: Fit simulation model to real data (minimize prediction error)
3. **Update Simulation**: Use identified parameters in training
4. **Iterate**: Re-train policy, collect more data, refine parameters

---

### Methods

**Black-Box Optimization**:
- Try different parameter values, simulate, compare to real data
- Use Bayesian optimization, CMA-ES to search parameter space

**Gradient-Based**:
- Use differentiable simulator (e.g., MuJoCo)
- Gradient descent on parameters to minimize sim-real error

**Example**: Identify joint friction by commanding torques, measuring joint velocities, fitting friction model

---

### Challenges

**1. Identifiability**: Some parameters are hard to distinguish
- Example: Motor torque constant vs gear ratio (both affect output torque)

**2. Non-Stationarity**: Parameters change over time
- Wear, temperature, battery voltage affect dynamics

**Solution**: Periodic re-identification, online adaptation

---

## Progressive Training

### Curriculum from Sim to Real

**Idea**: Gradually transition from easy (sim) to hard (real)

**Stages**:
1. **Stage 1**: Train in idealized simulation (no noise, perfect physics)
2. **Stage 2**: Add noise and randomization
3. **Stage 3**: Fine-tune on real robot with safety constraints
4. **Stage 4**: Unconstrained real-world deployment

**Benefit**: Policy learns basic skill in safe sim, then adapts to real-world nuances

---

## Fine-Tuning with Real-World Data

### Why Fine-Tuning Works

**Pre-Training (Sim)**: Learn general features (grasp affordances, balance strategies)

**Fine-Tuning (Real)**: Adjust to real-world specifics (actual friction, sensor noise)

**Benefit**: Requires far less real data than training from scratch

---

### Approaches

**1. Supervised Fine-Tuning**
- Collect demonstrations on real robot (teleoperation)
- Fine-tune sim-trained policy to mimic demonstrations

**2. Reinforcement Learning Fine-Tuning**
- Continue RL training on real robot
- Use sim-trained policy as initialization

**3. Residual Learning**
- Sim policy provides base action
- Small residual network learns correction from real data
- **Action = sim_policy(state) + residual(state)**

**Example**: Sim policy plans grasps, residual adjusts finger positions based on tactile feedback

---

## Privileged Information

### Concept

**In Simulation**: Access to privileged information (true object pose, contact forces, hidden state)

**In Reality**: No access (must rely on noisy sensors)

**Challenge**: How to use privileged info in training without requiring it at deployment?

---

### Teacher-Student Framework

**Teacher Policy** (simulation-only):
- Has access to privileged information
- Learns task using full state

**Student Policy** (deployment):
- Only has access to real sensors (vision, proprioception)
- Learns to imitate teacher

**Training**:
1. Train teacher in sim with privileged info
2. Collect (sensor_observation, teacher_action) pairs
3. Train student to predict teacher's actions from sensors
4. Deploy student (doesn't need privileged info)

**Example**:
- Teacher sees true object 6-DOF pose (privileged)
- Student only sees RGB image
- Student learns to infer pose from vision, imitates teacher's grasps

---

## Visual Domain Adaptation

### The Visual Gap

**Sim Images**: Synthetic, perfect, artifact-free
**Real Images**: Motion blur, noise, lighting variations, reflections

**Challenge**: Vision policies trained on sim images often fail on real images

---

### Techniques

**1. Photorealistic Rendering**
- Use advanced rendering (ray tracing, global illumination)
- Simulate camera artifacts (lens distortion, chromatic aberration)

**Limitation**: Expensive (slow rendering), still not perfect

---

**2. Domain Randomization (Visual)**
- Randomize lighting, textures, backgrounds
- Policy learns to ignore appearance, focus on geometry

**Success Story**: Tobin et al. (2017) - Object localization with only synthetic images, transferred to real

---

**3. CycleGAN / Image Translation**
- Train GAN to translate sim images → realistic images
- Train policy on translated images

**Process**:
1. Collect paired sim and real images (same scene)
2. Train CycleGAN (sim ↔ real translation)
3. Generate realistic images from sim
4. Train policy on realistic images

**Challenge**: Requires unpaired real images (easier) or paired (harder)

---

**4. Perception-Agnostic Representations**
- Use depth, segmentation, keypoints instead of raw RGB
- These transfer better (less sensitive to appearance)

**Example**: Policy uses depth images (from RGB-D in real, perfect depth in sim) instead of RGB

---

## What Transfers Easily vs Not

### Easy to Transfer

**1. Geometric Relationships**
- Spatial layouts, object positions
- These are sim-invariant (assuming accurate geometry)

**2. High-Level Policies**
- Task-level decisions (which object to grasp)
- Less sensitive to low-level dynamics

**3. Model-Free RL with Randomization**
- Policies that don't rely on precise models
- Robust to parameter variations

---

### Hard to Transfer

**1. Fine Manipulation**
- Insertion, threading, delicate grasping
- Requires accurate contact, friction, compliance

**2. Fluid/Deformable Interaction**
- Pouring, cutting, cloth manipulation
- Physics models are highly approximate

**3. Perception in Uncontrolled Lighting**
- Outdoor, variable lighting
- Hard to randomize exhaustively

**Solution for Hard Cases**: More real-world data, hybrid sim+real training

---

## Practical Transfer Pipeline

### Recommended Workflow

1. **Define Task**: Clear success criteria, expected variations
2. **Sim Training**: RL/imitation in simulation (millions of samples)
3. **Randomization**: Physics, visual, dynamics randomization
4. **Sys-ID** (optional): Identify key parameters from real robot
5. **Sim Validation**: Test with increasing randomization until robust
6. **Initial Real-World Test**: Deploy policy, measure success rate
7. **Analysis**: Where does it fail? (vision, contact, dynamics?)
8. **Fine-Tuning**: Collect targeted real data, fine-tune
9. **Iteration**: Adjust randomization based on failure modes, repeat

---

## Case Study: Sim-to-Real Quadruped Locomotion

**Task**: Legged robot walking on rough terrain

**Approach**:
1. **Simulation**: Train RL policy in Isaac Gym (1000 parallel robots)
2. **Randomization**: Terrain (slopes, stairs, obstacles), friction, mass, motor strength
3. **Privileged Info**: Terrain height map (teacher), only proprioception (student)
4. **Transfer**: Deploy student policy on real robot (ANYmal)

**Result**: Zero-shot transfer—robot walked on real terrain without real-world training

**Key Factors**:
- Aggressive terrain randomization spanned real variations
- Student learned robust proprioceptive policy
- High-frequency control (100Hz) reduced latency sensitivity

---

## Summary

Successful sim-to-real transfer requires strategic use of multiple techniques:

- **Domain randomization**: Vary physics, visuals, dynamics to span real-world variations
- **System identification**: Estimate real robot parameters to improve sim fidelity
- **Fine-tuning**: Adapt sim-trained policies with limited real data (supervised, RL, residual)
- **Privileged information**: Teacher-student framework uses sim-only data to train sensor-based policies
- **Visual domain adaptation**: Photorealism, randomization, image translation, depth-based policies
- **What transfers**: Geometry, high-level strategies, robust policies
- **What doesn't**: Fine manipulation, complex physics (fluids, deformables), precise low-level control
- **Practical pipeline**: Sim training → randomization → sys-ID → real testing → fine-tuning → iteration

Effective transfer combines multiple approaches—no single technique solves the sim-to-real gap, but together they enable robust real-world performance from simulation-trained policies.

---

## Related Topics

- **[Simulation vs. Reality](./simulation-vs-reality)** - Understanding the sim-to-real gap
- **[Reinforcement Learning](./reinforcement-learning)** - Learning methods that benefit from sim-to-real
- **[Multimodal Sensing](../../module-4-perception/multimodal-sensing)** - Sensor modalities for transfer (depth, tactile)
