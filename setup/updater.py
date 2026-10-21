"""Install any requirement that the downloaded source needs but the slug lacks.

usage: updater.py <installed_requirements.txt> <source_requirements.txt>
"""
import asyncio
import shlex
import sys
from typing import List, Tuple


def read_requirements(path: str) -> List[str]:
    with open(path, encoding="utf-8") as f:
        lines = [line.strip() for line in f]
    return [line for line in lines if line and not line.startswith(("#", "-"))]


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def update_requirements(main: str, new: str) -> None:
    try:
        installed = set(read_requirements(main))
        wanted = read_requirements(new)
    except OSError as e:
        print(f"Could not read requirements files: {e}")
        return

    for req in wanted:
        if req in installed:
            continue
        _, err, code, _ = await runcmd(
            f"{shlex.quote(sys.executable)} -m pip install --no-input {shlex.quote(req)}"
        )
        if code == 0:
            print(f"Successfully installed {req}")
        else:
            print(f"Failed to install {req}: {err.splitlines()[-1] if err else code}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    asyncio.run(update_requirements(sys.argv[1], sys.argv[2]))
