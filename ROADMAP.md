# Trajence roadmap

## Overview

Trajence is an early-stage framework for deterministic testing of AI-agent behavior. The roadmap below focuses on building a stable core, improving usability, and preparing the project for wider adoption.

## Phase 1: Core stability and polish

### Goals
- lock down the trajectory model and public API
- improve assertion clarity and reliability
- harden CLI behavior and exit codes
- verify compatibility across supported Python versions
- document the core workflow end-to-end

### Deliverables
- stable assertion primitives
- clearer error and failure reporting
- better CLI usage docs
- more realistic examples and test fixtures
- improved cassette save/load/diff behavior

## Phase 2: Developer experience

### Goals
- make adoption easier for new users
- improve debugging and reporting
- add more examples for common workflows
- support richer comparisons between runs

### Deliverables
- HTML report improvements
- better diff summaries for trajectory deviations
- richer example scenarios
- contributor setup guide and issue templates
- clearer guidance for integrating into CI/CD

## Phase 3: Real-world validation

### Goals
- validate on realistic tool-using agent workflows
- improve performance and ergonomics for larger trajectories
- handle failure modes common in multi-step agents

### Deliverables
- more end-to-end agent examples
- loop and retry scenario validation
- budget and cost enforcement improvements
- stronger safeguards for production-like runs

## Phase 4: Ecosystem and adoption

### Goals
- make the project easier to integrate into wider engineering workflows
- support more automation and reporting options
- prepare the project for a broader public-facing release

### Deliverables
- optional hosted reporting or dashboard integrations
- GitHub Actions support
- PR and workflow automation helpers
- expanded documentation for enterprise and CI usage

## Phase 5: Long-term platform vision

### Goals
- mature Trajence into a broader platform for agent observability and validation
- support richer tracing, comparison, and governance features

### Deliverables
- advanced reporting and analytics
- richer policy and rules engine
- tool governance and audit workflows
- broader ecosystem integrations

## Current focus

The immediate priority is to strengthen the core product: clear semantics, stable execution testing, richer diagnostics, and a better developer experience. The project is already functionally promising; the next step is to make it easier to trust, use, and contribute to.
