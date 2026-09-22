from collections import deque
import time
class RateLimiter:
    def __init__(self, per_minute:int, delay:float): self.per_minute=per_minute; self.delay=delay; self.events=deque(); self.last=0.0
    def wait(self):
        now=time.monotonic()
        if now-self.last<self.delay: time.sleep(self.delay-(now-self.last))
        now=time.monotonic()
        while self.events and now-self.events[0]>=60: self.events.popleft()
        if len(self.events)>=self.per_minute: time.sleep(max(0,60-(now-self.events[0])))
        now=time.monotonic(); self.events.append(now); self.last=now
