from prompts import CODING_SYSTEM, GENERAL_SYSTEM


class Specialist:
    def __init__(self, ollama, model: str, system_prompt: str, temperature: float):
        self.ollama = ollama
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature

    def answer(self, user_text: str) -> str:
        return self.ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=self.temperature,
        )


class AgentManager:
    def __init__(
        self,
        ollama,
        coding_model: str,
        general_model: str,
        temperature: float,
    ):
        self.agents = {
            "coding": Specialist(
                ollama, coding_model, CODING_SYSTEM, temperature
            ),
            "general": Specialist(
                ollama, general_model, GENERAL_SYSTEM, temperature
            ),
        }

    def answer(self, specialist: str, user_text: str) -> str:
        return self.agents[specialist].answer(user_text)
