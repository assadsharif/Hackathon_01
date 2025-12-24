---
sidebar_position: 1
title: Major Platforms
description: Survey leading humanoid robot platforms and their capabilities
---

# Major Platforms

## Key Concepts

- **Humanoid Robot**: Robot with human-like body structure (head, torso, arms, legs)
- **Degrees of Freedom (DoF)**: Number of independent movement axes
- **Actuation**: Methods of generating movement (electric motors, hydraulics, pneumatics)
- **Platform Capability**: The tasks a robot platform can perform
- **Commercial vs Research Platforms**: Production systems vs experimental prototypes

---

## Introduction

Humanoid robots represent decades of engineering progress—from early research prototypes to today's commercialization-ready platforms. This chapter surveys the major humanoid robots shaping the field, comparing their capabilities, design philosophies, and application domains.

---

## Leading Humanoid Platforms

### Boston Dynamics Atlas

**Overview**: Research platform demonstrating extreme dynamic capabilities

**Specifications**:
- Height: 1.5m, Weight: 89kg
- 28 hydraulic joints (high power-to-weight ratio)
- 3D LIDAR, stereo cameras
- Capable of: Parkour, backflips, dynamic running

**Design Philosophy**: Push the boundaries of dynamic locomotion through aggressive control and hydraulic actuation

**Applications**: Research, disaster response demonstrations, not commercially available

**Key Innovation**: Whole-body control algorithms that enable dynamic maneuvers (jumping, flipping) previously impossible for humanoids

---

### Tesla Optimus (Tesla Bot)

**Overview**: General-purpose humanoid for manufacturing and domestic tasks

**Specifications**:
- Height: 1.73m, Weight: 57kg
- 40+ actuators (electric motors)
- Vision-based perception (no LIDAR)
- Target capabilities: Lifting 20kg, carrying 45kg

**Design Philosophy**: Mass-producible, cost-effective ($20K target), leveraging Tesla's automotive manufacturing and AI

**Applications**: Factory automation, household assistance (future)

**Key Innovation**: Adapting autonomous vehicle AI (FSD stack) to humanoid perception and navigation

---

### Figure 01

**Overview**: Commercial humanoid for warehouse and logistics applications

**Specifications**:
- Height: 1.68m, Weight: 60kg
- Electric actuation (energy efficient)
- Vision and touch sensing
- Payload: 20kg

**Design Philosophy**: Practical, deployable systems for near-term commercial use

**Applications**: Warehouse automation, manufacturing, retail

**Key Innovation**: Rapid deployment timelines (demo to deployment in months, not years)

---

### Unitree H1

**Overview**: Affordable humanoid platform for research and development

**Specifications**:
- Height: 1.80m, Weight: 47kg
- Low-cost design ($90K)
- High-speed locomotion (3.3 m/s)
- Open development platform

**Design Philosophy**: Democratize humanoid robotics through affordability

**Applications**: Academic research, algorithm development

**Key Innovation**: Cost reduction while maintaining capable hardware

---

### Others Notable Platforms

**Honda ASIMO** (Retired): Early pioneer, demonstrated stair climbing and running (2000-2018)

**SoftBank Pepper**: Social companion robot, focused on human interaction rather than manipulation

**Agility Robotics Digit**: Bipedal robot optimized for package handling (not fully humanoid—no head)

**Toyota T-HR3**: Teleoperated humanoid for remote assistance

---

## Capability Comparison

| Platform | Locomotion | Manipulation | Perception | Primary Use |
|----------|-----------|--------------|------------|-------------|
| **Atlas** | ★★★★★ Dynamic | ★★★ Research-grade | ★★★★ Multi-modal | Research |
| **Optimus** | ★★★ Walking | ★★★★ Dexterous hands | ★★★★ Vision-based | Manufacturing |
| **Figure 01** | ★★★ Stable walking | ★★★★ Warehouse tasks | ★★★ Vision + touch | Logistics |
| **Unitree H1** | ★★★★ Fast walking | ★★ Basic | ★★ Vision | Research/Dev |

---

## Design Tradeoffs

### Hydraulic vs Electric Actuation

**Hydraulic** (Atlas):
- ✅ High power-to-weight ratio, explosive dynamics
- ❌ Complex, noisy, requires pump/cooling system

**Electric** (Optimus, Figure 01):
- ✅ Simple, efficient, precise control
- ❌ Lower power density, less dynamic performance

### Perception Approaches

**Vision-Only** (Optimus):
- ✅ Cost-effective, leverages CV advances
- ❌ Depth perception challenges, lighting sensitivity

**Multi-Modal** (Atlas):
- ✅ Robust, complementary sensing
- ❌ Higher cost, sensor fusion complexity

---

## Commercialization Trends

### From Research to Products
1. **2000-2010**: Lab prototypes (ASIMO, HRP-4)
2. **2010-2020**: Dynamic research (Atlas, ANYmal)
3. **2020-Present**: Commercial deployment (Figure 01, Optimus, Digit)

**Drivers**:
- Advances in AI/ML (vision, control policies)
- Manufacturing scale (Tesla's automotive expertise)
- Market demand (labor shortages, aging populations)

---

## Summary

Major humanoid platforms demonstrate diverse approaches:

- **Atlas**: Research excellence, dynamic performance
- **Optimus**: Mass production vision, cost targets
- **Figure 01**: Near-term commercial deployment
- **Unitree H1**: Affordable research access

**Key Trends**:
- Shift from hydraulic to electric actuation
- Vision-centric perception
- Rapid commercialization (2023-2025)
- Target cost reduction ($20-90K range)

Humanoid robotics is transitioning from decades of research to commercial reality, with multiple platforms competing on capability, cost, and deployability.

---

## Related Topics

- **[Bipedal Locomotion](./bipedal-locomotion)** - Challenges of two-legged walking
- **[Human-Robot Morphology](./human-robot-morphology)** - Design choices and tradeoffs
- **[Module 1: Application Domains](../../module-1-intro/application-domains)** - Where humanoids are deployed
