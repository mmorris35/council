"""Investment agent implementations."""
from .base import BaseAgent
from .bogle import BogleAgent
from .buffett import BuffettAgent
from .graham import GrahamAgent
from .lynch import LynchAgent
from .dalio import DalioAgent
from .wood import WoodAgent

__all__ = [
    "BaseAgent",
    "BogleAgent",
    "BuffettAgent",
    "GrahamAgent",
    "LynchAgent",
    "DalioAgent",
    "WoodAgent",
]
