# scanners/registry.py
import asyncio
from typing import Callable, Dict, Any

# Each entry: action_name -> (callable, timeout_seconds)
# callable must be async or a regular function (we will wrap blocking calls)
Registry: Dict[str, tuple[Callable[[str], Any], int]] = {}

def register(action: str, func: Callable[[str], Any], timeout: int = 15):
    Registry[action] = (func, timeout)

async def run_action(action: str, target_url: str) -> dict:
    if action not in Registry:
        return {"status": "error", "error": f"Unknown action '{action}'"}

    func, timeout = Registry[action]
    # If callable is coroutinefunction -> call directly; else run in thread
    if asyncio.iscoroutinefunction(func):      
        coro = func(target_url)
    else:
        coro = asyncio.to_thread(func, target_url)

    try:
        result = await asyncio.wait_for(coro, timeout=timeout)
        return {"status": "ok", "action": action, "result": result}
    except asyncio.TimeoutError:
        return {"status": "timeout", "action": action, "error": f"Action exceeded {timeout}s"}
    except Exception as e:
        return {"status": "error", "action": action, "error": str(e)}
