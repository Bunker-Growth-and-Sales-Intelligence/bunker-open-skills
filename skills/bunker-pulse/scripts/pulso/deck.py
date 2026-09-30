"""O deck da Bunker: palco 1920x1080, um gráfico por slide, capa e fecho em preto.

O formato segue o deck institucional da Bunker: `@page { size:1920px
1080px; margin:0 }`, Schibsted Grotesk embutida, asterisco e régua no cabeçalho, logo no
canto de todo slide de conteúdo. O miolo é de quem chama: cada slide recebe a pergunta, a
manchete e o desenho já prontos, e a cor viva vem de `pulso.paleta` (a do cliente).

Montagem típica:

    from pulso import deck, saida
    slides = [deck.capa('RELATÓRIO · CLIENTE · 29/09/2026', 'Onde a margem está hoje',
                        'O que o desconto levou e onde ele se concentra.',
                        'Números lidos da base de pedidos, sem digitação à mão')]
    slides.append(deck.slide('Margem', 'A margem planejada chegou ao pedido?',
                             'Sim: 94% da margem planejada chegou, e 6% virou desconto.',
                             svg, 'Fonte: pedidos de jan a set de 2026', 2))
    slides.append(deck.fecho('base de pedidos · 29/09/2026'))
    open('deck.html', 'w').write(deck.render('Relatório de margem', slides))
    saida.para_pdf('deck.html', 'deck.pdf')
"""
import re

from . import paleta
from .marca import asterisco, embutir, fontes, logo_preto, logo_branco, CASA, SITE
from .paleta import esc

LARG, ALT = 1920, 1080
CLASSIFICACAO = 'Confidencial · uso do cliente'
# A assinatura discreta: uma linha no rodapé de cada slide e o site no fecho. O material é
# de quem gerou, e a Bunker aparece como a ferramenta, não como a autora.
ASSINATURA = 'Feito com a skill pública da Bunker · bunkerconsultancy.com'
FECHO_SUB = 'Cada gráfico deste relatório responde uma pergunta sobre o andamento do trabalho.'


# ------------------------------------------------------------------ ler um bloco pronto

def partes(secao_html):
    """Quebra um `<section>` de `pulso.pagina.secao` nas partes que o slide reaproveita.

    O painel e o deck escrevem cabeçalhos diferentes em volta do MESMO desenho, então o
    que atravessa é o desenho inteiro, byte a byte, e não uma reconstrução dele. Assim o
    slide mostrado ao cliente é exatamente o gráfico que passou pelas conferências.

    O corte é posicional, e não por remoção de pedaços: o cabeçalho é o que está dentro do
    primeiro `div.pergunta-resposta`, o desenho é tudo entre o fim dele e a linha da fonte.
    Recortar por expressão regular deixava tag desbalanceada nos blocos que desenham com
    `div` em vez de `svg`, e um slide mal fechado engolia os dez seguintes.

    Devolve (pergunta, manchete, desenho, fonte, como_ler).
    """
    perg = re.search(r'<p class="perg">(.*?)</p>', secao_html, re.S)
    manch = re.search(r'<h2>(.*?)</h2>', secao_html, re.S)
    fonte = re.search(r'<p class="fonte">(.*?)</p>', secao_html, re.S)
    comoler = re.search(r'<p class="comoler">Como ler: (.*?)</p>', secao_html, re.S)
    cabeca = secao_html.index('<div class="pergunta-resposta">')
    corpo_ini = secao_html.index('</div>', cabeca) + len('</div>')
    corpo_fim = secao_html.index('<p class="fonte">') if fonte else secao_html.index('</section>')
    return (perg.group(1) if perg else '',
            manch.group(1) if manch else '',
            secao_html[corpo_ini:corpo_fim].strip(),
            fonte.group(1) if fonte else '',
            comoler.group(1).strip() if comoler else '')


# ------------------------------------------------------------------ capa, divisor e fecho

def capa(rotulo, titulo, sub, pe, direita=CLASSIFICACAO, foto='capa.jpg'):
    """A capa institucional: foto em preto e branco, marca na esquerda, casa na direita.

    O que ela tem de dizer em três segundos, de longe: que documento é este, de que
    cliente, de quando, e de onde vieram os números. `rotulo`, `titulo`, `sub` e `pe`
    entram como HTML (escape antes o que vier de fora).

    O recorte e o preto e branco da foto vêm prontos no arquivo. Fazer isso no CSS obriga
    o Chrome a rasterizar a foto inteira em alta, e o PDF engorda 2 MB.
    """
    fundo = (f'\n  <img class="fundo" src="{embutir(foto, "image/jpeg")}" alt="">'
             if foto else '')
    return f'''<deck-stage class="capa">{fundo}
  <div class="veu"></div>
  <div class="marca">
    <img class="logo" src="{logo_branco()}" alt="Bunker">
    <p class="casa">{CASA}</p>
  </div>
  <div class="corpo">
    <p class="rot"><span class="ast">{asterisco('#ffffff', 17)}</span>{rotulo}</p>
    <h1>{titulo}</h1>
    <p class="sub">{sub}</p>
  </div>
  <div class="pe">
    <span>{pe}</span>
    <span class="dir">{esc(direita)}</span>
  </div>
</deck-stage>'''


def divisor(titulo, sub, n):
    return f'''<deck-stage class="divisor">
  <p class="rot">{esc(str(n).zfill(2))}</p>
  <h1>{esc(titulo)}</h1>
  <p class="sub">{esc(sub)}</p>
</deck-stage>'''


def fecho(pe, titulo='Obrigado.', sub=FECHO_SUB, link='', direita=SITE,
          rotulo=CLASSIFICACAO.upper()):
    """O encerramento é um obrigado, e nada mais.

    O fecho existe para encerrar, não para argumentar de novo diante de quem já viu tudo.
    """
    return f'''<deck-stage class="capa fecho">
  <div class="marca">
    <img class="logo" src="{logo_branco()}" alt="Bunker">
    <p class="casa">{CASA}</p>
  </div>
  <div class="corpo">
    <p class="rot"><span class="ast">{asterisco('#ffffff', 17)}</span>{esc(rotulo)}</p>
    <h1>{titulo}</h1>
    <p class="sub">{sub}</p>
    {f'<p class="link">{esc(link)}</p>' if link else ''}
  </div>
  <div class="pe">
    <span>{pe}</span>
    <span class="dir">{esc(direita)}</span>
  </div>
</deck-stage>'''


# ------------------------------------------------------------------ as partes do slide

def tirar_leitura(desenho):
    """Tira a nota de leitura de dentro do desenho e devolve as duas partes.

    Dentro do SVG ela é escrita em 10px sobre um desenho de 468: no slide isso encolhe para
    um fio de texto embaixo do gráfico. Embaixo do título, no tamanho do texto de apoio,
    ela é lida antes do desenho, que é a ordem certa.
    """
    notas = re.findall(r'<text class="leitura"[^>]*>(.*?)</text>', desenho, re.S)
    limpo = re.sub(r'<text class="leitura"[^>]*>.*?</text>\s*', '', desenho, flags=re.S)
    texto = ' · '.join(re.sub(r'<[^>]+>', '', x).strip() for x in notas if x.strip())
    texto = texto.replace('como ler: ', '').replace('&#183;', '·')
    return limpo, (f'Como ler este gráfico: {texto}.' if texto else '')


def nota_de(texto, glossario):
    """A sigla que o cliente não tem obrigação de conhecer ganha uma linha de explicação.
    Devolve (sigla, explicação), ou ('', '')."""
    for chave, nota in (glossario or {}).items():
        if chave in texto:
            return chave, nota
    return '', ''


def afirmar(pergunta, manchete):
    """O título é a manchete, como ela foi escrita na origem.

    Houve uma máquina de costurar "sim", "não" ou "quase" dentro da pergunta, e saía coisa
    que não é resposta nem é português. Regra não escreve texto: quem escreve a manchete é
    quem monta o bloco. Aqui só sobra a garantia de que o título não fica vazio.
    """
    return (manchete or '').strip() or pergunta.rstrip('?').strip()


def frases(texto):
    """Pedaços de nota separados por "·" ou ";" viram frases com maiúscula e ponto."""
    partes_ = [x.strip(' .') for x in re.split(r'\s*[·;]\s*', texto) if x.strip(' .')]
    return ' '.join(x[0].upper() + x[1:] + '.' for x in partes_)


def alfinete():
    """A tachinha que prende a nota, na cor primária do cliente.

    Cabeça redonda na cor do cliente, com um contorno claro fino: sem ele, um verde escuro
    some sobre o cinza da nota. A agulha é cinza, e a sombra é curta.
    """
    return (f'<svg class="pin" viewBox="0 0 32 32" width="34" height="34" aria-hidden="true">'
            f'<line x1="16" y1="17" x2="21" y2="28" stroke="#9a9a9a" stroke-width="1.6" '
            f'stroke-linecap="round"/>'
            f'<ellipse cx="17" cy="19" rx="7" ry="2.2" fill="#000000" opacity=".35"/>'
            f'<circle cx="15" cy="12" r="8" fill="{paleta.PRIMARIA}" stroke="#ffffff" '
            f'stroke-opacity=".75" stroke-width="1.3"/>'
            f'<circle cx="12.3" cy="9.3" r="2.3" fill="#ffffff" opacity=".35"/></svg>')


def nota_adesiva(texto, rotulo='Como ler este gráfico', onde='texto'):
    """A nota adesiva: cinza bem escuro, texto branco, canto dobrado, tachinha do cliente.

    Serve a várias finalidades (ensinar a ler a forma, explicar uma sigla, dar contexto),
    e o rótulo diz qual é. Posta por posição absoluta: o título fica onde estava.
    """
    return (f'<div class="adesivo{" no-palco" if onde == "palco" else ""}"><div class="nota">{alfinete()}<p class="nrot">{esc(rotulo)}</p>'
            f'<p>{esc(texto)}</p></div></div>')


def cabecalho(n, rotulo, cor='#0a0a0a', suave='#555555'):
    """O cabeçalho da casa: asterisco, número, régua, o rótulo em caixa alta e o logo."""
    return (f'<div class="cab"><span class="ast">{asterisco(cor)}</span>'
            f'<span class="num">{str(n).zfill(2)}</span>'
            f'<span class="regua" style="background:{cor}"></span>'
            f'<span class="rot" style="color:{suave}">{esc(rotulo)}</span>'
            f'<img class="logo-cab" src="{logo_preto()}" alt="Bunker"></div>')


def rodape(esquerda, pag, convite=False, classificacao=CLASSIFICACAO):
    """A fonte do dado à esquerda; a assinatura, a classificação e a página à direita.

    `convite` fica na assinatura por compatibilidade e não muda nada: a assinatura é a
    mesma linha discreta em todo slide de conteúdo.
    """
    return (f'<div class="rodape"><span>{esquerda}</span>'
            f'<span>{esc(ASSINATURA)} · {esc(classificacao)} · {pag}</span></div>')


# A nota ensina a ler a FORMA, e aparece só na primeira vez que a forma entra no material.
JA_EXPLICADO = set()
# Formas que se leem sem nota: o mapa de calor. A chave é um trecho do texto de
# leitura da forma.
SEM_NOTA = ('quanto mais escuro',)


def slide(bloco, perg, manchete, desenho, fonte, pag, ler='', traduzir=None, glossario=None,
          contexto=None):
    """Um gráfico por slide: bloco e pergunta no cabeçalho, resposta como título.

    A pergunta é de NEGÓCIO e vai no cabeçalho; a manchete é a RESPOSTA, conclusiva
    sozinha, e vai como título à esquerda; o desenho ocupa a metade direita. `traduzir`
    troca o vocabulário de ferramenta pelo do cliente em todo texto do slide; `glossario`
    ({sigla: explicação}) põe uma nota adesiva na primeira vez que a sigla aparece.
    """
    tr = traduzir or (lambda x: x)
    perg, manchete = tr(perg), tr(manchete or '')
    desenho, fonte = tr(desenho), tr(fonte)
    desenho, como_ler = tirar_leitura(desenho)
    ler = tr(ler or como_ler.replace('Como ler este gráfico: ', ''))
    chave_sigla, sigla = nota_de(perg + manchete, glossario)
    if ler and any(s in ler for s in SEM_NOTA):
        ler = ''
    chave = ler or sigla
    nota_texto = nota_palco = ''
    if chave and chave not in JA_EXPLICADO:
        JA_EXPLICADO.add(chave)
        # a nota de leitura fica sob a manchete, que é onde se aprende a ler antes de olhar;
        # a de glossário vai para baixo do desenho, perto do número que ela explica
        if ler:
            nota_texto = nota_adesiva(frases(ler))
        else:
            nota_palco = nota_adesiva(sigla, f'O que é {chave_sigla}', 'palco')
    # o contexto é o porquê que o número não conta sozinho ("isso espera aquilo, decidido
    # em tal reunião"). Ele vai sob a manchete, e a nota de leitura, se havia, desce para o palco
    if contexto:
        if nota_texto and not nota_palco:
            nota_palco = nota_texto.replace('class="adesivo"', 'class="adesivo no-palco"', 1)
        nota_texto = nota_adesiva(contexto, 'Contexto')
    nota = nota_texto or nota_palco
    rotulo = f'{bloco} · {perg}' if bloco else perg
    return f'''<deck-stage>
  {cabecalho(pag, rotulo)}
  <div class="dois">
    <div class="texto"><h2>{esc(afirmar(perg, manchete) if manchete else perg)}</h2>
    {nota_texto}</div>
    <div class="palco"><div class="desenho">{desenho}</div>{nota_palco}</div>
  </div>
  {rodape(fonte, pag, convite=bool(nota))}
</deck-stage>'''


def slides_tabela(tabela, pag, por_slide=5, teto=15, titulo='O que continua em aberto',
                  rotulo='O que segue aberto', apoio='',
                  sobra='Outros {n} itens seguem abaixo destes.', fonte='Fonte: dados do cliente'):
    """Uma tabela longa quebrada em slides de `por_slide` linhas, até `teto` linhas.

    Vinte e duas linhas cabem numa PÁGINA de relatório, e não num SLIDE: no palco de
    1080px a tabela era cortada na quinta linha, sem aviso. A ordem da tabela é mantida,
    então o primeiro slide carrega o que vem antes.
    """
    cabeca = re.search(r'<thead>.*?</thead>', tabela, re.S)
    linhas = re.findall(r'<tr(?![^>]*class="cab").*?</tr>', tabela[tabela.index('<tbody>'):], re.S) \
        if '<tbody>' in tabela else re.findall(r'<tr.*?</tr>', tabela, re.S)[1:]
    if not cabeca:
        cabeca = re.search(r'<tr.*?</tr>', tabela, re.S)
    sobraram = max(0, len(linhas) - teto)
    linhas = linhas[:teto]
    saida = []
    total = -(-len(linhas) // por_slide)
    for k in range(0, len(linhas), por_slide):
        parte = k // por_slide + 1
        pag += 1
        corpo = (f'<table class="abertas">{cabeca.group(0) if cabeca else ""}'
                 f'{"".join(linhas[k:k + por_slide])}</table>')
        de, ate = k + 1, min(k + por_slide, len(linhas))
        tit = (titulo + (f' ({parte}/{total})' if total > 1 else ''))
        resto = (' ' + sobra.format(n=sobraram)) if sobraram else ''
        saida.append(f'''<deck-stage class="tabelao">
  {cabecalho(pag, f'{rotulo} · itens {de} a {ate} de {len(linhas)}')}
  <div class="titulo-largo"><h2>{esc(tit)}</h2>
  <p class="apoio">{apoio}{resto}</p></div>
  <div class="tabelona">{corpo}</div>
  {rodape(fonte, pag)}
</deck-stage>''')
    return saida, pag


CSS = '''
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{background:#4a4a4a}
body{font-family:"Schibsted Grotesk",-apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif;
 -webkit-font-smoothing:antialiased}
deck-stage{display:block;position:relative;width:1920px;height:1080px;background:#ffffff;
 color:#0a0a0a;overflow:hidden;padding:96px 120px 76px;margin:0 auto 24px;
 page-break-after:always;break-after:page}
deck-stage:last-child{page-break-after:auto;break-after:auto}
.cab{display:flex;align-items:center;gap:18px;height:40px}
.cab .ast{display:flex;align-items:center}
.cab .num{font-size:19px;font-weight:700;font-variant-numeric:tabular-nums}
.cab .regua{width:46px;height:2px;display:inline-block}
.cab .rot{font-size:19px;font-weight:600;letter-spacing:.17em;text-transform:uppercase}
.dois{position:absolute;left:120px;right:120px;top:214px;bottom:128px;display:grid;
 grid-template-columns:640px 1fr;gap:96px;align-items:center}
.texto .apoio{font-size:21px;line-height:1.45;color:#969696;margin-top:22px}
.texto{position:relative}
.cab .logo-cab{height:30px;width:auto;margin-left:auto}
.adesivo{position:absolute;left:0;top:calc(100% + 36px);width:620px;
 transform:rotate(-1.4deg);transform-origin:top left;
 filter:drop-shadow(0 12px 18px rgba(0,0,0,.22))}
.nota{position:relative;background:#262626;color:#ffffff;padding:22px 30px 28px;
 font-size:19px;line-height:1.42;
 clip-path:polygon(0 0,100% 0,100% calc(100% - 40px),calc(100% - 40px) 100%,0 100%)}
.nota::after{content:"";position:absolute;right:0;bottom:0;width:40px;height:40px;
 background:linear-gradient(135deg,#6e6e6e 0,#4a4a4a 50%,transparent 50%)}
.palco{position:relative}
.adesivo.no-palco{top:auto;left:auto;right:0;bottom:34px;transform:rotate(1.2deg);
 transform-origin:bottom right}
.nota .pin{position:absolute;right:20px;top:14px}
.nota .nrot{font-size:15px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;
 color:#bdbdbd;margin-bottom:10px}
.texto h2{font-size:43px;line-height:1.14;font-weight:900;letter-spacing:-.02em;
 overflow-wrap:break-word}
.palco{display:flex;align-items:center;justify-content:center;height:100%;min-width:0}
.desenho{width:100%;height:100%;display:flex;flex-direction:column;
 align-items:center;justify-content:center}
.desenho>svg{width:100%;height:auto;max-height:100%}
.desenho .fl{display:flex;align-items:center;width:100%;max-width:860px;
 font-size:29px;margin:17px 0;gap:28px}
.desenho .fl .flb{flex:1;background:#ededed;overflow:hidden;display:flex;align-items:center;
 justify-content:center;height:30px;border-radius:3px}
.desenho .fl .flb i{display:block;height:100%;border-radius:3px}
.desenho .fl .fln{width:196px;color:#969696}
.desenho .fl .flv{width:72px;text-align:right;font-weight:600;font-variant-numeric:tabular-nums}
.desenho .fl .flp{width:94px;text-align:right;color:#969696;font-size:26px;
 font-variant-numeric:tabular-nums}
.rodape{position:absolute;left:120px;right:120px;bottom:54px;display:flex;
 justify-content:space-between;gap:40px;font-size:18px;color:#969696;
 border-top:1px solid #dddddd;padding-top:18px}
.rodape .convite{color:#0a0a0a;white-space:nowrap}
.rodape>span:last-child{white-space:nowrap}
.capa{background:#0a0a0a;color:#ffffff;padding:96px 120px}
.capa .fundo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
 object-position:center}
.capa .veu{position:absolute;inset:0;background:linear-gradient(90deg,
 rgba(8,8,8,.95) 0%,rgba(8,8,8,.90) 34%,rgba(8,8,8,.62) 58%,rgba(8,8,8,.30) 78%,
 rgba(8,8,8,.12) 100%)}
.fecho .veu{background:#0a0a0a}
.capa .marca{position:absolute;left:120px;right:120px;top:88px;display:flex;
 align-items:center;justify-content:space-between}
.capa .marca .logo{height:52px;width:auto;filter:none}
.capa .marca .casa{font-size:23px;letter-spacing:.14em;text-transform:uppercase;color:#ffffff}
.capa .corpo{position:absolute;left:120px;right:120px;top:376px}
.capa .rot{color:#bdbdbd}
.capa h1{font-size:122px;line-height:1.02;font-weight:900;letter-spacing:-.035em;margin-top:30px;
 max-width:20ch}
.capa .sub{font-size:31px;line-height:1.5;color:#cecece;margin-top:38px;max-width:50ch}
.capa .pe{position:absolute;left:120px;right:120px;bottom:84px;display:flex;
 justify-content:space-between;align-items:flex-end;gap:60px;font-size:20px;color:#bdbdbd;
 line-height:1.5}
.capa .pe .dir{text-transform:uppercase;letter-spacing:.14em;white-space:nowrap;color:#ffffff}
.capa .rot{display:flex;align-items:center;gap:14px;color:#dddddd}
.fecho{background:#0a0a0a}
.fecho h1{margin-top:0}
.fecho .corpo{top:330px}
.fecho .sub{max-width:44ch}
.fecho .link{font-size:26px;margin-top:34px;letter-spacing:.02em;color:#ffffff;
 border-top:1px solid rgba(255,255,255,.28);padding-top:22px;display:inline-block}
.divisor{background:#0a0a0a;color:#ffffff;padding:120px;display:flex;flex-direction:column;
 justify-content:center}
.divisor .rot{font-size:26px;color:#969696}
.divisor h1{font-size:104px;font-weight:900;letter-spacing:-.03em;margin-top:26px;max-width:22ch}
.divisor .sub{font-size:31px;color:#cecece;margin-top:30px;max-width:56ch}
.titulo-largo{margin-top:34px}
.titulo-largo h2{font-size:54px;line-height:1.06;font-weight:900;letter-spacing:-.025em}
.titulo-largo .apoio{font-size:24px;color:#969696;margin-top:12px}
.tabelona{position:absolute;left:120px;right:120px;top:336px;bottom:128px;overflow:hidden}
table.abertas{width:100%;border-collapse:collapse;font-size:25px;line-height:1.4}
table.abertas th{text-align:left;font-weight:600;font-size:19px;color:#969696;
 text-transform:uppercase;letter-spacing:.06em;padding:0 20px 16px 0;border-bottom:2px solid #0a0a0a}
table.abertas td{padding:16px 20px 16px 0;border-bottom:1px solid #ededed;vertical-align:top}
table.abertas td.num{white-space:nowrap;text-align:right;font-variant-numeric:tabular-nums}
table.abertas td.nd{color:#969696}
table.abertas a{color:inherit;text-decoration:none;font-weight:600}
table.abertas .tags{margin-top:8px;display:flex;flex-wrap:wrap;gap:7px}
table.abertas .porque{font-size:19px;color:#555555;margin-top:8px;line-height:1.35}
table.abertas code{font-family:ui-monospace,Menlo,monospace;font-size:19px;
 background:rgba(128,128,128,.13);padding:4px 9px;border-radius:4px;color:#969696}
@page{size:1920px 1080px;margin:0}
@media screen{
 body{padding:18px 12px 40px}
 deck-stage{transform:scale(var(--z,1));transform-origin:top left;
  margin:0 0 calc(1080px * (var(--z,1) - 1) + 22px)}
}
.imprimir{position:fixed;right:16px;top:12px;z-index:9;font:600 14px/1 "Schibsted Grotesk",sans-serif;
 background:#0a0a0a;color:#fff;border:0;border-radius:6px;padding:11px 16px;cursor:pointer}
@media print{.imprimir{display:none}html,body{background:#ffffff}
 deck-stage{margin:0;transform:none}}
'''


def render(titulo, slides):
    """O HTML do deck: fonte embutida, CSS do palco e o ajuste de escala para a tela."""
    return f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>{titulo}</title>
<style>{fontes()}{CSS}</style></head><body>
<button class="imprimir" onclick="window.print()">Salvar em PDF</button>
{chr(10).join(slides)}
<script>
(function () {{
  var z = function () {{
    var s = Math.min(1, (document.documentElement.clientWidth - 24) / 1920);
    document.documentElement.style.setProperty('--z', s);
  }};
  z();
  addEventListener('resize', z);
}})();
</script>
</body></html>'''
