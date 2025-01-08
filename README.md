# My own simple physics simulator and bridge builder game written in Pygame
<i>Inspired by polybridge and its clones, I wanted to have a go at a bit of physics simulation

This project started as a final assignment for a course at school. 

However, I enjoyed working on it so much that it ended up going far beyond the original scope.</i>

## Game overview:
- You play as an infrastructure contractor company <b>"Mostex"</b>.
- Your job is to construct bridges using the limited budget and ensure fatalities on 'opening day' stay within limits.
- You can use different beam types for your bridge, all of which have different prices and physical properties.
- You need to provide a path for the incoming cars using paved beams.
- The cost of a single beam scales as a square of its length - so build small - but remember that every node adds weight!

### Controls:
- **Left Mouse button (point & click)** - selecting a node for beam construction & menu interactions.
- **Right Mouse button (click)** - cycle through the available beam types.
- **Control + Left Mouse button (point & click)** - deleting a node & cancelling beam creation.
- **Control + "Z" Key** - undo creation of the last beam.

## Some screenshots:

### Home Screen
<img width="800" alt="Home Screen" src="https://github.com/user-attachments/assets/3278fd0d-a15b-4663-a68c-5556cc0cb656" />

### Level 1
<img width="800" alt="Level 1" src="https://github.com/user-attachments/assets/b497a274-586c-4060-b5ad-ff32f92c8cbd" />

## Physics overview:
It all operates based on a system of **Nodes** and **Beams**:
- **Nodes** are physical points with mass, inertia, and gravity.
- **Beams** convey forces - they have a set default length and will apply forces to nodes, depending on if they are in tension or compression.
- **Beams** will change color depending on the force applied:  
  - <span style="color: blue;">Blue</span>: at rest  
  - More <span style="color: green;">Green</span>: in tension  
  - More <span style="color: red;">Red</span>: in compression  
- Each **Beam** exists between two **Nodes** and keeps a reference to both.
- On top of the compression/tension system is a basic collision detector needed for driveable paved beams - a "wheel" node will collide with any paved beam.

## Note on architecture:
The code is split into multiple files, but I left a large degree of intercommunication between the component modules. 
So it needs to load a reference to a 'game' handler for most other objects, at least for painting stuff to display. 

This probably isn't the best way of doing this, but doing it another way would require a rewrite of a lot of code, and since it works, I just decided to leave it as-is.
