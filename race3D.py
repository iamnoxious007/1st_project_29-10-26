from ursina import *
import random

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

ROAD_WIDTH = 12
SEGMENT_LENGTH = 40
SEGMENT_COUNT = 6
TOTAL_LENGTH = SEGMENT_LENGTH * SEGMENT_COUNT

speed = 0.0
distance = 0.0

MAX_SPEED = 35
ACCELERATION = 15
BRAKING = 25

# =====================================
# 3. SKY
# =====================================

Sky()

# =====================================
# 4. PLAYER CAR
# =====================================

car = Entity(position=(0, 0, 0))

# Car body
Entity(
    parent=car,
    model="cube",
    color=color.red,
    shader=unlit_shader,
    scale=(1.5, 0.6, 2.8),
    position=(0, 0.55, 0)
)

# Cabin
Entity(
    parent=car,
    model="cube",
    color=color.blue,
    shader=unlit_shader,
    scale=(1.05, 0.55, 1.2),
    position=(0, 1.1, -0.2)
)

# Four wheels
for x in [-0.8, 0.8]:
    for z in [-0.85, 0.85]:
        Entity(
            parent=car,
            model="cube",
            color=color.black,
            shader=unlit_shader,
            scale=(0.3, 0.45, 0.55),
            position=(x, 0.3, z)
        )

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
        color=color.black,
        shader=unlit_shader,
        scale=(ROAD_WIDTH, 0.1, SEGMENT_LENGTH),
        position=(0, -0.05, z)
    )

    # Road edge lines
    for x in [-1.7, 5.7]:
        Entity(
            parent=road,
            model="cube",
            color=color.black,
            shader=unlit_shader,
            scale=(0.1, 0.03, SEGMENT_LENGTH),
            position=(x, 1.56, 0)
        )

    # Dashed centre line
    for lane_z in range(-16, 20, 8):
        Entity(
            parent=road,
            model="cube",
            color=color.pink,
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
                color=color.green,
                shader=unlit_shader,
                scale=(0.45, 2, 0.45),
                position=(tx, 1, tz)
            )

            leaves = Entity(
                model="sphere",
                color=color.green,
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
