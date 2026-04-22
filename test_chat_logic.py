import unittest

from chat_logic import (
    ConversationState,
    detect_base_color,
    detect_technique,
    detect_water_test,
    process_input,
)


class ChatLogicTests(unittest.TestCase):
    def test_detect_base_color_accepts_common_synonyms(self) -> None:
        self.assertEqual(detect_base_color("Meu cabelo e moreno escuro"), "castanho")
        self.assertEqual(detect_base_color("Estou loira"), "loiro")
        self.assertEqual(detect_base_color("Tenho fios canosos"), "grisalho")

    def test_detect_technique_accepts_common_terms(self) -> None:
        self.assertEqual(detect_technique("Quero fazer balayage"), "balayage")
        self.assertEqual(detect_technique("Vou de descoloracao global"), "descoloracao global")
        self.assertEqual(detect_technique("Preciso de retoque na raiz"), "retoque de raiz")

    def test_detect_water_test_accepts_common_terms(self) -> None:
        self.assertEqual(detect_water_test("O fio boia"), "boia")
        self.assertEqual(detect_water_test("Ele ficou no meio do copo"), "meio")
        self.assertEqual(detect_water_test("A mecha afunda rapido"), "afunda")

    def test_first_step_updates_context_when_base_color_is_found(self) -> None:
        result = process_input("Castanho medio", ConversationState())

        self.assertEqual(result.state.step, 1)
        self.assertEqual(result.state.base_color, "castanho")
        self.assertIn("Sua base atual e castanho", result.response)

    def test_second_step_asks_for_technique(self) -> None:
        result = process_input(
            "Loiro platinado",
            ConversationState(step=1, base_color="preto"),
        )

        self.assertEqual(result.state.step, 2)
        self.assertEqual(result.state.target_color, "Loiro platinado")
        self.assertIn("qual tecnica", result.response.lower())

    def test_full_protocol_includes_oswald_formula_and_water_plan(self) -> None:
        result = process_input(
            "afunda",
            ConversationState(
                step=3,
                base_color="preto",
                target_color="Loiro platinado",
                technique="descoloracao global",
            ),
        )

        self.assertEqual(result.state.step, 4)
        self.assertEqual(result.state.water_test, "afunda")
        self.assertIn("Estrela de Oswald", result.response)
        self.assertIn("30 g de cor natural + 30 g de cor fantasia", result.response)
        self.assertIn("alta porosidade", result.response)
        self.assertIn("descoloracao global", result.response)

    def test_restart_resets_state_from_any_step(self) -> None:
        result = process_input(
            "Reiniciar",
            ConversationState(
                step=4,
                base_color="loiro",
                target_color="matizacao",
                technique="mechas",
                water_test="meio",
            ),
        )

        self.assertTrue(result.restart)
        self.assertEqual(result.state.step, 0)
        self.assertEqual(result.state.base_color, "")


if __name__ == "__main__":
    unittest.main()
