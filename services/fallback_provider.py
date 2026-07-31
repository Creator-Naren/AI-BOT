class FallbackProvider:
    def generate_reply(self, message):
        normalized = message.lower()
        if "hello" in normalized or "hi" in normalized:
            return "Hello! I am running in fallback mode and ready to help."
        if "project" in normalized:
            return "Great project idea. Tell me what module you want to build next."
        if "help" in normalized:
            return "I can help with coding guidance, explanations, and planning."
        return "I am in local fallback mode right now. Please share more details and I will help."
