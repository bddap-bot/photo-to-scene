import argparse
import re
from pathlib import Path


def violations(root):
    failures = []
    for path in sorted(root.glob('*.md')):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if re.search(r'\bmust\b', line, re.IGNORECASE):
                gate = re.search(r'\[Gate:\s*[^;\]]+', line)
                recourse = re.search(r'Recourse:\s*[^\]]+\]', line)
                if not gate or not recourse:
                    failures.append(f'{path}:{number}: must line needs [Gate: ...; Recourse: ...]')
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('prompts', nargs='?', type=Path, default=Path('prompts'))
    args = parser.parse_args()
    failures = violations(args.prompts)
    if failures:
        print('\n'.join(failures))
        raise SystemExit(1)
    print(f'prompt policy: {args.prompts} passed')


if __name__ == '__main__':
    main()
