#!/usr/bin/env python3
"""Fila WSJF a partir das etiquetas das issues do GitHub.

Uso:
  python3 fila.py rotulos DONO/REPO [--simular]
      cria no repositório as etiquetas da régua (bv-, tc-, rr-, sp-, P0 a P3 e estados)
  python3 fila.py nota DONO/REPO NUMERO VALOR URGENCIA RISCO TAMANHO [--simular]
      grava as quatro notas e a prioridade na issue, trocando as antigas
  python3 fila.py fila DONO/REPO [--todas]
      mostra as issues abertas em ordem de WSJF; --todas inclui agendado, delegado e aguardando

Precisa só do gh autenticado (https://cli.github.com).
"""
import json
import subprocess
import sys

FIB = (1, 2, 3, 5, 8, 13)
FAMILIAS = {"bv": "valor", "tc": "urgência", "rr": "risco", "sp": "tamanho"}
CORES = {"bv": "0e8a16", "tc": "d93f0b", "rr": "5319e7", "sp": "1d76db"}
PRIORIDADES = {
    "P0": ("b60205", "WSJF 8 ou mais"),
    "P1": ("d93f0b", "WSJF de 5 a 7,99"),
    "P2": ("fbca04", "WSJF de 3 a 4,99"),
    "P3": ("c5def5", "WSJF abaixo de 3"),
}
ESTADOS = ("estado: agendado", "estado: delegado", "estado: aguardando", "estado: algum dia")


def wsjf(bv, tc, rr, sp):
    for nota in (bv, tc, rr, sp):
        if nota not in FIB:
            raise ValueError(f"nota {nota} fora da régua; use {FIB}")
    return round((bv + tc + rr) / sp, 2)


def prioridade(valor_wsjf):
    if valor_wsjf >= 8:
        return "P0"
    if valor_wsjf >= 5:
        return "P1"
    if valor_wsjf >= 3:
        return "P2"
    return "P3"


def e_rotulo_de_nota(nome):
    familia, _, numero = nome.partition("-")
    return familia in FAMILIAS and numero.isdigit() and int(numero) in FIB


def notas_de(rotulos):
    notas = {}
    for nome in rotulos:
        if e_rotulo_de_nota(nome):
            familia, _, numero = nome.partition("-")
            notas[familia] = int(numero)
    return notas


def gh(*args, simular=False, escreve=False):
    if simular and escreve:
        print("simular: gh " + " ".join(args))
        return ""
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip() or f"gh falhou: {' '.join(args)}")
    return r.stdout


def cmd_rotulos(repo, simular):
    existentes = {r["name"] for r in json.loads(
        gh("label", "list", "--repo", repo, "--limit", "500", "--json", "name"))}
    novos = []
    for familia, nome in FAMILIAS.items():
        for n in FIB:
            novos.append((f"{familia}-{n}", CORES[familia], f"{nome} {n}"))
    for p, (cor, desc) in PRIORIDADES.items():
        novos.append((p, cor, desc))
    for estado in ESTADOS:
        novos.append((estado, "ededed", "fora da fila até a data do bloco ou do follow-up"))
    criados = 0
    for nome, cor, desc in novos:
        if nome in existentes:
            continue
        gh("label", "create", nome, "--repo", repo, "--color", cor, "--description", desc,
           simular=simular, escreve=True)
        criados += 1
    verbo = "seriam criadas" if simular else "criadas"
    print(f"{criados} etiquetas {verbo}, {len(novos) - criados} já existiam")


def cmd_nota(repo, numero, bv, tc, rr, sp, simular):
    valor_wsjf = wsjf(bv, tc, rr, sp)
    p = prioridade(valor_wsjf)
    dados = json.loads(gh("issue", "view", str(numero), "--repo", repo, "--json", "labels,state"))
    if dados["state"] != "OPEN":
        sys.exit(f"issue {numero} está fechada; nada gravado")
    atuais = [r["name"] for r in dados["labels"]]
    novos = [f"bv-{bv}", f"tc-{tc}", f"rr-{rr}", f"sp-{sp}", p]
    tirar = [r for r in atuais if (e_rotulo_de_nota(r) or r in PRIORIDADES) and r not in novos]
    args = ["issue", "edit", str(numero), "--repo", repo]
    for r in novos:
        args += ["--add-label", r]
    for r in tirar:
        args += ["--remove-label", r]
    gh(*args, simular=simular, escreve=True)
    print(f"issue {numero}: WSJF {valor_wsjf} ({p})")


def cmd_fila(repo, todas):
    issues = json.loads(gh("issue", "list", "--repo", repo, "--state", "open",
                           "--limit", "500", "--json", "number,title,labels"))
    linhas, sem_nota = [], []
    for issue in issues:
        nomes = [r["name"] for r in issue["labels"]]
        estado = next((e for e in ESTADOS if e in nomes), None)
        if estado and not todas:
            continue
        notas = notas_de(nomes)
        if len(notas) < 4:
            sem_nota.append(issue["number"])
            continue
        valor_wsjf = wsjf(notas["bv"], notas["tc"], notas["rr"], notas["sp"])
        linhas.append((valor_wsjf, issue["number"], issue["title"], estado))
    linhas.sort(key=lambda linha: (-linha[0], linha[1]))
    if not linhas:
        print("nenhuma issue com as quatro notas")
    for pos, (valor_wsjf, numero, titulo, estado) in enumerate(linhas, 1):
        marca = f"  [{estado}]" if estado else ""
        print(f"{pos:>3}. {prioridade(valor_wsjf)}  WSJF {valor_wsjf:>5}  issue {numero}: {titulo}{marca}")
    if sem_nota:
        print(f"\nsem as quatro notas ({len(sem_nota)}): " + ", ".join(str(n) for n in sem_nota))


def main(argv):
    simular = "--simular" in argv
    todas = "--todas" in argv
    args = [a for a in argv if not a.startswith("--")]
    if len(args) >= 2 and args[0] == "rotulos":
        cmd_rotulos(args[1], simular)
    elif len(args) == 7 and args[0] == "nota":
        repo, numero, *notas = args[1:]
        cmd_nota(repo, int(numero), *[int(n) for n in notas], simular=simular)
    elif len(args) >= 2 and args[0] == "fila":
        cmd_fila(args[1], todas)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
