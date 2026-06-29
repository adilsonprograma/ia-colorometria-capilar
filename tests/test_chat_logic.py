import unittest

from chat_logic import (
    ConversationState,
    build_formula_profile,
    build_protocol_response,
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

    def test_build_formula_profile_supports_numeric_color_code(self) -> None:
        formula_profile = build_formula_profile("Quero chegar no 7.4", "castanho")

        self.assertEqual(formula_profile.base_tone, "5")
        self.assertEqual(formula_profile.natural_tone, "7")
        self.assertEqual(formula_profile.fantasy_tone, "0.4")
        self.assertEqual(formula_profile.approximate_result, "7.4")
        self.assertEqual(formula_profile.oxidant_volume, 20)

    def test_build_formula_profile_maps_acaju_to_marsala_reflection(self) -> None:
        formula_profile = build_formula_profile("Quero um acaju profundo", "castanho")

        self.assertEqual(formula_profile.natural_tone, "5")
        self.assertEqual(formula_profile.fantasy_tone, "0.5")
        self.assertEqual(formula_profile.approximate_result, "5.5")

    def test_protocol_for_acaju_uses_marsala_family_guidance(self) -> None:
        response = build_protocol_response(
            ConversationState(
                step=4,
                base_color="castanho",
                target_color="acaju",
                technique="coloracao sem descolorir",
                water_test="meio",
            )
        )

        self.assertIn("Reflexo sugerido: 0.5 (acaju ou marsala).", response)
        self.assertIn("Cor desejada aproximada: 5.5.", response)
        self.assertIn("Para manter marsala, preserve reflexos vermelho-violeta sem neutralizar demais.", response)

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
        self.assertIn("Leitura da numeracao", result.response)
        self.assertIn("Quimica da formula", result.response)
        self.assertIn("Estrela de Oswald", result.response)
        self.assertIn(
            "Altura de tom sugerida: 10 (loiro clarissimo).",
            result.response,
        )
        self.assertIn(
            "Reflexo sugerido: 0.11 (acinzentado intenso).",
            result.response,
        )
        self.assertIn(
            "Cor desejada aproximada: 10.11.",
            result.response,
        )
        self.assertIn(
            "Formula em gramas: 30 g do tom natural 10 + 30 g da nuance 0.11 = 60 g de coloracao.",
            result.response,
        )
        self.assertIn(
            "OX pela leitura da elevacao: 40 volumes. Clareia ate 4 tons.",
            result.response,
        )
        self.assertIn(
            "Pela regra do projeto, OX = 1,5 vezes o total da coloracao (proporcao 1:1,5): 60 x 1.5 = 90 g de oxidante.",
            result.response,
        )
        self.assertIn(
            "Regra do 11 para mix ou matizador: 11 - 10 = 1.",
            result.response,
        )
        self.assertIn(
            "Mecanismo de acao",
            result.response,
        )
        self.assertIn(
            "Abertura: o alcalinizante eleva o pH e abre as cuticulas.",
            result.response,
        )
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
