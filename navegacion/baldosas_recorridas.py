from controller import Robot
import math

TIME_STEP = 32
MAX_VEL = 6.28

robot = Robot()

gps = robot.getDevice("gps")
gps.enable(TIME_STEP)

iu = robot.getDevice("inertial_unit")
iu.enable(TIME_STEP)


wheel_l = robot.getDevice("wheel_left_motor")
wheel_l.setPosition(float("inf"))
wheel_l.setVelocity(0)

wheel_r = robot.getDevice("wheel_right_motor")
wheel_r.setPosition(float("inf"))
wheel_r.setVelocity(0)

l_distance = robot.getDevice("left_distance")
l_distance.enable(TIME_STEP)

r_distance = robot.getDevice("right_distance")
r_distance.enable(TIME_STEP)

f_distance = robot.getDevice("front_distance")
f_distance.enable(TIME_STEP)

position = {"x": 0, "y": 0}
rotation = 0

def update_position():
    global position
    x, _, y = gps.getValues()
    position = {"x": x, "y": y}

def update_rotation():
    global rotation
    _, _, rotation = iu.getRollPitchYaw()

def update_vars():
    update_position()
    update_position()

def step():
    result = robot.step(TIME_STEP)
    update_vars()
    return result

def angle_diff(a, b):
    clockwise = (a - b) % math.tau
    counterclockwise = (b - a) % math.tau
    return min(clockwise, counterclockwise)

def girar(rad):
    lastRot = rotation
    deltaRot = 0

    while step() != -1:
        deltaRot += angle_diff(rotation, lastRot)
        lastRot = rotation

        diff = angle_diff(deltaRot, abs(rad))

        if diff <= 0.01:
            break

        mul = (4 / math.pi) * diff
        mul = min(max(mul, 0.1), 1)

        if rad > 0:
            wheel_l.setVelocity(mul * MAX_VEL)
            wheel_r.setVelocity(-mul * MAX_VEL)
        else:
            wheel_l.setVelocity(-mul * MAX_VEL)
            wheel_r.setVelocity(mul * MAX_VEL)

    wheel_l.setVelocity(0)
    wheel_r.setVelocity(0)

def dist(pt1, pt2):
    return math.sqrt((pt2["x"] - pt1["x"]) ** 2 + (pt2["y"] - pt1["y"]) ** 2)

def avanzar(distance):
    initPos = position

    while step() != -1:
        diff = abs(distance) - dist(position, initPos)

        vel = min(max(diff / 0.01, 0.1), 1)
        if distance < 0: vel = -1

        wheel_l.setVelocity(vel * MAX_VEL)
        wheel_r.setVelocity(vel * MAX_VEL)

        if diff < 0.001:
            break

    wheel_l.setVelocity(0)
    wheel_r.setVelocity(0)

def evaluar_baldosa_delantera():
    coordenada_y = position['y']
    baldosa_delantera_a_evaluar = coordenada_y - 0.12
    return baldosa_delantera_a_evaluar

def evaluar_baldosa_derecha():
    coordenada_x = position['x']
    baldosa_derecha_a_evaluar = coordenada_x + 0.12
    return baldosa_derecha_a_evaluar

def evaluar_baldosa_izquierda():
    coordenada_x = position['x']
    baldosa_izquierda_a_evaluar = coordenada_x - 0.12
    return baldosa_izquierda_a_evaluar


def isVisited(visitedTiles):
    gridIndex = positionToGrid(posicion_inicial)
    return gridIndex in visitedTiles


def positionToGrid(posicion_inicial): # devuelve las coordenadas dentro de la grilla
    grilla = []
    columna = round((position['x'] - posicion_inicial['x']) / 0.12)
    grilla.append(columna)
    fila = round((position['y'] - posicion_inicial['y']) / 0.12)
    grilla.append(fila)
    tupla_grilla = tuple(grilla)
    return tupla_grilla

def avanzarBien(difurcaciones, baldosas_recorridas, nro_baldosa):
    baldosa_avanzada = 0
    if front_distance < 0.13:
        if left_distance < 0.13 and right_distance < 0.13:
            girar(-0.25 * math.tau)
        elif left_distance < 0.13:
            girar(0.25 * math.tau)
        elif right_distance < 0.13:
            girar(-0.25 * math.tau)
        else:
            girar(-0.25 * math.tau)
    else:
        avanzar(0.12)
        print(isVisited(baldosas_recorridas))
        # print(difurcaciones)
        
        if not positionToGrid(posicion_inicial) in baldosas_recorridas: # agrego nuevo if, que solo marque True si lo que devuelve positionToGrid no está en baldosas_recorridas
            baldosas_recorridas[positionToGrid(posicion_inicial)] = True # saco argumento position
            for k, value in baldosas_recorridas.items():
                print(f'{k}: {value}')
            print("---")
        # else:
        #     baldosas_recorridas[positionToGrid()] = False
        baldosa_avanzada = 1
        if left_distance >= 0.13 or right_distance >= 0.13 and front_distance <= 0.08:
            if baldosa_avanzada == 1 and len(difurcaciones) == 0:
                print('primera difurcacion')
                difurcaciones.append(position.copy())
                print(difurcaciones)
        elif front_distance >= 0.13 and (left_distance >= 0.13 or right_distance >= 0.13):
            if baldosa_avanzada == 1 and len(difurcaciones) == 0:
                print('primera difurcacion')
                difurcaciones.append(position.copy())
                print(difurcaciones)
    return nro_baldosa


difurcaciones = []
baldosas_recorridas = {}
nro_baldosa = 0
start_time = robot.getTime()
me_aleje_de_difurcacion = False

step()
posicion_inicial = position.copy()
while step() != -1:
    left_distance = l_distance.getValue()
    right_distance = r_distance.getValue()
    front_distance = f_distance.getValue()
    nro_baldosa = avanzarBien(difurcaciones, baldosas_recorridas, nro_baldosa)
    if difurcaciones and dist(position, difurcaciones[0]) > 0.5:
        me_aleje_de_difurcacion = True
    if difurcaciones and dist(position, difurcaciones[0]) < 0.1 and me_aleje_de_difurcacion:
        if front_distance > 0.13 and right_distance >= 0.13:
            girar(0.25 * math.tau)
        elif front_distance > 0.13 and left_distance >= 0.13:
            girar(-0.25 * math.tau)
        me_aleje_de_difurcacion = False
    if (robot.getTime() - start_time) * 1000.0 >= 120000:
        break
