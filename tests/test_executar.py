"""Conferir a sequência do comando único sem regenerar dados nem aceder à rede."""

import subprocess
import unittest
from unittest.mock import patch

import executar


class ExecutarTests(unittest.TestCase):
    def test_runs_all_steps_in_order(self):
        with patch("executar.subprocess.run") as run:
            self.assertEqual(executar.main(), 0)
        scripts = [call.args[0][-1] for call in run.call_args_list]
        self.assertEqual(scripts, [str(executar.ROOT / script) for _, script in executar.ETAPAS])
        self.assertTrue(all(call.kwargs["check"] for call in run.call_args_list))

    def test_stops_before_weather_if_verification_fails(self):
        error = subprocess.CalledProcessError(1, "verificar_resultados.py")
        with patch("executar.subprocess.run", side_effect=[None, error]) as run:
            self.assertEqual(executar.main(), 1)
        self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
