---
sidebar_position: 2
title: Bipedal Locomotion
description: Understand the challenges of two-legged walking for robots
---

# Bipedal Locomotion

## Key Concepts

- **Bipedal Locomotion**: Walking on two legs
- **Zero Moment Point (ZMP)**: Point where tipping forces are zero
- **Center of Mass (CoM)**: Average position of mass distribution
- **Gait**: Pattern of leg movement during locomotion
- **Static vs Dynamic Stability**: Balanced at rest vs balanced through motion

---

## Introduction

Bipedal walking is deceptively difficult. Humans make it look effortless, but roboticists have spent decades trying to match even a toddler's walking ability. Why is standing and walking on two legs so challenging?

This chapter explores the fundamental difficulties of bipedal locomotion and the strategies robots use to achieve stable walking.

---

## Why Bipedal Locomotion is Hard

### The Fundamental Challenge
**Problem**: Two-legged systems are inherently unstable—small perturbations can cause falls.

**Why?**
- **Small support base**: Only feet contact ground (vs four-legged animals)
- **High center of mass**: Body weight is elevated, creating large tipping moments
- **Underactuated**: Cannot directly control CoM position—only apply forces through feet

### Contrast with Wheeled/Four-Legged Robots

| Locomotion Type | Stability | Terrain Capability | Energy Efficiency |
|----------------|-----------|-------------------|-------------------|
| **Wheeled** | High (always supported) | Flat surfaces only | Excellent |
| **Quadruped** | High (3+ legs always down) | Rough terrain | Good |
| **Biped** | Low (frequent weight shifts) | Human-designed spaces | Moderate |

**Bipedal Advantage**: Navigate stairs, narrow spaces, human environments—but at the cost of complexity.

---

## Key Concepts in Bipedal Stability

### Zero Moment Point (ZMP)

**Definition**: The point on the ground where the sum of tipping moments is zero.

**Intuition**: If ZMP stays within the support polygon (area between feet), the robot won't tip over.

**ZMP Criterion**: For stable walking, keep ZMP inside the foot/feet contact region.

**How Robots Use ZMP**:
- Plan trajectories that maintain ZMP within support
- Monitor ZMP in real-time and adjust gait if approaching boundary
- Conservative walking (static stability) keeps ZMP centered

---

### Center of Mass (CoM) Control

**Goal**: Move the CoM (body's average mass position) along desired trajectory while maintaining stability.

**Challenge**: CoM cannot be directly controlled—only influenced by applying forces through feet.

**Strategy**: Plan joint trajectories that move CoM while satisfying ZMP constraints.

---

## Gait Types

### Static Walking
**Definition**: CoM always remains above support polygon—robot could freeze at any moment without falling.

**Characteristics**:
- Slow, deliberate
- High stability margin
- Low energy efficiency

**Example**: ASIMO's early walking (0.5 m/s)

### Dynamic Walking
**Definition**: CoM may venture outside support polygon during motion—stability emerges from forward momentum.

**Characteristics**:
- Faster, more natural
- Requires continuous motion (can't freeze mid-step)
- Higher energy efficiency (like falling forward and catching yourself)

**Example**: Atlas running and jumping, human walking

---

## Control Strategies

### Trajectory Optimization
**Approach**: Pre-compute trajectories that satisfy ZMP constraints, then track with joint-level control.

**Pros**: Predictable, proven for flat terrain
**Cons**: Cannot adapt to unexpected disturbances

### Model Predictive Control (MPC)
**Approach**: Continuously re-plan short-horizon trajectories based on current state.

**Pros**: Can handle disturbances, adapt to terrain changes
**Cons**: Computationally expensive, requires accurate model

### Learning-Based Control
**Approach**: Train neural network policies through reinforcement learning (often in simulation).

**Pros**: Can discover novel gaits, adapt to diverse terrains
**Cons**: Requires extensive training, sim-to-real gap

---

## Challenges in Real-World Walking

### Uneven Terrain
**Problem**: Flat-ground assumptions break down on stairs, slopes, rubble.

**Solutions**:
- Vision-based terrain classification
- Adaptive foot placement
- Compliant leg control (absorb impacts)

### External Disturbances
**Problem**: Pushes, slippery surfaces, unexpected obstacles.

**Solutions**:
- Rapid re-planning (adjust within one step)
- Whole-body momentum control
- Foot slip detection and recovery

### Energy Efficiency
**Problem**: Walking is metabolically expensive for robots (constant actuation).

**Solutions**:
- Passive dynamics (let gravity help)
- Energy storage in springs/tendons
- Optimize gaits for minimal energy expenditure

---

## Case Studies

**Boston Dynamics Atlas**: Dynamic walking with push recovery—can be shoved and maintain balance through aggressive whole-body control.

**Cassie (Agility Robotics)**: Efficient dynamic walking on diverse terrain using passive dynamics in leg design.

**ASIMO**: Pioneered smooth, human-like walking using ZMP-based trajectory planning.

---

## Summary

Bipedal locomotion is fundamentally challenging due to inherent instability:

- **Small support base and high CoM** create tipping risk
- **ZMP criterion** provides stability metric (keep ZMP inside support)
- **Gait types** range from static (slow, stable) to dynamic (fast, efficient)
- **Control strategies** include trajectory optimization, MPC, and learning-based approaches
- **Real-world challenges** include terrain variability, disturbances, energy efficiency

Despite difficulties, bipedal locomotion enables humanoids to navigate human-designed environments (stairs, doorways, furniture) that challenge wheeled and four-legged robots.

Recent advances (2020+) show dramatic improvements: robots now run, jump, and recover from pushes—capabilities unthinkable a decade ago.

---

## Related Topics

- **[Major Platforms](./major-platforms)** - How different robots implement bipedal locomotion
- **[Human-Robot Morphology](./human-robot-morphology)** - Body design impacts walking capability
- **[Module 5: Control Hierarchies](../../module-5-control/control-hierarchies)** - Multi-level control for locomotion
