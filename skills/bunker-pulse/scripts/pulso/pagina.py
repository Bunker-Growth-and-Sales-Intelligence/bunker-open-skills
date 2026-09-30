"""O esqueleto do HTML autocontido: cabeça, tema claro e escuro, grade e o bloco.

Uma página de painel é uma grade de duas colunas de blocos. Cada bloco (`secao`) tem a
PERGUNTA de negócio no alto, a MANCHETE com a conclusão, o desenho e UMA linha de fonte.
Nenhum parágrafo de texto: o que não cabe na manchete vai para a linha de fonte ou sai.

    from pulso import pagina, formas
    blocos = [pagina.secao('A margem planejada chegou ao pedido?',
                           'Sim: 94% chegou, e 6% virou desconto.',
                           formas.desempenho(94, 6),
                           pagina.linha_fonte('pedidos do ERP', '312 pedidos de set/2026', agora))]
    open('painel.html', 'w').write(pagina.documento('Margem de setembro', blocos))

O tema escuro vem por `prefers-color-scheme` e pode ser forçado com `data-theme="dark"` ou
`"light"` no `<html>`. `documento` traz também o ajuste que faz o SVG acompanhar o tema:
o preto do desenho vira a tinta do tema, e a grade vira a linha do tema.
"""
from . import paleta
from .paleta import esc
import re

FONTE_GOOGLE = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                '<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:'
                'wght@400;500;600;700&display=swap" rel="stylesheet">')


def cabeca(titulo):
    """Do doctype até a abertura do `<style>`, com a fonte da casa pelo Google Fonts.

    Para tela o link basta. Para PDF, use `marca.fontes()` dentro do `<style>`: o link nem
    sempre chega a tempo no Chrome headless.
    """
    return (f'<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{titulo}</title>\n{FONTE_GOOGLE}\n<style>\n')


def tema(ink=None, txt=None):
    """As quatro variáveis do tema (tinta, papel, texto discreto, linha), claro e escuro."""
    INK, TXT = ink or paleta.INK, txt or paleta.TXT
    return (f''':root{{--ink:{INK};--papel:#ffffff;--txt:{TXT};--linha:#ECECEC}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ink:#F2F2F2;--papel:#0B0B0B;--txt:#8F8F8F;--linha:#232323}}}}
:root[data-theme="dark"]{{--ink:#F2F2F2;--papel:#0B0B0B;--txt:#8F8F8F;--linha:#232323}}
''')


def css_painel():
    """O CSS do painel em grade: seções, blocos, pergunta e manchete, a grade de três, a
    barra de funil (`.fl`), a tabela de conferência, a tabela nominal e o rodapé."""
    INK, TXT, AMBAR = paleta.INK, paleta.TXT, paleta.AMBAR
    return tema(INK, TXT) + f'''*{{box-sizing:border-box}}
body{{margin:0;background:var(--papel);color:var(--ink);padding:28px 16px 56px;
 font-family:"Schibsted Grotesk",system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}}
.w{{max-width:1000px;margin:0 auto}}
header{{margin-bottom:40px;padding-bottom:18px;border-bottom:1px solid var(--linha)}}
h1{{font-size:15px;font-weight:600;margin:0}}
header p{{color:var(--txt);font-size:12.5px;margin:3px 0 0;max-width:74ch;line-height:1.55}}
main{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:52px 40px;align-items:start}}
section{{margin:0;min-width:0}}
section.larga{{grid-column:1/-1}}
.perg{{color:var(--txt);font-size:12px;margin:0 0 5px;text-transform:uppercase;letter-spacing:.07em}}
.rumo{{font-size:11px;margin:7px 0 0;color:var(--txt);letter-spacing:.01em}}
main{{align-items:stretch}}
section{{display:flex;flex-direction:column}}
section>svg,section>.tres{{height:300px;margin-top:auto}}
section.larga>svg,section.larga>.tres{{height:360px}}
section>.tres{{display:grid}}
section>.tres svg{{height:100%;min-height:0}}
.secao{{grid-column:1/-1;margin:30px 0 -14px;padding-top:26px;border-top:2px solid var(--ink)}}
.secao:first-child{{margin-top:0;padding-top:0;border-top:none}}
.secao.abre h1{{font-size:28px}}
.secao h1{{font-size:24px;font-weight:700;margin:0;letter-spacing:-.02em}}
.secao p{{font-size:13px;color:var(--txt);margin:5px 0 0}}
.secao span{{font-size:10.5px;color:var(--txt);text-transform:uppercase;letter-spacing:.07em}}
section.tabelona{{display:block}}
table.abertas{{width:100%;border-collapse:collapse;font-size:12.5px;line-height:1.45}}
table.abertas th{{text-align:left;font-weight:600;font-size:10.5px;color:var(--txt);
 text-transform:uppercase;letter-spacing:.06em;padding:0 10px 8px 0;border-bottom:1px solid var(--ink)}}
table.abertas td{{padding:10px 10px 10px 0;border-bottom:1px solid var(--linha);vertical-align:top}}
table.abertas td.num{{white-space:nowrap;text-align:right;font-variant-numeric:tabular-nums}}
table.abertas td.nd{{color:var(--txt);opacity:.75}}
table.abertas a{{color:inherit;text-decoration:none;font-weight:600}}
table.abertas a:hover{{text-decoration:underline}}
table.abertas .tags{{margin-top:5px;display:flex;flex-wrap:wrap;gap:4px}}
table.abertas code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;
 background:rgba(128,128,128,.13);padding:2px 5px;border-radius:3px;color:var(--txt)}}
.rumo::before{{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;
 background:{AMBAR};margin-right:6px;vertical-align:middle}}
section h2{{font-size:17px;font-weight:600;line-height:1.35;margin:0;letter-spacing:-.015em}}
.pergunta-resposta{{margin:0 0 18px;min-height:5.4em;display:flex;flex-direction:column;justify-content:flex-end}}
section.larga .pergunta-resposta{{min-height:0;margin-bottom:20px}}
.fonte{{font-size:10.5px;color:var(--txt);margin:10px 0 0;letter-spacing:.01em;opacity:.85}}
.fl{{display:flex;align-items:center;gap:14px;margin:9px 0;font-size:13px}}
.tres{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}}
.tres p.sub{{font-size:11.5px;font-weight:600;margin:0 0 7px;letter-spacing:.01em}}
@media(max-width:860px){{.tres{{grid-template-columns:1fr}}}}
.fln{{width:78px;color:var(--txt)}}
.flb{{flex:1;height:14px;background:var(--linha);border-radius:7px;overflow:hidden;
 display:flex;align-items:center;justify-content:center}}
.flb i{{display:block;height:100%;border-radius:7px}}
.flv{{width:30px;text-align:right;font-weight:600;font-variant-numeric:tabular-nums}}
.flp{{width:40px;text-align:right;color:var(--txt);font-size:12px;font-variant-numeric:tabular-nums}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;font-weight:500;color:var(--txt);font-size:11.5px;text-transform:uppercase;
 letter-spacing:.06em;padding:0 10px 8px 0;border-bottom:1px solid var(--linha)}}
td{{padding:11px 10px 11px 0;border-bottom:1px solid var(--linha)}}
td.n,th.n{{text-align:right;font-variant-numeric:tabular-nums;width:74px}}
td.pct{{font-weight:600}}
td.bar{{width:180px}}
td.bar span{{display:block;height:8px;background:var(--linha);border-radius:4px;overflow:hidden}}
td.bar i{{display:block;height:100%;border-radius:4px}}
footer{{color:var(--txt);font-size:11.5px;border-top:1px solid var(--linha);padding-top:14px;
 margin-top:44px;line-height:1.6;max-width:80ch}}
@media(max-width:860px){{main{{grid-template-columns:1fr}}.pergunta-resposta{{min-height:0}}}}
@media(max-width:620px){{.fln{{width:60px}}.flp{{display:none}}td.bar{{display:none}}}}
'''


# O desenho sai com a cor escrita no próprio SVG, para funcionar fora da página. No tema
# escuro, o preto da tinta e o cinza da grade seriam invisíveis sobre o papel escuro, e
# CSS vence atributo de apresentação: estas regras trocam só as duas cores neutras.
CSS_SVG_TEMA = ('''
svg [fill="#0a0a0a"]{fill:var(--ink)}svg [stroke="#0a0a0a"]{stroke:var(--ink)}
svg [stroke="#ededed"],svg [stroke="#ECECEC"]{stroke:var(--linha)}svg [fill="#ededed"]{fill:var(--linha)}
''')


def linha_fonte(origem, recorte, quando, fuso='UTC'):
    """A linha de fonte de todo gráfico: de onde veio, que recorte, e QUANDO foi medido.

    Sem o quando, a página afirma um estado do mundo sem dizer de que momento. `origem` e
    `recorte` entram como HTML (escape o que vier de fora); `quando` é um datetime.
    """
    return (f'Fonte: {origem} &#183; {recorte} &#183; '
            f'medido em {quando.strftime("%d/%m/%Y %H:%M")} {fuso}')


def secao(pergunta, manchete, desenho, fonte, larga=False):
    """Um bloco: pergunta, manchete, desenho e a linha de fonte.

    `manchete` vazia deixa só a pergunta. A nota de leitura que a forma traz dentro do SVG
    (`<text class="leitura">`) sai do desenho e vira `p.comoler`, que o deck transforma em
    nota adesiva e o painel pode esconder.
    """
    cls = ' class="larga"' if larga else ''
    cab = f'<p class="perg">{esc(pergunta)}</p>'
    if manchete:
        cab += f'<h2>{esc(manchete)}</h2>'
    notas = re.findall(r'<text class="leitura"[^>]*>(.*?)</text>', desenho, re.S)
    desenho = re.sub(r'<text class="leitura"[^>]*>.*?</text>\s*', '', desenho, flags=re.S)
    txt = ' · '.join(re.sub(r'<[^>]+>', '', x).strip() for x in notas if x.strip())
    leitura_html = (f'<p class="comoler">Como ler: '
                    f'{txt.replace("como ler: ", "")}.</p>' if txt else '')
    return (f'<section{cls}><div class="pergunta-resposta">{cab}{leitura_html}</div>'
            f'{desenho}<p class="fonte">{fonte}</p></section>')


def titulo_secao(titulo, sub, n, abre=False):
    """O separador entre grupos de blocos, na largura da grade inteira."""
    return (f'<div class="secao{" abre" if abre else ""}"><h1>{esc(titulo)}</h1>'
            f'<p>{esc(sub)}</p><span>{n} formas</span></div>')


def documento(titulo, blocos, rodape='', cabecalho='', css_extra=''):
    """A página inteira, autocontida, com o tema escuro valendo também para o SVG.

    `blocos` é uma lista de HTML (saídas de `secao` e `titulo_secao`), `rodape` vai no
    `<footer>`, `cabecalho` antes da grade (logo e título, por exemplo).
    """
    return (cabeca(esc(titulo)) + css_painel() + CSS_SVG_TEMA + css_extra
            + '.comoler{display:none}\n'
            # a grade fixa a altura do desenho para alinhar colunas; forma baixa (cartões,
            # barra única) ficava boiando numa caixa de 300px
            + 'section>svg,section.larga>svg{height:auto;max-height:360px}\n'
            + '</style></head><body><div class="w">\n' + cabecalho
            + '<main>' + ''.join(b for b in blocos if b) + '</main>\n'
            + (f'<footer>{rodape}</footer>\n' if rodape else '')
            + '</div></body></html>')
