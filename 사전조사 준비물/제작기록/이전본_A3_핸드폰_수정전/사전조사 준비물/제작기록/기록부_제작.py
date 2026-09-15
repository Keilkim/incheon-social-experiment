"""200명 기준 기록부 제작 진입점."""
from 기록부_200_제작 import build

if __name__ == "__main__":
    for phase in (0, 1, 2):
        build(phase)
