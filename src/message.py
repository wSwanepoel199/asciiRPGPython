from __future__ import annotations
from typing import List, Iterable, Reversible, Tuple, TYPE_CHECKING
import textwrap, tcod

if TYPE_CHECKING:
  from src.engine import Engine

class Message:
  def __init__(self, text: str = "", fg: Tuple[int, int, int] = (255, 255, 255)) -> None:
    self.text_p = text
    self.fg = fg
    self.count = 1
  @property
  def text_full(self) -> str:
    if self.count > 1:
      return f"{self.text_p} (x{self.count})"
    return self.text_p

class MessageLog:
  def __init__(self) -> None:
    self.messages: List[Message] = []

  def add_message(
    self,
    text:str,
    fg: Tuple[int, int, int] = (255,255,255),
    *,
    stack: bool = False
  ) -> None:
    if stack and stack.messages and text == self.messages[-1].text_p:
      self.messages[-1].count += 1
    else:
      self.messages.append(Message(text=text, fg=fg))
  
  def render(
    self,
    console: tcod.console.Console,
    x: int,
    y: int,
    width: int,
    height: int
  ) -> None:
    self.render_messages(
      console=console,
      x=x,
      y=y,
      width=width,
      height=height,
      messages=self.messages
    )
  @staticmethod
  def wrap(string:str, width:int) -> Iterable[str]:
    for line in string.splitlines():
      yield from textwrap.wrap(
        text=line, width=width, expand_tabs=True)
  @classmethod
  def render_messages(
    cls,
    console: tcod.console.Console,
    x: int,
    y: int,
    width: int,
    height: int,
    messages: Reversible[Message]
  ) -> None:
    y_offset = height - 1
    for message in reversed(messages):
      for line in reversed(list(cls.wrap(string=message.text_full, width=width))):
        console.print(
          x=x,
          y=y+y_offset,
          string=line,
          fg=message.fg
        )
        y_offset -= 2
        if y_offset < 0:
          return