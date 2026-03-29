import random
from pydantic import BaseModel
from typing import Optional
from tasks import TASKS, grade_action

# ---------- Typed Models (OpenEnv spec) ----------

class Action(BaseModel):
    action_type: str        # "classify", "locate", or "correct"
    content: str            # the agent's actual answer

class Observation(BaseModel):
    task_id: str
    text: str               # the article or claim shown to the agent
    instruction: str        # what the agent must do
    step: int
    done: bool

class Reward(BaseModel):
    score: float            # 0.0 to 1.0
    feedback: str           # human-readable explanation of score

class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict

# ---------- Environment Class ----------

class MisinformationEnv:

    def __init__(self):
        self.current_task = None
        self.current_step = 0
        self.max_steps = 5
        self.done = False
        self.task_queue = list(TASKS.keys())
        self.task_index = 0

    def reset(self, task_id: Optional[str] = None) -> Observation:
        """Start a fresh episode. Returns the first observation."""
        self.current_step = 0
        self.done = False

        # Pick task (cycle through all 3 if not specified)
        if task_id:
            self.current_task = TASKS[task_id]
        else:
            tid = self.task_queue[self.task_index % len(self.task_queue)]
            self.current_task = TASKS[tid]
            self.task_index += 1

        return Observation(
            task_id=self.current_task["id"],
            text=self.current_task["text"],
            instruction=self.current_task["instruction"],
            step=self.current_step,
            done=False
        )

    def step(self, action: Action) -> StepResult:
        """Take one action. Returns observation, reward, done, info."""
        self.current_step += 1

        if self.done:
            return StepResult(
                observation=self._current_obs(),
                reward=Reward(score=0.0, feedback="Episode already done."),
                done=True,
                info={"warning": "stepped after done"}
            )

        # Grade the action
        score, feedback = grade_action(
            task_id=self.current_task["id"],
            action=action
        )

        # Episode ends after 1 real attempt (fact-checking is one-shot)
        self.done = True

        # Partial reward shaping: penalise empty or very short answers
        if len(action.content.strip()) < 3:
            score = 0.0
            feedback = "Answer was empty or too short."

        return StepResult(
            observation=self._current_obs(),
            reward=Reward(score=score, feedback=feedback),
            done=True,
            info={
                "task_id": self.current_task["id"],
                "steps_taken": self.current_step
            }
        )

    def state(self) -> dict:
        """Return current internal state (for debugging/logging)."""
        return {
            "current_task_id": self.current_task["id"] if self.current_task else None,
            "current_step": self.current_step,
            "done": self.done,
            "max_steps": self.max_steps
        }

    def _current_obs(self) -> Observation:
        return Observation(
            task_id=self.current_task["id"],
            text=self.current_task["text"],
            instruction=self.current_task["instruction"],
            step=self.current_step,
            done=self.done
        )