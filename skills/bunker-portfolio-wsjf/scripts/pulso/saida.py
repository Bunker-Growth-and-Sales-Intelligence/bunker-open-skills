"""Do HTML ao PDF, pelo Google Chrome sem janela.

O HTML já tem o botão "Salvar em PDF", que usa a impressão do navegador. Este módulo é o
caminho automático, para quem roda a skill num computador com o Chrome instalado.

Cada `<deck-stage>` vira UMA página de 1920x1080, que é o que faz o PDF abrir como slide.
O documento sai em lotes de 10, porque o Chrome para de imprimir por volta da décima
primeira página desse tamanho sem dar erro. Os lotes são costurados pelo `pdfunite`
(pacote poppler) quando ele existe; sem ele, o deck de mais de 10 slides pede o botão.
"""
import os
import re
import shutil
import subprocess

_CANDIDATOS = [
    os.environ.get('BUNKER_CHROME', ''),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
]


def achar_chrome():
    for c in _CANDIDATOS:
        if c and (os.path.isfile(c) or shutil.which(c)):
            return c if os.path.isfile(c) else shutil.which(c)
    raise FileNotFoundError('Google Chrome não encontrado (defina BUNKER_CHROME)')


def chrome(*args):
    return subprocess.run([achar_chrome(), '--headless=new', '--disable-gpu'] + list(args),
                          check=True, capture_output=True)


def paginas(pdf):
    """Conta as páginas sem depender de ferramenta externa."""
    dados = open(pdf, 'rb').read()
    return len(re.findall(rb'/Type\s*/Page(?!s)', dados))


def para_pdf(html, pdf, por_lote=10, palco='deck-stage'):
    fonte = open(html, encoding='utf-8').read()
    palcos = re.findall(rf'<{palco}.*?</{palco}>', fonte, re.S)
    cabeca = fonte[:fonte.index(f'<{palco}')]
    if len(palcos) > por_lote and not shutil.which('pdfunite'):
        raise RuntimeError('deck com mais de 10 slides e sem pdfunite para costurar os lotes')
    base = os.path.splitext(pdf)[0]
    lotes = []
    for k in range(0, len(palcos), por_lote):
        parte = f'{base}-lote{k // por_lote}'
        open(parte + '.html', 'w', encoding='utf-8').write(
            cabeca + '\n'.join(palcos[k:k + por_lote]) + '\n</body></html>')
        chrome('--no-pdf-header-footer', f'--print-to-pdf={parte}.pdf',
               '--virtual-time-budget=20000', '--run-all-compositor-stages-before-draw',
               'file://' + os.path.abspath(parte + '.html'))
        lotes.append(parte)
    if len(lotes) == 1:
        os.replace(lotes[0] + '.pdf', pdf)
    else:
        subprocess.run(['pdfunite'] + [x + '.pdf' for x in lotes] + [pdf], check=True)
        for x in lotes:
            os.remove(x + '.pdf')
    for x in lotes:
        os.remove(x + '.html')
    pags = paginas(pdf)
    if pags != len(palcos):
        raise RuntimeError(f'{pags} páginas para {len(palcos)} slides; o PDF saiu cortado')
    return pdf
