# بسم الله الرحمن الرحيم

# Nine Mens's Morris Game Engine

Game engine with minimal UI for the Nine Men's Morris Game

# Getting started:

## Installation:

1. Clone the repo into one of your local folders `git clone https://github.com/ksbupm/nine-mens-morris`
1. Download and install [`Anaconda`](https://www.anaconda.com/download/success)
1. Once installed, open `Anaconda Command Prompt` from the **start menu**.
1. Navigate to the cloned repo !
1. Create a new environment using `conda create -n ai381 python=3.11`
1. Activate the new evironment using `conda activate ai381`
1. Install `poetry` using `pip install poetry`
1. Install the game `poetry install`
1. YOU'RE READY TO GO !!!



## Run the UI:

1. Activate the environment using `conda activate ai381`

2. Run in the terminal:

```python
python -m nmm.ui
```

3. Try out the human vs human mode using:

```python
python -m nmm.ui.game AIHu
```


## Implement your AI Agent:

1. Implement your AI agent in the `nmm/agent.py` file.
1. Try it out by running:

```python
python -m nmm.ui.game AIAgent
```