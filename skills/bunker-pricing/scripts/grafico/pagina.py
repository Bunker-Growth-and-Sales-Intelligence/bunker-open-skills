"""O HTML autocontido: o painel de tela e as folhas A4 do PDF.

Cada bloco (`secao`) tem a PERGUNTA de negócio no alto, a MANCHETE com a conclusão e os
números, e o desenho. Nenhum parágrafo explicativo: o que não cabe na manchete vai para o
rodapé, e a fonte dos números aparece uma vez só, no rodapé da página.

O painel segue o tema do sistema (claro ou escuro) e pode ser forçado com `data-theme` no
`<html>`. O SVG sai com a cor escrita nele; no escuro, `CSS_SVG_TEMA` troca só o preto da
tinta e o cinza da grade pelo tema, e a cor do cliente fica como está.
"""
from . import marca, paleta
from .paleta import esc


def tema():
    return ''':root{--ink:#0a0a0a;--papel:#ffffff;--txt:#6f6f6f;--linha:#e6e6e6;--fundo2:#f5f5f5}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#F2F2F2;--papel:#0B0B0B;--txt:#9a9a9a;--linha:#262626;--fundo2:#161616}}
:root[data-theme="dark"]{--ink:#F2F2F2;--papel:#0B0B0B;--txt:#9a9a9a;--linha:#262626;--fundo2:#161616}
'''


CSS_SVG_TEMA = '''svg [fill="#0a0a0a"]{fill:var(--ink)}svg [stroke="#0a0a0a"]{stroke:var(--ink)}svg [fill="#fffffe"]{fill:var(--papel)}
svg [stroke="#ededed"]{stroke:var(--linha)}svg [fill="#ededed"]{fill:var(--linha)}
'''


BOM = '#1e7b45'   # o desvio que vai bem; o que vai mal usa o alerta da marca


def css_dre():
    """A tabela da DRE: nome, planejado, realizado, desvio, % da receita bruta e as três colunas
    de nome (Alumni, skill, Pricing Designer)."""
    return f'''table.dre{{width:100%;border-collapse:collapse;font-size:12.5px}}
table.dre td.v,table.dre td.dsv,table.dre td.prb{{font-variant-numeric:tabular-nums}}
table.dre th,table.dre td{{padding:4px 8px 4px 0;border-bottom:1px solid var(--linha);text-align:right;white-space:nowrap;
 vertical-align:top}}
table.dre thead th{{vertical-align:bottom}}
table.dre .n0{{text-align:left;white-space:normal;width:25%}}
table.dre td.n0 small{{display:block;color:var(--txt);font-size:.85em}}
table.dre thead th{{white-space:normal;font-size:10px;font-weight:600;color:var(--txt);text-transform:uppercase;letter-spacing:.05em;
 border-bottom:1.5px solid var(--ink);vertical-align:bottom}}
table.dre tr.grp td{{padding-top:12px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;
 color:var(--txt);border-bottom:none;text-align:left}}
table.dre tr.sub td{{font-weight:600}}
table.dre tr.tot td{{font-weight:700;border-bottom:1.5px solid var(--ink)}}
table.dre tr.ind td{{color:var(--txt)}}
table.dre tr.ind td.n0 .nome{{padding-left:10px}}
table.dre tr td.dsv{{font-weight:400}}
table.dre td.dsv.bom{{color:{BOM}}}
table.dre td.dsv.mau{{color:{paleta.alerta()}}}
table.dre .sinal{{color:var(--txt);font-weight:400}}
table.dre .al{{white-space:nowrap}}
table.dre .nmc{{text-align:left;white-space:normal;width:12.5%;font-size:.76em;font-weight:400;color:var(--txt);line-height:1.3}}
table.dre th.nmc small{{display:block;text-transform:none;letter-spacing:0;font-weight:400}}
table.dre th.nmc.sk,table.dre td.nmc.sk{{color:var(--ink)}}
table.dre tr.tot td.nmc,table.dre tr.sub td.nmc{{font-weight:400}}
table.dre .nmc em,table.dre .nm em{{display:block;font-style:normal;font-size:.72em;letter-spacing:.08em;text-transform:uppercase;opacity:.8}}
table.dre .falta{{color:{paleta.alerta()}}}
table.dre.conc .n0{{width:34%}}
'''


def css_edicao():
    """O campo dentro da célula, no tamanho da letra dela e sem mudar a altura da linha; os botões
    de nome, as abas da DRE da venda e o aviso de números editados."""
    return f'''input.ed{{font:inherit;color:inherit;background:transparent;border:0;border-bottom:1px dotted var(--txt);
 padding:0;margin:0;height:auto;line-height:inherit;text-align:right;min-width:3ch;border-radius:0;
 -webkit-appearance:none;appearance:none;box-shadow:none;vertical-align:baseline}}
input.ed:hover{{background:var(--fundo2)}}
input.ed:focus{{outline:none;background:var(--fundo2);border-bottom:1px solid var(--ink)}}
table.dre button.nm{{font:inherit;text-align:left;width:100%;background:transparent;border:1px solid transparent;color:inherit;
 padding:1px 4px;margin:-2px 0;cursor:pointer;border-radius:0;line-height:1.3}}
table.dre button.nm:hover{{border-color:var(--linha);background:var(--fundo2)}}
table.dre button.nm:focus-visible{{outline:2px solid var(--ink);outline-offset:1px}}
table.dre button.nm.sk{{color:var(--ink)}}
table.dre button.nm.falta{{color:{paleta.alerta()}}}
table.dre button.nm[aria-pressed="true"]{{background:var(--ink);color:var(--papel);border-color:var(--ink)}}
.abas{{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}}
.abas button{{font:inherit;font-size:12px;background:transparent;color:var(--txt);border:1px solid var(--linha);padding:5px 10px;
 cursor:pointer;border-radius:2px}}
.abas button[aria-selected="true"]{{color:var(--papel);background:var(--ink);border-color:var(--ink)}}
p.un{{font-size:11px;color:var(--txt);text-transform:uppercase;letter-spacing:.06em;margin:0 0 6px}}
.multiplos{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px 28px;margin-top:22px}}
.multiplos svg{{max-width:340px}}
.editado{{position:sticky;bottom:12px;z-index:5;display:flex;gap:14px;align-items:center;justify-content:space-between;
 background:var(--ink);color:var(--papel);font-size:12.5px;padding:9px 14px;margin-top:28px;border-radius:3px}}
.editado[hidden]{{display:none}}
.editado button{{font:inherit;background:transparent;color:var(--papel);border:1px solid var(--papel);padding:4px 10px;cursor:pointer}}
body.mexido .estatico{{opacity:.35}}
@media(max-width:760px){{.tw table.dre{{min-width:760px}}.tw table.dre.conc{{min-width:560px}}
 .tw table.dre .n0{{position:sticky;left:0;background:var(--papel);z-index:1;width:170px;min-width:170px;padding-right:10px}}}}
'''


def css_painel():
    return tema() + f'''*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--papel);color:var(--ink);padding:28px 16px 56px;
 font-family:"Schibsted Grotesk",system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}}
.w{{max-width:1000px;margin:0 auto}}
header.topo{{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;
 margin-bottom:36px;padding-bottom:18px;border-bottom:2px solid var(--ink)}}
header.topo img{{height:26px;display:block;margin-bottom:14px}}
header.topo .claro{{display:block}}header.topo .escuro{{display:none}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]) header.topo .claro{{display:none}}:root:not([data-theme="light"]) header.topo .escuro{{display:block}}}}
:root[data-theme="dark"] header.topo .claro{{display:none}}:root[data-theme="dark"] header.topo .escuro{{display:block}}
header.topo h1{{font-size:28px;font-weight:800;margin:0;letter-spacing:-.02em;line-height:1.15}}
header.topo p{{color:var(--txt);font-size:13px;margin:6px 0 0}}
header.topo .quando{{font-size:12px;color:var(--txt);text-align:right}}
main{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:52px 40px;align-items:start}}
section{{margin:0;min-width:0}}
section.larga{{grid-column:1/-1}}
.perg{{color:var(--txt);font-size:12px;margin:0 0 6px;text-transform:uppercase;letter-spacing:.06em;line-height:1.4}}
section h2{{font-size:17px;font-weight:600;line-height:1.35;margin:0 0 16px;letter-spacing:-.01em}}
section svg{{display:block;width:100%;height:auto;margin-top:6px}}
.tw{{overflow-x:auto}}
footer{{color:var(--txt);font-size:11.5px;border-top:1px solid var(--linha);padding-top:14px;margin-top:48px;line-height:1.6}}
@media(max-width:860px){{main{{grid-template-columns:minmax(0,1fr)}}header.topo .quando{{text-align:left}}}}
''' + css_dre() + css_edicao()


def secao(pergunta, manchete, desenho, larga=False, classe=''):
    """Um bloco: a pergunta de negócio, a manchete com a conclusão, e o desenho."""
    cls = ' '.join(x for x in ('larga' if larga else '', classe) if x)
    h2 = f'<h2>{esc(manchete)}</h2>' if manchete else ''
    return (f'<section{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}><p class="perg">{esc(pergunta)}</p>'
            f'{h2}{desenho}</section>')


def documento(titulo, blocos, sub='', quando='', rodape='', fim=''):
    """O painel inteiro, autocontido, com a fonte embutida e o tema escuro valendo para o SVG."""
    cab = (f'<header class="topo"><div><img class="claro" src="{marca.logo_preto()}" alt="Bunker">'
           f'<img class="escuro" src="{marca.logo_branco()}" alt="Bunker"><h1>{esc(titulo)}</h1>'
           + (f'<p>{esc(sub)}</p>' if sub else '') + '</div>'
           + (f'<div class="quando">{esc(quando)}</div>' if quando else '') + '</header>')
    return ('<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{esc(titulo)}</title>\n<style>\n{marca.fontes()}\n{css_painel()}{CSS_SVG_TEMA}</style></head>\n'
            f'<body><div class="w">{cab}<main>{"".join(b for b in blocos if b)}</main>'
            + (f'<footer>{rodape}</footer>' if rodape else '') + f'</div>{fim}</body></html>\n')


# ------------------------------------------------------------------ folhas A4 do PDF

def css_folhas():
    """A4 em pé, sem margem de impressão: a folha desenha a própria margem de 18 mm."""
    return f'''@page{{size:A4;margin:0}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;background:#ffffff}}
body{{font-family:"Schibsted Grotesk",system-ui,sans-serif;color:#0a0a0a;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.folha{{width:210mm;height:297mm;padding:16mm 18mm 14mm;position:relative;overflow:hidden;page-break-after:always;break-after:page;
 display:flex;flex-direction:column}}
.folha:last-child{{page-break-after:auto;break-after:auto}}
.folha .cab{{display:flex;justify-content:space-between;align-items:center;padding-bottom:9px;border-bottom:1.5px solid #0a0a0a;
 margin-bottom:9mm;font-size:9.5px;color:#6f6f6f;letter-spacing:.06em;text-transform:uppercase}}
.folha .cab img{{height:15px;display:block}}
.folha .pe{{margin-top:auto;padding-top:8px;border-top:1px solid #e6e6e6;display:flex;justify-content:space-between;gap:16px;
 font-size:8.5px;color:#6f6f6f;line-height:1.5}}
.folha .pe span:last-child{{white-space:nowrap}}
.bloco{{margin-bottom:7mm}}
.bloco .perg{{color:#6f6f6f;font-size:10px;margin:0 0 5px;text-transform:uppercase;letter-spacing:.06em}}
.bloco .perg + .tw,.bloco .perg + .estatico{{margin-top:6px}}
.bloco h2{{font-size:15.5px;font-weight:600;line-height:1.35;margin:0 0 10px;letter-spacing:-.01em}}
.bloco svg{{display:block;width:100%;height:auto}}
h1.titulo{{font-size:22px;font-weight:800;margin:0 0 7mm;letter-spacing:-.02em}}
.capa,.fecho{{background:#0a0a0a;color:#ffffff;padding:22mm 20mm}}
.capa .b{{position:absolute;right:-18mm;bottom:26mm;width:105mm;height:auto;opacity:.13}}
.fecho .b{{position:absolute;right:20mm;bottom:24mm;width:52mm;height:auto;opacity:.13}}
.capa .logo,.fecho .logo{{width:160px;height:auto;align-self:flex-start;flex:none;display:block}}
.folha .cab img{{width:auto;flex:none}}
.capa .rot{{margin-top:70mm;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:#bdbdbd}}
.capa h1{{font-size:44px;line-height:1.08;font-weight:900;margin:6mm 0 0;letter-spacing:-.03em;max-width:150mm}}
.capa .sub{{font-size:15px;color:#d6d6d6;margin:6mm 0 0;max-width:140mm;line-height:1.45}}
.capa .pe,.fecho .pe{{border-top:1px solid #333;color:#bdbdbd;font-size:10px;position:relative}}
.fecho h1{{font-size:32px;font-weight:900;margin:24mm 0 4mm;letter-spacing:-.02em}}
.fecho p.sub{{font-size:13px;color:#d6d6d6;margin:0 0 12mm;max-width:150mm;line-height:1.5}}
.fecho svg{{display:block;width:100%;height:auto}}
.fecho-caixa{{background:#0a0a0a;color:#ffffff;border-radius:4px;padding:7mm 8mm 8mm;margin:4mm 0 0}}
.fecho-caixa h3{{font-size:20px;font-weight:900;margin:0 0 2mm;letter-spacing:-.02em}}
.fecho-caixa p{{font-size:11px;color:#d6d6d6;margin:0 0 5mm}}
.fecho-caixa svg{{display:block;width:100%;height:auto}}
''' + css_dre().replace('var(--linha)', '#e6e6e6').replace('var(--ink)', '#0a0a0a').replace('var(--txt)', '#6f6f6f') + '''
table.dre{font-size:8.4px}table.dre th,table.dre td{padding:1.5px 4px 1.5px 0}
table.dre tr.grp td{padding-top:6px;font-size:7.6px}table.dre thead th{font-size:7px}
table.dre .n0{width:22%}table.dre .nmc{width:15%;font-size:6.8px;line-height:1.15}
table.dre td.nmc.sk{font-weight:600}
table.dre.conc{font-size:9.6px}table.dre.conc th,table.dre.conc td{padding:3px 6px 3px 0}
.multiplos{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;margin-top:2mm}
'''


def folha(conteudo, cabeca_txt, pe_txt, n, total):
    """Uma folha A4 de conteúdo: cabeçalho com o logo, o conteúdo e o rodapé com a fonte e a página."""
    return (f'<section class="folha"><div class="cab"><img src="{marca.logo_preto()}" alt="Bunker">'
            f'<span>{esc(cabeca_txt)}</span></div>{conteudo}'
            f'<div class="pe"><span>{pe_txt}</span><span>{n} / {total}</span></div></section>')


def bloco_folha(pergunta, manchete, desenho):
    h2 = f'<h2>{esc(manchete)}</h2>' if manchete else ''
    return f'<div class="bloco"><p class="perg">{esc(pergunta)}</p>{h2}{desenho}</div>'


def documento_folhas(titulo, folhas):
    return ('<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">\n'
            f'<title>{esc(titulo)}</title>\n<style>\n{marca.fontes()}\n{css_folhas()}</style></head>\n'
            f'<body>{"".join(folhas)}</body></html>\n')
