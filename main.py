from character import Character
import random

def elegir_role():
    roles = {
        "1": "rogue",
        "2": "tanque",
        "3": "wizard",
        "4": "paladin"
    }
    print("Elige un personaje:")
    print("1) Rogue - alto daño, bajo HP, parry bajo, crítico medio")
    print("2) Tanque - daño medio, HP alta, parry alto, crítico medio")
    print("3) Wizard - daño bajo, HP bajo, parry bajo, crítico muy alto")
    print("4) Paladin - daño bajo, HP alta, parry alto, crítico bajo")
    choice = None
    while choice not in roles:
        choice = input("Selecciona 1/2/3/4: ").strip()
    return roles[choice]

def crear_personaje(nombre, role):
    if role == "rogue":
        return Character(nombre, role, hp=100, base_damage=20, parry_prob=0.2, crit_prob=0.2)
    if role == "tanque":
        return Character(nombre, role, hp=300, base_damage=10, parry_prob=0.4, crit_prob=0.2)
    if role == "wizard":
        return Character(nombre, role, hp=100, base_damage=5, parry_prob=0.2, crit_prob=0.5)
    if role == "paladin":
        return Character(nombre, role, hp=200, base_damage=5, parry_prob=0.5, crit_prob=0.1)

def elegir_jugador_vivo_index(jugadores):
    vivos = [i for i, j in enumerate(jugadores) if j.is_alive()]
    if not vivos:
        return None
    return random.choice(vivos)

def elegir_objetivo(jugador_actual, jugadores, allow_self=False, multiple=False):
    vivos = [p for p in jugadores if p.is_alive()]
    if not allow_self:
        vivos = [p for p in vivos if p is not jugador_actual]
    if not vivos:
        return []
    if multiple:
        return [p for p in jugadores if p.is_alive() and p is not jugador_actual]
    print("Elige objetivo:")
    opciones = []
    for idx, p in enumerate(jugadores, start=1):
        if p.is_alive() and (allow_self or p is not jugador_actual):
            opciones.append((idx, p))
            print(f"{idx}) {p.describe()}")
    while True:
        sel = input("Ingresa el número del objetivo: ").strip()
        if not sel.isdigit():
            print("Entrada inválida.")
            continue
        seln = int(sel)
        for idx, p in opciones:
            if seln == idx:
                return [p]
        print("Opción no válida, intenta de nuevo.")

def main():
    print("Bienvenido al juego de luchas más grande del mundo (versión consola con habilidades)")
    while True:
        try:
            numero_Jugadores = int(input("Selecciona el numero de jugadores [2,3,4]: ").strip())
            if numero_Jugadores in (2,3,4):
                break
        except:
            pass
        print("Entrada inválida. Intenta 2, 3 o 4.")
    while True:
        try:
            numero_turnos = int(input("Selecciona el numero de turnos por jugar: ").strip())
            if numero_turnos > 0:
                break
        except:
            pass
        print("Ingresa un número de turnos válido (>0).")
    lista_jugadores = []
    for i in range(1, numero_Jugadores + 1):
        nombre = input(f"Elija el nombre del jugador {i}: ").strip() or f"Jugador{i}"
        role = elegir_role()
        player = crear_personaje(nombre, role)
        lista_jugadores.append(player)
        print(f"Creado: {player.describe()}")
        print("Habilidades:")
        print(player.list_skills())
        print("-" * 40)
    for turno_idx in range(1, numero_turnos + 1):
        print("\n" + "=" * 50)
        print(f"TURNO {turno_idx} / {numero_turnos}")
        vivos = [p for p in lista_jugadores if p.is_alive()]
        if len(vivos) <= 1:
            print("Queda 0 o 1 jugador en pie: termina la partida.")
            break
        atacante_idx = elegir_jugador_vivo_index(lista_jugadores)
        atacante = lista_jugadores[atacante_idx]
        print(f"Es el turno de: {atacante.describe()}")
        print("Opciones:\n1) Atacar\n2) Usar habilidad\n3) Pasar")
        accion = input("Elige 1/2/3: ").strip()
        if accion == "1":
            targets = elegir_objetivo(atacante, lista_jugadores, allow_self=False)
            if targets:
                atacante.attack(targets[0])
        elif accion == "2":
            print("Habilidades disponibles:")
            for i, (k, v) in enumerate(atacante.skills.items(), start=1):
                print(f"{i}) {k} - {v.get('desc','')} (usos: {v.get('uses','-')}, dur: {v.get('duration','-')})")
            sel = input("Selecciona el número de la habilidad o ENTER para cancelar: ").strip()
            if sel.isdigit():
                seln = int(sel)
                keys = list(atacante.skills.keys())
                if 1 <= seln <= len(keys):
                    skill_name = keys[seln - 1]
                    if skill_name in ("Meteor",):
                        targets = elegir_objetivo(atacante, lista_jugadores, allow_self=False, multiple=True)
                    elif skill_name in ("Blessing",):
                        targets = elegir_objetivo(atacante, lista_jugadores, allow_self=False)
                    elif skill_name in ("RepairArmor", "ShieldWall", "ArcaneSurge", "Shadowdance"):
                        targets = [atacante]
                    elif skill_name in ("Backstab", "HolyStrike"):
                        targets = elegir_objetivo(atacante, lista_jugadores, allow_self=False)
                    else:
                        targets = elegir_objetivo(atacante, lista_jugadores, allow_self=False)
                    if not isinstance(targets, list):
                        targets = [targets] if targets else []
                    if targets or atacante.skills[skill_name].get("type") in ("single", "uses"):
                        atacante.use_skill(skill_name, targets, lista_jugadores)
                else:
                    print("Selección inválida.")
            else:
                print("Cancelado.")
        else:
            print(f"{atacante.nombre} decide esperar este turno.")
        for p in lista_jugadores:
            if p.is_alive():
                p.end_turn_update()
        print("\nEstado actual de jugadores:")
        for p in lista_jugadores:
            print(p.describe())
    ganador = None
    for p in lista_jugadores:
        if ganador is None or p.hp > ganador.hp:
            ganador = p
    if ganador:
        print(f"\nEl ganador es {ganador.nombre} con {ganador.hp} HP restante. ¡Felicidades!")
    else:
        print("No hay ganador.")

if __name__ == "__main__":
    main()
