*Project is a STUB*

# genetic-musical-material-generator
Framework for developing musical material using genetic algorithm. The fitness criteria is "how much you like it"

## Songs
"Songs" are stored in a database:
- genetic structure
- rating
- "Family" (projects which can be forked)
- parents
- generation
- custom display name
- highlight display colour

## Program Flow
1. random generation <=> Discard unplayable
	- until specified number of initial "Songs" exist
2. Present results for listening, rating, or forking
3. Breeding of new generation weighted according to the rating <=> Discard unplayable
	- until specified number of offspring are created
4. goto 2

## Genetic code
- Genetic codes drive an engine which builds each "song"
- Loosely inspired by LOGO. The genetic code informs the movements and drawing of sound by a "turtle" in musical space.

### Language elements
- Interval : I{ -24, -23, ... 24 }
	- specifies a movement by musical interval of the turtle. (number of semitones)

- Note : N{ 21, 22, ... 108 }
	- specifies a jump to a particular note.  We use general MIDI note numbers, confined to the range of the piano.  

- movement mode : M0 ; M1 ; MT
	- When receiving interval and note commands, the turtle either progresses automatically after engraving the note by the rhythmic value set by turtle speed or it doesn't.  In essence this builds either melodies or chords respectively.  
	- M0 and M1 turn off and on the automatic progress respectively, MT toggles the state.

- Turtle speed : [1-8]/[1-8]
	- in essence sets note length and rhythmic value for both turtle progression (when turtle progress is on) and step forwards/backwards commands.
	- expressed as a fraction of a beat.

- Snap forwards/backwards : GF ; GB
	- moves the turtle forwards or backwards to the next multiple of the current turtle speed.  This is like a "snap to grid" command.

- Skip forwards/backwards : S[FB][1-8]/[1-8]
	- moves turtle by the designated rhythmic value (independently of current turtle speed)

- Pen up / down / toggle : PU ; PD ; PT
	- with pen up, the turtle follows the rhythmic and intervalic directions of the genetic code without actually engraving notes

- Marker / Goto : M ; R
	- these control movement of the cursor reading the genetic code and feeding it to the engine
	- one use of a Marker or Goto destroys it
	- a Goto scans back through the genetic code until a Marker is found, or to the beginning of the code, and continues reading through it again

## Discard
Need a representation of what human hands can physically play on a piano keyboard.  This makes up the discard engine, which rejects anything impossible to play.  

## Rating
The songs in the current generation are presented for appraisal.

You can listen and vote up, without limit.

## Breeding
The highest rated songs are "paired".

Method of combining genetic code?

Something allowing code to change in length
