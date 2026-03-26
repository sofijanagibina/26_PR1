import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple

class Mezgls:
    def __init__(self, id, vertiba, punkti_pirmais, punkti_otrais, banka, dzilums, kuras_kartas_speles=True):
        self.id = id
        self.vertiba = vertiba
        self.punkti_pirmais = punkti_pirmais
        self.punkti_otrais = punkti_otrais
        self.banka = banka
        self.dzilums = dzilums
        self.pecteci = []
        self.kuras_kartas_speles = kuras_kartas_speles  # True ja cilvēks, False ja dators

class Koks:
    def __init__(self):
        self.mezgli = []
    def pievienot(self, mezgls):
        self.mezgli.append(mezgls)

#Globālie mainīgie
koks = Koks()
MAX_DZILUMS = 5
TERMINAL_VALUE = 1200
MULTIPLIERS = (2, 3, 4)
nakamais_id = 0        

def izrekini_rezultatu(skaitlis, reizinatajs, punkti, bank):
    jauns_skaitlis = skaitlis * reizinatajs
    jauni_punkti = punkti
    jauna_banka = bank
    if jauns_skaitlis % 2 == 0:
        jauni_punkti = jauni_punkti - 1
    else:
        jauni_punkti = jauni_punkti + 1
    if jauns_skaitlis % 10 == 0 or jauns_skaitlis % 10 == 5:
        jauna_banka = jauna_banka + 1

    # Pārbauda, vai spēle beidzas
    if jauns_skaitlis >= 1200:
        jauni_punkti += jauna_banka
        jauna_banka = 0 

    return jauns_skaitlis, jauni_punkti, jauna_banka

def genereet_koku(sakuma_skaitlis, max_dzilums, cilveks_sak=True):
    koks = Koks()
    nakamais_id = 0

    sakne = Mezgls(nakamais_id, sakuma_skaitlis, 0, 0, 0, 0, cilveks_sak)
    koks.pievienot(sakne)
    nakamais_id = nakamais_id + 1

    rinda = []
    rinda.append(sakne)

    while len(rinda) > 0:
        tagad = rinda[0]
        rinda.pop(0)
        if tagad.dzilums >= max_dzilums:
            continue
        if tagad.vertiba >= 1200:
            continue
        for reiz in [2, 3, 4]:
            if tagad.kuras_kartas_speles:
                rez, jp, jb = izrekini_rezultatu(tagad.vertiba, reiz, tagad.punkti_pirmais, tagad.banka)
                j_p1 = jp
                j_p2 = tagad.punkti_otrais
            else:
                rez, jp, jb = izrekini_rezultatu(tagad.vertiba, reiz, tagad.punkti_otrais, tagad.banka)
                j_p1 = tagad.punkti_pirmais
                j_p2 = jp
            if rez >= 1200:
                if tagad.kuras_kartas_speles:
                    j_p1 = j_p1 + jb
                else:
                    j_p2 = j_p2 + jb
                jb = 0
            jaunais = Mezgls(nakamais_id, rez, j_p1, j_p2, jb, tagad.dzilums + 1, kuras_kartas_speles=not tagad.kuras_kartas_speles)
            koks.pievienot(jaunais)
            tagad.pecteci.append(nakamais_id)
            nakamais_id = nakamais_id + 1
            if rez < 1200:
                rinda.append(jaunais)

    return koks

def izveidot_pecteci(mezgls):
    global koks, nakamais_id

    if len(mezgls.pecteci) > 0 or mezgls.vertiba >= 1200:
        return

    for reiz in [2,3,4]:
        if mezgls.kuras_kartas_speles:  
            rez, jp1, jb = izrekini_rezultatu(mezgls.vertiba, reiz, mezgls.punkti_pirmais, mezgls.banka)
            j_p1 = jp1
            j_p2 = mezgls.punkti_otrais
        else: 
            rez, jp2, jb = izrekini_rezultatu(mezgls.vertiba, reiz, mezgls.punkti_otrais, mezgls.banka)
            j_p1 = mezgls.punkti_pirmais
            j_p2 = jp2

        if rez >= 1200:
            if mezgls.kuras_kartas_speles:
                j_p1 += jb
            else:
                j_p2 += jb
            jb = 0

        jaunais = Mezgls(nakamais_id, rez, j_p1, j_p2, jb, mezgls.dzilums + 1,
                          kuras_kartas_speles=not mezgls.kuras_kartas_speles)
        koks.pievienot(jaunais)
        mezgls.pecteci.append(nakamais_id)
        nakamais_id += 1

# Šī funkcija aprēķina heiristisko vērtējumu virsotnei
def heiristika(mezgls):
    # Aprēķina punktu starpību starp spēlētājiem
    starpiba = mezgls.punkti_pirmais - mezgls.punkti_otrais
    # Aprēķina skaitļa paritātes ietekmi, pārbaudot, vai skaitlis ir pāra vai nepāra
    if mezgls.vertiba % 2 == 0:
        paritate = -1
    else:
        paritate = 1  
    # Aprēķina bankas punktu nozīmīgumu atkarībā no spēles beigu tuvuma    
    beigu_faktors = bankas_beigu_faktors(mezgls)
    # Apvieno visus faktorus vienā vērtējumā
    h_vertiba = starpiba + 0.2 * paritate + beigu_faktors * mezgls.banka
    return h_vertiba
# Šī funkcija aprēķina bankas punktu nozīmīgumu atkarībā no spēles beigu tuvuma
def bankas_beigu_faktors(mezgls):
    # Iespējamie reizinātāji
    reizinataji = [2, 3, 4]
    # Pārbauda, vai spēlētājs var pabeigt spēli šajā gājienā
    for r in reizinataji:
        if r * mezgls.vertiba >= 1200:
            return 1
    # Pārbauda, vai pretinieks var pabeigt spēli nākamajā gājienā
    for r1 in reizinataji:
        for r2 in reizinataji:
            if r1 * r2 * mezgls.vertiba >= 1200:
                return -1    
    # Ja spēles beigas nav tuvu, bankas ietekme ir nulle
    return 0

apmekleti_mezgli_minimax = 0
apmekleti_mezgli_alfabeta = 0

def minimax(mezgls, dzilums, maksimizetajs):
    global apmekleti_mezgli_minimax
    apmekleti_mezgli_minimax += 1

    if dzilums == 0 or mezgls.vertiba >= 1200:
        return heiristika(mezgls), mezgls.id

    if len(mezgls.pecteci) == 0:
        izveidot_pecteci(mezgls)

    if maksimizetajs:
        labs_vertejums = float('-inf')
        labs_id = None
        for pectec_id in mezgls.pecteci:
            pectec_mezgls = koks.mezgli[pectec_id]
            vertejums, _ = minimax(pectec_mezgls, dzilums - 1, False)
            if vertejums > labs_vertejums:
                labs_vertejums = vertejums
                labs_id = pectec_id
        return labs_vertejums, labs_id
    else:
        labs_vertejums = float('inf')
        labs_id = None
        for pectec_id in mezgls.pecteci:
            pectec_mezgls = koks.mezgli[pectec_id]
            vertejums, _ = minimax(pectec_mezgls, dzilums - 1, True)
            if vertejums < labs_vertejums:
                labs_vertejums = vertejums
                labs_id = pectec_id
        return labs_vertejums, labs_id

def alfabeta(mezgls, dzilums, maksimizetajs, alfa = float('-inf'), beta = float('inf')):
    global apmekleti_mezgli_alfabeta
    apmekleti_mezgli_alfabeta += 1

    if dzilums == 0 or mezgls.vertiba >= 1200:
        return heiristika(mezgls), mezgls.id

    if len(mezgls.pecteci) == 0:
        izveidot_pecteci(mezgls)

    if maksimizetajs:
        labs_vertejums = float('-inf')
        labs_id = None
        for pectec_id in mezgls.pecteci:
            pectec_mezgls = koks.mezgli[pectec_id]
            vertejums, _ = alfabeta(pectec_mezgls, dzilums - 1, False, alfa, beta)
            if vertejums > labs_vertejums:
                labs_vertejums = vertejums
                labs_id = pectec_id
            if labs_vertejums >= beta:
                break    
            alfa = max(alfa, labs_vertejums)
        return labs_vertejums, labs_id
    else:
        labs_vertejums = float('inf')
        labs_id = None
        for pectec_id in mezgls.pecteci:
            pectec_mezgls = koks.mezgli[pectec_id]
            vertejums, _ = alfabeta(pectec_mezgls, dzilums - 1, True, alfa, beta)
            if vertejums < labs_vertejums:
                labs_vertejums = vertejums
                labs_id = pectec_id
            if labs_vertejums <= alfa:
                break    
            beta = min(beta, labs_vertejums)    
        return labs_vertejums, labs_id

class GameEngine:
    def __init__(self, max_dzilums: int = MAX_DZILUMS) -> None:
        self.max_dzilums = max_dzilums
        self.koks = Koks()
        self.nakamais_id = 0
        self.tagad: Optional[Mezgls] = None
        self.algoritms = "Minimax"
        self.apmekleti_mezgli_minimax = 0
        self.apmekleti_mezgli_alfabeta = 0

    @staticmethod
    def izrekini_rezultatu(skaitlis: int, reizinatajs: int, punkti: int, bank: int) -> Tuple[int, int, int]:
        jauns_skaitlis = skaitlis * reizinatajs
        jauni_punkti = punkti
        jauna_banka = bank

        if jauns_skaitlis % 2 == 0:
            jauni_punkti -= 1
        else:
            jauni_punkti += 1

        if jauns_skaitlis % 10 == 0 or jauns_skaitlis % 10 == 5:
            jauna_banka += 1

        if jauns_skaitlis >= TERMINAL_VALUE:
            jauni_punkti += jauna_banka
            jauna_banka = 0

        return jauns_skaitlis, jauni_punkti, jauna_banka

    def reset(self) -> None:
        self.koks = Koks()
        self.nakamais_id = 0
        self.tagad = None
        self.apmekleti_mezgli_minimax = 0
        self.apmekleti_mezgli_alfabeta = 0

    def start_game(self, sakuma_skaitlis: int, cilveks_sak: bool, algoritms: str) -> None:
        if not 8 <= sakuma_skaitlis <= 18:
            raise ValueError("Sākuma skaitlim jābūt no 8 līdz 18.")
        if algoritms not in {"Minimax", "Alfabeta"}:
            raise ValueError("Algoritmam jābūt 'Minimax' vai 'Alfabeta'.")

        self.reset()
        self.algoritms = algoritms

        sakne = Mezgls(
            id=self.nakamais_id,
            vertiba=sakuma_skaitlis,
            punkti_pirmais=0,
            punkti_otrais=0,
            banka=0,
            dzilums=0,
            kuras_kartas_speles=cilveks_sak,
        )
        self.koks.pievienot(sakne)
        self.tagad = sakne
        self.nakamais_id += 1

    def izveidot_pecteci(self, mezgls: Mezgls) -> None:
        if mezgls.pecteci or mezgls.vertiba >= TERMINAL_VALUE:
            return

        for reiz in MULTIPLIERS:
            if mezgls.kuras_kartas_speles:
                rez, jp1, jb = self.izrekini_rezultatu(
                    mezgls.vertiba, reiz, mezgls.punkti_pirmais, mezgls.banka
                )
                j_p1 = jp1
                j_p2 = mezgls.punkti_otrais
            else:
                rez, jp2, jb = self.izrekini_rezultatu(
                    mezgls.vertiba, reiz, mezgls.punkti_otrais, mezgls.banka
                )
                j_p1 = mezgls.punkti_pirmais
                j_p2 = jp2

            jaunais = Mezgls(
                id=self.nakamais_id,
                vertiba=rez,
                punkti_pirmais=j_p1,
                punkti_otrais=j_p2,
                banka=jb,
                dzilums=mezgls.dzilums + 1,
                kuras_kartas_speles=not mezgls.kuras_kartas_speles,
            )
            self.koks.pievienot(jaunais)
            mezgls.pecteci.append(self.nakamais_id)
            self.nakamais_id += 1

    @staticmethod
    def bankas_beigu_faktors(mezgls: Mezgls) -> int:
        for r in MULTIPLIERS:
            if r * mezgls.vertiba >= TERMINAL_VALUE:
                return 1
        for r1 in MULTIPLIERS:
            for r2 in MULTIPLIERS:
                if r1 * r2 * mezgls.vertiba >= TERMINAL_VALUE:
                    return -1
        return 0

    def heiristika(self, mezgls: Mezgls) -> float:
        starpiba = mezgls.punkti_pirmais - mezgls.punkti_otrais
        paritate = -1 if mezgls.vertiba % 2 == 0 else 1
        beigu_faktors = self.bankas_beigu_faktors(mezgls)
        return starpiba + 0.2 * paritate + beigu_faktors * mezgls.banka

    def minimax(self, mezgls: Mezgls, dzilums: int, maksimizetajs: bool) -> Tuple[float, int]:
        self.apmekleti_mezgli_minimax += 1

        if dzilums == 0 or mezgls.vertiba >= TERMINAL_VALUE:
            return self.heiristika(mezgls), mezgls.id

        if not mezgls.pecteci:
            self.izveidot_pecteci(mezgls)

        if maksimizetajs:
            labs_vertejums = float("-inf")
            labs_id = mezgls.id
            for pectec_id in mezgls.pecteci:
                pectec_mezgls = self.koks.mezgli[pectec_id]
                vertejums, _ = self.minimax(pectec_mezgls, dzilums - 1, False)
                if vertejums > labs_vertejums:
                    labs_vertejums = vertejums
                    labs_id = pectec_id
            return labs_vertejums, labs_id

        labs_vertejums = float("inf")
        labs_id = mezgls.id
        for pectec_id in mezgls.pecteci:
            pectec_mezgls = self.koks.mezgli[pectec_id]
            vertejums, _ = self.minimax(pectec_mezgls, dzilums - 1, True)
            if vertejums < labs_vertejums:
                labs_vertejums = vertejums
                labs_id = pectec_id
        return labs_vertejums, labs_id

    def alfabeta(
        self,
        mezgls: Mezgls,
        dzilums: int,
        maksimizetajs: bool,
        alfa: float = float("-inf"),
        beta: float = float("inf"),
    ) -> Tuple[float, int]:
        self.apmekleti_mezgli_alfabeta += 1

        if dzilums == 0 or mezgls.vertiba >= TERMINAL_VALUE:
            return self.heiristika(mezgls), mezgls.id

        if not mezgls.pecteci:
            self.izveidot_pecteci(mezgls)

        if maksimizetajs:
            labs_vertejums = float("-inf")
            labs_id = mezgls.id
            for pectec_id in mezgls.pecteci:
                pectec_mezgls = self.koks.mezgli[pectec_id]
                vertejums, _ = self.alfabeta(pectec_mezgls, dzilums - 1, False, alfa, beta)
                if vertejums > labs_vertejums:
                    labs_vertejums = vertejums
                    labs_id = pectec_id
                if labs_vertejums >= beta:
                    break
                alfa = max(alfa, labs_vertejums)
            return labs_vertejums, labs_id

        labs_vertejums = float("inf")
        labs_id = mezgls.id
        for pectec_id in mezgls.pecteci:
            pectec_mezgls = self.koks.mezgli[pectec_id]
            vertejums, _ = self.alfabeta(pectec_mezgls, dzilums - 1, True, alfa, beta)
            if vertejums < labs_vertejums:
                labs_vertejums = vertejums
                labs_id = pectec_id
            if labs_vertejums <= alfa:
                break
            beta = min(beta, labs_vertejums)
        return labs_vertejums, labs_id

    def get_state(self) -> dict:
        if self.tagad is None:
            return {
                "vertiba": 0,
                "player": 0,
                "computer": 0,
                "banka": 0,
                "human_turn": True,
                "game_over": False,
                "winner": "",
            }

        winner = ""
        if self.tagad.vertiba >= TERMINAL_VALUE:
            if self.tagad.punkti_pirmais > self.tagad.punkti_otrais:
                winner = "Cilvēks uzvarēja"
            elif self.tagad.punkti_pirmais < self.tagad.punkti_otrais:
                winner = "Dators uzvarēja"
            else:
                winner = "Neizšķirts"

        return {
            "vertiba": self.tagad.vertiba,
            "player": self.tagad.punkti_pirmais,
            "computer": self.tagad.punkti_otrais,
            "banka": self.tagad.banka,
            "human_turn": self.tagad.kuras_kartas_speles,
            "game_over": self.tagad.vertiba >= TERMINAL_VALUE,
            "winner": winner,
        }

    def human_move(self, reiz: int) -> str:
        if self.tagad is None:
            raise RuntimeError("Spēle vēl nav sākta.")
        if self.tagad.vertiba >= TERMINAL_VALUE:
            raise RuntimeError("Spēle jau ir beigusies.")
        if not self.tagad.kuras_kartas_speles:
            raise RuntimeError("Pašlaik ir datora gājiens.")
        if reiz not in MULTIPLIERS:
            raise ValueError("Atļauti tikai reizinātāji 2, 3 vai 4.")

        if not self.tagad.pecteci:
            self.izveidot_pecteci(self.tagad)

        rez, j_p1, jb = self.izrekini_rezultatu(
            self.tagad.vertiba, reiz, self.tagad.punkti_pirmais, self.tagad.banka
        )
        j_p2 = self.tagad.punkti_otrais

        for pectecis_id in self.tagad.pecteci:
            pectecis = self.koks.mezgli[pectecis_id]
            if (
                pectecis.vertiba == rez
                and pectecis.punkti_pirmais == j_p1
                and pectecis.punkti_otrais == j_p2
                and pectecis.banka == jb
            ):
                self.tagad = pectecis
                return f"Tu izvēlējies x{reiz}. Jaunā vērtība: {self.tagad.vertiba}."

        raise RuntimeError("Neizdevās atrast nākamo stāvokli pēc cilvēka gājiena.")

    def computer_move(self) -> str:
        if self.tagad is None:
            raise RuntimeError("Spēle vēl nav sākta.")
        if self.tagad.vertiba >= TERMINAL_VALUE:
            raise RuntimeError("Spēle jau ir beigusies.")
        if self.tagad.kuras_kartas_speles:
            raise RuntimeError("Pašlaik ir cilvēka gājiens.")

        if self.algoritms == "Minimax":
            score, labs_id = self.minimax(self.tagad, self.max_dzilums, False)
            apmekleti = self.apmekleti_mezgli_minimax
            nosaukums = "Minimax"
        else:
            score, labs_id = self.alfabeta(self.tagad, self.max_dzilums, False)
            apmekleti = self.apmekleti_mezgli_alfabeta
            nosaukums = "Alfabeta"

        ieprieks = self.tagad.vertiba
        self.tagad = self.koks.mezgli[labs_id]
        reiz = self.tagad.vertiba // ieprieks if ieprieks else 0
        return (
            f"Dators izvēlējās x{reiz} ar {nosaukums} "
            f"(vērtējums: {score:.2f}, apmeklētie mezgli: {apmekleti})."
        )

class GameGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Skaitļu spēle")
        self.root.geometry("820x620")
        self.root.minsize(760, 560)

        self.engine = GameEngine()

        self.start_number_var = tk.StringVar(value="8")
        self.first_player_var = tk.StringVar(value="cilvēks")
        self.algorithm_var = tk.StringVar(value="Minimax")

        self.current_value_var = tk.StringVar(value="-")
        self.player_score_var = tk.StringVar(value="0")
        self.computer_score_var = tk.StringVar(value="0")
        self.bank_var = tk.StringVar(value="0")
        self.turn_var = tk.StringVar(value="-")
        self.status_var = tk.StringVar(value="Sāc jaunu spēli")

        self._build_ui()
        self._set_move_buttons_state(False)

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        setup = ttk.LabelFrame(main, text="Iestatījumi", padding=12)
        setup.pack(fill="x")

        ttk.Label(setup, text="Sākuma skaitlis (8-18):").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(setup, textvariable=self.start_number_var, width=10).grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(setup, text="Kurš sāk:").grid(row=0, column=2, sticky="w", padx=(18, 8), pady=4)
        ttk.Combobox(
            setup,
            textvariable=self.first_player_var,
            state="readonly",
            values=["cilvēks", "dators"],
            width=12,
        ).grid(row=0, column=3, sticky="w", pady=4)

        ttk.Label(setup, text="Algoritms:").grid(row=0, column=4, sticky="w", padx=(18, 8), pady=4)
        ttk.Combobox(
            setup,
            textvariable=self.algorithm_var,
            state="readonly",
            values=["Minimax", "Alfabeta"],
            width=12,
        ).grid(row=0, column=5, sticky="w", pady=4)

        ttk.Button(setup, text="Sākt spēli", command=self.start_game).grid(row=0, column=6, padx=(18, 0), pady=4)

        state = ttk.LabelFrame(main, text="Spēles stāvoklis", padding=12)
        state.pack(fill="x", pady=(12, 0))

        labels = [
            ("Pašreizējā vērtība", self.current_value_var),
            ("Tavi punkti", self.player_score_var),
            ("Datora punkti", self.computer_score_var),
            ("Banka", self.bank_var),
            ("Gājiens", self.turn_var),
        ]
        for i, (title, var) in enumerate(labels):
            card = ttk.Frame(state, padding=8)
            card.grid(row=0, column=i, sticky="nsew", padx=4, pady=4)
            ttk.Label(card, text=title).pack(anchor="center")
            ttk.Label(card, textvariable=var, font=("TkDefaultFont", 12, "bold")).pack(anchor="center", pady=(6, 0))
            state.columnconfigure(i, weight=1)

        ttk.Label(main, textvariable=self.status_var, font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(12, 0))

        moves = ttk.LabelFrame(main, text="Tavs gājiens", padding=12)
        moves.pack(fill="x", pady=(12, 0))

        self.move_buttons = []
        for reiz in MULTIPLIERS:
            btn = ttk.Button(moves, text=f"x{reiz}", command=lambda r=reiz: self.play_human_move(r))
            btn.pack(side="left", padx=6)
            self.move_buttons.append(btn)

        ttk.Button(moves, text="Datora gājiens", command=self.play_computer_move).pack(side="left", padx=(24, 6))

        log_frame = ttk.LabelFrame(main, text="Notikumu žurnāls", padding=12)
        log_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.log = tk.Text(log_frame, wrap="word", height=18, state="disabled")
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        scrollbar.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=scrollbar.set)

    def add_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_move_buttons_state(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for btn in self.move_buttons:
            btn.configure(state=state)

    def refresh_state(self) -> None:
        state = self.engine.get_state()
        self.current_value_var.set(str(state["vertiba"]))
        self.player_score_var.set(str(state["player"]))
        self.computer_score_var.set(str(state["computer"]))
        self.bank_var.set(str(state["banka"]))
        self.turn_var.set("cilvēks" if state["human_turn"] else "dators")

        if state["game_over"]:
            self.status_var.set(f"Spēle beigusies — {state['winner']}")
            self._set_move_buttons_state(False)
            self.add_log(f"Spēle beigusies. {state['winner']}")
        else:
            self.status_var.set("Cilvēka gājiens" if state["human_turn"] else "Datora gājiens")
            self._set_move_buttons_state(state["human_turn"])

    def start_game(self) -> None:
        try:
            skaitlis = int(self.start_number_var.get())
            cilveks_sak = self.first_player_var.get() == "cilvēks"
            algoritms = self.algorithm_var.get()
            self.engine.start_game(skaitlis, cilveks_sak, algoritms)
        except ValueError as exc:
            messagebox.showerror("Kļūda", str(exc))
            return

        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        self.add_log(
            f"Sākta jauna spēle. Sākuma skaitlis: {skaitlis}. "
            f"Pirmais: {'cilvēks' if cilveks_sak else 'dators'}. Algoritms: {algoritms}."
        )
        self.refresh_state()

        if not cilveks_sak:
            self.root.after(250, self.play_computer_move)

    def play_human_move(self, reiz: int) -> None:
        try:
            text = self.engine.human_move(reiz)
        except (RuntimeError, ValueError) as exc:
            messagebox.showerror("Kļūda", str(exc))
            return

        self.add_log(text)
        self.refresh_state()

        if not self.engine.get_state()["game_over"] and not self.engine.get_state()["human_turn"]:
            self.root.after(250, self.play_computer_move)

    def play_computer_move(self) -> None:
        try:
            text = self.engine.computer_move()
        except RuntimeError as exc:
            messagebox.showerror("Kļūda", str(exc))
            return

        self.add_log(text)
        self.refresh_state()


def main() -> None:
    root = tk.Tk()
    try:
        style = ttk.Style(root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except tk.TclError:
        pass
    GameGUI(root)
    root.mainloop()

def spele():
    global koks, nakamais_id

    sakuma_skaitlis = int(input("Ievadiet sākuma skaitli (8-18): "))
    while sakuma_skaitlis < 8 or sakuma_skaitlis > 18:
        print("Skaitlim jabut no 8 lidz 18!")
        sakuma_skaitlis = int(input("Ievadiet sākuma skaitli (8-18): "))

    pirmais = input("True - cilveks, False - dators: ")
    cilveks_sak = (pirmais.lower() == "true")

    algoritms = input("Minimax vai Alfabeta: ")
    while algoritms.lower() not in ["minimax", "alfabeta"]:
        print("Ievadiet Minimax vai Alfabeta!")
        algoritms = input("Minimax vai Alfabeta: ")

    koks = genereet_koku(sakuma_skaitlis, MAX_DZILUMS, cilveks_sak)
    nakamais_id = len(koks.mezgli)
    tagad = koks.mezgli[0]

    while tagad.vertiba < 1200:

        print(f"\nVertiba tagad: {tagad.vertiba}")
        print(f"Jusu punkti: {tagad.punkti_pirmais}, Datora punkti: {tagad.punkti_otrais}, Banka: {tagad.banka}")

        if tagad.kuras_kartas_speles:
            print("Ievadiet reizinataju (2, 3, 4):")
            while True:
                try:
                    reiz = int(input())
                    if reiz in [2, 3, 4]:
                        break
                except:
                    pass
                print("Ievadiet 2, 3 vai 4") 
            rez, jp, jb = izrekini_rezultatu(tagad.vertiba, reiz, tagad.punkti_pirmais, tagad.banka)
            j_p1 = jp
            j_p2 = tagad.punkti_otrais
            if rez >= 1200:
                j_p1 += jb
                jb = 0
            for pectecis_id in tagad.pecteci:
                pectecis = koks.mezgli[pectecis_id]
                if pectecis.vertiba == rez and pectecis.punkti_pirmais == j_p1 and pectecis.punkti_otrais == j_p2 and pectecis.banka == jb:
                    tagad = pectecis
                    print(f"Jauns skaitlis: {tagad.vertiba}")
                    break
        else:
            if algoritms.lower() == "minimax":
                _, labs_id = minimax(tagad, MAX_DZILUMS, False)
            else:
                _, labs_id = alfabeta(tagad, MAX_DZILUMS, False)    
            tagad = koks.mezgli[labs_id]
            print(f"Jauns skaitlis: {tagad.vertiba}")

    print(f"Jusu punkti: {tagad.punkti_pirmais}, Datora punkti: {tagad.punkti_otrais}, Banka: {tagad.banka}")
    if tagad.punkti_pirmais > tagad.punkti_otrais:
        print("Uzvarēja cilvēks!")
    elif tagad.punkti_pirmais < tagad.punkti_otrais:
        print("Uzvarēja dators!")
    else:
        print("Neizšķirts!")    


rezims = input("Ievadiet rezimu (1 - konsole, 2 - GUI): ")
if rezims == "2":
    main()
else:
    spele()
