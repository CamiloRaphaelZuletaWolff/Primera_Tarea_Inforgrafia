import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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
                "Backstab": {"desc": "Ataque sorpresa: x3 daño y ignora parry (1 uso).", "type": "single", "uses": 1},
                "Shadowdance": {"desc": "2 turnos: +0.5 parry (1 uso).", "type": "duration", "duration": 2, "uses": 1}
            }
        elif self.role == "tanque":
            self.skills = {
                "ShieldWall": {"desc": "Reduce daño recibido a la mitad 2 turnos (2 usos).", "type": "uses_duration", "duration": 2, "uses": 2},
                "RepairArmor": {"desc": "Cura 50 HP (2 usos).", "type": "uses", "uses": 2}
            }
        elif self.role == "wizard":
            self.skills = {
                "Meteor": {"desc": "AOE: daña a todos los enemigos (2 usos).", "type": "uses", "uses": 2},
                "ArcaneSurge": {"desc": "2 turnos: +0.4 crítico (1 uso).", "type": "single_duration", "duration": 2, "uses": 1}
            }
        elif self.role == "paladin":
            self.skills = {
                "HolyStrike": {"desc": "Daño aumentado y cura un poco (1 uso).", "type": "single", "uses": 1},
                "Blessing": {"desc": "Aumenta daño de un aliado 2 turnos (2 usos).", "type": "uses", "uses": 2, "duration": 2}
            }
        else:
            self.skills = {}

    def is_alive(self):
        return self.hp > 0

    def attack(self, other, log_fn=print):
        if self.stunned:
            log_fn(f"{self.nombre} está aturdido y no puede actuar.")
            return

        damage = (self.base_damage + self.damage_bonus) * self.damage_multiplier
        crit_chance = max(0.0, min(1.0, self.crit_prob + self.crit_bonus))
        is_crit = False
        if random.random() <= crit_chance:
            damage *= 2
            is_crit = True

        damage = int(round(damage))
        log_fn(f"{self.nombre} ataca a {other.nombre}{' (CRÍTICO)' if is_crit else ''} por {damage}.")
        other.hurt(damage, log_fn=log_fn)

    def hurt(self, damage, ignore_parry=False, log_fn=print):
        if not self.is_alive():
            log_fn(f"{self.nombre} ya está fuera de combate.")
            return

        parry_chance = max(0.0, min(1.0, self.parry_prob + self.parry_bonus))
        if (not ignore_parry) and random.random() <= parry_chance:
            log_fn(f"{self.nombre} ejecutó parry y evitó el daño.")
            damage_taken = 0
        else:
            damage_taken = int(round(damage * self.defense_multiplier))
            self.hp -= damage_taken
            if self.hp < 0:
                self.hp = 0
        log_fn(f"{self.nombre} recibió {damage_taken} de daño. HP: {self.hp}/{self.max_hp}")

    def use_skill(self, skill_name: str, targets: list, all_players: list, log_fn=print):
        if skill_name not in self.skills:
            log_fn("Habilidad inválida.")
            return False

        skill = self.skills[skill_name]
        if skill.get("uses", 1) == 0:
            log_fn("No quedan usos de esa habilidad.")
            return False

        if skill_name == "Backstab":
            target = targets[0]
            damage = (self.base_damage + self.damage_bonus) * 3
            skill["uses"] = skill.get("uses", 1) - 1
            log_fn(f"{self.nombre} usa BACKSTAB sobre {target.nombre}!")
            target.hurt(int(round(damage)), ignore_parry=True, log_fn=log_fn)
            return True

        if skill_name == "Shadowdance":
            duration = skill.get("duration", 2)
            skill["uses"] = skill.get("uses", 1) - 1
            self._apply_effect(name="Shadowdance_parry", attr="parry_bonus", value=0.5, remaining=duration)
            log_fn(f"{self.nombre} activa SHADOWDANCE: +parry por {duration} turnos.")
            return True

        if skill_name == "ShieldWall":
            duration = skill.get("duration", 2)
            uses_left = skill.get("uses", 0)
            if uses_left <= 0:
                log_fn("No quedan usos.")
                return False
            skill["uses"] = uses_left - 1
            self._apply_effect(name="ShieldWall_def", attr="defense_multiplier", value=0.5, remaining=duration)
            log_fn(f"{self.nombre} activa SHIELDWALL: menos daño por {duration} turnos. (Usos restantes: {skill['uses']})")
            return True

        if skill_name == "RepairArmor":
            uses_left = skill.get("uses", 0)
            if uses_left <= 0:
                log_fn("No quedan usos.")
                return False
            heal = 50
            skill["uses"] = uses_left - 1
            self.hp += heal
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            log_fn(f"{self.nombre} usa REPAIRARMOR y cura {heal} HP. HP ahora: {self.hp}. (Usos restantes: {skill['uses']})")
            return True

        if skill_name == "Meteor":
            uses_left = skill.get("uses", 0)
            if uses_left <= 0:
                log_fn("No quedan usos.")
                return False
            skill["uses"] = uses_left - 1
            damage = int(round((self.base_damage + self.damage_bonus) * 2.5))
            log_fn(f"{self.nombre} lanza METEOR: {damage} a cada enemigo.")
            for t in targets:
                t.hurt(damage, log_fn=log_fn)
            return True

        if skill_name == "ArcaneSurge":
            uses_left = skill.get("uses", 1)
            if uses_left <= 0:
                log_fn("No quedan usos.")
                return False
            duration = skill.get("duration", 2)
            skill["uses"] = uses_left - 1
            self._apply_effect(name="ArcaneSurge_crit", attr="crit_bonus", value=0.4, remaining=duration)
            log_fn(f"{self.nombre} activa ARCANESURGE: +crit por {duration} turnos.")
            return True

        if skill_name == "HolyStrike":
            uses_left = skill.get("uses", 1)
            if uses_left <= 0:
                log_fn("No quedan usos.")
                return False
            target = targets[0]
            skill["uses"] = uses_left - 1
            damage = int(round((self.base_damage + self.damage_bonus) * 2.5))
            heal = int(round(damage * 0.35))
            log_fn(f"{self.nombre} usa HOLYSTRIKE sobre {target.nombre}: {damage} daño y cura {heal}.")
            target.hurt(damage, log_fn=log_fn)
            self.hp += heal
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            return True

        if skill_name == "Blessing":
            uses_left = skill.get("uses", 0)
            if uses_left <= 0:
                log_fn("No quedan usos.")
                return False
            duration = skill.get("duration", 2)
            skill["uses"] = uses_left - 1
            ally = targets[0]
            ally._apply_effect(name=f"Blessing_from_{self.nombre}", attr="damage_multiplier", value=1.4, remaining=duration)
            log_fn(f"{self.nombre} bendice a {ally.nombre}: +40% daño por {duration} turnos. (Usos restantes: {skill['uses']})")
            return True

        log_fn("Habilidad no implementada.")
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

    def end_turn_update(self, log_fn=print):
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
                log_fn(f"Efecto {eff['name']} en {self.nombre} expiró.")
            else:
                new_effects.append(eff)
        self.active_effects = new_effects

    def describe(self):
        return f"{self.nombre} ({self.role}) - HP: {self.hp}/{self.max_hp} - DMG: {self.base_damage} - Parry: {self.parry_prob + self.parry_bonus:.2f} - Crit: {self.crit_prob + self.crit_bonus:.2f}"

    def list_skills(self):
        lines = []
        for k, v in self.skills.items():
            uses = v.get("uses", "-")
            dur = v.get("duration", "-")
            lines.append(f"{k} - {v.get('desc','')} (usos: {uses}, dur: {dur})")
        return "\n".join(lines)

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego de Luchas - GUI (Tkinter)")
        self.players = []
        self.num_turns = 10
        self.turn_index = 0

        self._build_setup_frame()

    def _build_setup_frame(self):
        self.setup_frame = ttk.Frame(self.root, padding=12)
        self.setup_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(self.setup_frame, text="Configuración del juego", font=("Helvetica", 14, "bold")).grid(column=0, row=0, columnspan=3, pady=(0,10))

        ttk.Label(self.setup_frame, text="Número de turnos:").grid(column=0, row=1, sticky="w")
        self.spin_turns = tk.Spinbox(self.setup_frame, from_=1, to=100, width=5)
        self.spin_turns.grid(column=1, row=1, sticky="w")
        self.spin_turns.delete(0, tk.END)
        self.spin_turns.insert(0, "10")

        ttk.Label(self.setup_frame, text="Jugadores (2-4):").grid(column=0, row=2, sticky="w", pady=(10,0))
        self.btn_add = ttk.Button(self.setup_frame, text="Agregar jugador", command=self._add_player_dialog)
        self.btn_add.grid(column=1, row=2, sticky="w", pady=(10,0))

        self.lb_players = tk.Listbox(self.setup_frame, width=60, height=6)
        self.lb_players.grid(column=0, row=3, columnspan=3, pady=(8,0))

        self.btn_start = ttk.Button(self.setup_frame, text="Iniciar partida", command=self._start_game)
        self.btn_start.grid(column=0, row=4, pady=(12,0))

        self.btn_remove = ttk.Button(self.setup_frame, text="Eliminar seleccionado", command=self._remove_selected)
        self.btn_remove.grid(column=1, row=4, pady=(12,0))

        ttk.Label(self.setup_frame, text="Instrucciones: agrega entre 2 y 4 jugadores.").grid(column=0, row=5, columnspan=3, pady=(8,0))

    def _add_player_dialog(self):
        if len(self.players) >= 4:
            messagebox.showinfo("Límite", "Ya hay 4 jugadores.")
            return
        name = simpledialog.askstring("Nombre", "Nombre del jugador:", parent=self.root)
        if not name:
            return
        role = self._choose_role_dialog()
        if not role:
            return

        char = self._crear_personaje(name, role)
        self.players.append(char)
        self.lb_players.insert(tk.END, char.describe() )
        if len(self.players) >= 4:
            self.btn_add.config(state="disabled")

    def _choose_role_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Selecciona rol")
        dlg.transient(self.root)
        dlg.grab_set()
        sel = tk.StringVar(value="rogue")

        ttk.Label(dlg, text="Elige rol:", font=("Helvetica", 12)).grid(column=0, row=0, columnspan=2, pady=8)
        roles = [("Rogue","rogue"),("Tanque","tanque"),("Wizard","wizard"),("Paladin","paladin")]
        for i,(t,v) in enumerate(roles):
            ttk.Radiobutton(dlg, text=t, variable=sel, value=v).grid(column=0, row=i+1, sticky="w", padx=12)
        result = {"role": None}
        def ok():
            result["role"] = sel.get()
            dlg.destroy()
        ttk.Button(dlg, text="OK", command=ok).grid(column=0, row=6, pady=8)
        self.root.wait_window(dlg)
        return result["role"]

    def _remove_selected(self):
        sel = self.lb_players.curselection()
        if not sel:
            return
        idx = sel[0]
        self.lb_players.delete(idx)
        del self.players[idx]
        if len(self.players) < 4:
            self.btn_add.config(state="normal")

    def _crear_personaje(self, nombre, role):
        if role == "rogue":
            return Character(nombre, role, hp=100, base_damage=20, parry_prob=0.2, crit_prob=0.2)
        if role == "tanque":
            return Character(nombre, role, hp=300, base_damage=10, parry_prob=0.4, crit_prob=0.2)
        if role == "wizard":
            return Character(nombre, role, hp=100, base_damage=5, parry_prob=0.2, crit_prob=0.5)
        if role == "paladin":
            return Character(nombre, role, hp=200, base_damage=5, parry_prob=0.5, crit_prob=0.1)

    def _start_game(self):
        try:
            t = int(self.spin_turns.get())
            if t <= 0:
                raise ValueError
            self.num_turns = t
        except:
            messagebox.showerror("Error", "Número de turnos inválido.")
            return

        if len(self.players) < 2 or len(self.players) > 4:
            messagebox.showerror("Error", "Necesitas entre 2 y 4 jugadores.")
            return

        self.setup_frame.destroy()
        self._build_game_frame()

    def _build_game_frame(self):
        self.game_frame = ttk.Frame(self.root, padding=8)
        self.game_frame.grid(row=0, column=0, sticky="nsew")

        self.lbl_turn = ttk.Label(self.game_frame, text=f"Turno: 1 / {self.num_turns}", font=("Helvetica", 12, "bold"))
        self.lbl_turn.grid(column=0, row=0, sticky="w")

        self.lbl_current = ttk.Label(self.game_frame, text="Jugador actual: -", font=("Helvetica", 11))
        self.lbl_current.grid(column=1, row=0, sticky="w", padx=10)


        self.frame_status = ttk.Frame(self.game_frame, borderwidth=1, relief="solid", padding=8)
        self.frame_status.grid(column=0, row=1, rowspan=2, sticky="nsew", padx=(0,8))
        ttk.Label(self.frame_status, text="Jugadores:").grid(column=0, row=0, sticky="w")
        self.lb_status = tk.Listbox(self.frame_status, width=40, height=10)
        self.lb_status.grid(column=0, row=1, pady=6)


        self.frame_log = ttk.Frame(self.game_frame, borderwidth=1, relief="solid", padding=8)
        self.frame_log.grid(column=1, row=1, sticky="nsew")
        ttk.Label(self.frame_log, text="Registro de juego:").grid(column=0, row=0, sticky="w")
        self.txt_log = tk.Text(self.frame_log, width=60, height=12, state="disabled", wrap="word")
        self.txt_log.grid(column=0, row=1, pady=6)


        self.frame_controls = ttk.Frame(self.game_frame, padding=6)
        self.frame_controls.grid(column=0, row=3, columnspan=2, sticky="ew", pady=(8,0))
        self.btn_attack = ttk.Button(self.frame_controls, text="Atacar", command=self._action_attack)
        self.btn_attack.grid(column=0, row=0, padx=6)
        self.btn_skill = ttk.Button(self.frame_controls, text="Usar Habilidad", command=self._action_skill)
        self.btn_skill.grid(column=1, row=0, padx=6)
        self.btn_pass = ttk.Button(self.frame_controls, text="Pasar", command=self._action_pass)
        self.btn_pass.grid(column=2, row=0, padx=6)


        self.turn_index = 1
        self._refresh_status()
        self._next_turn()

    def _log(self, text):
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def _refresh_status(self):
        self.lb_status.delete(0, tk.END)
        for p in self.players:
            state = p.describe()
            if not p.is_alive():
                state += "  (FUERA)"
            self.lb_status.insert(tk.END, state)

    def _alive_players(self):
        return [p for p in self.players if p.is_alive()]

    def _choose_target_gui(self, allow_self=False, multiple=False):
        choices = []
        for p in self.players:
            if p.is_alive():
                if allow_self or p is not self.current_player:
                    choices.append(p)
        if not choices:
            return []

        if multiple:
            return [p for p in choices if p is not self.current_player]

        dlg = tk.Toplevel(self.root)
        dlg.title("Elegir objetivo")
        dlg.transient(self.root)
        dlg.grab_set()

        lb = tk.Listbox(dlg, width=50, height=8)
        for idx, p in enumerate(choices, start=1):
            lb.insert(tk.END, f"{idx}. {p.describe()}")
        lb.grid(column=0, row=0, padx=8, pady=8)

        result = {"sel": None}
        def ok():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Atención", "Selecciona un objetivo.")
                return
            result["sel"] = choices[sel[0]]
            dlg.destroy()
        ttk.Button(dlg, text="OK", command=ok).grid(column=0, row=1, pady=6)
        self.root.wait_window(dlg)
        return [result["sel"]] if result["sel"] else []

    def _next_turn(self):
        vivos = self._alive_players()
        if len(vivos) <= 1:
            self._end_game()
            return

        if self.turn_index > self.num_turns:
            self._end_game()
            return

        idx = random.choice([i for i,p in enumerate(self.players) if p.is_alive()])
        self.current_player = self.players[idx]
        self.lbl_turn.config(text=f"Turno: {self.turn_index} / {self.num_turns}")
        self.lbl_current.config(text=f"Jugador actual: {self.current_player.describe()}")
        self._log(f"--- Turno {self.turn_index}: {self.current_player.nombre} ---")
        self._refresh_status()

    def _action_attack(self):
        if not self.current_player.is_alive():
            messagebox.showinfo("Info", "Este jugador está fuera de combate.")
            return
        targets = self._choose_target_gui(allow_self=False, multiple=False)
        if not targets:
            return
        target = targets[0]
        self.current_player.attack(target, log_fn=self._log)
        self._after_action()

    def _action_skill(self):
        if not self.current_player.is_alive():
            messagebox.showinfo("Info", "Este jugador está fuera de combate.")
            return


        keys = list(self.current_player.skills.keys())
        if not keys:
            messagebox.showinfo("Info", "No tiene habilidades.")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Seleccionar habilidad")
        dlg.transient(self.root)
        dlg.grab_set()

        lb = tk.Listbox(dlg, width=60, height=8)
        for k in keys:
            v = self.current_player.skills[k]
            lb.insert(tk.END, f"{k} - {v.get('desc','')} (usos: {v.get('uses','-')})")
        lb.grid(column=0, row=0, padx=8, pady=8)

        result = {"skill": None}
        def ok():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Atención", "Selecciona una habilidad.")
                return
            result["skill"] = keys[sel[0]]
            dlg.destroy()
        ttk.Button(dlg, text="OK", command=ok).grid(column=0, row=1, pady=6)
        self.root.wait_window(dlg)

        skill = result["skill"]
        if not skill:
            return


        if skill in ("Meteor",):
            targets = self._choose_target_gui(allow_self=False, multiple=True)
        elif skill in ("Blessing",):
            targets = self._choose_target_gui(allow_self=False, multiple=False)
        elif skill in ("RepairArmor", "ShieldWall", "ArcaneSurge", "Shadowdance"):
            targets = [self.current_player]
        elif skill in ("Backstab", "HolyStrike"):
            targets = self._choose_target_gui(allow_self=False, multiple=False)
        else:
            targets = self._choose_target_gui(allow_self=False, multiple=False)

        if targets is None:
            return

        success = self.current_player.use_skill(skill, targets, self.players, log_fn=self._log)
        if success:
            self._after_action()

    def _action_pass(self):
        self._log(f"{self.current_player.nombre} pasa el turno.")
        self._after_action()

    def _after_action(self):

        for p in self.players:
            if p.is_alive():
                p.end_turn_update(log_fn=self._log)

        self._refresh_status()
        self.turn_index += 1
        self._next_turn()

    def _end_game(self):
        vivos = self._alive_players()
        if not vivos:
            self._log("Todos cayeron. Empate.")
            messagebox.showinfo("Fin", "Todos cayeron. Empate.")
            self.root.quit()
            return
        ganador = max(self.players, key=lambda p: p.hp)
        self._log(f"Partida finalizada. Ganador: {ganador.nombre} con {ganador.hp} HP.")
        messagebox.showinfo("Fin de la partida", f"Ganador: {ganador.nombre} (HP: {ganador.hp})")
        self.root.quit()

def main():
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
