---
sidebar_position: 3
title: Reinforcement Learning
description: Understand how RL enables robots to learn from experience
---

# Reinforcement Learning

## Key Concepts

- **Reinforcement Learning (RL)**: Learning by trial-and-error through reward feedback
- **Policy**: Mapping from states to actions (robot's behavior)
- **Reward Function**: Scalar signal indicating task success/failure
- **Value Function**: Expected cumulative reward from a state
- **Sample Efficiency**: Number of interactions needed to learn

---

## Introduction

**Reinforcement Learning** enables robots to learn skills through interaction—try actions, observe outcomes, improve based on rewards. Unlike supervised learning (requires labeled examples) or imitation learning (requires expert demonstrations), RL learns from sparse feedback (success/failure) through exploration.

This chapter covers RL fundamentals, how RL applies to Physical AI, and when RL is the right tool for robot learning.

---

## RL Fundamentals

### The RL Problem

**Agent** (robot) interacts with **environment** (physical world):

1. **Observe State** (s): Robot's configuration, environment state
2. **Take Action** (a): Joint commands, gripper closure
3. **Receive Reward** (r): Scalar feedback (1 if grasped object, 0 otherwise)
4. **Transition to Next State** (s'): World updates

**Goal**: Learn policy π(a|s) that maximizes cumulative reward

---

### Key Components

**1. State (s)**
- **Definition**: Information needed to choose action
- **Examples**:
  - Joint angles, velocities (proprioception)
  - Object positions from vision
  - Contact forces from tactile sensors

**Partial Observability**: Real robots don't see full state (hidden objects, occluded surfaces)

---

**2. Action (a)**
- **Continuous**: Joint torques, velocities (humanoid control)
- **Discrete**: Grasp locations, navigation waypoints

**Action Space Design**:
- High-dimensional (30 DOF humanoid) → hard to explore
- Low-dimensional (task-level commands) → easier but less flexible

---

**3. Reward Function (r)**
- **Definition**: Scalar indicating desirability of outcome
- **Examples**:
  - **Sparse**: r = 1 if object grasped, 0 otherwise
  - **Dense**: r = -distance_to_object (every step)

**Challenge**: Reward design is critical—misspecified rewards lead to unexpected behaviors (reward hacking)

---

**4. Policy (π)**
- **Deterministic**: a = π(s)
- **Stochastic**: a ~ π(·|s) (sample action from distribution)

**Representation**:
- Neural network (deep RL)
- Linear function
- Decision tree

---

**5. Value Function (V, Q)**
- **State Value V^π(s)**: Expected cumulative reward starting from s, following policy π
- **Action Value Q^π(s,a)**: Expected cumulative reward from taking action a in state s, then following π

**Use**: Evaluate how good a state or action is

---

## RL Algorithms for Robotics

### 1. Policy Gradient Methods

**Core Idea**: Directly optimize policy parameters to maximize reward

**Algorithm**: REINFORCE, PPO (Proximal Policy Optimization), TRPO

**How It Works**:
- Sample trajectories using current policy
- Compute rewards
- Update policy to increase probability of high-reward actions

**Pros**: Works with continuous actions, stochastic policies
**Cons**: Sample inefficient (needs many trajectories), high variance

**Use in Robotics**: Locomotion, manipulation with continuous control

---

### 2. Actor-Critic Methods

**Core Idea**: Combine policy (actor) and value function (critic)

**Algorithm**: SAC (Soft Actor-Critic), TD3 (Twin Delayed DDPG)

**How It Works**:
- Actor proposes actions
- Critic estimates value function
- Critic's estimate guides actor's update (reduces variance)

**Pros**: More sample-efficient than pure policy gradient
**Cons**: Still requires many samples

**Use in Robotics**: Continuous control tasks (arm reaching, quadruped walking)

---

### 3. Q-Learning (Off-Policy)

**Core Idea**: Learn optimal action-value function Q*, derive policy from it

**Algorithm**: DQN (Deep Q-Network), Rainbow

**How It Works**:
- Estimate Q(s,a) for all actions
- Choose action with max Q (greedy)
- Learn Q from experience replay buffer

**Pros**: Sample-efficient (reuses past experience)
**Cons**: Limited to discrete actions (hard for high-DOF robots)

**Use in Robotics**: Discrete decision-making (grasp selection, navigation goals)

---

### 4. Model-Based RL

**Core Idea**: Learn model of environment dynamics, use for planning

**Algorithm**: PETS, Dreamer, MuZero

**How It Works**:
1. Learn forward model: predict s' given s, a
2. Use model to plan (simulate actions, choose best)
3. Execute action, collect data, improve model

**Pros**: Very sample-efficient (model enables planning without real interaction)
**Cons**: Model errors compound (inaccurate model → poor plans)

**Use in Robotics**: Sample-limited scenarios (real robot), predictable dynamics

---

## RL for Physical AI: Unique Challenges

### 1. Sample Efficiency

**Challenge**: RL typically requires millions of samples (simulated experiences), but real robots are slow (1 sample/second)

**Example**: Walking policy needs 10M steps in sim (10 GPU-hours), but 10M steps on real robot = 115 days

**Solutions**:
- **Sim-to-real**: Train in simulation, transfer to real
- **Model-based RL**: Learn dynamics model, plan efficiently
- **Imitation pre-training**: Bootstrap from demonstrations, fine-tune with RL

---

### 2. Safety

**Challenge**: Exploration (trying random actions) can damage robot or environment

**Example**: Random joint torques during exploration → robot falls, breaks

**Solutions**:
- **Safe exploration**: Constrain actions to safe region (joint limits, torque limits)
- **Simulation first**: Explore in sim where failures are free
- **Shielding**: Safety controller overrides RL policy if dangerous action proposed

---

### 3. Partial Observability

**Challenge**: Robots can't see full state (occluded objects, hidden contacts)

**Example**: Grasping object—don't know exact mass, friction, shape

**Solution**:
- **Recurrent policies** (LSTM, GRU): Maintain memory of past observations
- **Belief state**: Estimate probability distribution over hidden state

---

### 4. Continuous Control

**Challenge**: Humanoids have continuous action spaces (joint torques ∈ ℝ^30), hard to explore

**Solution**:
- **Actor-critic methods**: SAC, TD3 handle continuous actions
- **Action discretization**: Bin continuous actions (loses precision)
- **Hierarchical RL**: High-level policy chooses sub-goal, low-level controller executes

---

### 5. Reward Specification

**Challenge**: Specifying reward for complex tasks is hard—sparse rewards (success/failure) are hard to learn, dense rewards risk reward hacking

**Example**: "Walk forward"
- **Sparse reward**: r = 1 if robot reaches goal (hard to learn—no guidance)
- **Dense reward**: r = velocity_forward (risk: robot falls forward to maximize velocity)

**Solutions**:
- **Reward shaping**: Add intermediate rewards (stand upright, maintain balance)
- **Inverse RL**: Learn reward from demonstrations
- **Curriculum learning**: Start with easier reward, gradually increase difficulty

---

## When to Use RL for Physical AI

### RL is Appropriate When:

**1. Sparse Feedback**
- Task has clear success/failure, but no demonstrations
- Example: "Navigate maze"—know when goal is reached, but don't know optimal path

**2. Exploration is Possible**
- Safe to try random actions (in sim or constrained real environment)
- Example: Grasping in bin picking—failures are acceptable

**3. Optimization Objective is Clear**
- Can define reward function that captures task
- Example: "Walk as fast as possible while staying upright"

**4. Sample Efficiency is Not Critical**
- Have access to simulation or large robot farm
- Example: Google's robot grasping (14 robots, months of data)

---

### RL is NOT Appropriate When:

**1. Demonstrations Available**
- If expert demonstrations exist, imitation learning is more sample-efficient
- Example: Teleoperated manipulation—just clone demonstrated behavior

**2. Reward is Hard to Specify**
- Complex tasks with subjective quality (aesthetics, comfort)
- Example: "Arrange room to look nice"—hard to define reward

**3. Safety is Critical**
- Exploration could cause harm
- Example: Surgical robot—can't afford random exploration on patients

**4. Dynamics are Highly Unpredictable**
- RL assumes some regularity (same action in same state gives similar outcome)
- Example: Interacting with unpredictable humans

---

## Case Studies

### 1. Quadruped Locomotion (ETH Zurich, ANYmal)

**Task**: Legged robot walking on rough terrain

**Approach**:
- **Algorithm**: PPO (policy gradient)
- **Training**: Isaac Gym simulation (1000 parallel robots, 4000 environments)
- **Reward**: Forward velocity, energy efficiency, stability
- **Transfer**: Domain randomization, teacher-student

**Result**: Zero-shot transfer to real robot, robust walking on stairs, obstacles, uneven terrain

**Key Insight**: Massive parallelization in sim (1000x speedup) overcomes sample inefficiency

---

### 2. Dexterous Manipulation (OpenAI, Rubik's Cube)

**Task**: Robot hand solves Rubik's cube

**Approach**:
- **Algorithm**: PPO
- **Training**: 100 years simulated experience (distributed training)
- **Reward**: Cube state progress toward solved
- **Transfer**: Aggressive domain randomization (cube size, mass, friction, hand dynamics)

**Result**: Real Shadow Hand solved cube (50 consecutive solves)

**Key Insight**: RL enabled learning complex manipulation without demonstrations (hard to teleoperate 24-DOF hand)

---

### 3. Robot Grasping (Google, QT-Opt)

**Task**: Grasp diverse objects in clutter

**Approach**:
- **Algorithm**: Off-policy Q-learning (QT-Opt)
- **Training**: 800K real-world grasps (14 robots, 4 months)
- **Reward**: Binary (grasp success/failure)

**Result**: 96% grasp success on novel objects

**Key Insight**: Large-scale real-world RL (robot farm) achieved sample efficiency competitive with simulation

---

## Hybrid Approaches

### Combining RL with Other Methods

**1. Imitation + RL (Pre-training + Fine-Tuning)**
- **Pre-train**: Imitation learning from demonstrations (fast)
- **Fine-tune**: RL to optimize beyond demonstrations (improve performance)

**Example**: Demonstrate walking, then RL optimizes speed

---

**2. Model-Based + Model-Free**
- **Model-based**: Learn dynamics, use for initial policy
- **Model-free**: Fine-tune with policy gradient (correct model errors)

**Example**: Learn forward model for grasping, plan initial approach, RL adjusts contact

---

**3. Hierarchical RL**
- **High-level**: Learn task-level policy (which object to grasp)
- **Low-level**: Learn motion-level policy (how to grasp)

**Example**: High-level chooses grasp target, low-level executes reaching motion

---

## Practical Considerations

### 1. Reward Engineering

**Design Principles**:
- **Alignment**: Reward captures true objective (not proxy)
- **Density**: Provide guidance (not just sparse terminal reward)
- **Normalization**: Scale rewards to similar ranges (avoid dominance)

**Example**: Walking
- **Sparse**: r = 1 if walk 10 meters (hard to learn)
- **Dense**: r = velocity_forward - 0.1·energy - 10·fell (easier, but check for reward hacking)

---

### 2. Hyperparameter Tuning

**Critical Hyperparameters**:
- Learning rate
- Discount factor (γ): How much to value future rewards
- Exploration noise (for continuous control)

**Recommendation**: Use established defaults (PPO, SAC have well-tuned defaults), sweep if needed

---

### 3. Monitoring Training

**Key Metrics**:
- **Episode return**: Total reward per episode (should increase)
- **Success rate**: % of episodes achieving goal
- **Exploration**: Action entropy (should decrease as policy converges)

**Debugging**: If not learning, check reward scale, exploration, network capacity

---

## Summary

Reinforcement Learning enables robots to learn through trial-and-error:

- **RL fundamentals**: States, actions, rewards, policies, value functions
- **Algorithms**: Policy gradient (PPO), actor-critic (SAC), Q-learning (DQN), model-based (PETS)
- **Challenges for Physical AI**: Sample inefficiency, safety, partial observability, continuous control, reward specification
- **When to use RL**: Sparse feedback, exploration possible, clear objective, simulation available
- **When NOT to use RL**: Demonstrations available, reward hard to specify, safety critical, unpredictable dynamics
- **Case studies**: Quadruped locomotion, dexterous manipulation, robot grasping
- **Hybrid approaches**: Imitation + RL, model-based + model-free, hierarchical RL

RL is most effective when combined with simulation (for sample efficiency), domain randomization (for transfer), and other learning paradigms (imitation, model-based)—leveraging RL's strength (learning from sparse feedback through exploration) while mitigating its weaknesses (sample inefficiency, safety).

---

## Related Topics

- **[Simulation vs. Reality](./simulation-vs-reality)** - Using simulation to make RL sample-efficient
- **[Transfer Learning](./transfer-learning)** - Transferring RL policies from sim to real
- **[Physical Interaction Learning](../../module-2-embodied/physical-interaction-learning)** - Learning through real-world interaction
