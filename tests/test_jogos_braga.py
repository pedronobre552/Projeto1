"""Conferir erros que poderiam omitir jogos ou inventar horários na extração."""

import unittest

from aquisicao.obter_jogos_braga import extrair


def linha(numero, hora="20:15"):
    return (f'<tr><td>1</td><td>sex 13/08/2010</td><td>{hora}</td><td>C</td>'
            '<td></td><td></td><td class="no-border-links hauptlink">'
            '<a title="Adversário">Adversário</a></td><td>4-4-2</td>'
            f'<td><a class="ergebnis-link" href="/spielbericht/index/spielbericht/{numero}">3:1</a></td></tr>')


def pagina(n_liga=30, hora="20:15", taca="Taça de Portugal"):
    return (f'<html><div class="box"><h2>Liga Portugal</h2><table>'
            + ''.join(linha(i, hora) for i in range(n_liga))
            + f'</table></div><div class="box"><h2>{taca}</h2><table>'
            + linha(100) + '</table></div><div class="box"><h2>Allianz Cup</h2><table>'
            + linha(101) + '</table></div></html>')


class JogosTests(unittest.TestCase):
    def test_preserva_resultado_adversario_data_e_proveniencia(self):
        jogos, contagens = extrair(pagina(), 2010)
        self.assertEqual(len(jogos), 32)
        self.assertEqual(contagens["Liga Portugal"], 30)
        self.assertEqual(jogos[0]["data"], "2010-08-13")
        self.assertEqual(jogos[0]["adversario"], "Adversário")
        self.assertEqual(jogos[0]["resultado_fonte"], "3:1")
        self.assertTrue(jogos[0]["url_fonte"].endswith("/spielbericht/0"))

    def test_hora_desconhecida_nao_vira_meia_noite(self):
        jogos, _ = extrair(pagina(hora="-"), 2010)
        self.assertEqual(jogos[0]["hora_inicio_portugal"], "")

    def test_jogo_antigo_sem_classe_css_de_resultado_nao_e_omitido(self):
        jogos, _ = extrair(pagina().replace('class="ergebnis-link"', 'class=""'), 2010)
        self.assertEqual(len(jogos), 32)

    def test_jornada_em_falta_interrompe(self):
        with self.assertRaisesRegex(ValueError, "esperados 30"):
            extrair(pagina(n_liga=29), 2010)

    def test_competicao_desconhecida_nao_entra_silenciosamente(self):
        with self.assertRaisesRegex(ValueError, "competição não reconhecida"):
            extrair(pagina(taca="Amigáveis"), 2010)

    def test_data_invalida_interrompe(self):
        with self.assertRaises(ValueError):
            extrair(pagina().replace("13/08/2010", "99/99/2010"), 2010)


if __name__ == "__main__":
    unittest.main()
