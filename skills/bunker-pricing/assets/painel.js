/*CAMADAS*/
// As duas camadas da DRE, a mesma conta de scripts/camadas.py, sobre o Motor do simulador.
// O teste de paridade (scripts/test_entrega.py) roda esta parte no node e confere cada número
// contra o Python, em 4 casas.
var Camadas = (function () {
  var L = Motor.limpa, r2 = Motor.r2;
  function soma(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]; return L(s); }
  function vazio(x) { return x === null || x === undefined || x === ''; }
  function topo(l) {
    if (l.piso) { var ac = l.niveis.filter(function (n) { return n.chave !== 'teto'; }); if (ac.length) return ac[0]; }
    return l.niveis[0];
  }
  function venda(l, bruta) {
    var p = Object.assign({}, l.p, { q: 1 }), t = topo(l), u = l.usado;
    var custoReal = vazio(bruta.custo_real) ? null : +bruta.custo_real;
    var plan = Motor.dre(t.preco, p), usado = Motor.dre(u.preco, p), mesmo = Motor.dre(l.negociado, p);
    var real = Motor.dre(l.negociado, p, custoReal);
    return { nome: l.nome, p: p, topo: t, usado: u, negociado: l.negociado, plan: plan, usadoDre: usado, mesmo: mesmo,
      real: real, vrs: p.vrs, base: plan.rl, campanha: L(t.preco - u.preco), tatico: L(u.preco - l.negociado),
      cedida_campanha: L(plan.mc - usado.mc), cedida_tatico: L(usado.mc - mesmo.mc), cedida_custo: L(mesmo.mc - real.mc) };
  }
  var CH = ['rb', 'deducoes', 'rl_contabil', 'desp_total', 'rl', 'cpv', 'mc'];
  function somaD(ds) {
    var o = {};
    CH.concat(['comissao', 'frete', 'outras']).forEach(function (k) { o[k] = soma(ds.map(function (d) { return d[k]; })); });
    o.imp = {};
    ds.forEach(function (d) { d.impostos.forEach(function (x) { o.imp[x[0]] = L((o.imp[x[0]] || 0) + x[1]); }); });
    return o;
  }
  function dec(cen, k) { return vazio(cen[k]) ? null : +cen[k]; }
  function fixas(cen) {
    if (cen.despesas_fixas && cen.despesas_fixas.length) return cen.despesas_fixas.map(function (d) { return [d.nome, +d.valor]; });
    if (!vazio(cen.custo_fixo_mes)) return [['Despesas operacionais fixas', +cen.custo_fixo_mes]];
    return [];
  }
  function tatico(l) { return l.cascata.filter(function (c) { return c.chave === 'tatico'; })[0]; }
  function mes(cen, ls) {
    var orc = somaD(ls.map(function (l) { return topo(l).dre; })), rea = somaD(ls.map(function (l) { return l.real; }));
    var o = { orcado: orc, realizado: rea, rec_teto: orc.rb,
      desc_campanha: soma(ls.map(function (l) { return L(topo(l).dre.rb - l.usado.dre.rb); })),
      desc_tatico: soma(ls.map(function (l) { return L(l.usado.dre.rb - l.real.rb); })),
      mesa_campanha: soma(ls.map(function (l) { return L(topo(l).dre.mc - l.usado.dre.mc); })),
      mesa_tatico: soma(ls.map(function (l) { return L(l.usado.dre.mc - tatico(l).mc); })),
      mesa_custo: soma(ls.map(function (l) { return L(tatico(l).mc - l.real.mc); })) };
    o.mesa_total = L(orc.mc - rea.mc);
    [orc, rea].forEach(function (d) {
      d.mc_rl = d.rl > 0 ? d.mc / d.rl * 100 : null;
      d.mc_rb = d.rb > 0 ? d.mc / d.rb * 100 : null;
    });
    o.fixas = fixas(cen);
    o.tem_fixo = o.fixas.length > 0;
    if (o.tem_fixo) {
      var tot = soma(o.fixas.map(function (f) { return f[1]; })), rf = dec(cen, 'receitas_financeiras') || 0,
        df = dec(cen, 'despesas_financeiras') || 0, ir = dec(cen, 'irpj_csll_pct'),
        presumido = ['presumido', 'lucro presumido'].indexOf(String(cen.regime || '').trim().toLowerCase()) >= 0;
      o.fixo = tot; o.rec_fin = rf; o.desp_fin = df; o.ir_pct = ir;
      [orc, rea].forEach(function (d) {
        d.fixo = tot; d.ro = L(d.mc - tot); d.lair = L(d.ro + rf - df);
        // no Lucro Presumido, IRPJ e CSLL saem da receita bruta e pesam mesmo com prejuízo
        if (ir === null) d.ir = 0;
        else if (presumido) d.ir = d.rb > 0 ? r2(d.rb * ir / 100) : 0;
        else d.ir = d.lair > 0 ? r2(d.lair * ir / 100) : 0;
        d.ll = L(d.lair - d.ir); d.final = ir !== null ? d.ll : d.lair;
        d.ml = (ir !== null && d.rl_contabil > 0) ? d.ll / d.rl_contabil * 100 : null;
        d.peso = d.rb > 0 ? tot / d.rb * 100 : null;
      });
    }
    return o;
  }
  function vendasAMais(ls, vendas) {
    var linhas = ls.map(function (l, i) {
      var q = l.p.q, perf = topo(l).dre.mc, un = vendas[i].real.mc, nec = un > 0 ? perf / un : null;
      var amais = nec === null ? null : L(nec - q);
      return { q: q, perf: perf, un: un, nec: nec, amais: amais, pct: (amais === null || !q) ? null : amais / q * 100,
        esforco: amais === null ? null : amais * vendas[i].negociado };
    });
    var ok = linhas.every(function (x) { return x.nec !== null; }), q = soma(linhas.map(function (x) { return x.q; }));
    var t = { q: q, nec: null, amais: null, pct: null, esforco: null };
    if (ok) {
      t.nec = soma(linhas.map(function (x) { return x.nec; })); t.amais = L(t.nec - q);
      t.pct = q ? t.amais / q * 100 : null; t.esforco = soma(linhas.map(function (x) { return x.esforco; }));
    }
    return { linhas: linhas, total: t };
  }
  function calcular(cen) {
    cen = Motor.normalizar(cen);
    var res = Motor.calcular(cen), ruins = res.linhas.filter(function (l) { return l.erro; });
    if (ruins.length) return { erro: ruins.map(function (l) { return l.nome + ': ' + l.erro; }).join(' ') };
    var vendas = res.linhas.map(function (l, i) { return venda(l, cen.linhas[i]); });
    return { res: res, vendas: vendas, mes: mes(cen, res.linhas), amais: vendasAMais(res.linhas, vendas) };
  }
  // Os números do painel num mapa só, chave por chave; o Python grava as mesmas chaves nas células
  function valores(c) {
    var V = { '0': 0 };
    function D(pre, d) {
      V[pre + 'rb'] = d.rb; V[pre + 'deducoes'] = d.deducoes; V[pre + 'rlc'] = d.rl_contabil; V[pre + 'desp'] = d.desp_total;
      V[pre + 'rl'] = d.rl; V[pre + 'cpv'] = d.cpv; V[pre + 'mc'] = d.mc; V[pre + 'mc_rl'] = d.mc_rl; V[pre + 'mc_rb'] = d.mc_rb;
      V[pre + 'com'] = d.comissao; V[pre + 'fre'] = d.frete; V[pre + 'out'] = d.outras;
      if (d.impostos) d.impostos.forEach(function (x) { V[pre + 'imp.' + x[0]] = x[1]; });
      else Object.keys(d.imp).forEach(function (k) { V[pre + 'imp.' + k] = d.imp[k]; });
      if (d.fora) { d.fora.forEach(function (x) { V[pre + 'fora.' + x[0]] = x[3]; }); V[pre + 'nota'] = d.nota; }
      ['ro', 'lair', 'ir', 'll', 'ml', 'peso'].forEach(function (k) { if (d[k] !== undefined) V[pre + k] = d[k]; });
    }
    c.vendas.forEach(function (v, i) {
      var pre = 'v' + i + '.', l = c.res.linhas[i], a = c.amais.linhas[i];
      V[pre + 'custo'] = v.p.custo; V[pre + 'base'] = v.base; V[pre + 'mcplan'] = L(v.base - v.p.custo); V[pre + 'vrs'] = v.vrs;
      V[pre + 'trib'] = L(v.topo.preco - v.base - v.vrs); V[pre + 'teto'] = v.topo.preco; V[pre + 'usado'] = v.usado.preco;
      V[pre + 'neg'] = v.negociado; V[pre + 'camp'] = v.campanha; V[pre + 'tat'] = v.tatico;
      V[pre + 'ced_camp'] = v.cedida_campanha; V[pre + 'ced_tat'] = v.cedida_tatico; V[pre + 'ced_custo'] = v.cedida_custo;
      D(pre + 'P.', v.plan); D(pre + 'U.', v.usadoDre); D(pre + 'R.', v.real);
      V[pre + 'q'] = a.q; V[pre + 'perf'] = a.perf; V[pre + 'un'] = a.un; V[pre + 'nec'] = a.nec; V[pre + 'amais'] = a.amais;
      V[pre + 'amais_pct'] = a.pct; V[pre + 'esforco'] = a.esforco; V[pre + 'minimo'] = l.minimo;
    });
    var m = c.mes;
    D('m.O.', m.orcado); D('m.R.', m.realizado);
    ['rec_teto', 'desc_campanha', 'desc_tatico', 'mesa_campanha', 'mesa_tatico', 'mesa_custo', 'mesa_total'].forEach(function (k) { V['m.' + k] = m[k]; });
    if (m.tem_fixo) {
      V['m.fixo'] = m.fixo; V['m.rec_fin'] = m.rec_fin; V['m.desp_fin'] = m.desp_fin; V['m.ir_pct'] = m.ir_pct;
      m.fixas.forEach(function (f, k) { V['m.fix.' + k] = f[1]; });
    }
    var t = c.amais.total;
    V['t.q'] = t.q; V['t.nec'] = t.nec; V['t.amais'] = t.amais; V['t.amais_pct'] = t.pct; V['t.esforco'] = t.esforco;
    return V;
  }
  function s(x) { if (x === null || x === undefined) return null; var v = Motor.rnd(x, 4); return (v === 0 ? 0 : v).toFixed(4); }
  function numeros(cen) {
    var c = calcular(cen); if (c.erro) return { erro: c.erro };
    var V = valores(c), o = {}; Object.keys(V).forEach(function (k) { o[k] = s(V[k]); }); return o;
  }
  return { calcular: calcular, valores: valores, numeros: numeros, topo: topo };
})();
/*FIM-CAMADAS*/

(function () {
  'use strict';
  var fonte = document.getElementById('cenario-painel');
  if (!fonte) return;
  var ORIG = JSON.parse(fonte.textContent), cen = JSON.parse(JSON.stringify(ORIG)), editado = false;

  function br(x, c) {
    var v = Motor.rnd(x, c), t = Math.abs(v).toFixed(c).split('.'), i = t[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return (v < 0 ? '−' : '') + i + (c ? ',' + t[1] : '');
  }
  function fmt(v, f) {
    if (v === null || v === undefined) return '';
    if (f === 'pc' || f === 'pq') return br(v, 1) + '%';
    return br(v, 2);
  }
  function numero(txt) {
    var t = String(txt).trim().replace(/\s/g, '').replace(/^R\$/, '').replace('−', '-');
    if (!t) return null;
    if (t.indexOf(',') >= 0) t = t.replace(/\./g, '').replace(',', '.');
    var x = Number(t);
    return isFinite(x) ? x : null;
  }
  function pega(obj, caminho) {
    var ps = caminho.split('.'), o = obj;
    for (var i = 0; i < ps.length; i++) { if (o === null || o === undefined) return undefined; o = o[ps[i]]; }
    return o;
  }
  function poe(obj, caminho, v) {
    var ps = caminho.split('.'), o = obj;
    for (var i = 0; i < ps.length - 1; i++) { if (o[ps[i]] === null || o[ps[i]] === undefined) o[ps[i]] = {}; o = o[ps[i]]; }
    if (v === undefined) delete o[ps[ps.length - 1]]; else o[ps[ps.length - 1]] = v;
  }
  // desvio com seta e cor que julga: s="+" quando subir é bom, s="-" quando subir é ruim
  function desvio(td, d, f) {
    var c = (f === 'pc' || f === 'pq') ? 1 : 2, v = d === null || d === undefined ? 0 : Motor.rnd(d, c), s = td.getAttribute('data-s');
    td.classList.remove('bom', 'mau');
    if (!v) { td.textContent = ''; return; }
    td.textContent = (v > 0 ? '▲ ' : '▼ ') + br(Math.abs(v), c) + (f === 'pc' ? ' p.p.' : (f === 'pq' ? '%' : ''));
    if (s === '+' || s === '-') td.classList.add((v > 0) === (s === '+') ? 'bom' : 'mau');
  }
  function num(V, k) { return k === undefined || k === null ? null : (V[k] === undefined ? 0 : V[k]); }

  function pinta(V) {
    document.querySelectorAll('[data-k]').forEach(function (el) {
      var v = num(V, el.getAttribute('data-k')), sinal = +(el.getAttribute('data-sinal') || 1), f = el.getAttribute('data-f');
      if (v !== null && sinal !== 1) v = Motor.limpa(v * sinal);
      if (el.tagName === 'INPUT') { if (el !== document.activeElement) { el.value = fmt(v, 'rs'); ajusta(el); } }
      else el.textContent = fmt(v, f);
    });
    document.querySelectorAll('[data-da]').forEach(function (td) {
      var a = num(V, td.getAttribute('data-da')), b = num(V, td.getAttribute('data-db')), sg = +(td.getAttribute('data-sinal') || 1);
      desvio(td, a === null || b === null ? null : Motor.limpa(b * sg - a), td.getAttribute('data-f'));
    });
    document.querySelectorAll('[data-dv]').forEach(function (td) {
      var v = num(V, td.getAttribute('data-dv'));
      desvio(td, v === null ? null : Motor.limpa(v * +(td.getAttribute('data-sinal') || 1)), td.getAttribute('data-f'));
    });
    document.querySelectorAll('[data-pn]').forEach(function (td) {
      var a = num(V, td.getAttribute('data-pn')), b = num(V, td.getAttribute('data-pd')), sg = +(td.getAttribute('data-sinal') || 1);
      td.textContent = a === null || !b ? '' : br(a * sg / b * 100, 1) + '%';
    });
    document.querySelectorAll('input.ed[data-campo]:not([data-k])').forEach(function (el) {
      if (el === document.activeElement) return;
      var v = pega(cen, el.getAttribute('data-campo'));
      el.value = v === undefined || v === null || v === '' ? '0,00' : br(+v, 2); ajusta(el);
    });
  }
  function ajusta(el) { el.style.width = Math.max(el.value.length, 3) + 0.6 + 'ch'; }

  var aviso = document.querySelector('.editado'), msg = aviso && aviso.querySelector('span');
  function marca(sim, txt) {
    editado = sim;
    document.body.classList.toggle('mexido', sim);
    if (aviso) { aviso.hidden = !sim && !txt; if (msg) msg.textContent = txt || 'Números editados. Os gráficos seguem o cenário original.'; }
  }
  function escreve(el) {
    var x = numero(el.value); if (x === null) return;
    var campo = el.getAttribute('data-campo'), modo = el.getAttribute('data-modo') || 'set';
    var i = el.getAttribute('data-linha'), l = i === null ? null : cen.linhas[+i];
    if (modo === 'set') poe(cen, campo, x);
    else if (modo === 'esp') { l.preco_especifico = Motor.r2(x); delete l.mc_especifica; }
    else if (modo === 'camp') {
      l.preco_especifico = Motor.r2(+el.getAttribute('data-teto') - +(el.getAttribute('data-sinal') || 1) * x); delete l.mc_especifica;
    }
    else if (modo === 'tat') {
      var u = +el.getAttribute('data-usado'), sinal = +(el.getAttribute('data-sinal') || 1);
      l.preco_praticado = Motor.r2(u - sinal * x); delete l.desconto;
    }
    var c = Camadas.calcular(cen);
    if (c.erro) { marca(true, 'Com esse número a conta não fecha: ' + c.erro); return; }
    // a política e o tático partem do preço de cada nível: guarda o de agora para a próxima edição
    document.querySelectorAll('input.ed[data-modo="camp"],input.ed[data-modo="tat"]').forEach(function (e) {
      var j = +e.getAttribute('data-linha'), v = c.vendas[j];
      e.setAttribute('data-teto', v.topo.preco); e.setAttribute('data-usado', v.usado.preco);
    });
    pinta(Camadas.valores(c));
    marca(true);
  }
  document.addEventListener('input', function (ev) {
    var el = ev.target; if (!el.classList || !el.classList.contains('ed')) return;
    ajusta(el); escreve(el);
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Enter' && ev.target.classList && ev.target.classList.contains('ed')) ev.target.blur();
  });
  document.addEventListener('focusout', function (ev) {
    if (ev.target.classList && ev.target.classList.contains('ed')) { var c = Camadas.calcular(cen); if (!c.erro) pinta(Camadas.valores(c)); }
  });
  var volta = document.querySelector('.editado button');
  if (volta) volta.addEventListener('click', function () {
    cen = JSON.parse(JSON.stringify(ORIG));
    var c = Camadas.calcular(cen);
    document.querySelectorAll('input.ed[data-modo="camp"],input.ed[data-modo="tat"]').forEach(function (e) {
      var v = c.vendas[+e.getAttribute('data-linha')]; e.setAttribute('data-teto', v.topo.preco); e.setAttribute('data-usado', v.usado.preco);
    });
    pinta(Camadas.valores(c)); marca(false);
  });
  document.querySelectorAll('input.ed').forEach(ajusta);

  // as abas da DRE da venda, uma por produto
  document.querySelectorAll('.abas button').forEach(function (b) {
    b.addEventListener('click', function () {
      var i = b.getAttribute('data-aba');
      document.querySelectorAll('.abas button').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
      document.querySelectorAll('.dre-venda').forEach(function (d) { d.hidden = d.getAttribute('data-i') !== i; });
    });
  });

  // os nomes: a escolha de cada linha fica neste navegador e troca o nome da primeira coluna
  var CHAVE = 'bunker-pricing-nomes', esc = {};
  try { esc = JSON.parse(localStorage.getItem(CHAVE) || '{}') || {}; } catch (e) { esc = {}; }
  function nomes() {
    document.querySelectorAll('tr[data-nm]').forEach(function (tr) {
      var op = esc[tr.getAttribute('data-nm')], nome = tr.querySelector('.nome');
      tr.querySelectorAll('button.nm').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-src') === op ? 'true' : 'false'); });
      var alvo = op && tr.querySelector('button.nm[data-src="' + op + '"]');
      if (nome) nome.textContent = alvo ? alvo.getAttribute('data-nome') : nome.getAttribute('data-padrao');
    });
  }
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest && ev.target.closest('button.nm'); if (!b) return;
    var id = b.closest('tr').getAttribute('data-nm'), src = b.getAttribute('data-src');
    if (esc[id] === src) delete esc[id]; else esc[id] = src;
    try { localStorage.setItem(CHAVE, JSON.stringify(esc)); } catch (e) { /* sem armazenamento, a escolha vale só nesta tela */ }
    nomes();
  });
  nomes();
})();
