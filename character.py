import random

class Character:
    def __init__(self, nombre: str, role: str, hp: int, base_damage: int, parry_prob: float, crit_prob: float):
        self.nombre = nombre
        self.role = role
        self.max_hp = hp
        self.hp = hp
        self.base_damage = base_damage
        self.parry_prob = parry_prob
        self.crit_prob = crit_prob
        self.damage_bonus = 0
        self.damage_multiplier = 1.0
        self.defense_multiplier = 1.0
        self.parry_bonus = 0.0
        self.crit_bonus = 0.0
        self.stunned = False
        self.skills = {}
        self.active_effects = []
        self._assign_skills_by_role()

    def _assign_skills_by_role(self):
        if self.role == "rogue":
            self.skills = {
                "Backstab": {"desc": "Ataque sorpresa: x3 daño y ignora parry (uso único).", "type": "single", "uses": 1},
                "Shadowdance": {"desc": "Durante 2 turnos aumenta parry (+0.5).", "type": "duration", "duration": 2, "uses": 1}
            }
        elif self.role == "tanque":
            self.skills = {
                "ShieldWall": {"desc": "Reduce daño recibido a la mitad durante 2 turnos (2 usos).", "type": "uses_duration", "duration": 2, "uses": 2},
                "RepairArmor": {"desc": "Cura 50 HP (2 usos).", "type": "uses", "uses": 2}
            }
        elif self.role == "wizard":
            self.skills = {
                "Meteor": {"desc": "Ataque de área: daña a todos los enemigos (2 usos).", "type": "uses", "uses": 2},
                "ArcaneSurge": {"desc": "Aumenta probabilidad de crítico por 2 turnos (uso único).", "type": "single_duration", "duration": 2, "uses": 1}
            }
        elif self.role == "paladin":
            self.skills = {
                "HolyStrike": {"desc": "Golpe sagrado: daño mayor y te cura (uso único).", "type": "single", "uses": 1},
                "Blessing": {"desc": "Aumenta daño de un aliado durante 2 turnos (2 usos).", "type": "uses", "uses": 2, "duration": 2}
            }
        else:
            self.skills = {}

    def is_alive(self):
        return self.hp > 0

    def attack(self, other):
        if self.stunned:
            print(f"{self.nombre} está aturdido y no puede actuar este turno.")
            return
        damage = (self.base_damage + self.damage_bonus) * self.damage_multiplier
        crit_chance = max(0.0, min(1.0, self.crit_prob + self.crit_bonus))
        if random.random() <= crit_chance:
            damage *= 2
            is_crit = True
        else:
            is_crit = False
        damage = int(round(damage))
        print(f"{self.nombre} ataca a {other.nombre} {'(CRÍTICO!)' if is_crit else ''} por {damage} de potencia.")
        other.hurt(damage)

    def hurt(self, damage, ignore_parry=False):
        if not self.is_alive():
            print(f"{self.nombre} ya está fuera de combate.")
            return
        parry_chance = max(0.0, min(1.0, self.parry_prob + self.parry_bonus))
        if (not ignore_parry) and random.random() <= parry_chance:
            print(f"{self.nombre} ha logrado parry y no recibe daño.")
            damage_taken = 0
        else:
            damage_taken = int(round(damage * self.defense_multiplier))
            self.hp -= damage_taken
            if self.hp < 0:
                self.hp = 0
        print(f"{self.nombre} recibió {damage_taken} de daño. HP restante: {self.hp}")

    def use_skill(self, skill_name: str, targets: list, players: list):
        if skill_name not in self.skills:
            print("Habilidad inválida.")
            return False
        skill = self.skills[skill_name]
        if skill.get("uses", 1) == 0:
            print("No quedan usos de esa habilidad.")
            return False
        if skill_name == "Backstab":
            target = targets[0]
            damage = (self.base_damage + self.damage_bonus) * 3
            skill["uses"] = skill.get("uses", 1) - 1
            print(f"{self.nombre} usa BACKSTAB sobre {target.nombre}!")
            target.hurt(int(round(damage)), ignore_parry=True)
            return True
        if skill_name == "Shadowdance":
            duration = skill.get("duration", 2)
            skill["uses"] = skill.get("uses", 1) - 1
            self._apply_effect(name="Shadowdance_parry", attr="parry_bonus", value=0.5, remaining=duration)
            print(f"{self.nombre} entra en las sombras aumentando evasión por {duration} turnos.")
            return True
        if skill_name == "ShieldWall":
            duration = skill.get("duration", 2)
            uses_left = skill.get("uses", 0)
            if uses_left <= 0:
                print("No quedan usos.")
                return False
            skill["uses"] = uses_left - 1
            self._apply_effect(name="ShieldWall_def", attr="defense_multiplier", value=0.5, remaining=duration)
            print(f"{self.nombre} levanta el ShieldWall: recibe menos daño por {duration} turnos. (Usos restantes: {skill['uses']})")
            return True
        if skill_name == "RepairArmor":
            uses_left = skill.get("uses", 0)
            if uses_left <= 0:
                print("No quedan usos.")
                return False
            heal = 50
            skill["uses"] = uses_left - 1
            self.hp += heal
            print(f"{self.nombre} repara su armadura y recupera {heal} HP. HP ahora: {self.hp} (Usos restantes: {skill['uses']})")
            return True
        if skill_name == "Meteor":
            uses_left = skill.get("uses", 0)
            if uses_left <= 0:
                print("No quedan usos.")
                return False
            skill["uses"] = uses_left - 1
            damage = int(round((self.base_damage + self.damage_bonus) * 2.5))
            print(f"{self.nombre} lanza METEOR! Afecta a {len(targets)} enemigos por {damage} cada uno.")
            for t in targets:
                t.hurt(damage)
            return True
        if skill_name == "ArcaneSurge":
            uses_left = skill.get("uses", 1)
            if uses_left <= 0:
                print("No quedan usos.")
                return False
            duration = skill.get("duration", 2)
            skill["uses"] = uses_left - 1
            self._apply_effect(name="ArcaneSurge_crit", attr="crit_bonus", value=0.4, remaining=duration)
            print(f"{self.nombre} activa ArcaneSurge: +crit por {duration} turnos.")
            return True
        if skill_name == "HolyStrike":
            uses_left = skill.get("uses", 1)
            if uses_left <= 0:
                print("No quedan usos.")
                return False
            target = targets[0]
            skill["uses"] = uses_left - 1
            damage = int(round((self.base_damage + self.damage_bonus) * 2.5))
            heal = int(round(damage * 0.35))
            print(f"{self.nombre} ejecuta HOLY STRIKE sobre {target.nombre}: {damage} daño y cura {heal}.")
            target.hurt(damage)
            self.hp += heal
            print(f"{self.nombre} recupera {heal} HP (HP ahora: {self.hp}).")
            return True
        if skill_name == "Blessing":
            uses_left = skill.get("uses", 0)
            if uses_left <= 0:
                print("No quedan usos.")
                return False
            duration = skill.get("duration", 2)
            skill["uses"] = uses_left - 1
            ally = targets[0]
            ally._apply_effect(name=f"Blessing_from_{self.nombre}", attr="damage_multiplier", value=1.4, remaining=duration)
            print(f"{self.nombre} bendice a {ally.nombre}: +40% daño por {duration} turnos. (Usos restantes: {skill['uses']})")
            return True
        print("Habilidad no implementada.")
        return False

    def _apply_effect(self, name: str, attr: str, value, remaining: int):
        if attr == "parry_bonus":
            self.parry_bonus += value
        elif attr == "crit_bonus":
            self.crit_bonus += value
        elif attr == "defense_multiplier":
            prev = self.defense_multiplier
            self.defense_multiplier = value
            effect = {"name": name, "attr": attr, "value": value, "remaining": remaining, "prev": prev}
            self.active_effects.append(effect)
            return
        elif attr == "damage_multiplier":
            self.damage_multiplier *= value
        else:
            current = getattr(self, attr, None)
            if isinstance(current, (int, float)):
                setattr(self, attr, current + value)
        effect = {"name": name, "attr": attr, "value": value, "remaining": remaining}
        self.active_effects.append(effect)

    def end_turn_update(self):
        new_effects = []
        for eff in self.active_effects:
            eff["remaining"] -= 1
            if eff["remaining"] <= 0:
                attr = eff["attr"]
                val = eff.get("value")
                if attr == "parry_bonus":
                    self.parry_bonus -= val
                elif attr == "crit_bonus":
                    self.crit_bonus -= val
                elif attr == "defense_multiplier":
                    prev = eff.get("prev", 1.0)
                    self.defense_multiplier = prev
                elif attr == "damage_multiplier":
                    if val != 0:
                        self.damage_multiplier = max(0.0, self.damage_multiplier / val)
                else:
                    current = getattr(self, attr, None)
                    if isinstance(current, (int, float)):
                        setattr(self, attr, current - val)
                print(f"El efecto {eff['name']} sobre {self.nombre} ha expirado.")
            else:
                new_effects.append(eff)
        self.active_effects = new_effects

    def describe(self):
        s = f"{self.nombre} ({self.role}) - HP: {self.hp}/{self.max_hp} - DMG: {self.base_damage} - Parry: {self.parry_prob + self.parry_bonus:.2f} - Crit: {self.crit_prob + self.crit_bonus:.2f}"
        return s

    def list_skills(self):
        lines = []
        for k, v in self.skills.items():
            uses = v.get("uses", "-")
            dur = v.get("duration", "-")
            lines.append(f"{k} - {v.get('desc','')} (usos: {uses}, dur: {dur})")
        return "\n".join(lines)
