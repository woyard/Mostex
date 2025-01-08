# My own simple physics simulator and bridge builder game written in Pygame for a school project.

## Some screenshots:

### home screen
<img width="800" alt="Snipaste_2025-01-08_13-11-09" src="https://github.com/user-attachments/assets/3278fd0d-a15b-4663-a68c-5556cc0cb656" />

### level 1
<img width="800" alt="Snipaste_2025-01-08_13-11-33" src="https://github.com/user-attachments/assets/b497a274-586c-4060-b5ad-ff32f92c8cbd" />

## Physics overview:
It all operates based on a system of <b>Nodes</b> and <b>Beams</b> 
- <b>Nodes</b> nodes are physical points witb mass, inertia and gravity
- <b>Beams</b> beams convey forces - they have a set default length, and will apply forces to nodes, depending if in tension or compression
 each <b>Beam</b> and <b>Nodes</b> exists between two node and keeps a reference to them

## note on architecture:
The code is split into multiple files, but I left a large degree of intercommunication between the component modules, 
so it needs to load a reference to a 'game' game handler for most other objects, at least for painting stuff to display. 

This probably isn't the best way for doing this but doing it another way would require a rewrite of a lot of code, and since it works I just deciced to leave it as-is.
