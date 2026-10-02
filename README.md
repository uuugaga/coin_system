
## Installation

### Environment

- Python 3.9.13

### Packages

```
pip install -r requirements.txt
pip install --no-deps "cnstd>=1.2.2,<1.2.3"
```

`cnstd` is installed separately because it declares `Polygon3`, which ships only
as C source and needs the Visual C++ build tools, while nothing in `cnstd`
actually imports it. Its real dependencies are in `requirements.txt`.

### Package installation Problem

win32gui: DLL load failed while importing win32gui
```
https://blog.csdn.net/qq_48691686/article/details/124447610
```

## How to use

1. Turn on your Albion Online.

2. Set your Albion Online to window mode (1280 x 720), with the in-game UI
   scale at 100%: the coordinates are calibrated against that, and the game's
   interface does not scale linearly.

3. Open your bag.

4. Run `main.py` in project root directory.

- Press `q` to stop the program. (Need some time to stop)

The bot finds the coin market itself, by clicking the coin icon in the bag, and
closes the panels that open over the game: the events window, the advertising
pop-ups, and the dialog that confirms a submitted order. After a disconnect or
the morning maintenance it logs back in on its own, and waits out a server
outage for up to two hours before giving up.

## Tools

In `debug/`, none of which click or type; they only read the screen.

| | |
|---|---|
| `diagnose.py` | Reports the window geometry and writes an overlay of every click target and OCR region onto a capture of the game. Run this first when something is clicked in the wrong place. |
| `check_ocr.py` | Shows what the OCR reads for each region, with the crops saved enlarged. |
| `capture_reference.py` | Recaptures the images in `references/` that the bot matches the interface against. Needed when the game changes an interface element. |
| `monitor.py` | Watches in the background and saves a capture whenever the game window disappears, the screen stops changing, or during the maintenance window. |
| `screenshot.py` | Saves a plain capture of the game's client area. |

## Calibration

Coordinates in `position.py` are fractions of the game's client area, so the
window can be anywhere on screen, and the title bar and borders do not matter.
They are calibrated for a 1280x720 client at 100% in-game UI scale.

`references/` holds small cuts of interface artwork that `screen.py` matches to
tell what the game is showing: whether the bag is open, whether the client is at
the login or character select screen, and whether a panel is covering the game.
If the game updates and one of them stops matching, the bot saves a capture to
`debug/incidents/` and stops rather than clicking blind; recapture that
reference with `capture_reference.py`.
