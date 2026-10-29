
from ursina import *
from panda3d.core import Fog
import random
from ursina.models.procedural.cylinder import Cylinder
# =====================================
# 1. START GAME
# =====================================

app = Ursina()

window.title = "3D Endless Racing"
window.color = color.rgb(135, 190, 230)
window.fps_counter.enabled = True

# Use unlit materials so colors stay visible
from ursina.shaders import unlit_shader

# =====================================
# 2. GAME SETTINGS
# =====================================

ROAD_WIDTH = 13
SEGMENT_LENGTH = 300
SEGMENT_COUNT = 6
TOTAL_LENGTH = SEGMENT_LENGTH * SEGMENT_COUNT

speed = 0.0
distance = 0.0

MAX_SPEED = 35
ACCELERATION = 15
BRAKING = 25

# =====================================
# 3. SKY AND FOG
# =====================================

Sky()

fog_color = color.rgb(135, 190, 230)

distance_fog = Fog("distance_fog")
distance_fog.setColor(
    135 / 255,
    190 / 255,
    230 / 255
)
distance_fog.setLinearRange(40, 130)

render.setFog(distance_fog)

# =====================================
# 4. PLAYER CAR
# =====================================

car = Entity(position=(0, 0, 0))

# Car body
Entity(
    parent=car,
    model="cube",
    color=color.hex("#314FBC"),
    shader=unlit_shader,
    scale=(1.5, 0.6, 2.8),
    position=(0, 0.55, 0)
)

# Cabin
Entity(
    parent=car,
    model="cube",
    color=color.hex("#C66A00"),
    shader=unlit_shader,
    scale=(1.05, 0.55, 1.2),
    position=(0, 1.1, -0.2)
)


# Four cylindrical wheels
wheels = []

for x in [-1.0, 0.69]:
    for z in [-0.85, 0.85]:
        wheel = Entity(
            parent=car,
            model=Cylinder(resolution=16, radius=0.5, height=0.3),
            color=color.hex("#B6AEAE"),
            shader=unlit_shader,
            scale=(1, 1, 1),
            rotation=(0, 0, 90),
            position=(x, 0.3, z)
        )
        wheels.append(wheel)




# =====================================
# 5. ENDLESS ROAD AND GRASS
# =====================================

segments = []

for i in range(SEGMENT_COUNT):

    z = i * SEGMENT_LENGTH

    # Grass section
    grass = Entity(
        model="cube",
        color=color.green,
        shader=unlit_shader,
        scale=(250, 0.2, SEGMENT_LENGTH),
        position=(0, -0.2, z)
    )

    # Asphalt
    road = Entity(
        model="cube",
        color=color.hex("#454545"),
        shader=unlit_shader,
        scale=(ROAD_WIDTH, 0.1, SEGMENT_LENGTH),
        position=(0, -0.05, z)
    )

    # Road edge lines
    for x in [-0.5, 0.5]:
        Entity(
            parent=road,
            model="cube",
            color=color.red,
            shader=unlit_shader,
            scale=(0.1, 0.03, SEGMENT_LENGTH),
            position=(x, 0.56, 0)
        )

    # Dashed centre line
    for lane_z in range(-16, 20, 8):
        Entity(
            parent=road,
            model="cube",
            color=color.hex("#FFFFFF"),
            shader=unlit_shader,
            scale=(0.06, 0.03, 3),
            position=(0, 0.56, lane_z)
        )

    # Trees for this section
    trees = []

    for side in [-1, 1]:
        for j in range(5):

            tx = side * random.uniform(9, 16)
            tz = z + random.uniform(
                -SEGMENT_LENGTH / 2,
                SEGMENT_LENGTH / 2
            )

            trunk = Entity(
                model="cube",
                color=color.hex("#8B4513"),
                shader=unlit_shader,
                scale=(0.45, 2, 0.45),
                position=(tx, 1, tz)
            )

            leaves = Entity(
                model="sphere",
                color=color.hex("#006400"),
                shader=unlit_shader,
                scale=(2.5, 3, 2.5),
                position=(tx, 3, tz)
            )

            trees.append((trunk, leaves, side))

    segments.append({
        "z": z,
        "grass": grass,
        "road": road,
        "trees": trees
    })

# =====================================
# 6. CAMERA
# =====================================

camera.position = (0, 7, -12)
camera.rotation_x = 20
camera.fov = 90

# =====================================
# 7. SPEED AND DISTANCE DISPLAY
# =====================================

speed_text = Text(
    text="Speed: 0 km/h",
    position=(-0.85, 0.45),
    scale=1.5,
    color=color.white
)

distance_text = Text(
    text="Distance: 0 m",
    position=(-0.85, 0.39),
    scale=1.2,
    color=color.white
)

# =====================================
# 8. GAME LOOP
# =====================================

def update():
    global speed, distance

    dt = time.dt

    # Acceleration
    if held_keys["w"] or held_keys["up arrow"]:
        speed += ACCELERATION * dt

    # Braking
    elif held_keys["s"] or held_keys["down arrow"]:
        speed -= BRAKING * dt

    # Natural slowdown
    else:
        speed -= 6 * dt

    speed = max(0, min(speed, MAX_SPEED))

    # Forward movement
    movement = speed * dt
    car.z += movement
    distance += movement

    # Steering
    steering = 7 * dt * (0.5 + speed / MAX_SPEED)

    if held_keys["a"] or held_keys["left arrow"]:
        car.x -= steering

    if held_keys["d"] or held_keys["right arrow"]:
        car.x += steering

    # Stay on road
    car.x = max(-4.5, min(4.5, car.x))

    # Recycle entire sections ahead of the car
    for segment in segments:

        if car.z > segment["z"] + SEGMENT_LENGTH:

            segment["z"] += TOTAL_LENGTH

            segment["grass"].z = segment["z"]
            segment["road"].z = segment["z"]

            # Reposition trees with the new section
            for trunk, leaves, side in segment["trees"]:

                tx = side * random.uniform(9, 16)
                tz = segment["z"] + random.uniform(
                    -SEGMENT_LENGTH / 2,
                    SEGMENT_LENGTH / 2
                )

                trunk.position = (tx, 1, tz)
                leaves.position = (tx, 3, tz)

    # Follow car
    camera.position = (
        car.x,
        car.y + 7,
        car.z - 12
    )

    # HUD
    speed_text.text = f"Speed: {int(speed * 4)} km/h"
    distance_text.text = f"Distance: {int(distance)} m"


# =====================================
# 9. RUN GAME
# =====================================

app.run()
