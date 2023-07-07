<h1 align="center">dauricum</h1>

![Commits](https://img.shields.io/github/commit-activity/m/Maxdsdsdsd/dauricum)
![Stars](https://img.shields.io/github/stars/Maxdsdsdsd/dauricum)

*A work-in-progress Python 3.10+ obfuscator with many obfuscation methods.*
 
 This obfuscator is built on ast. Inspired by [jargonaut](https://github.com/mad-cat-lon/jargonaut/tree/master).
 
 Note that this is a proof-of-concept and a work in progress.

## Features
 * MBA Expressions
 * In Outline
 * Control Flow
 * Try Catch
 * Try Catch Normalizer

## Examples
Check out examples folder

## How to
### Installation

Install with pip

```bash
  pip install dauricum
```

Install from github

```bash
  git clone https://github.com/Maxdsdsdsd/dauricum.git
  cd dauricum
  
  build.bat
```

### Use

Obfuscate .py file

```bash
  py -m dauricum -input example1-unobf.py -output a.py --mba-expression
  --mba-expression-mode true --in-outline
  --control-flow --try-catch --try-catch-mode true
  --try-catch-iter 3 --try-normalizer --try-normalizer-iter 5
```

Get help

```bash
  py -m dauricum --help
```
