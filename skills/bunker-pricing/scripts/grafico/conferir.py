"""As conferências que rodam sobre a página pronta, antes de mostrar a alguém.

Cada uma nasceu de um defeito que só o olho do operador pegou, e existe para aquele defeito
não voltar. As oito primeiras leem o HTML; as três últimas abrem a página no Chrome
headless, fotografam e medem.

  1. geometria       elemento desenhado fora da moldura do SVG
  2. bloco vazio     seção sem desenho nenhum
  3. legibilidade    texto que, DEPOIS da escala, renderiza abaixo do mínimo legível
  4. manchete        manchete que descreve a forma em vez de concluir
  5. denominador     total repetido dentro do desenho quando já está na manchete
  6. pergunta        pergunta sobre o DESENHO, ou enunciado mecânico de contagem
  7. sobreposicao    dois textos ocupando o mesmo pedaço da tela
  8. texto cortado   texto cuja LARGURA passa da borda do desenho
  9. fotos           a página fotografada inteira em 1440 e em 390 px, para ler com os olhos
 10. rolagem lateral a página passa da largura da tela e rola para o lado
 11. texto x gráfico num bloco, o texto ocupa mais área que o desenho

  python3 -m grafico.conferir painel.html
  python3 -m grafico.conferir painel.html --largura 980
  python3 -m grafico.conferir painel.html --fotos pasta-das-fotos

Roda de dentro de `scripts/`. Só a biblioteca padrão; as fotos pedem o Chrome da máquina.

Sai com 1 se qualquer conferência achar algo.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

MIN_PX = 9.0          # abaixo disto o texto deixa de se ler na tela
DESCRITIVA = re.compile(r'^(Uma |O |A )(barra|célula|pilha|zero|faixa|coluna|linha|forma)\b', re.I)
# vocabulário de DESENHO. A pergunta é do negócio, e quem lê não pergunta pela inclinação
# de uma curva: pergunta se fechamos o que entrou.
DE_DESENHO = re.compile(r'\b(curva|inclina[çc][ãa]o|quadrante|eixo|[áa]rea proporcional|'
                        r'cruzamento|dispers[ãa]o|empilhad|treemap|cascata|'
                        r'sobre a pr[óo]pria base|em cada par de)\b', re.I)
# Enunciado mecânico: conta caixinhas em vez de perguntar o que o negócio quer saber.
# "Quantos pedidos há em cada faixa de desconto" descreve a operação do gráfico;
# "Qual faixa de desconto leva a maior parte da margem" é a pergunta de quem decide.
# "Qual etapa acumula a maior parte do trabalho" veio de um comentário em 24/09/2026: quem
# decide não quer saber qual barra é a maior, quer saber se o que está aberto vira entrega.
MECANICA = re.compile(r'^(Quantas?|Quantos?) .{0,60}\b(em cada|há por|há em|por cada)\b|'
                      r'^Qual é a contagem\b|^Qual é a m[ée]dia\b|'
                      r'^Qual \w+ (acumula|concentra|tem) .{0,40}'
                      r'(maior parte|maior volume|mais issues|maior número)\b|'
                      r'^(Como está|Qual é) a distribuição\b', re.I)


def svgs(html):
    for m in re.finditer(r'<svg viewBox="0 0 ([\d.]+) ([\d.]+)"(.*?)</svg>', html, re.S):
        yield float(m.group(1)), float(m.group(2)), m.group(3), m.group(0)


def geometria(html):
    fora = []
    for W, H, corpo, _ in svgs(html):
        for e in re.finditer(r'<(text|rect|circle|line)\b([^>]*)>', corpo):
            at = dict(re.findall(r'(\w+)="([-\d.]+)"', e.group(2)))
            xs = [float(at[k]) for k in ('x', 'x1', 'x2', 'cx') if k in at]
            ys = [float(at[k]) for k in ('y', 'y1', 'y2', 'cy') if k in at]
            if 'width' in at and 'x' in at:
                xs.append(float(at['x']) + float(at['width']))
            if 'height' in at and 'y' in at:
                ys.append(float(at['y']) + float(at['height']))
            if any(v < -1 or v > W + 1 for v in xs) or any(v < -1 or v > H + 1 for v in ys):
                fora.append(e.group(0)[:90])
    return fora


def blocos_vazios(html):
    vazios = []
    for b in re.findall(r'<section\b.*?</section>', html, re.S):
        if '<svg' not in b and '<table' not in b:
            t = re.search(r'<p class="perg">(.*?)</p>', b, re.S)
            vazios.append(re.sub('<[^>]+>', '', t.group(1))[:60] if t else '?')
    return vazios


def legibilidade(html, coluna_cheia=980.0):
    """O tamanho do texto NA TELA é o declarado vezes a escala do SVG.

    Um desenho nascido em 468 e mostrado numa coluna de 313 encolhe o texto em um terço, e
    foi assim que a legenda do treemap virou um borrão. A conferência mede a largura real
    de cada coluna pelo CSS da página e reprova o que cair abaixo do mínimo.
    """
    tres = 'class="tres"' in html
    larg_terco = (coluna_cheia - 40) / 3 if tres else coluna_cheia
    ruins = []
    for W, H, corpo, inteiro in svgs(html):
        # a largura de destino depende de onde o SVG está: dentro da grade de três, ou não
        pos = html.index(inteiro)
        trecho = html[max(0, pos - 400):pos]
        alvo = larg_terco if 'class="tres"' in trecho else (
            coluna_cheia if W > 700 else (coluna_cheia - 40) / 2)
        escala = alvo / W
        for e in re.finditer(r'<text[^>]*font-size="([\d.]+)"[^>]*>([^<]{0,40})', corpo):
            px = float(e.group(1)) * escala
            if px < MIN_PX:
                ruins.append((round(px, 1), round(escala, 2), e.group(2)[:30]))
    return ruins


def perguntas_de_desenho(html):
    """A pergunta é do NEGÓCIO, e nunca do desenho.

    Ao endurecer os enunciados para o lado técnico eu produzi o oposto do pedido: "a curva
    acumulada de aberturas e a de fechamentos têm a mesma inclinação" é uma pergunta sobre
    o gráfico, e não sobre a operação. Quem lê quer saber se fechamos o que entrou.
    """
    qs = re.findall(r'<p class="perg">([^<]+)</p>', html)
    return [q for q in qs if DE_DESENHO.search(q) or MECANICA.search(q)]


def sobreposicao(html):
    """Dois textos ocupando o mesmo pedaço da tela.

    É o defeito que mais voltou, e nenhuma das outras conferências o pegava: o desenho fica
    dentro da moldura, o texto fica no tamanho certo, e mesmo assim um rótulo cai em cima do
    outro. A geometria só olhava o que saía da tela.

    A largura de um texto é estimada em 0,55 do tamanho da fonte por caractere, que é a
    média de uma grotesca. A estimativa erra para mais em textos com muitos "i" e "l", e
    errar para mais é o lado certo: ela avisa antes de encostar.
    """
    maus = []
    for W, H, corpo, _ in svgs(html):
        caixas = []
        for e in re.finditer(r'<text([^>]*)>([^<]*)</text>', corpo):
            at = dict(re.findall(r'([\w-]+)="([^"]*)"', e.group(1)))
            try:
                x, y = float(at.get('x', 0)), float(at.get('y', 0))
            except ValueError:
                continue
            fs = float(at.get('font-size', 11))
            txt = re.sub(r'&#?\w+;', 'x', e.group(2))
            if not txt.strip():
                continue
            larg = len(txt) * fs * 0.55
            anc = at.get('text-anchor', 'start')
            x0 = x - larg if anc == 'end' else (x - larg / 2 if anc == 'middle' else x)
            caixas.append((x0, y - fs * 0.8, x0 + larg, y + fs * 0.2, txt[:22]))
        for i in range(len(caixas)):
            for j in range(i + 1, len(caixas)):
                a1, b1, c1, d1, t1 = caixas[i]
                a2, b2, c2, d2, t2 = caixas[j]
                dx = min(c1, c2) - max(a1, a2)
                dy = min(d1, d2) - max(b1, b2)
                if dx > 2 and dy > 2:
                    maus.append(f'"{t1}" x "{t2}"')
    return maus


def texto_cortado(html):
    """Texto cuja largura estimada passa da borda do SVG.

    A conferência de geometria olha a COORDENADA do elemento, e uma legenda que começa em
    414 numa tela de 468 passa nela: o ponto está dentro. O que sai é o texto, que precisa
    de 78 pixels e tem 54. Só o olho pegava, e virava "legenda sobreposta" no relato.
    """
    maus = []
    for W, H, corpo, _ in svgs(html):
        for e in re.finditer(r'<text([^>]*)>([^<]*)</text>', corpo):
            at = dict(re.findall(r'([\w-]+)="([^"]*)"', e.group(1)))
            try:
                x = float(at.get('x', 0))
            except ValueError:
                continue
            txt = re.sub(r'&#?\w+;', 'x', e.group(2))
            if not txt.strip():
                continue
            fs = float(at.get('font-size', 11))
            fator = 0.62 if at.get('font-weight', '400') in ('600', '700') else 0.55
            larg = len(txt) * fs * fator
            anc = at.get('text-anchor', 'start')
            x0 = x - larg if anc == 'end' else (x - larg / 2 if anc == 'middle' else x)
            if x0 < -1 or x0 + larg > W + 1:
                maus.append(f'"{txt[:26]}" vai ate {x0 + larg:.0f} numa tela de {W:.0f}')
    return maus


def manchetes_descritivas(html):
    return [h for h in re.findall(r'<h2>([^<]*)</h2>', html) if DESCRITIVA.match(h)]


def denominador_repetido(html):
    dentro = ''.join(i for _, _, _, i in svgs(html))
    return re.findall(r'[^<>]{0,24}no total', dentro)


# ============================================================ a página no navegador

LARGURAS = (1440, 390)

# Mede na página renderizada e manda o resultado para a moldura por postMessage. A página
# roda dentro de um iframe da largura pedida porque a janela do Chrome headless não desce de
# 500 px: com --window-size=390 o layout acontecia em 500 e a foto saía cortada, o que
# escondia exatamente a rolagem lateral do celular.
_MEDIR = r"""
<script>
addEventListener('load', function () { setTimeout(function () {
  var r = {larg: innerWidth, rola: document.documentElement.scrollWidth - innerWidth,
           altura: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
           blocos: []};
  var area = function (el) { var b = el.getBoundingClientRect(); return b.width * b.height; };
  document.querySelectorAll('section, deck-stage').forEach(function (s, k) {
    var graf = 0, txt = 0;
    s.querySelectorAll('svg, table, canvas, img, .fl').forEach(function (g) {
      if (!g.parentElement.closest('svg, table, .fl')) graf += area(g); });
    s.querySelectorAll('p, h1, h2, h3, li').forEach(function (t) {
      if (!t.closest('svg, table, .fl') && t.offsetParent !== null) txt += area(t); });
    var t = s.querySelector('h2, .perg, h1');
    r.blocos.push({k: k, graf: Math.round(graf), txt: Math.round(txt),
                   nome: t ? t.textContent.trim().slice(0, 60) : ''});
  });
  parent.postMessage(JSON.stringify(r), '*');
}, 300); });
</script>
"""

_MOLDURA = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:#ffffff}}iframe{{border:0;display:block}}</style></head>
<body><iframe src="{src}" style="width:{w}px;height:{h}px"></iframe>
<script>addEventListener('message', function (e) {{
  var p = document.createElement('pre'); p.id = 'medida'; p.textContent = e.data;
  document.body.appendChild(p); }});</script></body></html>"""


def _chrome():
    from .saida import achar_chrome
    exe = achar_chrome()
    if not exe:
        raise SystemExit('as fotos pedem o Chrome; nenhum foi achado nesta máquina (ou defina BUNKER_CHROME)')
    return exe


def _temp(pasta, texto, sufixo='.html'):
    with tempfile.NamedTemporaryFile('w', suffix=sufixo, delete=False, dir=pasta,
                                     encoding='utf-8') as f:
        f.write(texto)
        return f.name


def medir(html_path, largura):
    """Abre a página na largura dada e devolve a medida (rolagem, altura, blocos)."""
    pasta = os.path.dirname(os.path.abspath(html_path))
    fonte = open(html_path, encoding='utf-8').read()
    alvo = fonte.replace('</body>', _MEDIR + '</body>') if '</body>' in fonte else fonte + _MEDIR
    pag = _temp(pasta, alvo)
    moldura = _temp(pasta, _MOLDURA.format(src=os.path.basename(pag), w=largura, h=900))
    try:
        r = subprocess.run([_chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars',
                            f'--window-size={max(largura, 500)},900', '--virtual-time-budget=8000',
                            '--dump-dom', f'file://{moldura}'], capture_output=True, text=True)
    finally:
        os.remove(pag)
        os.remove(moldura)
    m = re.search(r'<pre id="medida">(.*?)</pre>', r.stdout, re.S)
    if not m:
        raise SystemExit(f'não consegui medir {html_path} em {largura}px: {r.stderr[-300:]}')
    return json.loads(m.group(1).replace('&quot;', '"').replace('&amp;', '&')
                      .replace('&lt;', '<').replace('&gt;', '>'))


def fotografar(html_path, pasta, larguras=LARGURAS, teto=16000):
    """A página inteira em PNG, uma foto por largura. Leia cada uma: a medida não vê tudo.

    Devolve {largura: (caminho da foto, medida)}.
    """
    os.makedirs(pasta, exist_ok=True)
    base = os.path.splitext(os.path.basename(html_path))[0]
    origem = os.path.dirname(os.path.abspath(html_path))
    saida = {}
    for w in larguras:
        med = medir(html_path, w)
        alto = min(max(med['altura'], 600), teto)
        foto = os.path.join(pasta, f'{base}-{w}.png')
        moldura = _temp(origem, _MOLDURA.format(src=os.path.basename(html_path), w=w, h=alto))
        try:
            subprocess.run([_chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars',
                            f'--window-size={max(w, 500)},{alto}', '--virtual-time-budget=8000',
                            f'--screenshot={os.path.abspath(foto)}', f'file://{moldura}'],
                           check=True, capture_output=True)
        finally:
            os.remove(moldura)
        if w < 500:
            # a janela tem 500 px e a página, a largura pedida; o resto da foto sai em branco.
            # Com o Pillow na máquina, a foto é recortada na largura exata.
            try:
                from PIL import Image
                Image.open(foto).crop((0, 0, w, alto)).save(foto)
            except ImportError:
                pass
        saida[w] = (foto, med)
    return saida


def rolagem_lateral(medidas):
    """A página não pode rolar para o lado, em largura nenhuma. No celular é o defeito que
    mais passa: o desktop está perfeito e a tabela de 390 empurra a tela inteira."""
    return [f'{w}px: {m["rola"]}px de rolagem lateral' for w, (_, m) in medidas.items() if m['rola'] > 0]


def texto_contra_grafico(medidas, folga=1.0):
    """Num bloco, o texto não pode ocupar mais área que o desenho.

    Entrega visual é gráfico e número grande. Bloco em que a pergunta, a manchete e a
    fonte somam mais área que o gráfico está explicando o que deveria mostrar. Bloco sem
    desenho nenhum fica de fora: quem pega esse é a conferência de bloco vazio.
    """
    maus = []
    for w, (_, m) in medidas.items():
        for b in m['blocos']:
            if b['graf'] and b['txt'] > b['graf'] * folga:
                maus.append(f'{w}px: "{b["nome"]}" tem texto {b["txt"]} px² contra {b["graf"]} de desenho')
    return maus


def conferir(html, larg=980.0):
    """As oito conferências de HTML: [(nome, achados, o que reprova)]."""
    return [
        ('geometria', geometria(html), 'elemento fora da moldura'),
        ('bloco vazio', blocos_vazios(html), 'seção sem desenho'),
        ('legibilidade', legibilidade(html, larg), f'texto abaixo de {MIN_PX}px na tela'),
        ('manchete', manchetes_descritivas(html), 'manchete que descreve a forma'),
        ('denominador', denominador_repetido(html), 'total repetido dentro do desenho'),
        ('pergunta', perguntas_de_desenho(html), 'pergunta sobre o desenho, e não sobre a operação'),
        ('sobreposicao', sobreposicao(html), 'pares de texto ocupando o mesmo espaço'),
        ('texto cortado', texto_cortado(html), 'textos que passam da borda do desenho'),
    ]


def main(argv=None):
    argv = sys.argv if argv is None else argv
    alvo = argv[1]
    larg = float(argv[argv.index('--largura') + 1]) if '--largura' in argv else 980.0
    html = open(alvo, encoding='utf-8').read()
    checks = conferir(html, larg)
    if '--fotos' in argv:
        pasta = argv[argv.index('--fotos') + 1]
        medidas = fotografar(alvo, pasta)
        for w, (foto, _) in medidas.items():
            print(f'  foto {w}px: {foto}')
        checks += [
            ('rolagem', rolagem_lateral(medidas), 'larguras com rolagem lateral'),
            ('texto x graf', texto_contra_grafico(medidas), 'blocos em que o texto ganha do gráfico'),
        ]
    ruim = 0
    for nome, achados, oque in checks:
        print(f'  {"REPROVA" if achados else "ok     "}  {nome:<13} {len(achados)} {oque}')
        for a in achados[:4]:
            print(f'              {a}')
        ruim += len(achados)
    print(f'\n{alvo}: {ruim} achado(s)')
    return 1 if ruim else 0


if __name__ == '__main__':
    raise SystemExit(main())
