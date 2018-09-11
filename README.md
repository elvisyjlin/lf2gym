# LF2 Gym

An OpenAI-gym-like environment for Little Fighter 2

The major contributors of this repository include [Yu-Jing Lin](https://github.com/elvisyjlin), 
[Po-Wei Wu](https://github.com/willylulu), [Yu-Jhe Li](https://github.com/YuJheLi) 
and [Hsin-Yu Chang](https://github.com/acht7111020).

[Little Fighter 2](http://lf2.net/) is a freeware PC 2.5D fighting game. 
We wrapped its open source version, [F.LF](http://www.projectf.hk/F.LF/), 
into a trainable environment for reinforcement learning.

This environment is used and described in the paper "Deep Reinforcement Learning for Playing 2.5D Fighting Games" (https://arxiv.org/abs/1805.02070).


#### Demo

By applying reinforcement learning methods on the LF2 Gym, 
the agent is able to play **Woody (the one in green)** against Louis as shown below.

![Demo](https://github.com/elvisyjlin/lf2gym/blob/master/demo/woody_vs_louis.gif)


## Installation

1. Clone the LF2 Gym repository.

   ```bash
   git clone https://github.com/elvisyjlin/lf2gym.git
   cd lf2gym
   ```

2. Download the open source LF2 from [Project F](https://github.com/Project-F) 
and make it trainable (see [here](https://github.com/elvisyjlin/lf2gym#modifications-to-the-original-game)).

   ```bash
   sh setup.sh
   ```

3. Install Python 3 and get all dependencies.

   This project is developed under Python 3.6.2 and has been tested in Python 3.4.0.

   ```bash
   pip3 install -r requirements.txt
   ```

4. Install Tkinter (optional, for screen rendering)

   Install Tkinter if you want to render the game on screen. 
   On the other hand, you can use Google Chrome to run the game without calling `render()`.

   Install Tkinter in Ubuntu for Python 3.

   ```bash
   sudo apt-get install python3-tk
   ```

   Install Tkinter in CentOS for Python 3
   ```bash
   sudo yum install python3-tkinter
   ```


## To start


### Env

Make an LF2 environment.  
Note: The web driver will be closed automatically when the process exits.

```python
import lf2gym
env = lf2gym.make()
```

All parameters for `make()` are described [here](https://github.com/elvisyjlin/lf2gym#parameters).


### Server

Or if you simply want to run a LF2Server.

```python
import lf2gym
lf2gym.start_server(port=8000)
```

Open your browser, and connect to `http://127.0.0.1:8000/game/game.html` to play LF2!

Keyboard control setting is described [here](https://github.com/elvisyjlin/lf2gym#keyboard-control).


### Need Helps?

If you encounter `selenium.common.exceptions.WebDriverException: Message: unknown error: cannot find Chrome binary`, which means Selenium cannot find the Chrome browser on your computer, please install it.

```bash
sudo apt-get install chromium-browser
```

If you encounter `selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start: exited abnormally`, which means your computer probably doesn't support GUI, please run Chromedriver under `headless mode`.

```bash
env = lf2gym.make(headless=True)
```


### Examples

Some examples demonstrate how to use the LF2 Gym. 

```bash
cd example
```

1. To try a simple example.

   ```bash
   python test.py
   ```

   `test.py` simulates an agent with predefined actions to play Davis against dumb Dennis, and saves the recording to `test.avi`. 

2. To play with a baby agent, which only takes random actions.

   ```bash
   python baby_play.py
   ```

   You can even choose the characters to play with.

   ```bash
   python baby_play.py [Your Character] [Your Enemy]
   ```


## Available Methods of Env

Reset the environment.

```python
env.reset()
```

Reset with custom options.

```python
options = env.get_reset_options() # {'ai_epsilon': None, 'hp_full': 500, 'mp_full': 500, 'mp_start': 500}
options['ai_epsilon'] = 0.1
options['hp_full'] = 1000
options['mp_full'] = 2e8
options['mp_start'] = 2e8
env.reset(options)
```

Option | Description | Default Value
--- | --- | ---
ai_epsilon | Action epsilon for the rule-based AI. Should be in (0, 1). | `None` I.e. `0`.
hp_full | Full HP for all characters. | `500`
mp_full | Full MP for all characters. | `500`
mp_start | Initial MP for all characters. | `500`

Render the environment in a new window.

```python
env.render()
```

Take an action.

```python
observation, reward, done, info = env.step(0) # actions are defined in the action space
```

Return | Type | Description
--- | --- | ---
observation | (160, 380, 4) | stacked frames from screenshots
reward | float | game reward
done | Boolean | game over
info | Boolean | step succeed

Get the specification of environment.

```python
state_size   = env.observation_space.n
action_size  = env.action_space.n
action_space = env.action_space
```

Get the log in the browser.

```python
env.get_log()
```

Get current game information (hp, mp, position, speed, action, ...) of each character.

```python
env.get_detail()
```

Skip N frames. `N` is an integer. E.g. `100`.

```python
env.idle(N)
```

Perform specific key actions. `sequence` can be an action or several actions (sequential key inputs). E.g. `['w']`.

```python
env.perform_actions(sequence)
```

### Screen Recording

1. Start recording  
   The frames will be store in the buffer whenever `env.step()`.

   ```python
   env.start_recording()
   ```

2. Stop recording  
   Stop storing frames to the buffer.

   ```python
   env.stop_recording()
   ```

3. Save the recorded frames to a video file.  
   It supports `.avi` and `.mp4` formats.

   ```python
   env.save_recording(filename, delete_after_saved=True)
   ```

## Parameters

Parameter | Description | Available Values | Default Value
--- | --- | --- | ---
ip | The LF2Server IP. | A string of IP. | `'127.0.0.1'`
port | The LF2Server port. | An Integer of port. | `8000`
startServer | Start a new LF2Server. | A Boolean. | `True`
wrap | Wrap the env with memory 4 or with a skip-4 wrapper. | `'4'` or `'skip4'`, `'skip5'`, ... | `'skip4'`
driverType | Web driver type. | `WebDriver.PhantomJS`, `WebDriver.Chrome` or `WebDriver.Firefox` | `WebDriver.PhantomJS`
characters | Character selection [Me, AI]. | Character. | `[Character.Davis, Character.Dennis]`
difficulty | Difficulty of enemies. | `Difficulty.Dumbass'`, `Difficulty.Challangar` or `Difficulty.Crusher` | `Difficulty.Dumbass`
background | Background selection. | Background. | `Background.HK_Coliseum`
action_options | Please refer to [Group of Actions](https://github.com/elvisyjlin/lf2gym#group-of-actions). | A list of strings of action groups. | `['Basic', 'AJD', 'Full Combos']`
versusPlayer | Versus player. If `True`, the second character will be controlled by user and the game will not be paused. | A Boolean. | `False`
duel | Two agents duel. If `True`, step() takes two actions for the two agents. | A Boolean. | `False`
rewardList | Take what factors into account for rewards. | `['hp']` or `['hp', 'mp']` | `['hp']`
localDriver | Whether to use local web driver. | A Boolean. | `True`
headless | Enable browser headless mode (currently for Chrome only). | A Boolean. | `False`
canvasSize | The canvas size to capture in the browser. | A tuple of 2 integers. | (550, 794)
debug | Print out debug messages. | A Boolean. | `False`

The all available web drivers, characters, difficulties, and backgrounds are defined in `config.py`.

Although we implemented PhantomJS, ChromeDriver and GeckoDriver, 
some errors occur when using GeckoDriver with Firefox. 
Therefore, we recommend to use PhantomJS or ChromeDriver with Google Chrome. 
Note that Google Chrome browser or Firefox browser should be installed first. 


## Action Space


#### Base Action Space

Value | Action | Skip-N Action | Value | Action | Skip-N Action
--- | --- | --- | --- | --- | ---
0 | idle | idle | 11 | v> | A
1 | ^ | ^ | 12 | ^< | J
2 | v | v | 13 | v< | D
3 | < | < | 14 |  | D < A
4 | > | > | 15 |  | D > A
5 | A | ^> | 16 |  | D < J
6 | J | v> | 17 |  | D > J
7 | D | ^< | 18 |  | D ^ A
8 | < < | v< | 19 |  | D v A
9 | > > | < < | 20 |  | D ^ J
10 | ^> | > > | 21 |  | D v J

With the default `action_options`, which is `['Basic', 'AJD', 'Full Combos']`, the skip-N action space is 

Value | SN Act | Value | SN Act | Value | SN Act | Value | SN Act
--- | --- | --- | --- | --- | --- | --- | ---
0 | idle | 4 | > | 8 | D < A | 12 | D ^ A
1 | ^ | 5 | A | 9 | D > A | 13 | D v A
2 | v | 6 | J | 10 | D < J | 14 | D ^ J
3 | < | 7 | D | 11 | D > J | 15 | D v J


#### Group of Actions

Group | Actions
--- | ---
`'Basic'` | [0, 1, 2, 3, 4]
`'Advanced'` | [5, 6, 7, 8]
`'Run'` | [9, 10]
`'AJD'` | [11, 12, 13]
`'Full Combos'` | [14, 15, 16, 17, 18, 19, 20, 21]
`'No Combos'` | [], and remove all actions of 'Full Combos'


## Keyboard Control

Action | Player 1 | Player 2
--- | --- | ---
Up | W | Up (U)
Right | D | Right (K)
Down | X | Down (M)
Left | A | Left (H)
Attack | S | J (J)
Jump | Q | U (I)
Defense | Z | M (,)


## Modifications to F.LF

In order to train the agent better, we did some modifications to the original game. 
See [here](https://github.com/elvisyjlin/lf2gym/tree/master/modify#modified-files). 


## Web Drivers

The web drivers will be downloaded automatically when used.

The following web drivers are utilized to run the game.

1. PhantomJS  
   http://phantomjs.org/download.html
2. ChromeDriver ([Google Chrome](https://www.google.com/chrome/))  
   https://sites.google.com/a/chromium.org/chromedriver/
3. GeckoDriver ([Firefox](https://www.mozilla.org/en-US/firefox/))  
   https://github.com/mozilla/geckodriver/releases


# Reference

This project is based on the open source Little Fighter 2 game of [Project F](https://github.com/Project-F).  
The [OpenAI Gym](https://gym.openai.com/docs/) is taken for reference to design the architecture of `lf2gym`.


---

If you find our code useful for your research, please cite

```text
@inproceedings{li2018deep,
  title={Deep Reinforcement Learning for Playing 2.5D Fighting Games},
  author={Li, Yu-Jhe and Chang, Hsin-Yu and Lin, Yu-Jing and Wu, Po-Wei and Wang, Yu-Chiang},
  booktitle={IEEE International Conference on Image Processing ({ICIP})},
  year={2018}
}
```
