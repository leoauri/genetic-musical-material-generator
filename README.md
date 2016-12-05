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
1. Initial random generation
2. Discard unplayable
3. Present results for rating
4. Breeding of new generation weighted according to the rating
5. goto 2

## Genetic code
Loosely inspired by LOGO

### Language elements
- Pen up / down / toggle
  
