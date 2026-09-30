"""Do HTML ao PDF, pelo Chrome headless da máquina.

O PDF sai do Chrome headless, e não do "Salvar como PDF" do navegador: o diálogo de impressão
pode meter margem e cabeçalho e entregar um arquivo diferente do HTML. O tamanho da folha é o
que a página declara em `@page` (aqui, A4 sem margem, e a página desenha a própria margem).

O Chrome é procurado nesta ordem: a variável BUNKER_CHROME, os caminhos de instalação do
macOS e do Windows, e os nomes de comando do Linux. Chromium, Edge e Brave servem. Sem nenhum
deles, `achar_chrome()` devolve None, e quem chama entrega o HTML para imprimir.
"""
import os
import re
import shutil
import subprocess

_MAC = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
]
_WIN = [
    r'%ProgramFiles%\Google\Chrome\Application\chrome.exe',
    r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe',
    r'%LocalAppData%\Google\Chrome\Application\chrome.exe',
    r'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe',
    r'%ProgramFiles%\Microsoft\Edge\Application\msedge.exe',
]
_LINUX = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'brave-browser']


def achar_chrome():
    """O executável do Chrome (ou de um Chromium) desta máquina, ou None."""
    env = os.environ.get('BUNKER_CHROME')
    if env and os.path.exists(env):
        return env
    casa = os.path.expanduser('~')
    for c in _MAC + [casa + c for c in _MAC]:
        if os.path.exists(c):
            return c
    for c in _WIN:
        c = os.path.expandvars(c)
        if os.path.exists(c):
            return c
    for c in _LINUX:
        achado = shutil.which(c)
        if achado:
            return achado
    return None


def chrome(*args, capture=True):
    exe = achar_chrome()
    if not exe:
        raise FileNotFoundError('Chrome não encontrado nesta máquina')
    return subprocess.run([exe, '--headless=new', '--disable-gpu'] + list(args), check=True, capture_output=capture)


def paginas(pdf):
    """Quantas páginas o PDF tem. Usa o `pdfinfo` se existir; senão conta os objetos de página."""
    if shutil.which('pdfinfo'):
        saiu = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
        m = re.search(r'Pages:\s+(\d+)', saiu)
        if m:
            return int(m.group(1))
    with open(pdf, 'rb') as f:
        return len(re.findall(rb'/Type\s*/Page(?!s)', f.read())) or None


def para_pdf(html, pdf, esperadas=None):
    """A página em PDF, respeitando o `@page` dela, com a contagem de páginas conferida.

    Devolve o caminho do PDF, ou None quando a máquina não tem Chrome. `esperadas` é quantas
    folhas a página desenha; se o PDF sair com outra conta, a função falha alto, porque o
    Chrome às vezes para de imprimir no meio sem erro nenhum.
    """
    if not achar_chrome():
        return None
    chrome('--no-pdf-header-footer', f'--print-to-pdf={os.path.abspath(pdf)}', '--virtual-time-budget=20000',
           '--run-all-compositor-stages-before-draw', 'file://' + os.path.abspath(html))
    n = paginas(pdf)
    if esperadas and n and n != esperadas:
        raise SystemExit(f'{pdf}: {n} páginas para {esperadas} folhas; o PDF saiu cortado ou transbordou')
    return pdf
