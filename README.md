---
title: Misinformation Detector
emoji: 🔍
colorFrom: red
colorTo: blue
sdk: docker
app_port: 7860
tags:
  - openenv
  - fact-checking
  - content-moderation
---

# Misinformation Detector — OpenEnv Environment

## Description
A real-world AI training environment where agents learn to detect,
analyze, and correct misinformation in news articles and claims.
Simulates tasks performed by human fact-checkers at newsrooms daily.

## Tasks
- **Task 1 (Easy):** Classify a claim as REAL, FAKE, or UNCLEAR
- **Task 2 (Medium):** Find the false sentence in a paragraph  
- **Task 3 (Hard):** Rewrite a manipulated article with corrections

## API Endpoints
- POST /reset — start a new episode
- POST /step — submit an action
- GET /state — get current state
- GET /tasks — list all tasks

## Baseline Scores
- Task 1 Easy: 1.00 / 1.00
- Task 2 Medium: 1.00 / 1.00
- Task 3 Hard: 1.00 / 1.00
- Average: 1.00 / 1.00

## Setup
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 7860
